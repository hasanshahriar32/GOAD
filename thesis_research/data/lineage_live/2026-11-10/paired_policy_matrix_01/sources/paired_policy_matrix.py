"""Hold the signed CSR/key fixed across policy intervention conditions.

Extends the frozen first matrix without overwriting its attempts or changing
the original collector. Readiness checks address observed RPC transport errors;
they do not retry or discard an unfavorable certificate/authentication outcome.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import subprocess
import time

from .live_policy_matrix import Runner, ROOT, digest, dump, freeze as base_freeze
from scripts.capture_trace7_split_actor_delayed_pkinit import pull_file_winrm


class PairedRunner(Runner):
    def __init__(self,args,output):
        super().__init__(args,output)
        self.matrix_root=output
        self.request_cache={}
        self.active_trial=None

    def run_trial(self,trial,original):
        self.active_trial=trial
        return super().run_trial(trial,original)

    def ps(self,session,name,script,required=True):
        if name=="99_remove_private_export":
            match=re.search(r"Remove-Item '([^']+)'",script)
            if match:
                script=f"if(Test-Path '{match.group(1)}'){{Remove-Item '{match.group(1)}'}}; 'PRIVATE_EXPORT_ABSENT'"
        if name=="07_csr":
            match=re.search(r"WriteAllText\('([^']+)\.inf'",script)
            if not match:raise ValueError("Unexpected CSR creation script")
            remote=match.group(1)+".req"
            trial=self.active_trial
            key=(trial["id"].split("_",1)[0],trial["requested_upn"])
            if key in self.request_cache:
                raw=self.request_cache[key]
                before=time.time()
                self.push(session,raw,remote,"07_reused_csr")
                result={"host_before":before,"host_after":time.time(),"returncode":0,
                        "stdout":"Identical signed CSR reused from this intervention block", "stderr":"",
                        "request_sha256":hashlib.sha256(raw).hexdigest()}
                dump(self.output/(name+".json"),result)
            else:
                result=super().ps(session,name,script,required)
                raw=pull_file_winrm(self.dc,remote)
                self.request_cache[key]=raw
            (self.output/"request.csr").write_bytes(raw)
            dump(self.output/"request_binding.json",{"block":key[0],"requested_upn":key[1],
                 "request_sha256":hashlib.sha256(raw).hexdigest(),"scope":"Identical signed request bytes and public key across the administrative policy conditions in this block"})
            return result
        result=super().ps(session,name,script,required)
        if name=="05_controlled_cache_refresh":
            # Test the same enrollment RPC interface as the same low-privilege
            # submitter, before the single request attempt recorded for a trial.
            probe="""$ready=$false
for($attempt=0;$attempt -lt 15;$attempt++) {
  & certutil.exe -config 'braavos.essos.local\CertGraph-Lab-CA' -ping
  if($LASTEXITCODE -eq 0){$ready=$true;break}
  Start-Sleep -Seconds 2
}
if(-not $ready){throw 'CA_ENROLLMENT_RPC_NOT_READY'}
'RPC_READY'"""
            super().ps(self.submitter,"05_lowpriv_rpc_readiness",probe)
        return result

    def state(self,name):
        state=super().state(name)
        script="""$nc=(Get-ADRootDSE).configurationNamingContext
$t=Get-ADObject -Identity ('CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Properties *
@{dn=$t.DistinguishedName;name_flag=[int]$t.'msPKI-Certificate-Name-Flag';enrollment_flag=$t.'msPKI-Enrollment-Flag';ra_signatures=$t.'msPKI-RA-Signature';eku=$t.pKIExtendedKeyUsage;sddl=$t.nTSecurityDescriptor.GetSecurityDescriptorSddlForm('All');template_oid=$t.'msPKI-Cert-Template-OID'} | ConvertTo-Json -Compress -Depth 6"""
        super().ps(self.dc,name+"_effective_policy",script)
        return state


def freeze(path,repeats):
    base_freeze(path,repeats)
    protocol=json.loads(path.read_text())
    protocol.update(schema=2,request_control="Reuse identical signed CSR bytes within each repeat and requested UPN; no replayed certificate or private-key export substitution",
                    readiness_control="Successful enrollment RPC ping as the submitter before the single request attempt; preserve all failures",
                    source_sha256={**protocol["source_sha256"],str(Path(__file__).relative_to(ROOT)):digest(Path(__file__))})
    dump(path,protocol)


def run(args):
    protocol=json.loads(args.protocol.read_text())
    for name,expected in protocol["source_sha256"].items():
        if digest(ROOT/name)!=expected:raise ValueError("Frozen source changed: "+name)
    args.output.mkdir(parents=True,exist_ok=False)
    dump(args.output/"protocol.json",protocol)
    snapshots=args.output/"sources";snapshots.mkdir()
    for name in protocol["source_sha256"]:
        (snapshots/Path(name).name).write_bytes((ROOT/name).read_bytes())
    version=subprocess.run([args.certipy,"-v"],capture_output=True,text=True,check=True)
    dump(args.output/"tool_versions.json",{"certipy":(version.stdout+version.stderr).strip(),"scope":protocol["scope"]})
    runner=PairedRunner(args,args.output)
    original=runner.state("00_initial_state")["name_flag"]
    if original!=protocol["original_name_flag_required"]:raise ValueError("Unexpected baseline")
    results=[]
    for trial in protocol["trials"]:
        runner.output=args.output/trial["id"]
        outcome=runner.run_trial(trial,original)
        results.append(outcome);dump(args.output/"progress.json",results)
        print(json.dumps({k:outcome.get(k) for k in ("id","status","restored","privileged_san_present","error")}),flush=True)
        if not outcome["restored"] or outcome["status"]=="infrastructure_error":break
    dump(args.output/"run_manifest.json",{"protocol_sha256":digest(args.protocol),"trials_attempted":len(results),"trials_planned":len(protocol["trials"]),"scope":protocol["scope"]})


if __name__=="__main__":
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="action",required=True)
    f=sub.add_parser("freeze");f.add_argument("protocol",type=Path);f.add_argument("--repeats",type=int,default=3)
    r=sub.add_parser("run");r.add_argument("protocol",type=Path);r.add_argument("output",type=Path)
    r.add_argument("--dc-url",required=True);r.add_argument("--ca-url",required=True);r.add_argument("--certipy",required=True)
    r.add_argument("--ldap-ip",required=True);r.add_argument("--ldap-port",type=int,default=1389);r.add_argument("--auth-ip",default="127.0.0.2")
    args=parser.parse_args()
    if args.action=="freeze":
        if args.repeats<1:parser.error("Positive repetitions required")
        freeze(args.protocol,args.repeats)
    else:run(args)
