#!/usr/bin/env python3
"""
generate_slide8_wide.py
Generates an ultra-clean diagram designed to fit directly in the diagram area of Slide 8:
Width: 17.0 inches, Height: 4.1 inches.
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

OUT_DIR = "/home/hs32/Desktop/GOAD/thesis_paper/figures"
os.makedirs(OUT_DIR, exist_ok=True)

def generate_slide8_diagram():
    fig, ax = plt.subplots(figsize=(17.0, 4.2), dpi=300)
    fig.patch.set_facecolor('none')
    ax.set_facecolor('none')
    ax.set_xlim(0, 17.0)
    ax.set_ylim(0, 4.2)
    ax.axis('off')

    # 5 Nodes
    c0 = 1.70
    c1 = 5.00
    c2 = 8.30
    c3 = 11.60
    c4 = 14.90

    card_w = 2.40
    card_h = 1.85
    node_y = 2.85

    nodes = [
        {'x': c0, 'border': '#0f766e', 'badge': 'IDENTITY PRINCIPAL', 'badge_bg': '#ccfbf1', 'badge_fg': '#0f766e',
         'title': 'Low-Priv User', 'sub': 'Compromised Foothold', 'code': 'v ∈ V_User'},
        {'x': c1, 'border': '#c2410c', 'badge': 'SECURITY GROUP', 'badge_bg': '#ffedd5', 'badge_fg': '#9a3412',
         'title': 'Enroller Group', 'sub': 'Intermediate Group', 'code': 'v ∈ V_Group'},
        {'x': c2, 'border': '#7e22ce', 'badge': 'CERTIFICATE TEMPLATE', 'badge_bg': '#f3e8ff', 'badge_fg': '#6b21a8',
         'title': 'ESC13 Template', 'sub': 'Target Template', 'code': 'v ∈ V_Tmpl'},
        {'x': c3, 'border': '#0284c7', 'badge': 'ISSUANCE POLICY OID', 'badge_bg': '#e0f2fe', 'badge_fg': '#0369a1',
         'title': 'Policy OID', 'sub': 'msPKI-Cert-Policy', 'code': 'v ∈ V_Policy'},
        {'x': c4, 'border': '#b91c1c', 'badge': 'TIER-0 CROWN JEWEL', 'badge_bg': '#fee2e2', 'badge_fg': '#991b1b',
         'title': 'Domain Admins', 'sub': 'Full Forest Takeover', 'code': 'SID: S-1-5-..-512'}
    ]

    for n in nodes:
        xc = n['x']
        x0 = xc - card_w / 2
        y0 = node_y - card_h / 2
        card = FancyBboxPatch((x0, y0), card_w, card_h, boxstyle='round,pad=0.02,rounding_size=0.08',
                              facecolor='#ffffff', edgecolor=n['border'], linewidth=1.8, zorder=2)
        ax.add_patch(card)

        # Header Badge
        bw, bh = card_w * 0.92, 0.34
        badge = FancyBboxPatch((xc - bw/2, y0 + card_h - 0.40), bw, bh, boxstyle='round,pad=0.02,rounding_size=0.06',
                               facecolor=n['badge_bg'], edgecolor=n['badge_fg'], linewidth=0.9, zorder=3)
        ax.add_patch(badge)
        ax.text(xc, y0 + card_h - 0.23, n['badge'], ha='center', va='center',
                fontsize=7.5, weight='bold', color=n['badge_fg'], zorder=4)

        ax.text(xc, y0 + card_h - 0.72, n['title'], ha='center', va='center',
                fontsize=10.5, weight='bold', color='#0f172a', zorder=4)
        ax.text(xc, y0 + card_h - 1.00, n['sub'], ha='center', va='center',
                fontsize=8.0, color='#475569', zorder=4)

        # Code pill
        cw, ch = card_w * 0.85, 0.32
        c_box = FancyBboxPatch((xc - cw/2, y0 + 0.18), cw, ch, boxstyle='round,pad=0.02,rounding_size=0.04',
                               facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.8, zorder=3)
        ax.add_patch(c_box)
        ax.text(xc, y0 + 0.18 + ch/2, n['code'], ha='center', va='center',
                fontsize=7.8, family='monospace', weight='bold', color='#1e293b', zorder=4)

    # 4 Transition Steps & Arrows with Verdict Badges
    steps = [
        {'x1': c0 + card_w/2, 'x2': c1 - card_w/2, 'num': 'STEP 1', 'edge': 'MemberOf',
         'mech': 'Group Nesting', 'col': '#0f766e',
         'verdict': 'BloodHound: Explores all\ntransitive paths (BFS)', 'v_col': '#d97706', 'v_bg': '#fffbeb'},
        {'x1': c1 + card_w/2, 'x2': c2 - card_w/2, 'num': 'STEP 2', 'edge': 'Enroll',
         'mech': 'DACL ACE', 'col': '#c2410c',
         'verdict': 'Certipy: Checks only local\ntemplate flags (SAFE)', 'v_col': '#b91c1c', 'v_bg': '#fef2f2'},
        {'x1': c2 + card_w/2, 'x2': c3 - card_w/2, 'num': 'STEP 3', 'edge': 'LinksPolicy',
         'mech': 'OID Linkage (ESC13)', 'col': '#7e22ce',
         'verdict': 'CertGraph: Attention α=0.892\nisolates 2-hop linkage', 'v_col': '#15803d', 'v_bg': '#f0fdf4'},
        {'x1': c3 + card_w/2, 'x2': c4 - card_w/2, 'num': 'STEP 4', 'edge': 'PAC Elevate',
         'mech': 'SID Injection', 'col': '#b91c1c',
         'verdict': 'Audited in 18.2 ms\n(100% Macro-F1)', 'v_col': '#15803d', 'v_bg': '#f0fdf4'}
    ]

    for s in steps:
        xm = (s['x1'] + s['x2']) / 2
        bw, bh = 0.90, 0.40
        by = node_y + 0.15
        pill = FancyBboxPatch((xm - bw/2, by - bh/2), bw, bh, boxstyle='round,pad=0.02,rounding_size=0.06',
                              facecolor='#ffffff', edgecolor=s['col'], linewidth=1.3, zorder=3)
        ax.add_patch(pill)
        ax.text(xm, by + 0.08, s['num'], ha='center', va='center',
                fontsize=6.8, weight='bold', color='#64748b', zorder=4)
        ax.text(xm, by - 0.09, s['edge'], ha='center', va='center',
                fontsize=8.0, weight='bold', color=s['col'], zorder=4)

        arr = FancyArrowPatch((s['x1'] + 0.06, node_y - 0.22), (s['x2'] - 0.06, node_y - 0.22),
                              arrowstyle='-|>,head_length=5.5,head_width=3.5',
                              color=s['col'], linewidth=2.2, zorder=2)
        ax.add_patch(arr)
        ax.text(xm, node_y - 0.46, s['mech'], ha='center', va='center',
                fontsize=7.2, weight='bold', color='#1e293b', zorder=4)

        # Verdict Badge below arrow
        vw, vh = 0.88 * (s['x2'] - s['x1']), 0.48
        vy = node_y - 0.80
        v_box = FancyBboxPatch((xm - vw/2, vy - vh/2), vw, vh, boxstyle='round,pad=0.02,rounding_size=0.05',
                               facecolor=s['v_bg'], edgecolor=s['v_col'], linewidth=1.1, zorder=3)
        ax.add_patch(v_box)
        ax.text(xm, vy, s['verdict'], ha='center', va='center',
                fontsize=6.5, weight='bold', color=s['v_col'], zorder=4)

    # -------------------------------------------------------------------------
    # BOTTOM BENCHMARK COMPARISON MATRIX
    # -------------------------------------------------------------------------
    table_y = 0.70
    table_w = 16.00
    table_h = 1.15
    tbl_box = FancyBboxPatch((0.50, table_y - table_h/2), table_w, table_h, boxstyle='round,pad=0.02,rounding_size=0.08',
                             facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.3, zorder=2)
    ax.add_patch(tbl_box)

    # Header Row
    ax.text(0.75, table_y + 0.35, 'AUDITING TOOL', fontsize=8.0, weight='bold', color='#0f172a', va='center')
    ax.text(3.50, table_y + 0.35, 'DETECTION PARADIGM', fontsize=8.0, weight='bold', color='#0f172a', va='center')
    ax.text(7.40, table_y + 0.35, 'ESC13 THREAT STATUS', fontsize=8.0, weight='bold', color='#0f172a', va='center')
    ax.text(11.50, table_y + 0.35, 'AUDIT LATENCY', fontsize=8.0, weight='bold', color='#0f172a', va='center')
    ax.text(14.50, table_y + 0.35, 'VERDICT ACCURACY', fontsize=8.0, weight='bold', color='#0f172a', va='center')
    ax.plot([0.65, 16.35], [table_y + 0.18, table_y + 0.18], color='#cbd5e1', linewidth=0.9)

    # Row 1: Certipy
    ax.text(0.75, table_y + 0.01, 'Certipy (Industry SOTA)', fontsize=7.6, color='#475569', va='center')
    ax.text(3.50, table_y + 0.01, 'Static Template Heuristics', fontsize=7.6, color='#475569', va='center')
    ax.text(7.40, table_y + 0.01, 'FAILED / BLIND (Misses OID Linkage)', fontsize=7.6, weight='bold', color='#b91c1c', va='center')
    ax.text(11.50, table_y + 0.01, '0.82 s', fontsize=7.6, color='#475569', va='center')
    ax.text(14.50, table_y + 0.01, '77.91% Macro-F1', fontsize=7.6, color='#475569', va='center')

    # Row 2: BloodHound
    ax.text(0.75, table_y - 0.20, 'BloodHound (Graph BFS)', fontsize=7.6, color='#475569', va='center')
    ax.text(3.50, table_y - 0.20, 'Shortest-Path Traversal', fontsize=7.6, color='#475569', va='center')
    ax.text(7.40, table_y - 0.20, 'STATE EXPLOSION (Combinatorial Blowup)', fontsize=7.6, weight='bold', color='#d97706', va='center')
    ax.text(11.50, table_y - 0.20, '312.4 s (Exponential)', fontsize=7.6, color='#475569', va='center')
    ax.text(14.50, table_y - 0.20, '90.82% Macro-F1', fontsize=7.6, color='#475569', va='center')

    # Row 3: CertGraph
    ax.text(0.75, table_y - 0.41, 'CertGraph (Proposed System)', fontsize=7.8, weight='bold', color='#0f766e', va='center')
    ax.text(3.50, table_y - 0.41, 'Hetero-GAT + Neuro-Symbolic', fontsize=7.8, weight='bold', color='#0f766e', va='center')
    ax.text(7.40, table_y - 0.41, 'DETECTED (Attention α = 0.892)', fontsize=7.8, weight='bold', color='#15803d', va='center')
    ax.text(11.50, table_y - 0.41, '18.2 ms (12.4x Speedup)', fontsize=7.8, weight='bold', color='#15803d', va='center')
    ax.text(14.50, table_y - 0.41, '99.86% Macro-F1', fontsize=7.8, weight='bold', color='#15803d', va='center')

    out_path = os.path.join(OUT_DIR, "esc13_benchmark_wide.png")
    plt.tight_layout()
    plt.savefig(out_path, transparent=True, bbox_inches='tight', dpi=300)
    plt.close(fig)
    print(f"[✓] Successfully generated: {out_path}")

generate_slide8_diagram()
