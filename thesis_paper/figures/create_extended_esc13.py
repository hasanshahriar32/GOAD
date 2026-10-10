#!/usr/bin/env python3
"""
Generate an ultra-high quality, publication-grade diagram for the ESC13 Case Study.
Extends the original defense presentation slide with:
1. Complete 4-Hop Attack Chain with entity cards & exact AD relation types.
2. Direct Failure Annotations at specific hops (BloodHound state explosion at nesting, Certipy blind spot at OID).
3. The Atomic Invariant banner (Every permission is benign in isolation).
4. The Honest 4-Way Paradigm Audit:
   - Certipy (0% ESC13, 63.3% Community)
   - BloodHound (Exponential BFS State Explosion)
   - Pure GNN (80.0%, Succumbs to Shortcut Learning on Hard Negatives: 1.59%)
   - CertGraph-Hybrid (100.0%, 343 ms Screening + 128 ms Symbolic Proof = 0% FP)
5. Theorem 2 Stackelberg Remediation Cut on the rogue DACL ACE.
6. Real Enterprise Benchmarks from Chapter 6 (GOAD Multi-Domain, 30/30 External, 63/63 Temporal).
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
import numpy as np
import os

OUTPUT_DIR = '/home/hs32/Desktop/GOAD/thesis_paper/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)
OUTPUT_IMG = os.path.join(OUTPUT_DIR, 'esc13_benchmark_extended.png')

# Colors matching the presentation theme
TEAL_HEADER = '#0f766e'      # Identity objects header
NAVY_HEADER = '#1e3a5f'      # PKI objects header
DARK_SLATE  = '#0f172a'
MID_SLATE   = '#334155'
LIGHT_SLATE = '#64748b'
CARD_BG     = '#ffffff'
CARD_EDGE   = '#cbd5e1'
GOLD_ACCENT = '#d97706'      # BFS State explosion / warnings
CRIMSON     = '#dc2626'      # Certipy failure / attack arrows
GREEN_VERIF = '#059669'      # CertGraph Hybrid success
PURPLE_OID  = '#831843'      # ESC13 Policy OID
RED_TARGET  = '#991b1b'      # Tier-0 Target / Domain Admins

def draw_card(ax, x, y, w, h, title, title_bg, body_lines, radius=0.08, shadow=True):
    """Draw a slide-styled entity card with colored header and white body."""
    if shadow:
        shadow_box = FancyBboxPatch(
            (x - w/2 + 0.07, y - h/2 - 0.07), w, h,
            boxstyle=f"round,pad=0.0,rounding_size={radius}",
            facecolor='#000000', edgecolor='none', alpha=0.06, zorder=2
        )
        ax.add_patch(shadow_box)

    body_box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor=CARD_BG, edgecolor=CARD_EDGE, linewidth=1.4, zorder=3
    )
    ax.add_patch(body_box)

    header_h = h * 0.30
    header_box = FancyBboxPatch(
        (x - w/2, y + h/2 - header_h), w, header_h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor=title_bg, edgecolor='none', zorder=4
    )
    ax.add_patch(header_box)

    header_cover = patches.Rectangle(
        (x - w/2, y + h/2 - header_h), w, header_h * 0.4,
        facecolor=title_bg, edgecolor='none', zorder=4
    )
    ax.add_patch(header_cover)

    ax.text(x, y + h/2 - header_h/2, title,
            ha='center', va='center', fontsize=11.2, fontweight='bold',
            color='white', zorder=5)

    line_y = y + h/2 - header_h - 0.22
    for text, style, color, size in body_lines:
        weight = 'bold' if 'bold' in style else 'normal'
        ax.text(x, line_y, text,
                ha='center', va='center', fontsize=size,
                fontweight=weight, color=color, family='monospace' if 'mono' in style else 'sans-serif',
                zorder=5)
        line_y -= 0.28


def draw_arrow(ax, x1, y1, x2, y2, label='', sublabel='', color='#334155', lw=2.2, dashed=False,
               label_offset=0.22, sublabel_offset=-0.22, label_color=None):
    """Draw an arrow between attack chain nodes with step labels."""
    linestyle = '--' if dashed else '-'
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=5.5,head_width=3.5",
        color=color, linewidth=lw, linestyle=linestyle, zorder=4
    )
    ax.add_patch(arrow)

    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    lcol = label_color or color
    if label:
        ax.text(mx, my + label_offset, label,
                ha='center', va='center', fontsize=8.2,
                color=lcol, fontweight='bold', zorder=6,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                          edgecolor=color, alpha=0.95, lw=0.8))
    if sublabel:
        ax.text(mx, my + sublabel_offset, sublabel,
                ha='center', va='center', fontsize=7.5,
                color=MID_SLATE, style='italic', zorder=6)


def generate_diagram():
    fig_w, fig_h = 19.2, 10.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # ========================================================================
    # 1. SLIDE HEADER
    # ========================================================================
    ax.text(0.8, 10.35, "The Multi-Hop Attack Challenge: ESC13 Case Study",
            fontsize=23, fontweight='bold', color='#0f172a', ha='left', va='center')
    ax.text(0.8, 9.95, "Diagnostic Benchmark: Why Flat Scanners and Pure GNNs Fail on Composite Paths  |  Evaluated on Game of Active Directory (GOAD)",
            fontsize=11.2, color='#475569', ha='left', va='center')

    # Tag on top-right
    tag_box = FancyBboxPatch(
        (13.2, 9.85), 5.2, 0.45,
        boxstyle="round,pad=0.06",
        facecolor='#f1f5f9', edgecolor='#94a3b8', linewidth=1.0, zorder=3
    )
    ax.add_patch(tag_box)
    ax.text(15.8, 10.07, "Threat Vector: SpecterOps / Oliveau (2024) · Thesis §2.6 & §6.1",
            ha='center', va='center', fontsize=8.2, color='#334155', fontweight='bold', zorder=4)

    # ========================================================================
    # 2. TOP SECTION: THE 5-NODE ESC13 ATTACK CHAIN
    # ========================================================================
    chain_y = 8.10
    node_w = 3.0
    node_h = 1.65

    # 5 Node positions horizontally
    n_xs = [2.2, 5.8, 9.5, 13.2, 16.9]

    # Node 1: Identity Principal
    draw_card(ax, n_xs[0], chain_y, node_w, node_h,
              "Identity Principal", TEAL_HEADER,
              [
                  ("Low-Priv User", 'bold', DARK_SLATE, 10.0),
                  ("Compromised foothold", '', MID_SLATE, 8.2),
                  ("Domain Users group", 'mono', TEAL_HEADER, 8.0)
              ])

    # Node 2: Security Group
    draw_card(ax, n_xs[1], chain_y, node_w, node_h,
              "Security Group", TEAL_HEADER,
              [
                  ("Enroller Group", 'bold', DARK_SLATE, 10.0),
                  ("Intermediate group", '', MID_SLATE, 8.2),
                  ("Holds template DACL", 'mono', TEAL_HEADER, 8.0)
              ])

    # Node 3: Certificate Template (ESC13)
    draw_card(ax, n_xs[2], chain_y, node_w, node_h,
              "Certificate Template", NAVY_HEADER,
              [
                  ("ESC13 Template", 'bold', DARK_SLATE, 10.0),
                  ("Target template object", '', MID_SLATE, 8.2),
                  ("msPKI-Cert-Policy OID", 'mono', NAVY_HEADER, 8.0)
              ])

    # Node 4: Issuance Policy OID
    draw_card(ax, n_xs[3], chain_y, node_w, node_h,
              "Issuance Policy OID", PURPLE_OID,
              [
                  ("Policy OID Object", 'bold', DARK_SLATE, 10.0),
                  ("Issuance policy mapping", '', MID_SLATE, 8.2),
                  ("Linked to target group", 'mono', PURPLE_OID, 8.0)
              ])

    # Node 5: Tier-0 Target (Crown Jewel)
    draw_card(ax, n_xs[4], chain_y, node_w, node_h,
              "Tier-0 Target Asset", RED_TARGET,
              [
                  ("Domain Admins", 'bold', DARK_SLATE, 10.0),
                  ("Tier-0 crown jewel", '', MID_SLATE, 8.2),
                  ("Full forest takeover", 'mono', RED_TARGET, 8.0)
              ])

    # ========================================================================
    # 3. ATTACK CHAIN STEP ARROWS & ANNOTATIONS
    # ========================================================================
    # Arrow 1: User -> Group
    draw_arrow(ax, n_xs[0] + node_w/2, chain_y, n_xs[1] - node_w/2, chain_y,
               label="Step 1: MemberOf", sublabel="Transitive nesting", color='#0f172a', lw=2.2)

    # Arrow 2: Group -> Template
    draw_arrow(ax, n_xs[1] + node_w/2, chain_y, n_xs[2] - node_w/2, chain_y,
               label="Step 2: Enroll", sublabel="DACL ACE permission", color='#0f172a', lw=2.2,
               label_offset=0.26, sublabel_offset=-0.26)

    # Cut marker on Arrow 2 (The Stackelberg Remediation Edge!)
    cut_x = (n_xs[1] + node_w/2 + n_xs[2] - node_w/2) / 2
    ax.scatter([cut_x], [chain_y], s=260, marker='X', color=CRIMSON, zorder=8, edgecolors='#ffffff', linewidths=2.0)
    ax.text(cut_x, chain_y + 0.68, "[CUT] Theorem 2 Cut\n(Minimal-cost ACE revocation)",
            ha='center', va='center', fontsize=7.0, fontweight='bold', color=CRIMSON,
            bbox=dict(boxstyle='round,pad=0.14', facecolor='#fef2f2', edgecolor=CRIMSON, lw=0.9), zorder=9)

    # Arrow 3: Template -> Policy OID (The Novel ESC13 Edge)
    draw_arrow(ax, n_xs[2] + node_w/2, chain_y, n_xs[3] - node_w/2, chain_y,
               label="Step 3: LinksPolicy", sublabel="OID pointer link", color=CRIMSON, lw=2.8, label_color=CRIMSON)

    # Arrow 4: Policy OID -> Domain Admins
    draw_arrow(ax, n_xs[3] + node_w/2, chain_y, n_xs[4] - node_w/2, chain_y,
               label="Step 4: PAC Elevate", sublabel="Kerberos SID injection", color=CRIMSON, lw=2.8, label_color=CRIMSON)

    # ========================================================================
    # 4. FAILURE CALLOUTS POINTING DIRECTLY TO THE HOPS
    # ========================================================================
    # BloodHound failure callout below Step 1
    callout_bh = FancyBboxPatch(
        (2.6, 6.25), 3.8, 0.72,
        boxstyle="round,pad=0.06",
        facecolor='#fffbeb', edgecolor=GOLD_ACCENT, linewidth=1.4, zorder=4
    )
    ax.add_patch(callout_bh)
    ax.text(4.5, 6.72, "[FAILURE] BloodHound State Explosion",
            ha='center', va='center', fontsize=8.2, fontweight='bold', color='#b45309', zorder=5)
    ax.text(4.5, 6.45, "BFS suffers 2^k combinatorial explosion on deep group\nnestings (>100K objects) -> Out-of-Memory / Timeout",
            ha='center', va='center', fontsize=7.2, color='#78350f', zorder=5, linespacing=1.1)

    # Arrow pointing from callout to Step 1 arrow
    ax.annotate('', xy=(4.0, chain_y - 0.28), xytext=(4.0, 6.97),
                arrowprops=dict(arrowstyle='->', color=GOLD_ACCENT, lw=1.2, linestyle='--'))

    # Certipy failure callout below Step 3
    callout_cp = FancyBboxPatch(
        (9.8, 6.25), 3.8, 0.72,
        boxstyle="round,pad=0.06",
        facecolor='#fef2f2', edgecolor=CRIMSON, linewidth=1.4, zorder=4
    )
    ax.add_patch(callout_cp)
    ax.text(11.7, 6.72, "[FAILURE] Certipy Blind Spot (0% Detection)",
            ha='center', va='center', fontsize=8.2, fontweight='bold', color=CRIMSON, zorder=5)
    ax.text(11.7, 6.45, "Evaluates template in isolation; static signature engine\nlacks logic to resolve msPKI-Certificate-Policy references",
            ha='center', va='center', fontsize=7.2, color='#7f1d1d', zorder=5, linespacing=1.1)

    # Arrow pointing from callout to Step 3 arrow
    ax.annotate('', xy=(11.35, chain_y - 0.28), xytext=(11.35, 6.97),
                arrowprops=dict(arrowstyle='->', color=CRIMSON, lw=1.2, linestyle='--'))

    # ========================================================================
    # 5. ATOMIC INVARIANT CALLOUT BANNER
    # ========================================================================
    inv_banner = FancyBboxPatch(
        (0.8, 5.40), fig_w - 1.6, 0.50,
        boxstyle="round,pad=0.06",
        facecolor='#0f172a', edgecolor='none', zorder=3
    )
    ax.add_patch(inv_banner)
    ax.text(fig_w/2, 5.65,
            "THE CORE VULNERABILITY INVARIANT: Every permission is benign in isolation. No single object is misconfigured. "
            "The threat exists ONLY as a composite multi-hop path closure.",
            ha='center', va='center', fontsize=8.8, fontweight='bold', color='#f8fafc', zorder=4)

    # ========================================================================
    # 6. MIDDLE/BOTTOM SECTION: THE 4-WAY PARADIGM AUDIT
    # ========================================================================
    col_w = 4.15
    col_h = 3.25
    col_y = 3.45

    col_xs = [2.7, 7.2, 11.7, 16.2]

    # --- Column 1: Certipy Heuristics ---
    col1_lines = [
        ("Static rule-based scanner", '', MID_SLATE, 8.2),
        ("Evaluates objects in isolation", '', MID_SLATE, 8.2),
        ("Blind to LDAP OID pointers", 'bold', CRIMSON, 8.2),
        ("Blind to Kerberos PAC SID inject", '', MID_SLATE, 8.0),
        ("ESC13 Detection: 0.0% (Missed)", 'bold', CRIMSON, 8.5),
        ("Community Accuracy: 63.3%", 'bold', '#991b1b', 8.5)
    ]
    draw_card(ax, col_xs[0], col_y, col_w, col_h,
              "1. Heuristic Scanner (Certipy)", CRIMSON, col1_lines)

    badge1 = FancyBboxPatch((col_xs[0] - 1.6, col_y - col_h/2 - 0.18), 3.2, 0.36,
                            boxstyle="round,pad=0.04", facecolor='#fef2f2', edgecolor=CRIMSON, linewidth=1.1, zorder=6)
    ax.add_patch(badge1)
    ax.text(col_xs[0], col_y - col_h/2, "0% Detection (False Negative)", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color=CRIMSON, zorder=7)

    # --- Column 2: BloodHound Graph BFS ---
    col2_lines = [
        ("Deterministic graph traversal", '', MID_SLATE, 8.2),
        ("Exhaustive shortest-path BFS", '', MID_SLATE, 8.2),
        ("Explodes on deep group nesting", 'bold', '#b45309', 8.2),
        ("O(b^d) combinatorial search", 'mono', '#b45309', 8.0),
        ("Intractable on 100K+ entities", 'bold', '#b45309', 8.5),
        ("Memory exhaustion / Timeout", 'bold', '#92400e', 8.5)
    ]
    draw_card(ax, col_xs[1], col_y, col_w, col_h,
              "2. Graph Search (BloodHound)", GOLD_ACCENT, col2_lines)

    badge2 = FancyBboxPatch((col_xs[1] - 1.6, col_y - col_h/2 - 0.18), 3.2, 0.36,
                            boxstyle="round,pad=0.04", facecolor='#fffbeb', edgecolor=GOLD_ACCENT, linewidth=1.1, zorder=6)
    ax.add_patch(badge2)
    ax.text(col_xs[1], col_y - col_h/2, "Combinatorial State Explosion", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color='#b45309', zorder=7)

    # --- Column 3: Pure GNN (Deep Learning Alone) ---
    col3_lines = [
        ("Inductive neural screening", '', MID_SLATE, 8.2),
        ("Sub-second forward pass (343 ms)", '', MID_SLATE, 8.2),
        ("Detects ESC13 composite path", 'bold', '#1e40af', 8.2),
        ("SUCCUMBS TO SHORTCUT LEARNING", 'bold', CRIMSON, 8.2),
        ("Hard Negatives: 1.59% Acc (Collapses)", 'bold', CRIMSON, 8.5),
        ("Overall Community Acc: 80.0%", 'bold', MID_SLATE, 8.5)
    ]
    draw_card(ax, col_xs[2], col_y, col_w, col_h,
              "3. Pure GNN (Neural Alone)", '#475569', col3_lines)

    badge3 = FancyBboxPatch((col_xs[2] - 1.6, col_y - col_h/2 - 0.18), 3.2, 0.36,
                            boxstyle="round,pad=0.04", facecolor='#f1f5f9', edgecolor='#475569', linewidth=1.1, zorder=6)
    ax.add_patch(badge3)
    ax.text(col_xs[2], col_y - col_h/2, "Shortcut Learning Vulnerability", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color='#334155', zorder=7)

    # --- Column 4: CertGraph-Hybrid (Our Proposed System) ---
    col4_lines = [
        ("Two-Tier Neuro-Symbolic Engine", 'bold', GREEN_VERIF, 8.2),
        ("Tier 1: 343 ms GNN screening (<25 ms/1k)", '', MID_SLATE, 8.2),
        ("Tier 2: 128 ms sound symbolic proof", 'bold', '#047857', 8.2),
        ("Eliminates shortcut false alarms", '', MID_SLATE, 8.0),
        ("Zero False Positives (100% Prec)", 'bold', GREEN_VERIF, 8.5),
        ("Community Accuracy: 100.0% (30/30)", 'bold', GREEN_VERIF, 8.5)
    ]
    draw_card(ax, col_xs[3], col_y, col_w, col_h,
              "4. CertGraph-Hybrid (Ours)", GREEN_VERIF, col4_lines)

    badge4 = FancyBboxPatch((col_xs[3] - 1.6, col_y - col_h/2 - 0.18), 3.2, 0.36,
                            boxstyle="round,pad=0.04", facecolor='#ecfdf5', edgecolor=GREEN_VERIF, linewidth=1.1, zorder=6)
    ax.add_patch(badge4)
    ax.text(col_xs[3], col_y - col_h/2, "100% Detection & 0% False Positives", ha='center', va='center',
            fontsize=8.0, fontweight='bold', color=GREEN_VERIF, zorder=7)

    # ========================================================================
    # 7. BOTTOM PANEL: REAL-WORLD EMPIRICAL VERIFICATION (GOAD DATA)
    # ========================================================================
    bot_y = 0.70
    bot_box = FancyBboxPatch(
        (0.8, bot_y - 0.40), fig_w - 1.6, 0.80,
        boxstyle="round,pad=0.06",
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=2
    )
    ax.add_patch(bot_box)

    ax.text(1.2, bot_y + 0.16, "VERIFIED EMPIRICAL PERFORMANCE ON ENTERPRISE TESTBEDS (Thesis Chapter 6):",
            fontsize=9.2, fontweight='bold', color='#0f172a', ha='left', va='center')

    metrics = [
        ("External Community Data", "30/30 (100.0%)", "+36.7% vs Certipy (BloodHound-CE)"),
        ("Longitudinal Drift Stability", "63/63 (100.0%)", "56-Day Longitudinal Evaluation"),
        ("Multi-Domain Forests (GOAD)", "100.0% Accuracy", "sevenkingdoms, north, essos"),
        ("Sub-Second Latency", "343 ms Sweep", "O(1) Depth vs BloodHound Timeout")
    ]

    m_start = 1.2
    m_step = 4.35
    for i, (m_title, m_val, m_desc) in enumerate(metrics):
        mx = m_start + i * m_step
        ax.text(mx, bot_y - 0.08, m_title + ":", fontsize=8.0, fontweight='bold', color='#334155')
        ax.text(mx, bot_y - 0.26, m_val + "  ·  " + m_desc, fontsize=7.2, color='#059669', fontweight='bold')

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(OUTPUT_IMG, bbox_inches='tight', dpi=300, facecolor='#ffffff')
    plt.close()
    print(f"Successfully generated: {OUTPUT_IMG}")

if __name__ == '__main__':
    generate_diagram()
