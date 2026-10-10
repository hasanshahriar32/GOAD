#!/usr/bin/env python3
"""
Generate an ultra-high quality, publication-grade diagram showing
CertGraph's complete contributions extended ON TOP of the Active Directory Metagraph Schema.

Extends Slide 2 with:
1. Node-level linear projections W_tau & Theorem 1 Residual Skips (W_skip)
2. 4-head relational attention weights (alpha values) dynamically prioritizing toxic edges
3. Multi-class classification head (7 ESC classes: Safe, ESC1, 2, 3, 4, 9, 13)
4. Tier 2 Neuro-Symbolic Verification path (0% False Positives)
5. Theorem 2 Stackelberg Minimal-Cost Remediation Cut (red cut marker on toxic ACE)
6. Issuance Policy OID & Tier-0 Target (ESC13 complete multi-hop context)
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
OUTPUT_IMG = os.path.join(OUTPUT_DIR, 'certgraph_metagraph_extended.png')

# Colors matching the original presentation style
TEAL_HEADER = '#0f766e'      # Identity objects header
NAVY_HEADER = '#1e3a5f'      # PKI objects header
DARK_SLATE  = '#0f172a'
MID_SLATE   = '#334155'
LIGHT_SLATE = '#64748b'
CARD_BG     = '#ffffff'
CARD_EDGE   = '#cbd5e1'
GOLD_ACCENT = '#d97706'      # Theorem 1 skips
CRIMSON     = '#dc2626'      # High attention / attack vector
GREEN_VERIF = '#059669'      # Neuro-symbolic proof
BLUE_PROJ   = '#2563eb'      # Feature projections
PURPLE_OID  = '#7c3aed'      # Policy OID / Tier 0

def draw_card(ax, x, y, w, h, title, title_bg, body_lines, radius=0.08, shadow=True):
    """Draw a slide-styled entity card with colored header and white body."""
    if shadow:
        shadow_box = FancyBboxPatch(
            (x - w/2 + 0.08, y - h/2 - 0.08), w, h,
            boxstyle=f"round,pad=0.0,rounding_size={radius}",
            facecolor='#000000', edgecolor='none', alpha=0.06, zorder=2
        )
        ax.add_patch(shadow_box)

    # Body
    body_box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle=f"round,pad=0.0,rounding_size={radius}",
        facecolor=CARD_BG, edgecolor=CARD_EDGE, linewidth=1.4, zorder=3
    )
    ax.add_patch(body_box)

    # Header banner
    header_h = h * 0.28
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

    # Title text
    ax.text(x - w/2 + 0.18, y + h/2 - header_h/2, title,
            ha='left', va='center', fontsize=11.5, fontweight='bold',
            color='white', zorder=5)

    # Body text lines
    line_y = y + h/2 - header_h - 0.24
    for text, style, color, size in body_lines:
        weight = 'bold' if 'bold' in style else 'normal'
        ax.text(x - w/2 + 0.18, line_y, text,
                ha='left', va='center', fontsize=size,
                fontweight=weight, color=color, family='monospace' if 'mono' in style else 'sans-serif',
                zorder=5)
        line_y -= 0.30


def draw_skip_badge(ax, x, y, label="W_skip (Thm 1)"):
    """Draw a clean, compact Theorem 1 Skip badge attached to card."""
    badge = FancyBboxPatch(
        (x - 1.25, y - 0.20), 2.5, 0.40,
        boxstyle="round,pad=0.05",
        facecolor='#fef3c7', edgecolor=GOLD_ACCENT, linewidth=1.2, zorder=6
    )
    ax.add_patch(badge)
    ax.text(x, y, label, ha='center', va='center', fontsize=7.6,
            fontweight='bold', color='#92400e', zorder=7)


def draw_arrow(ax, x1, y1, x2, y2, label='', color='#334155', lw=1.8, dashed=False,
               label_pos=0.5, label_offset=0.18, label_x_offset=0.0, label_color=None,
               badge_text=None, badge_bg=CRIMSON, badge_pos=0.5, badge_offset=-0.22, badge_x_offset=0.0):
    """Draw a clean orthogonal or direct vector arrow with optional label & badge."""
    linestyle = '--' if dashed else '-'
    arrow = FancyArrowPatch(
        (x1, y1), (x2, y2),
        arrowstyle="-|>,head_length=5.5,head_width=3.5",
        color=color, linewidth=lw, linestyle=linestyle, zorder=4
    )
    ax.add_patch(arrow)

    if label:
        lx = x1 + (x2 - x1) * label_pos + label_x_offset
        ly = y1 + (y2 - y1) * label_pos + label_offset
        lcol = label_color or color
        ax.text(lx, ly, label,
                ha='center', va='center', fontsize=8.2,
                color=lcol, fontweight='bold', zorder=6,
                bbox=dict(boxstyle='round,pad=0.16', facecolor='white',
                          edgecolor=color, alpha=0.94, lw=0.8))

    if badge_text:
        bx = x1 + (x2 - x1) * badge_pos + badge_x_offset
        by = y1 + (y2 - y1) * badge_pos + badge_offset
        ax.text(bx, by, badge_text,
                ha='center', va='center', fontsize=8.2,
                color='white', fontweight='bold', zorder=7,
                bbox=dict(boxstyle='round,pad=0.18', facecolor=badge_bg,
                          edgecolor='none', alpha=0.98))


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
    ax.text(0.8, 10.35, "Active Directory Metagraph + CertGraph Intelligence",
            fontsize=23, fontweight='bold', color='#0f172a', ha='left', va='center')
    ax.text(0.8, 9.95, "5 Entity Classes · 16 Canonical Relations  |  Extended with Hetero-GAT, Theorem 1 Invariants, 7-Class Screening & Theorem 2 Defense",
            fontsize=11.2, color='#475569', ha='left', va='center')

    # ========================================================================
    # 2. ENTITY NODES (Precise Layout with ample breathing room)
    # ========================================================================
    card_w = 3.5
    card_h = 1.75

    # Top Row Y = 8.05
    # Bottom Row Y = 4.35
    row_top_y = 8.05
    row_bot_y = 4.35

    # (A) User Principal (Top-Left)
    up_x, up_y = 2.5, row_top_y
    draw_card(ax, up_x, up_y, card_w, card_h,
              "User Principal", TEAL_HEADER,
              [
                  (r"$v \in \mathcal{V}_{User}$", '', MID_SLATE, 9.2),
                  ("objectClass: user", 'mono', TEAL_HEADER, 9.2),
                  (r"$x_v \in \mathbb{R}^{d_u} \to h_v^{(0)} \in \mathbb{R}^{64}$ (via $W_u$)", 'bold', BLUE_PROJ, 8.2)
              ])
    draw_skip_badge(ax, up_x, up_y + card_h/2 + 0.22, r"$\mathbf{W_{skip}}$ (Thm 1: $\|\partial h/\partial x\| \geq \sigma_{min})$")

    # (B) Security Group (Top-Middle)
    sg_x, sg_y = 7.9, row_top_y
    draw_card(ax, sg_x, sg_y, card_w, card_h,
              "Security Group", TEAL_HEADER,
              [
                  (r"$v \in \mathcal{V}_{Group}$", '', MID_SLATE, 9.2),
                  ("objectClass: group", 'mono', TEAL_HEADER, 9.2),
                  (r"$x_v \in \mathbb{R}^{d_g} \to h_v^{(0)} \in \mathbb{R}^{64}$ (via $W_g$)", 'bold', BLUE_PROJ, 8.2)
              ])
    draw_skip_badge(ax, sg_x, sg_y + card_h/2 + 0.22, r"$\mathbf{W_{skip}}$ (Preserves Group Bitmask)")

    # Transitive nesting self-loop for Security Group
    sg_nest = FancyArrowPatch(
        (sg_x + 0.6, sg_y + card_h/2 - 0.05), (sg_x + 1.4, sg_y + card_h/2 - 0.05),
        arrowstyle='-|>,head_length=4.5,head_width=3.0',
        connectionstyle="arc,angleA=90,angleB=90,armA=22,armB=22,rad=0",
        color='#334155', linewidth=1.4, zorder=6
    )
    ax.add_patch(sg_nest)
    ax.text(sg_x + 1.0, sg_y + card_h/2 + 0.58, "MemberOf (nesting closure)",
            ha='center', va='center', fontsize=7.5, color='#334155', style='italic')

    # (C) Computer Object (Bottom-Left)
    co_x, co_y = 2.5, row_bot_y
    draw_card(ax, co_x, co_y, card_w, card_h,
              "Computer Object", TEAL_HEADER,
              [
                  (r"$v \in \mathcal{V}_{Comp}$", '', MID_SLATE, 9.2),
                  ("objectClass: computer", 'mono', TEAL_HEADER, 9.2),
                  (r"$x_v \in \mathbb{R}^{d_c} \to h_v^{(0)} \in \mathbb{R}^{64}$ (via $W_c$)", 'bold', BLUE_PROJ, 8.2)
              ])
    draw_skip_badge(ax, co_x, co_y + card_h/2 + 0.22, r"$\mathbf{W_{skip}}$ (Machine Invariant)")

    # (D) Certificate Template (Bottom-Middle - Focal Node)
    ct_x, ct_y = 7.9, row_bot_y
    ct_w, ct_h = 4.0, 1.95
    draw_card(ax, ct_x, ct_y, ct_w, ct_h,
              "Certificate Template  [Focal Node]", NAVY_HEADER,
              [
                  (r"$v \in \mathcal{V}_{Tmpl}$  · Focal Point of Exploit Paths", 'bold', MID_SLATE, 9.2),
                  ("class: pKICertificateTemplate", 'mono', NAVY_HEADER, 9.2),
                  (r"Attr Vector $x_v \in \mathbb{R}^{10}$ (EKU, Flags, DACLs)", 'mono', MID_SLATE, 8.2),
                  (r"Aggregated Latent: $z_{Tmpl} \in \mathbb{R}^{64}$ (2-hop context)", 'bold', '#1e40af', 8.4)
              ])
    # Place skip badge cleanly on the left side of the Template card
    draw_skip_badge(ax, ct_x - ct_w/2 + 1.25, ct_y + ct_h/2 + 0.22, r"$\mathbf{W_{skip}}$ (Prevents Feature Decay)")

    # (E) Enterprise CA (Middle-Right Top)
    ca_x, ca_y = 13.5, 7.6
    draw_card(ax, ca_x, ca_y, card_w, card_h,
              "Enterprise CA", NAVY_HEADER,
              [
                  (r"$v \in \mathcal{V}_{CA}$", '', MID_SLATE, 9.2),
                  ("class: pKIEnrollmentService", 'mono', NAVY_HEADER, 9.2),
                  (r"$x_v \in \mathbb{R}^{d_{ca}} \to h_v^{(0)} \in \mathbb{R}^{64}$ (via $W_{ca}$)", 'bold', BLUE_PROJ, 8.2)
              ])

    # (F) Tier-0 Target / Issuance Policy OID (Middle-Right Bottom)
    t0_x, t0_y = 13.5, 4.35
    draw_card(ax, t0_x, t0_y, card_w, card_h,
              "Tier-0 / Issuance Policy OID", '#831843',
              [
                  (r"ESC13 Target: $v \in \mathcal{V}_{OID}$ / Groups", 'bold', '#831843', 9.2),
                  ("Links: msPKI-Enrollment-Flag", 'mono', '#831843', 8.8),
                  ("Target: Enterprise / Domain Admins", 'bold', CRIMSON, 8.8),
                  ("Escalation: PAC SID Injection", 'mono', MID_SLATE, 8.2)
              ])

    # ========================================================================
    # 3. BASE & ATTENTION-WEIGHTED RELATIONAL EDGES
    # ========================================================================

    # Edge 1: User -> Security Group (MemberOf)
    draw_arrow(ax, up_x + card_w/2, up_y, sg_x - card_w/2, sg_y,
               label="MemberOf", color='#0f172a', lw=2.2, label_offset=0.20)

    # Edge 2: User -> Certificate Template (Enroll / WriteDacl)
    draw_arrow(ax, up_x + 0.7, up_y - card_h/2, ct_x - ct_w/2, ct_y + 0.5,
               label="Enroll / WriteDacl", color='#475569', lw=1.6, dashed=True,
               label_pos=0.45, label_offset=0.18,
               badge_text=r"$\alpha = 0.25$", badge_bg='#1e40af', badge_pos=0.68, badge_offset=-0.22)

    # Edge 3: Computer -> Certificate Template (Enroll / GenericAll)
    draw_arrow(ax, co_x + card_w/2, co_y, ct_x - ct_w/2, ct_y - 0.2,
               label="Enroll / GenericAll", color='#475569', lw=1.6, dashed=True,
               label_pos=0.45, label_offset=0.20,
               badge_text=r"$\alpha = 0.12$", badge_bg='#475569', badge_pos=0.72, badge_offset=-0.22)

    # Edge 4: Security Group -> Certificate Template (GenericAll / WriteOwner)
    # VERTICAL PRIMARY ATTACK EDGE (alpha = 0.55)
    attack_arrow_x = sg_x + 0.4
    draw_arrow(ax, attack_arrow_x, sg_y - card_h/2, attack_arrow_x, ct_y + ct_h/2,
               label="GenericAll / WriteOwner", color=CRIMSON, lw=3.6, dashed=False,
               label_pos=0.32, label_offset=0.0, label_x_offset=-1.55, label_color=CRIMSON,
               badge_text=r"$\alpha = 0.55$ [ATTACK VECTOR]", badge_bg=CRIMSON,
               badge_pos=0.68, badge_offset=0.0, badge_x_offset=-1.55)

    # Cut marker directly on the attack arrow
    cut_x = attack_arrow_x
    cut_y = (sg_y - card_h/2 + ct_y + ct_h/2) / 2
    ax.scatter([cut_x], [cut_y], s=360, marker='X', color=CRIMSON, zorder=8, edgecolors='#ffffff', linewidths=2.2)

    # Remediation callout box to the right with clear spacing
    cut_box = FancyBboxPatch(
        (cut_x + 0.55, cut_y - 0.45), 3.4, 0.90,
        boxstyle="round,pad=0.08",
        facecolor='#fef2f2', edgecolor=CRIMSON, linewidth=1.6, zorder=8
    )
    ax.add_patch(cut_box)
    ax.text(cut_x + 0.72, cut_y + 0.22, "[CUT] Theorem 2 Stackelberg Defense",
            fontsize=9.2, fontweight='bold', color=CRIMSON, zorder=9)
    ax.text(cut_x + 0.72, cut_y - 0.16, "NP-Hard Multiway Interdiction -> Minimal-cost\nACE revocation breaks path with 0 disruption",
            fontsize=7.8, color='#7f1d1d', zorder=9, linespacing=1.2)

    ax.annotate('', xy=(cut_x + 0.08, cut_y), xytext=(cut_x + 0.55, cut_y),
                arrowprops=dict(arrowstyle='->', color=CRIMSON, lw=1.5, zorder=9))

    # Edge 5: Certificate Template -> Enterprise CA (PublishedTo) - Orthogonal clean route
    pub_arrow = FancyArrowPatch(
        (ct_x + ct_w/2, ct_y + 0.5), (ca_x - card_w/2, ca_y - 0.3),
        arrowstyle="-|>,head_length=5.5,head_width=3.5",
        connectionstyle="arc3,rad=-0.12",
        color='#334155', linewidth=1.6, zorder=4
    )
    ax.add_patch(pub_arrow)
    ax.text(ct_x + ct_w/2 + 0.8, ct_y + 1.25, "PublishedTo",
            ha='center', va='center', fontsize=8.2, color='#334155', fontweight='bold', zorder=6,
            bbox=dict(boxstyle='round,pad=0.16', facecolor='white', edgecolor='#334155', alpha=0.94, lw=0.8))
    ax.text(ct_x + ct_w/2 + 0.8, ct_y + 0.85, r"$\alpha = 0.08$",
            ha='center', va='center', fontsize=8.0, color='white', fontweight='bold', zorder=7,
            bbox=dict(boxstyle='round,pad=0.18', facecolor='#64748b', edgecolor='none', alpha=0.98))

    # Edge 6: Security Group -> Enterprise CA (ManageCA / CertManager)
    draw_arrow(ax, sg_x + card_w/2, sg_y, ca_x - card_w/2, ca_y + 0.1,
               label="ManageCA / CertManager", color='#475569', lw=1.5, dashed=True,
               label_pos=0.50, label_offset=0.20)

    # Edge 7: Certificate Template -> Tier-0 / OID (LinksPolicy) - ESC13 Vector
    draw_arrow(ax, ct_x + ct_w/2, ct_y - 0.2, t0_x - card_w/2, t0_y - 0.2,
               label="LinksPolicy [ESC13 OID]", color='#831843', lw=2.8,
               label_pos=0.42, label_offset=0.22,
               badge_text="PAC Elevation", badge_bg='#831843', badge_pos=0.72, badge_offset=-0.22)

    # ========================================================================
    # 5. EXTENSION NOVELTY B: 7-CLASS CLASSIFIER HEAD
    # ========================================================================
    mlp_x, mlp_y = ct_x, 1.70
    mlp_w, mlp_h = 4.8, 1.30

    # Clean arrow down from Template to Classifier
    ax.annotate('', xy=(mlp_x, mlp_y + mlp_h/2), xytext=(ct_x, ct_y - ct_h/2),
                arrowprops=dict(arrowstyle='-|>,head_length=0.35,head_width=0.22',
                                color='#1e40af', lw=2.6, zorder=6))
    ax.text(ct_x + 0.15, (ct_y - ct_h/2 + mlp_y + mlp_h/2)/2,
            r"Template Latent $z_{Tmpl} \in \mathbb{R}^{64}$",
            ha='left', va='center', fontsize=8.2, fontweight='bold', color='#1e40af',
            bbox=dict(boxstyle='round,pad=0.14', facecolor='#eff6ff', edgecolor='#3b82f6', lw=0.8))

    # Classifier Box
    mlp_card = FancyBboxPatch(
        (mlp_x - mlp_w/2, mlp_y - mlp_h/2), mlp_w, mlp_h,
        boxstyle="round,pad=0.08",
        facecolor='#ffffff', edgecolor='#2563eb', linewidth=1.8, zorder=5
    )
    ax.add_patch(mlp_card)

    ax.text(mlp_x, mlp_y + 0.40, "CertGraph MLP Classifier Head (64 -> 32 -> 7 Classes)",
            ha='center', va='center', fontsize=10.2, fontweight='bold', color='#1e3a5f', zorder=6)
    ax.text(mlp_x, mlp_y + 0.14, r"Full AD CS Taxonomy Detection · Inductive $O(1)$ Inference <25 ms",
            ha='center', va='center', fontsize=7.8, color='#64748b', zorder=6)

    # 7 Class Pills
    classes = [
        ('Safe', '#059669', '#ecfdf5'),
        ('ESC1', CRIMSON, '#fef2f2'),
        ('ESC2', CRIMSON, '#fef2f2'),
        ('ESC3', CRIMSON, '#fef2f2'),
        ('ESC4', CRIMSON, '#fef2f2'),
        ('ESC9', CRIMSON, '#fef2f2'),
        ('ESC13', '#831843', '#fdf2f8')
    ]
    pill_start_x = mlp_x - 2.05
    for i, (cname, ccol, cbg) in enumerate(classes):
        px = pill_start_x + i * 0.68
        py = mlp_y - 0.28
        pbox = FancyBboxPatch(
            (px - 0.31, py - 0.17), 0.62, 0.34,
            boxstyle="round,pad=0.04",
            facecolor=cbg, edgecolor=ccol, linewidth=1.1, zorder=6
        )
        ax.add_patch(pbox)
        ax.text(px, py, cname, ha='center', va='center', fontsize=7.6,
                fontweight='bold', color=ccol, zorder=7)

    # Performance badge attached to MLP
    perf_badge = FancyBboxPatch(
        (mlp_x + mlp_w/2 - 0.15, mlp_y - mlp_h/2 - 0.32), 2.1, 0.42,
        boxstyle="round,pad=0.06",
        facecolor='#ecfdf5', edgecolor='#059669', linewidth=1.1, zorder=7
    )
    ax.add_patch(perf_badge)
    ax.text(mlp_x + mlp_w/2 + 0.90, mlp_y - mlp_h/2 - 0.11, "Macro-F1: 97.18%",
            ha='center', va='center', fontsize=8.6, fontweight='bold', color='#059669', zorder=8)

    # ========================================================================
    # 6. EXTENSION NOVELTY C: TIER 2 NEURO-SYMBOLIC SOUNDNESS VERIFICATION
    # ========================================================================
    ns_x, ns_y = 3.2, 1.70
    ns_w, ns_h = 4.4, 1.30
    ns_box = FancyBboxPatch(
        (ns_x - ns_w/2, ns_y - ns_h/2), ns_w, ns_h,
        boxstyle="round,pad=0.08",
        facecolor='#f0fdf4', edgecolor=GREEN_VERIF, linewidth=1.8, zorder=5
    )
    ax.add_patch(ns_box)
    ax.text(ns_x, ns_y + 0.40, "[SOUNDNESS] Tier 2: Neuro-Symbolic Verification",
            ha='center', va='center', fontsize=10.0, fontweight='bold', color='#065f46', zorder=6)
    ax.text(ns_x, ns_y + 0.12, "• Sound BFS verifies candidate queue (0% False Positives)",
            ha='center', va='center', fontsize=8.0, color='#047857', zorder=6)
    ax.text(ns_x, ns_y - 0.14, "• Prunes Shortcut Learning on Hard Negatives (1.59% -> 100%)",
            ha='center', va='center', fontsize=7.8, color='#065f46', zorder=6)
    ax.text(ns_x, ns_y - 0.40, "• Emits formal reachability proof tree before mitigation",
            ha='center', va='center', fontsize=7.8, color='#047857', style='italic', zorder=6)

    # Arrow from MLP head to Neuro-Symbolic Verification
    ax.annotate('', xy=(ns_x + ns_w/2 + 0.05, ns_y), xytext=(mlp_x - mlp_w/2 - 0.05, ns_y),
                arrowprops=dict(arrowstyle='<|-,head_length=0.28,head_width=0.18',
                                color=GREEN_VERIF, lw=1.8, linestyle='--'))
    ax.text((ns_x + ns_w/2 + mlp_x - mlp_w/2)/2, ns_y + 0.18, "Tier 1 Top-K\nCandidates",
            ha='center', va='center', fontsize=7.4, fontweight='bold', color=GREEN_VERIF)

    # ========================================================================
    # 7. EXTENSION NOVELTY D: OVERLAID MULTI-HOP PROOF PATH
    # ========================================================================
    sc_x, sc_y = 14.8, 1.70
    sc_w, sc_h = 4.2, 1.30
    sc_box = FancyBboxPatch(
        (sc_x - sc_w/2, sc_y - sc_h/2), sc_w, sc_h,
        boxstyle="round,pad=0.08",
        facecolor='#faf5ff', edgecolor=PURPLE_OID, linewidth=1.8, zorder=5
    )
    ax.add_patch(sc_box)
    ax.text(sc_x, sc_y + 0.40, "[BENCHMARK] Diagnostic ESC13 Multi-Hop Proof",
            ha='center', va='center', fontsize=10.0, fontweight='bold', color='#581c87', zorder=6)
    ax.text(sc_x, sc_y + 0.12, "User -> Group -> Template -> Policy OID -> DA",
            ha='center', va='center', fontsize=8.0, color='#6b21a8', fontweight='bold', zorder=6)
    ax.text(sc_x, sc_y - 0.14, "• Certipy: 0% Detection (Blind to OID link)",
            ha='center', va='center', fontsize=7.8, color=CRIMSON, zorder=6)
    ax.text(sc_x, sc_y - 0.38, "• BloodHound: Exponential BFS State Explosion\n• CertGraph: 343 ms Complete Path Discovery",
            ha='center', va='center', fontsize=7.6, color='#047857', zorder=6, linespacing=1.1)

    # ========================================================================
    # 8. LEGEND BAR (Bottom)
    # ========================================================================
    leg_y = 0.42
    leg_box = FancyBboxPatch(
        (0.8, leg_y - 0.28), fig_w - 1.6, 0.56,
        boxstyle="round,pad=0.05",
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.1, zorder=2
    )
    ax.add_patch(leg_box)

    items = [
        ("Identity Object (User/Group/Comp)", TEAL_HEADER, 'square'),
        ("PKI Object (CA/Template/OID)", NAVY_HEADER, 'square'),
        (r"Theorem 1 Skip ($W_{skip}$)", GOLD_ACCENT, 'badge'),
        ("Standard Relation (E_AD)", '#0f172a', 'line'),
        ("DACL ACE (E_DACL)", '#475569', 'dashed'),
        (r"Relational Attention ($\alpha$)", CRIMSON, 'thick'),
        ("Stackelberg Cut (Thm 2)", CRIMSON, 'cut'),
        ("Neuro-Symbolic (0% FP)", GREEN_VERIF, 'shield')
    ]

    ix_start = 1.15
    ix_step = 2.15
    for i, (lab, col, itype) in enumerate(items):
        ix = ix_start + i * ix_step
        if itype == 'square':
            ax.add_patch(patches.Rectangle((ix - 0.16, leg_y - 0.07), 0.14, 0.14, facecolor=col, edgecolor='none', zorder=4))
        elif itype == 'badge':
            ax.add_patch(FancyBboxPatch((ix - 0.18, leg_y - 0.08), 0.18, 0.16, boxstyle="round,pad=0.02", facecolor='#fef3c7', edgecolor=col, linewidth=1.0, zorder=4))
        elif itype == 'line':
            ax.plot([ix - 0.20, ix + 0.02], [leg_y, leg_y], color=col, lw=2.2, zorder=4)
        elif itype == 'dashed':
            ax.plot([ix - 0.20, ix + 0.02], [leg_y, leg_y], color=col, lw=1.8, linestyle='--', zorder=4)
        elif itype == 'thick':
            ax.plot([ix - 0.20, ix + 0.02], [leg_y, leg_y], color=col, lw=3.5, zorder=4)
        elif itype == 'cut':
            ax.scatter([ix - 0.09], [leg_y], s=70, marker='X', color=col, zorder=4)
        elif itype == 'shield':
            ax.scatter([ix - 0.09], [leg_y], s=70, marker='D', color=col, zorder=4)

        ax.text(ix + 0.07, leg_y, lab, ha='left', va='center', fontsize=7.1, color='#1e293b', fontweight='bold', zorder=4)

    plt.subplots_adjust(left=0.01, right=0.99, top=0.99, bottom=0.01)
    plt.savefig(OUTPUT_IMG, bbox_inches='tight', dpi=300, facecolor='#ffffff')
    plt.close()
    print(f"Successfully generated polished diagram: {OUTPUT_IMG}")

if __name__ == '__main__':
    generate_diagram()
