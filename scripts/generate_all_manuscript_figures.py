#!/usr/bin/env python3
"""
generate_manuscript_figures.py
Generates the publication-grade figures for the 7-figure suite of CertGraph:
1. certgraph_architecture_diagram.png (Enhanced with Bilinear Gating & Tier-2 Verifier)
2. cipg_architecture_diagram.png (Cross-Layer Directory, PKI, KDC, Jet DB Bridge & Invariant V)
3. gnn_ablation_and_hard_negatives.png (2-Panel: Skip/Perturbation Asymmetry & HN Per-Category Breakdown)
4. cipg_sensitivity_and_cone_scaling.png (2-Panel: 2D Sensitivity Heatmap & Min-Cut Scalability Speedup)
"""

import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = '/home/m4x1d/Desktop/GOAD/thesis_paper/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 11.0
plt.rcParams['text.color'] = '#0f172a'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.0

# =============================================================================
# 1. ENHANCED CERTGRAPH ARCHITECTURE DIAGRAM (Figure 2 in Paper)
# =============================================================================
def generate_certgraph_arch():
    fig_w, fig_h = 13.0, 7.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    BOX_BG = '#ffffff'
    BORDER_COLOR = '#1e293b'
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    ACCENT_RED = '#991b1b'
    ACCENT_BLUE = '#1d4ed8'
    ACCENT_GREEN = '#047857'

    col_h = 6.6
    col_y = 3.8
    col_w = 2.9
    col_gap = 0.32
    left_m = (fig_w - (4 * col_w + 3 * col_gap)) / 2

    col_xcs = [left_m + col_w / 2 + i * (col_w + col_gap) for i in range(4)]

    # --- Section 1: Input Heterogeneous Identity Graph ---
    s1_xc = col_xcs[0]
    box1 = patches.Rectangle((s1_xc - col_w/2, col_y - col_h/2), col_w, col_h,
                             facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2)
    ax.add_patch(box1)
    hdr1 = patches.Rectangle((s1_xc - col_w/2, col_y + col_h/2 - 0.55), col_w, 0.55,
                             facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3)
    ax.add_patch(hdr1)
    ax.text(s1_xc, col_y + col_h/2 - 0.28, "1. Input Multigraph", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(s1_xc, col_y + 2.35, r"$\mathcal{G} = (\mathcal{V}, \mathcal{E}, \phi, \psi)$",
            ha='center', va='center', fontsize=13.0, weight='bold', color=TEXT_MAIN)

    g_nodes = [
        (s1_xc - 0.8, col_y + 1.5, 'User', 'o', '#e2e8f0'),
        (s1_xc + 0.8, col_y + 1.6, 'Group', '^', '#e2e8f0'),
        (s1_xc - 0.7, col_y + 0.6, 'Comp', 's', '#e2e8f0'),
        (s1_xc + 0.1, col_y + 1.05, 'Tmpl', 'D', '#fee2e2'),
        (s1_xc + 0.85, col_y + 0.5, 'CA', 'h', '#e2e8f0'),
    ]
    ax.plot([s1_xc - 0.8, s1_xc + 0.8], [col_y + 1.5, col_y + 1.6], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc - 0.8, s1_xc + 0.1], [col_y + 1.5, col_y + 1.05], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc + 0.8, s1_xc + 0.1], [col_y + 1.6, col_y + 1.05], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc - 0.7, s1_xc + 0.1], [col_y + 0.6, col_y + 1.05], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc + 0.1, s1_xc + 0.85], [col_y + 1.05, col_y + 0.5], color='#64748b', lw=1.6, zorder=3)

    for gx, gy, glbl, gshape, gcol in g_nodes:
        ax.plot(gx, gy, marker=gshape, markersize=24, color=gcol,
                markeredgecolor=BORDER_COLOR, markeredgewidth=1.4, zorder=4)
        ax.text(gx, gy, glbl, ha='center', va='center', fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=5)

    ax.text(s1_xc, col_y - 0.15, "5 Entity Types / 16 Relations\n(DACLs, Enrollment, OID Links)",
            ha='center', va='center', fontsize=10.5, weight='bold', color=TEXT_MUTED, linespacing=1.2)

    proj_box = patches.Rectangle((s1_xc - 1.3, col_y - 3.0), 2.6, 2.3,
                                 facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=3)
    ax.add_patch(proj_box)
    ax.text(s1_xc, col_y - 1.0, "Type Projections:", ha='center', va='center',
            fontsize=11.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s1_xc, col_y - 1.6, r"$\mathbf{z}_u = \mathbf{W}_{\phi(u)}^{(0)} \mathbf{x}_u \in \mathbb{R}^d$",
            ha='center', va='center', fontsize=11.5, color=TEXT_MAIN, zorder=4)
    ax.text(s1_xc, col_y - 2.2, r"Template: $\mathbf{x}_t \in \{0, 1\}^{10}$",
            ha='center', va='center', fontsize=10.5, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(s1_xc, col_y - 2.7, "Flag Features: SAN, EKU, Approvals",
            ha='center', va='center', fontsize=9.5, color=TEXT_MUTED, zorder=4)

    arrow1 = patches.FancyArrowPatch((s1_xc + col_w/2, col_y), (col_xcs[1] - col_w/2, col_y),
                                     arrowstyle="-|>,head_length=7.0,head_width=5.0",
                                     color=BORDER_COLOR, linewidth=1.8, zorder=5)
    ax.add_patch(arrow1)

    # --- Section 2: Hetero-GAT with Theorem 1 Skips ---
    s2_xc = col_xcs[1]
    box2 = patches.Rectangle((s2_xc - col_w/2, col_y - col_h/2), col_w, col_h,
                             facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2)
    ax.add_patch(box2)
    hdr2 = patches.Rectangle((s2_xc - col_w/2, col_y + col_h/2 - 0.55), col_w, 0.55,
                             facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3)
    ax.add_patch(hdr2)
    ax.text(s2_xc, col_y + col_h/2 - 0.28, "2. Relational Attention", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN, zorder=4)

    mha_box = patches.Rectangle((s2_xc - 1.3, col_y + 0.35), 2.6, 2.3,
                                facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.2, zorder=3)
    ax.add_patch(mha_box)
    ax.text(s2_xc, col_y + 2.35, "Relational Multi-Head (MHA)", ha='center', va='center',
            fontsize=11.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y + 1.9, r"Heads $K=4, \; d_{\mathrm{head}} = 16$",
            ha='center', va='center', fontsize=10.5, color=TEXT_MUTED, zorder=4)
    ax.text(s2_xc, col_y + 1.35,
            r"$\alpha_{vu}^{(k,r)} = \operatorname{Softmax}_{\mathcal{N}_r(v)}\left(e_{vu}^{(k,r)}\right)$",
            ha='center', va='center', fontsize=11.0, color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y + 0.75,
            r"$e_{vu}^{(k,r)} = \operatorname{LeakyReLU}\left(\mathbf{a}_k^\top [\mathbf{z}_v \| \mathbf{z}_u]\right)$",
            ha='center', va='center', fontsize=10.5, color=TEXT_MAIN, zorder=4)

    skip_box = patches.Rectangle((s2_xc - 1.3, col_y - 3.0), 2.6, 2.9,
                                 facecolor='#eff6ff', edgecolor=ACCENT_BLUE, linewidth=1.2, zorder=3)
    ax.add_patch(skip_box)
    ax.text(s2_xc, col_y - 0.35, "Theorem 3.1 Residual Skip:", ha='center', va='center',
            fontsize=11.5, weight='bold', color=ACCENT_BLUE, zorder=4)
    ax.text(s2_xc, col_y - 0.95, r"$\tilde{\mathbf{h}}_v^{(l)} = \mathbf{h}_v^{(l)} + \mathbf{W}_{\mathrm{skip}}^{(l)} \tilde{\mathbf{h}}_v^{(l-1)}$",
            ha='center', va='center', fontsize=11.0, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y - 1.6, r"$\sigma_{\min}\left(\frac{\partial \tilde{\mathbf{h}}_v^{(L)}}{\partial \mathbf{x}_v}\right) \geq \prod \sigma_{\min}(\mathbf{W}_{\mathrm{skip}}) > 0$",
            ha='center', va='center', fontsize=10.0, color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y - 2.2, "Preserves Attribute Sensitivity",
            ha='center', va='center', fontsize=10.5, weight='bold', color=ACCENT_BLUE, zorder=4)
    ax.text(s2_xc, col_y - 2.7, "Cures pure feature erasure",
            ha='center', va='center', fontsize=9.5, style='italic', color=TEXT_MUTED, zorder=4)

    arrow2 = patches.FancyArrowPatch((s2_xc + col_w/2, col_y), (col_xcs[2] - col_w/2, col_y),
                                     arrowstyle="-|>,head_length=7.0,head_width=5.0",
                                     color=BORDER_COLOR, linewidth=1.8, zorder=5)
    ax.add_patch(arrow2)

    # --- Section 3: Multiplicative Bilinear Gating (The Cure) ---
    s3_xc = col_xcs[2]
    box3 = patches.Rectangle((s3_xc - col_w/2, col_y - col_h/2), col_w, col_h,
                             facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2)
    ax.add_patch(box3)
    hdr3 = patches.Rectangle((s3_xc - col_w/2, col_y + col_h/2 - 0.55), col_w, 0.55,
                             facecolor='#fef2f2', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3)
    ax.add_patch(hdr3)
    ax.text(s3_xc, col_y + col_h/2 - 0.28, "3. Bilinear Reachability Gate", ha='center', va='center',
            fontsize=12.5, weight='bold', color=ACCENT_RED, zorder=4)

    gate_box = patches.Rectangle((s3_xc - 1.3, col_y + 0.35), 2.6, 2.3,
                                 facecolor='#fef2f2', edgecolor=ACCENT_RED, linewidth=1.3, zorder=3)
    ax.add_patch(gate_box)
    ax.text(s3_xc, col_y + 2.35, "Reachability Gating Matrix:", ha='center', va='center',
            fontsize=11.2, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(s3_xc, col_y + 1.75, r"$\mathbf{g}_{uv} = \sigma\left(\mathbf{h}_u^{\top} \mathbf{W}_g \mathbf{h}_v + b_g\right)$",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y + 1.15, r"$\mathbf{m}_{vu}^{(l)} = \mathbf{g}_{uv}^{(l)} \odot \left(\mathbf{W}_r^{(l)} \mathbf{h}_u^{(l-1)}\right)$",
            ha='center', va='center', fontsize=11.0, color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y + 0.65, r"$\lim_{\mathbf{g} \to 0} \mathbf{m}_{vu} = \mathbf{0}$ (Zero-Out)",
            ha='center', va='center', fontsize=10.2, weight='bold', color=ACCENT_RED, zorder=4)

    cure_box = patches.Rectangle((s3_xc - 1.3, col_y - 3.0), 2.6, 2.9,
                                 facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, zorder=3)
    ax.add_patch(cure_box)
    ax.text(s3_xc, col_y - 0.35, "Curing Shortcut Collapse:", ha='center', va='center',
            fontsize=11.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y - 0.95, "Additive GNNs: 0.00% (0/63)\nMemorize flags, ignore paths",
            ha='center', va='center', fontsize=10.0, color=ACCENT_RED, linespacing=1.2, zorder=4)
    ax.text(s3_xc, col_y - 1.8, "Gated GNN: 65.08% (41/63)\nConditions aggregation on\nauthenticated reachability",
            ha='center', va='center', fontsize=10.0, weight='bold', color=ACCENT_GREEN, linespacing=1.2, zorder=4)
    ax.text(s3_xc, col_y - 2.65, "Resolves: Admin-Only, Deny,\nHorizon-4, Disabled Tmpls",
            ha='center', va='center', fontsize=9.2, color=TEXT_MUTED, linespacing=1.15, zorder=4)

    arrow3 = patches.FancyArrowPatch((s3_xc + col_w/2, col_y), (col_xcs[3] - col_w/2, col_y),
                                     arrowstyle="-|>,head_length=7.0,head_width=5.0",
                                     color=BORDER_COLOR, linewidth=1.8, zorder=5)
    ax.add_patch(arrow3)

    # --- Section 4: Neuro-Symbolic Verification & Output ---
    s4_xc = col_xcs[3]
    box4 = patches.Rectangle((s4_xc - col_w/2, col_y - col_h/2), col_w, col_h,
                             facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2)
    ax.add_patch(box4)
    hdr4 = patches.Rectangle((s4_xc - col_w/2, col_y + col_h/2 - 0.55), col_w, 0.55,
                             facecolor='#f0fdf4', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3)
    ax.add_patch(hdr4)
    ax.text(s4_xc, col_y + col_h/2 - 0.28, "4. Two-Tier Classification", ha='center', va='center',
            fontsize=13.0, weight='bold', color=ACCENT_GREEN, zorder=4)

    # GNN Head
    ax.text(s4_xc, col_y + 2.35, "Tier 1: Fast GNN Screener", ha='center', va='center',
            fontsize=11.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s4_xc, col_y + 1.85, r"$\hat{\mathbf{y}} = \operatorname{Softmax}(\operatorname{MLP}(\mathbf{h}_t)) \in \Delta^6$",
            ha='center', va='center', fontsize=11.0, color=TEXT_MAIN, zorder=4)

    # Tier 2 Verifier badge
    t2_badge = patches.FancyBboxPatch((s4_xc - 1.3, col_y + 0.35), 2.6, 1.1,
                                      boxstyle="round,pad=0.03,rounding_size=0.08",
                                      facecolor='#ecfdf5', edgecolor=ACCENT_GREEN, linewidth=1.3, zorder=3)
    ax.add_patch(t2_badge)
    ax.text(s4_xc, col_y + 1.1, "Tier 2: Symbolic Verifier", ha='center', va='center',
            fontsize=11.2, weight='bold', color=ACCENT_GREEN, zorder=4)
    ax.text(s4_xc, col_y + 0.65, "Resolves 22 residual cases\n(OID Links & CA Permissions) -> 100%",
            ha='center', va='center', fontsize=9.5, color=TEXT_MAIN, linespacing=1.15, zorder=4)

    # 7 Classes list
    esc_items = [
        ("Safe", ACCENT_GREEN, "Benign Baseline"),
        ("ESC1", ACCENT_RED, "Enrollee Supplies SAN"),
        ("ESC2", ACCENT_RED, "Any Purpose EKU"),
        ("ESC3", ACCENT_RED, "Cert Request Agent"),
        ("ESC4", ACCENT_RED, "DACL / WriteOwner"),
        ("ESC9", ACCENT_RED, "Shadow Credential"),
        ("ESC13", ACCENT_RED, "Policy OID Linkage"),
    ]
    y_start = col_y - 0.3
    row_h = 0.38
    for idx, (lbl, col, desc) in enumerate(esc_items):
        ry = y_start - (idx * row_h)
        badge = patches.FancyBboxPatch((s4_xc - 1.3, ry - 0.14), 0.7, 0.28,
                                       boxstyle="round,pad=0.02,rounding_size=0.04",
                                       facecolor='#fef2f2' if col == ACCENT_RED else '#f0fdf4',
                                       edgecolor=col, linewidth=1.1, zorder=3)
        ax.add_patch(badge)
        ax.text(s4_xc - 0.95, ry, lbl, ha='center', va='center',
                fontsize=9.5, weight='bold', color=col, zorder=4)
        ax.text(s4_xc - 0.5, ry, desc, ha='left', va='center',
                fontsize=9.5, color=TEXT_MAIN, zorder=4)

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'certgraph_architecture_diagram.png')
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[+] Successfully generated: {out_path}")


# =============================================================================
# 2. DEDICATED CIPG ARCHITECTURE DIAGRAM (Figure 4 in Paper)
# =============================================================================
def generate_cipg_architecture():
    fig_w, fig_h = 13.0, 7.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    BORDER_COLOR = '#1e293b'
    ACCENT_RED = '#b91c1c'
    ACCENT_BLUE = '#1d4ed8'
    ACCENT_GREEN = '#047857'

    # Background title header
    ax.text(fig_w/2, 7.4, "Cryptographic Invariant Provenance Graph (CIPG) & Cross-Layer Bridge",
            ha='center', va='center', fontsize=15.0, weight='bold', color=TEXT_MAIN)
    ax.text(fig_w/2, 7.05, r"Solving CA-KDC Schema Disjointness ($\pi_{\mathrm{CA}} \cap \pi_{\mathrm{KDC}} = \emptyset$) & Ephemeral Template Rollbacks",
            ha='center', va='center', fontsize=11.5, style='italic', color=TEXT_MUTED)

    # 3 Host/Service Column Boxes:
    # Col 1: DC03 Directory Service (NTDS) - LDAP Mutation & Rollback
    # Col 2: SRV03 Enterprise CA - Issuance & Jet DB Bridge
    # Col 3: DC03 Kerberos KDC - PKINIT Pre-Authentication
    box_w = 3.7
    box_h = 4.2
    y_box = 4.6

    # --- Column 1: DC03 Directory Layer ---
    c1_x = 0.55
    ax.add_patch(patches.Rectangle((c1_x, y_box - box_h/2), box_w, box_h,
                                   facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.4, zorder=2))
    ax.add_patch(patches.Rectangle((c1_x, y_box + box_h/2 - 0.5), box_w, 0.5,
                                   facecolor='#f1f5f9', edgecolor='#cbd5e1', linewidth=1.4, zorder=3))
    ax.text(c1_x + box_w/2, y_box + box_h/2 - 0.25, "1. Directory Layer (DC03)",
            ha='center', va='center', fontsize=12.0, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(c1_x + 0.2, y_box + 1.25, r"$\mathbf{t_1}$: Temporal LDAP Modification",
            ha='left', va='center', fontsize=10.5, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(c1_x + 0.2, y_box + 0.85, "Event 5136: Object Attribute Modified\nTemplate: ESC4-Vulnerable (WriteOwner)\nAttacker: ESSOS\\khal.drogo",
            ha='left', va='center', fontsize=9.2, color=TEXT_MUTED, linespacing=1.2, zorder=4)

    ax.text(c1_x + 0.2, y_box - 0.2, r"$\mathbf{t_3}$: Transient Rollback",
            ha='left', va='center', fontsize=10.5, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(c1_x + 0.2, y_box - 0.6, "Event 5136: Attribute Restored to Baseline",
            ha='left', va='center', fontsize=9.2, color=TEXT_MUTED, zorder=4)
    ax.text(c1_x + 0.2, y_box - 1.1, r"$\mathrm{SHA\text{-}256}(\mathcal{G}_{t_0}) = \mathrm{SHA\text{-}256}(\mathcal{G}_{t_3})$",
            ha='left', va='center', fontsize=10.2, weight='bold', color='#dc2626', zorder=4)
    ax.text(c1_x + 0.2, y_box - 1.6, "Static Periodic Scanners:\n0.0% Detection Recall (Completely Blind)",
            ha='left', va='center', fontsize=9.5, weight='bold', color=TEXT_MAIN, linespacing=1.2, zorder=4)

    # --- Column 2: SRV03 Enterprise CA Layer ---
    c2_x = 4.65
    ax.add_patch(patches.Rectangle((c2_x, y_box - box_h/2), box_w, box_h,
                                   facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.4, zorder=2))
    ax.add_patch(patches.Rectangle((c2_x, y_box + box_h/2 - 0.5), box_w, 0.5,
                                   facecolor='#f1f5f9', edgecolor='#cbd5e1', linewidth=1.4, zorder=3))
    ax.text(c2_x + box_w/2, y_box + box_h/2 - 0.25, "2. PKI Layer (SRV03 - CA)",
            ha='center', va='center', fontsize=12.0, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(c2_x + 0.2, y_box + 1.25, r"$\mathbf{t_2}$: Certificate Issuance",
            ha='left', va='center', fontsize=10.5, weight='bold', color=ACCENT_BLUE, zorder=4)
    ax.text(c2_x + 0.2, y_box + 0.75, "Event 4887: Certificate Issued\nRequester: ESSOS\\khal.drogo\nRequestId: 19 | Template: ESC1-Vuln",
            ha='left', va='center', fontsize=9.2, color=TEXT_MUTED, linespacing=1.2, zorder=4)

    # ASN.1 box
    asn_box = patches.FancyBboxPatch((c2_x + 0.15, y_box - 0.45), box_w - 0.3, 0.9,
                                     boxstyle="round,pad=0.03,rounding_size=0.06",
                                     facecolor='#fef2f2', edgecolor=ACCENT_RED, linewidth=1.1, zorder=3)
    ax.add_patch(asn_box)
    ax.text(c2_x + 0.25, y_box - 0.05, "PKCS#10 ASN.1 Concealment:", ha='left', va='center',
            fontsize=9.8, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(c2_x + 0.25, y_box - 0.32, "SAN (Administrator UPN) hidden in binary CSR;\nSuppressed from Event 4887 XML Attributes!",
            ha='left', va='center', fontsize=8.6, color=TEXT_MAIN, linespacing=1.15, zorder=4)

    # Jet DB Bridge box
    jet_box = patches.FancyBboxPatch((c2_x + 0.15, y_box - 1.75), box_w - 0.3, 1.1,
                                     boxstyle="round,pad=0.03,rounding_size=0.06",
                                     facecolor='#eff6ff', edgecolor=ACCENT_BLUE, linewidth=1.2, zorder=3)
    ax.add_patch(jet_box)
    ax.text(c2_x + 0.25, y_box - 1.35, "ICertView2 CA Database Bridge:", ha='left', va='center',
            fontsize=10.0, weight='bold', color=ACCENT_BLUE, zorder=4)
    ax.text(c2_x + 0.25, y_box - 1.65, r"$\tau_{\mathrm{crypto}} = \langle\mathrm{ReqID}, \mathrm{SKID}, \mathrm{Serial}, \mathrm{Thumb}\rangle$",
            ha='left', va='center', fontsize=9.2, weight='bold', color=TEXT_MAIN, zorder=4)

    # --- Column 3: DC03 KDC Layer ---
    c3_x = 8.75
    ax.add_patch(patches.Rectangle((c3_x, y_box - box_h/2), box_w, box_h,
                                   facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.4, zorder=2))
    ax.add_patch(patches.Rectangle((c3_x, y_box + box_h/2 - 0.5), box_w, 0.5,
                                   facecolor='#f1f5f9', edgecolor='#cbd5e1', linewidth=1.4, zorder=3))
    ax.text(c3_x + box_w/2, y_box + box_h/2 - 0.25, "3. KDC Layer (DC03 - PKINIT)",
            ha='center', va='center', fontsize=12.0, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(c3_x + 0.2, y_box + 1.25, r"$\mathbf{t_4}$: Kerberos Pre-Auth (PKINIT)",
            ha='left', va='center', fontsize=10.5, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(c3_x + 0.2, y_box + 0.75, "Event 4768: TGT Requested (PreAuth=16)\nTargetUser: Administrator\nCertSerialNumber: 19:00:00:00:1b\nCertThumbprint: 3f8a92...",
            ha='left', va='center', fontsize=9.2, color=TEXT_MUTED, linespacing=1.2, zorder=4)

    # Schema gap box
    gap_box = patches.FancyBboxPatch((c3_x + 0.15, y_box - 0.8), box_w - 0.3, 1.25,
                                     boxstyle="round,pad=0.03,rounding_size=0.06",
                                     facecolor='#fffbeb', edgecolor='#d97706', linewidth=1.1, zorder=3)
    ax.add_patch(gap_box)
    ax.text(c3_x + 0.25, y_box - 0.35, r"Proposition 2.1: $\pi_{\mathrm{CA}} \cap \pi_{\mathrm{KDC}} = \emptyset$",
            ha='left', va='center', fontsize=10.0, weight='bold', color='#b45309', zorder=4)
    ax.text(c3_x + 0.25, y_box - 0.72, "Event 4768 omits: RequestID & SKID\nEvent 4887 omits: Serial & Thumbprint\nSingle-host SIEM cannot correlate!",
            ha='left', va='center', fontsize=8.8, color=TEXT_MAIN, linespacing=1.2, zorder=4)

    # Cross-layer arrows
    arrow_c1_c2 = patches.FancyArrowPatch((c1_x + box_w, y_box + 0.8), (c2_x, y_box + 0.8),
                                          arrowstyle="-|>,head_length=6.0,head_width=4.5",
                                          color='#64748b', linewidth=1.6, zorder=5)
    ax.add_patch(arrow_c1_c2)
    ax.text((c1_x + box_w + c2_x)/2, y_box + 1.0, "Enables Req", ha='center', va='bottom', fontsize=8.5, weight='bold', color='#64748b')

    arrow_c2_c3 = patches.FancyArrowPatch((c2_x + box_w, y_box + 0.8), (c3_x, y_box + 0.8),
                                          arrowstyle="-|>,head_length=6.0,head_width=4.5",
                                          color='#64748b', linewidth=1.6, zorder=5)
    ax.add_patch(arrow_c2_c3)
    ax.text((c2_x + box_w + c3_x)/2, y_box + 1.0, "Presents Cert", ha='center', va='bottom', fontsize=8.5, weight='bold', color='#64748b')

    # --- Bottom Layer: Invariant V Automaton & Meta-Node Graph ---
    bot_y = 1.35
    bot_h = 2.1
    bot_w = 11.9
    bot_x = 0.55
    ax.add_patch(patches.Rectangle((bot_x, bot_y - bot_h/2), bot_w, bot_h,
                                   facecolor='#f8fafc', edgecolor=ACCENT_GREEN, linewidth=1.6, zorder=2))
    ax.add_patch(patches.Rectangle((bot_x, bot_y + bot_h/2 - 0.45), bot_w, 0.45,
                                   facecolor='#ecfdf5', edgecolor=ACCENT_GREEN, linewidth=1.6, zorder=3))
    ax.text(bot_x + bot_w/2, bot_y + bot_h/2 - 0.22,
            "4. Invariant V Automaton: Continuous Cross-Host Cryptographic Taint Tracking",
            ha='center', va='center', fontsize=12.5, weight='bold', color=ACCENT_GREEN, zorder=4)

    # 3 sub-cards inside bottom box
    sub_w = 3.65
    sub_gap = 0.25
    sub_y = bot_y - 0.22
    sub_h = 1.3

    # Sub 1: State Invariant Join
    s1_x = bot_x + 0.2
    ax.add_patch(patches.Rectangle((s1_x, sub_y - sub_h/2), sub_w, sub_h,
                                   facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.0, zorder=3))
    ax.text(s1_x + sub_w/2, sub_y + 0.45, "Continuous State Correlation", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s1_x + sub_w/2, sub_y - 0.05,
            r"$\tau_{\mathrm{join}} = \mathbf{e}_{4887} \bowtie_{\mathrm{ReqID}} \tau_{\mathrm{crypto}} \bowtie_{\mathrm{Thumb}} \mathbf{e}_{4768}$",
            ha='center', va='center', fontsize=9.2, weight='bold', color=ACCENT_BLUE, zorder=4)
    ax.text(s1_x + sub_w/2, sub_y - 0.45, "Bridges Disjoint KDC & CA Logs via Jet DB",
            ha='center', va='center', fontsize=8.5, color=TEXT_MUTED, zorder=4)

    # Sub 2: Invariant Check
    s2_x = s1_x + sub_w + sub_gap
    ax.add_patch(patches.Rectangle((s2_x, sub_y - sub_h/2), sub_w, sub_h,
                                   facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.0, zorder=3))
    ax.text(s2_x + sub_w/2, sub_y + 0.45, "Invariant V Violation Check", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s2_x + sub_w/2, sub_y - 0.05,
            r"$\mathrm{Viol}(\tau) \Longleftrightarrow \mathrm{Requester}(\mathbf{e}_{\mathrm{CA}}) \neq \mathrm{Target}(\mathbf{e}_{\mathrm{KDC}})$",
            ha='center', va='center', fontsize=9.2, weight='bold', color=ACCENT_RED, zorder=4)
    ax.text(s2_x + sub_w/2, sub_y - 0.45, "Flagged: 'khal.drogo' issued cert for 'Administrator'!",
            ha='center', va='center', fontsize=8.5, weight='bold', color=ACCENT_RED, zorder=4)

    # Sub 3: Meta-Node Compacting
    s3_x = s2_x + sub_w + sub_gap
    ax.add_patch(patches.Rectangle((s3_x, sub_y - sub_h/2), sub_w, sub_h,
                                   facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.0, zorder=3))
    ax.text(s3_x + sub_w/2, sub_y + 0.45, "Streaming Performance", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_x + sub_w/2, sub_y - 0.05,
            "100.0% Recall | 92.31% Precision\n76.61% Meta-Node Compression",
            ha='center', va='center', fontsize=9.2, weight='bold', color=ACCENT_GREEN, linespacing=1.2, zorder=4)
    ax.text(s3_x + sub_w/2, sub_y - 0.48, "Throughput: 13,192.4 events/sec (6.91 MB RAM)",
            ha='center', va='center', fontsize=8.2, color=TEXT_MUTED, zorder=4)

    # Connecting arrows from columns down to Invariant V box
    ax.add_patch(patches.FancyArrowPatch((c1_x + box_w/2, y_box - box_h/2), (s1_x + 0.8, bot_y + bot_h/2),
                                         arrowstyle="-|>,head_length=6.0,head_width=4.5",
                                         color='#64748b', linewidth=1.4, zorder=5))
    ax.add_patch(patches.FancyArrowPatch((c2_x + box_w/2, y_box - box_h/2), (s2_x + sub_w/2, bot_y + bot_h/2),
                                         arrowstyle="-|>,head_length=6.0,head_width=4.5",
                                         color=ACCENT_BLUE, linewidth=1.5, zorder=5))
    ax.add_patch(patches.FancyArrowPatch((c3_x + box_w/2, y_box - box_h/2), (s3_x + 1.2, bot_y + bot_h/2),
                                         arrowstyle="-|>,head_length=6.0,head_width=4.5",
                                         color='#64748b', linewidth=1.4, zorder=5))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'cipg_architecture_diagram.png')
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[+] Successfully generated: {out_path}")


# =============================================================================
# 3. GNN ABLATIONS & HARD NEGATIVES (Figure 5 in Paper)
# =============================================================================
def generate_gnn_ablation_and_hn():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.2), dpi=300)

    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    ACCENT_RED = '#b91c1c'
    ACCENT_BLUE = '#1d4ed8'
    ACCENT_GREEN = '#047857'

    # --- Panel (a): Residual Skip Ablation & Perturbation Asymmetry ---
    # Left inset / bar for skip ablation
    bar_x = [0.8, 1.8]
    bar_vals = [0.9986, 0.4768]
    bar_errs = [0.0029, 0.0532]
    colors = [ACCENT_BLUE, '#94a3b8']
    labels = [r'With Skips ($\mathbf{W}_{\mathrm{skip}} \neq \mathbf{0}$)', r'No Skips ($\mathbf{W}_{\mathrm{skip}} = \mathbf{0}$)']

    # We plot perturbation curves on ax1
    pert_x = [0, 5, 10, 20, 30]
    edge_drop_f1 = [0.9986, 0.9920, 0.9882, 0.9765, 0.9637]
    flag_flip_f1 = [0.9986, 0.8412, 0.7105, 0.5210, 0.4120]

    ax1.plot(pert_x, edge_drop_f1, marker='o', lw=2.2, color=ACCENT_BLUE,
             label='Edge-Drop Perturbation (Topology)')
    ax1.plot(pert_x, flag_flip_f1, marker='s', lw=2.2, color=ACCENT_RED, linestyle='--',
             label='Flag-Flip Perturbation (Configuration Attributes)')

    # Add text annotation about asymmetry
    ax1.annotate('Edge-Drop: 96.4% Retention\nat 30% Edge Removal',
                 xy=(30, 0.9637), xytext=(15, 0.91),
                 arrowprops=dict(arrowstyle="->", color=ACCENT_BLUE, lw=1.3),
                 fontsize=9.5, weight='bold', color=ACCENT_BLUE)

    ax1.annotate('Flag-Flip: Rapid Collapse\nto 0.7105 at 10% Flipping!',
                 xy=(10, 0.7105), xytext=(12, 0.65),
                 arrowprops=dict(arrowstyle="->", color=ACCENT_RED, lw=1.3),
                 fontsize=9.5, weight='bold', color=ACCENT_RED)

    # Inset bar chart for Theorem 1 W_skip ablation
    ax_ins = ax1.inset_axes([0.08, 0.12, 0.38, 0.42])
    ax_ins.bar([0, 1], bar_vals, yerr=bar_errs, capsize=4, color=colors, edgecolor='#1e293b', width=0.6)
    ax_ins.set_xticks([0, 1])
    ax_ins.set_xticklabels(['With Skips', r'$\mathbf{W}_{\mathrm{skip}}=0$'], fontsize=8.5, weight='bold')
    ax_ins.set_ylim(0, 1.15)
    ax_ins.set_ylabel('Macro-F1', fontsize=8.5)
    ax_ins.set_title(r'Theorem 3.1 ($p = 1.3\times 10^{-6}$)', fontsize=8.5, weight='bold')
    ax_ins.grid(axis='y', linestyle=':', alpha=0.5)
    for i, v in enumerate(bar_vals):
        ax_ins.text(i, v + 0.06, f"{v:.3f}", ha='center', fontsize=8.0, weight='bold')

    ax1.set_xlabel('Perturbation Rate (%)', fontsize=11.5, weight='bold')
    ax1.set_ylabel('5-Fold CV Macro-F1', fontsize=11.5, weight='bold')
    ax1.set_title('(a) Theorem 3.1 Ablation & Perturbation Asymmetry', fontsize=12.5, weight='bold', color=TEXT_MAIN)
    ax1.set_ylim(0.35, 1.05)
    ax1.grid(True, linestyle=':', alpha=0.6)
    ax1.legend(loc='lower left', fontsize=9.5, frameon=True)

    # --- Panel (b): Adversarial Hard-Negative Evaluation Breakdown (n=63) ---
    categories = [
        'Admin-Only\n(n=18)',
        'Explicit-Deny\n(n=10)',
        'Horizon-4\n(n=10)',
        'Disabled\n(n=3)',
        'OID-Links\n(n=15)',
        'Unenr. CA\n(n=7)',
        'Overall\n(n=63)'
    ]
    x_indices = np.arange(len(categories))
    width = 0.26

    # Accuracies in percentage
    acc_addskip = [0.0, 0.0, 0.0, 0.0, 0.0, 0.0, 0.0]
    acc_gated   = [100.0, 100.0, 100.0, 100.0, 0.0, 0.0, 65.08]
    acc_hybrid  = [100.0, 100.0, 100.0, 100.0, 100.0, 100.0, 100.0]

    b1 = ax2.bar(x_indices - width, acc_addskip, width, label='CertGraph-AddSkip (Additive)',
                 color='#ef4444', edgecolor='#b91c1c', alpha=0.85)
    b2 = ax2.bar(x_indices, acc_gated, width, label='CertGraph-Gated (Bilinear Gate)',
                 color='#3b82f6', edgecolor='#1d4ed8', alpha=0.9)
    b3 = ax2.bar(x_indices + width, acc_hybrid, width, label='Tier-2 Hybrid (Neuro-Symbolic)',
                 color='#10b981', edgecolor='#047857', alpha=0.9)

    ax2.set_xlabel('Adversarial Hard Negative Archetype', fontsize=11.5, weight='bold')
    ax2.set_ylabel('Classification Accuracy (%)', fontsize=11.5, weight='bold')
    ax2.set_title('(b) Zero-Shot Hard Negative Accuracy Breakdown', fontsize=12.5, weight='bold', color=TEXT_MAIN)
    ax2.set_xticks(x_indices)
    ax2.set_xticklabels(categories, fontsize=9.0, weight='bold')
    ax2.set_ylim(0, 120)
    ax2.grid(axis='y', linestyle=':', alpha=0.6)
    ax2.legend(loc='upper right', fontsize=9.2, frameon=True)

    # Highlight 65.08% and 100%
    ax2.text(x_indices[-1] - width, 5, '0.0%', ha='center', fontsize=8.0, weight='bold', color=ACCENT_RED)
    ax2.text(x_indices[-1], 70, '65.1%', ha='center', fontsize=8.5, weight='bold', color=ACCENT_BLUE)
    ax2.text(x_indices[-1] + width, 105, '100%', ha='center', fontsize=8.5, weight='bold', color=ACCENT_GREEN)

    # Annotate semantic crosstalk
    ax2.annotate('Multi-Attribute Semantic Crosstalk\n(Resolved by Tier-2 Symbolic Verifier)',
                 xy=(4.5, 30), xytext=(3.0, 50),
                 arrowprops=dict(arrowstyle="->", color='#64748b', lw=1.2),
                 fontsize=8.5, style='italic', color=TEXT_MUTED,
                 bbox=dict(boxstyle="round,pad=0.3", fc="#f8fafc", ec="#cbd5e1"))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'gnn_ablation_and_hard_negatives.png')
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[+] Successfully generated: {out_path}")


# =============================================================================
# 4. CIPG SENSITIVITY HEATMAP & MIN-CUT SCALABILITY (Figure 6 in Paper)
# =============================================================================
def generate_cipg_sensitivity_and_cone_scaling():
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(13.2, 5.2), dpi=300)

    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    ACCENT_RED = '#b91c1c'
    ACCENT_BLUE = '#1d4ed8'
    ACCENT_GREEN = '#047857'

    # --- Panel (a): 2D Sensitivity Heatmap (Table 4) ---
    delta_polls = ['1s', '5s', '15s', '60s']
    delta_ts = ['10s', '30s', '60s', '120s', '300s']

    # Table 4 Recall Matrix (in %)
    # delta_polls as columns, delta_ts as rows
    recall_matrix = np.array([
        [100.0, 97.92, 89.58, 89.58],   # 10s
        [100.0, 97.92, 89.58, 89.58],   # 30s
        [100.0, 100.0, 93.75, 89.58],   # 60s
        [100.0, 100.0, 95.83, 91.67],   # 120s
        [100.0, 100.0, 97.92, 93.75],   # 300s
    ])

    im = ax1.imshow(recall_matrix, cmap='YlGn', vmin=85, vmax=100, aspect='auto')
    cbar = fig.colorbar(im, ax=ax1, fraction=0.046, pad=0.04)
    cbar.set_label('Detection Recall (%)', fontsize=10.5, weight='bold')

    ax1.set_xticks(np.arange(len(delta_polls)))
    ax1.set_yticks(np.arange(len(delta_ts)))
    ax1.set_xticklabels([f"$\\Delta_{{\\mathrm{{poll}}}} = {p}$" for p in delta_polls], fontsize=10.0, weight='bold')
    ax1.set_yticklabels([f"$\\Delta t = {t}$" for t in delta_ts], fontsize=10.0, weight='bold')

    ax1.set_title('(a) CIPG Detection Recall vs. Polling Lag (Table 4)', fontsize=12.5, weight='bold', color=TEXT_MAIN)
    ax1.set_xlabel(r'CA Database Polling Interval ($\Delta_{\mathrm{poll}}$)', fontsize=11.0, weight='bold')
    ax1.set_ylabel(r'Correlation Window ($\Delta t$)', fontsize=11.0, weight='bold')

    # Print numerical values inside cells
    for i in range(len(delta_ts)):
        for j in range(len(delta_polls)):
            val = recall_matrix[i, j]
            color = 'black' if val > 92 else 'white'
            ax1.text(j, i, f"{val:.1f}%", ha='center', va='center',
                     fontsize=9.5, weight='bold', color=color)

    # --- Panel (b): Stackelberg Scalability Runtime Speedup (Table 6) ---
    nodes = [100, 500, 1000, 2500, 5000]
    whole_graph_ms = [7.2, 38.5, 108.7, 731.1, 3181.5]
    cipg_cone_ms    = [5.4, 8.3, 5.5, 3.1, 2.6]
    speedup        = [1.33, 4.64, 19.76, 235.84, 1246.3]

    ax2.plot(nodes, whole_graph_ms, marker='o', lw=2.4, color=ACCENT_RED,
             label='Whole-Graph Min-Cut Search')
    ax2.plot(nodes, cipg_cone_ms, marker='s', lw=2.4, color=ACCENT_GREEN,
             label='CIPG Provenance-Cone Guided Cut')

    ax2.set_xscale('log')
    ax2.set_yscale('log')
    ax2.set_xticks(nodes)
    ax2.get_xaxis().set_major_formatter(matplotlib.ticker.ScalarFormatter())
    ax2.set_xlabel('Active Directory Principals ($N$)', fontsize=11.5, weight='bold')
    ax2.set_ylabel('Remediation Runtime (ms, Log Scale)', fontsize=11.5, weight='bold')
    ax2.set_title('(b) Stackelberg Interdiction Speedup (Table 6)', fontsize=12.5, weight='bold', color=TEXT_MAIN)
    ax2.grid(True, which='both', linestyle=':', alpha=0.6)
    ax2.legend(loc='center left', fontsize=9.5, frameon=True)

    # Annotate 1,246x speedup at N=5000
    ax2.annotate(r'$\mathbf{1,246.3\times}$ Speedup' + '\n(3,181.5 ms $\\to$ 2.6 ms)',
                 xy=(5000, 2.6), xytext=(1200, 10),
                 arrowprops=dict(arrowstyle="->", color=ACCENT_GREEN, lw=1.4),
                 fontsize=9.5, weight='bold', color=ACCENT_GREEN,
                 bbox=dict(boxstyle="round,pad=0.3", fc="#ecfdf5", ec=ACCENT_GREEN, lw=1.1))

    plt.tight_layout()
    out_path = os.path.join(OUTPUT_DIR, 'cipg_sensitivity_and_cone_scaling.png')
    plt.savefig(out_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[+] Successfully generated: {out_path}")


if __name__ == '__main__':
    print("[*] Generating Publication-Grade 7-Figure Suite...")
    generate_certgraph_arch()
    generate_cipg_architecture()
    generate_gnn_ablation_and_hn()
    generate_cipg_sensitivity_and_cone_scaling()
    print("[+] All Figures Generated Successfully!")
