#!/usr/bin/env python3
"""
verify_live_traces_ingestion.py — Verifies live traces with upgraded CIPG engine
================================================================================
Ingests the 5 live captured traces and tests:
1. Trace 1 (ESC4 Rollback): flags CONFIRMED_EXPLOIT_ROLLBACK (Level 1, is_attack=True)
2. Trace 2 (ESC9 UPN Swap): flags CONFIRMED_EXPLOIT_ROLLBACK or UNEXPLOITED_CONFIG_DRIFT
3. Trace 4 (Benign Admin Typo): flags UNEXPLOITED_CONFIG_DRIFT (Level 2, is_attack=False, FPR=0%)
4. Trace 5 (Benign Normal Enrollment): flags 0 invariant violations
"""

import os
import sys
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD')

from thesis_research.src.phase3_cipg.models import CrossLayerGraph
from thesis_research.src.phase3_cipg.event_parser import ProvenanceEventParser
from thesis_research.src.phase3_cipg.invariants import InvariantEngine

DATA_DIR = "/home/m4x1d/Desktop/GOAD/thesis_research/data/live_goad_traces"
traces = [
    ("Trace 1: ESC4 Rollback Full", "trace_esc4_rollback_full.xml"),
    ("Trace 2: ESC9 UPN Swap Rollback", "trace_esc9_upn_swap_rollback.xml"),
    ("Trace 3: ESC6 CA Flag Abuse", "trace_esc6_ca_flag_abuse.xml"),
    ("Trace 4: Benign Admin Typo Rollback", "trace_benign_admin_typo_rollback.xml"),
    ("Trace 5: Benign Normal Enrollment", "trace_benign_normal_enrollment.xml"),
]

engine = InvariantEngine(delta_window_sec=300.0)

print("="*78)
print(" VERIFYING LIVE GOAD TRACES IN UPGRADED CIPG ENGINE")
print("="*78)

for label, filename in traces:
    filepath = os.path.join(DATA_DIR, filename)
    if not os.path.exists(filepath):
        print(f"[-] {label}: File NOT found: {filepath}")
        continue

    graph = CrossLayerGraph()
    count = ProvenanceEventParser.ingest_xml_stream(filepath, graph)
    violations = engine.evaluate_all(graph)

    attacks = [v for v in violations if v.is_attack]
    drifts = [v for v in violations if not v.is_attack]

    print(f"\n[*] {label} ({filename})")
    print(f"    - Ingested Events:    {count}")
    print(f"    - LDAP Mutations:     {len(graph.ldap_mutations)}")
    print(f"    - CA Issuances:       {len(graph.ca_issuances)}")
    print(f"    - PKINIT / Logons:    {len(graph.pkinit_auths)} PKINIT, {len(graph.logon_sessions)} Logons")
    print(f"    - Attack Alerts:      {len(attacks)}")
    for a in attacks:
        print(f"      [CRITICAL ALERT] {a.invariant_name} ({a.attack_class}): {a.description}")
    print(f"    - Audit Warnings:     {len(drifts)}")
    for d in drifts:
        print(f"      [INFORMATIONAL]  {d.invariant_name} ({d.attack_class}): {d.description}")

print("\n" + "="*78)
