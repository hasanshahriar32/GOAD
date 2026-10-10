#!/usr/bin/env python3
"""
Create proper visual graph diagrams (nodes + edges) for slides 5b and 6b,
matching the style of the original slides 5 and 7.

Slide 5b: GNN Methodology Pipeline as a graph — shows how data flows
          through the 3 stages with actual graph node/edge visuals.
Slide 6b: ESC13 benchmark with tool failure annotations on the attack chain.
"""

import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import numpy as np
import os

OUTPUT_DIR = '/home/hs32/Desktop/GOAD/thesis_paper/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# ============================================================================
# Color palette matching the original slides
# ============================================================================
DARK_TEAL = '#0f766e'
DARK_SLATE = '#0f172a'
MID_SLATE = '#334155'
LIGHT_BG = '#f8fafc'
NODE_USER = '#0f766e'       # teal
NODE_GROUP = '#1e40af'      # blue
NODE_TMPL = '#dc2626'       # red
NODE_CA = '#7c3aed'         # purple
NODE_COMP = '#475569'       # gray
EDGE_COLOR = '#334155'
ARROW_COLOR = '#0f172a'
HIGHLIGHT_GREEN = '#047857'
HIGHLIGHT_RED = '#b91c1c'
GOLD = '#b45309'


def draw_entity_node(ax, x, y, w, h, label, sublabel, color, text_color='white'):
    """Draw a rounded entity node matching the original slide style."""
    box = FancyBboxPatch(
        (x - w/2, y - h/2), w, h,
        boxstyle="round,pad=0.05",
        facecolor=color, edgecolor='#1e293b',
        linewidth=1.8, zorder=3
    )
    ax.add_patch(box)
    ax.text(x, y + 0.12, label,
            ha='center', va='center', fontsize=11, fontweight='bold',
            color=text_color, zorder=4)
    if sublabel:
        ax.text(x, y - 0.16, sublabel,
                ha='center', va='center', fontsize=8.5,
                color=text_color, alpha=0.85, zorder=4)


def draw_arrow(ax, x1, y1, x2, y2, label='', color=ARROW_COLOR, style='-|>',
               lw=1.8, label_offset=0.15, fontsize=8.5, curved=False):
    """Draw an arrow between two points with an optional label."""
    if curved:
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle=f"{style},head_length=6,head_width=4",
            color=color, linewidth=lw, zorder=2,
            connectionstyle="arc3,rad=0.25"
        )
    else:
        arrow = FancyArrowPatch(
            (x1, y1), (x2, y2),
            arrowstyle=f"{style},head_length=6,head_width=4",
            color=color, linewidth=lw, zorder=2
        )
    ax.add_patch(arrow)
    if label:
        mx, my = (x1 + x2) / 2, (y1 + y2) / 2 + label_offset
        ax.text(mx, my, label,
                ha='center', va='center', fontsize=fontsize,
                color=color, fontweight='bold', zorder=5,
                bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                          edgecolor=color, alpha=0.9, lw=0.8))


# ============================================================================
# DIAGRAM 1: Slide 5b — GNN Methodology as Visual Graph Pipeline
# ============================================================================
def create_methodology_graph():
    """
    Shows the 3-stage pipeline using actual graph node visuals:
    Left: Raw AD graph (5 node types + edges)
    Center: GNN processing (attention + skip connections)
    Right: Classification output
    """
    fig_w, fig_h = 18, 9
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # ---- Stage labels at top ----
    stages = [
        (3.2,  "STAGE 1", "Graph Formulation"),
        (9.0,  "STAGE 2", "Hetero-GAT Engine"),
        (14.8, "STAGE 3", "Neuro-Symbolic\nVerification"),
    ]
    for sx, s1, s2 in stages:
        bg = FancyBboxPatch(
            (sx - 2.1, 8.0), 4.2, 0.85,
            boxstyle="round,pad=0.08",
            facecolor=DARK_TEAL, edgecolor='none', zorder=3
        )
        ax.add_patch(bg)
        ax.text(sx, 8.55, s1, ha='center', va='center',
                fontsize=10, color='white', fontweight='bold', zorder=4)
        ax.text(sx, 8.25, s2, ha='center', va='center',
                fontsize=9.5, color='white', alpha=0.9, zorder=4,
                linespacing=1.1)

    # =========== STAGE 1: Raw heterogeneous graph ===========
    # 5 node types arranged as a small graph
    nodes_s1 = [
        (1.8, 6.3, 'User', 'v ∈ V_User',   NODE_USER),
        (4.6, 6.3, 'Group', 'v ∈ V_Group',  NODE_GROUP),
        (1.8, 4.2, 'Computer', 'v ∈ V_Comp', NODE_COMP),
        (4.6, 4.2, 'Template', 'v ∈ V_Tmpl', NODE_TMPL),
        (3.2, 2.2, 'CA', 'v ∈ V_CA',        NODE_CA),
    ]
    nw, nh = 1.5, 0.7
    for nx, ny, lab, sub, col in nodes_s1:
        draw_entity_node(ax, nx, ny, nw, nh, lab, sub, col)

    # Edges for Stage 1
    draw_arrow(ax, 2.55, 6.3, 3.85, 6.3, 'MemberOf', EDGE_COLOR,
               label_offset=0.22, fontsize=8)
    draw_arrow(ax, 4.6, 5.95, 4.6, 4.55, 'Enroll', EDGE_COLOR,
               label_offset=0.0, fontsize=8)
    draw_arrow(ax, 1.8, 5.95, 1.8, 4.55, 'WriteDacl', EDGE_COLOR,
               label_offset=0.0, fontsize=8)
    draw_arrow(ax, 3.85, 4.2, 2.55, 4.2, 'GenericAll', EDGE_COLOR,
               label_offset=0.22, fontsize=8)
    draw_arrow(ax, 4.6, 3.85, 3.95, 2.55, 'LinksPolicy', NODE_TMPL,
               label_offset=0.18, fontsize=8)
    draw_arrow(ax, 2.55, 4.0, 2.7, 2.55, 'PublishedTo', NODE_CA,
               label_offset=0.18, fontsize=8)

    # Feature annotation below Stage 1
    ax.text(3.2, 1.3, 'x_v ∈ ℝ^d  (ACL bits, EKU OIDs,\nenrollment flags)',
            ha='center', va='center', fontsize=8.5, color=MID_SLATE,
            style='italic', linespacing=1.3,
            bbox=dict(boxstyle='round,pad=0.2', facecolor='#f1f5f9',
                      edgecolor='#94a3b8', lw=0.8))

    # =========== Big arrow: Stage 1 → Stage 2 ===========
    ax.annotate('', xy=(6.6, 4.5), xytext=(5.7, 4.5),
                arrowprops=dict(arrowstyle='-|>,head_length=0.4,head_width=0.25',
                                color=DARK_TEAL, lw=3))
    ax.text(6.15, 5.0, 'Linear\nProjection\nW_τ · x_v',
            ha='center', va='center', fontsize=8, color=DARK_TEAL,
            fontweight='bold', linespacing=1.2)

    # =========== STAGE 2: GNN processing graph ===========
    # Show same nodes but with attention edges highlighted
    nodes_s2 = [
        (7.5, 6.5, 'U', None, NODE_USER),
        (10.5, 6.5, 'G', None, NODE_GROUP),
        (7.5, 4.2, 'C', None, NODE_COMP),
        (10.5, 4.2, 'T', None, NODE_TMPL),
        (9.0, 2.2, 'CA', None, NODE_CA),
    ]
    nw2, nh2 = 0.9, 0.6
    for nx, ny, lab, sub, col in nodes_s2:
        draw_entity_node(ax, nx, ny, nw2, nh2, lab, sub, col)

    # Attention edges (thicker, colored by weight)
    draw_arrow(ax, 7.95, 6.5, 10.05, 6.5, 'α = 0.82', HIGHLIGHT_GREEN,
               lw=2.8, label_offset=0.25, fontsize=7.5)
    draw_arrow(ax, 10.5, 6.2, 10.5, 4.5, 'α = 0.91', HIGHLIGHT_GREEN,
               lw=3.2, label_offset=0.0, fontsize=7.5)
    draw_arrow(ax, 7.5, 5.9, 7.5, 4.5, 'α = 0.45', '#94a3b8',
               lw=1.2, label_offset=0.0, fontsize=7.5)
    draw_arrow(ax, 10.05, 4.2, 7.95, 4.2, 'α = 0.73', GOLD,
               lw=2.2, label_offset=0.25, fontsize=7.5)
    draw_arrow(ax, 10.3, 3.9, 9.35, 2.5, 'α = 0.88', HIGHLIGHT_GREEN,
               lw=2.8, label_offset=0.18, fontsize=7.5)

    # Residual skip connection annotation
    skip_box = FancyBboxPatch(
        (7.3, 1.2), 3.4, 0.65,
        boxstyle="round,pad=0.08",
        facecolor='#fef3c7', edgecolor=GOLD, linewidth=1.2, zorder=3
    )
    ax.add_patch(skip_box)
    ax.text(9.0, 1.52, 'Theorem 1 Residual Skip: h_v^(l+1) = σ(Σα·W·h + W_res·h)',
            ha='center', va='center', fontsize=7.8, color='#78350f',
            fontweight='bold', zorder=4)

    # Label: multi-head attention
    ax.text(9.0, 7.5, 'Relational Multi-Head Attention (4 heads)',
            ha='center', va='center', fontsize=9, color=DARK_SLATE,
            fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.15', facecolor='white',
                      edgecolor=DARK_SLATE, lw=0.8))

    # =========== Big arrow: Stage 2 → Stage 3 ===========
    ax.annotate('', xy=(12.4, 4.5), xytext=(11.5, 4.5),
                arrowprops=dict(arrowstyle='-|>,head_length=0.4,head_width=0.25',
                                color=DARK_TEAL, lw=3))
    ax.text(11.95, 5.0, '64-dim\nEmbeddings\nz_t ∈ ℝ^64',
            ha='center', va='center', fontsize=8, color=DARK_TEAL,
            fontweight='bold', linespacing=1.2)

    # =========== STAGE 3: Verification + Classification output ===========
    # Tier 1: Neural screening
    t1_box = FancyBboxPatch(
        (12.7, 5.8), 4.2, 1.9,
        boxstyle="round,pad=0.08",
        facecolor='#ecfdf5', edgecolor=HIGHLIGHT_GREEN,
        linewidth=1.5, zorder=2
    )
    ax.add_patch(t1_box)
    ax.text(14.8, 7.35, 'Tier 1: Neural Screening (<25 ms)',
            ha='center', va='center', fontsize=9.5, color=HIGHLIGHT_GREEN,
            fontweight='bold', zorder=3)
    ax.text(14.8, 6.85, 'MLP: z_t → S(t) ∈ [0,1]',
            ha='center', va='center', fontsize=8.5, color=MID_SLATE, zorder=3)
    # Show template nodes being classified
    class_labels = ['Safe', 'ESC1', 'ESC4', 'ESC13']
    class_colors = [HIGHLIGHT_GREEN, HIGHLIGHT_RED, HIGHLIGHT_RED, HIGHLIGHT_RED]
    for i, (cl, cc) in enumerate(zip(class_labels, class_colors)):
        cx = 13.3 + i * 1.1
        cy = 6.15
        pill = FancyBboxPatch(
            (cx - 0.4, cy - 0.2), 0.8, 0.4,
            boxstyle="round,pad=0.05",
            facecolor=cc, edgecolor='none', alpha=0.15, zorder=3
        )
        ax.add_patch(pill)
        ax.text(cx, cy, cl, ha='center', va='center',
                fontsize=8, fontweight='bold', color=cc, zorder=4)

    # Tier 2: Symbolic proof
    t2_box = FancyBboxPatch(
        (12.7, 3.3), 4.2, 2.1,
        boxstyle="round,pad=0.08",
        facecolor='#fef2f2', edgecolor=HIGHLIGHT_RED,
        linewidth=1.5, zorder=2
    )
    ax.add_patch(t2_box)
    ax.text(14.8, 5.1, 'Tier 2: Symbolic Proof (128 ms)',
            ha='center', va='center', fontsize=9.5, color=HIGHLIGHT_RED,
            fontweight='bold', zorder=3)
    # Mini 3-node reachability proof
    proof_nodes = [
        (13.5, 4.2, 'U', NODE_USER, 0.6, 0.4),
        (14.8, 4.2, 'T', NODE_TMPL, 0.6, 0.4),
        (16.1, 4.2, 'DA', '#7c3aed', 0.6, 0.4),
    ]
    for px, py, pl, pc, pw, ph in proof_nodes:
        pbox = FancyBboxPatch(
            (px - pw/2, py - ph/2), pw, ph,
            boxstyle="round,pad=0.04",
            facecolor=pc, edgecolor='#1e293b', linewidth=1.2, zorder=4
        )
        ax.add_patch(pbox)
        ax.text(px, py, pl, ha='center', va='center',
                fontsize=8, fontweight='bold', color='white', zorder=5)
    draw_arrow(ax, 13.8, 4.2, 14.5, 4.2, '', HIGHLIGHT_RED, lw=2)
    draw_arrow(ax, 15.1, 4.2, 15.8, 4.2, '', HIGHLIGHT_RED, lw=2)
    ax.text(14.8, 3.65, '2-hop reachability → Verified escalation path',
            ha='center', va='center', fontsize=8, color=HIGHLIGHT_RED,
            style='italic', zorder=4)

    # Remediation output
    rem_box = FancyBboxPatch(
        (12.7, 1.4), 4.2, 1.5,
        boxstyle="round,pad=0.08",
        facecolor='#f0f9ff', edgecolor='#0369a1',
        linewidth=1.5, zorder=2
    )
    ax.add_patch(rem_box)
    ax.text(14.8, 2.65, 'Autonomous Remediation',
            ha='center', va='center', fontsize=9.5, color='#0369a1',
            fontweight='bold', zorder=3)
    ax.text(14.8, 2.15, 'Stackelberg game → minimal-cost ACE\nrevocation cuts',
            ha='center', va='center', fontsize=8.5, color=MID_SLATE,
            linespacing=1.3, zorder=3)

    # Arrow from Tier 2 to Remediation
    ax.annotate('', xy=(14.8, 2.95), xytext=(14.8, 3.25),
                arrowprops=dict(arrowstyle='-|>,head_length=0.3,head_width=0.2',
                                color='#0369a1', lw=2))

    plt.tight_layout(pad=0.3)
    out = f'{OUTPUT_DIR}/methodology_gnn_graph.png'
    plt.savefig(out, bbox_inches='tight', dpi=300, transparent=True)
    plt.close()
    print(f'Saved: {out}')


# ============================================================================
# DIAGRAM 2: Slide 6b — ESC13 Attack Chain + Tool Comparison
# ============================================================================
def create_esc13_benchmark_graph():
    """
    Same 5-node ESC13 attack chain as original slide 7, but annotated with:
    - Where Certipy fails (blind spot on LinksPolicy)
    - Where BloodHound fails (BFS state explosion)
    - Where CertGraph GNN detects (learned attention)
    """
    fig_w, fig_h = 18, 9
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')
    fig.patch.set_alpha(0)
    ax.set_facecolor('none')

    # ---- Attack chain: 5 nodes in a row ----
    chain_y = 5.8
    chain_nodes = [
        (1.8,  'Identity\nPrincipal', 'Low-Priv User',      NODE_USER),
        (5.4,  'Security\nGroup',     'Enroller Group',      NODE_GROUP),
        (9.0,  'Certificate\nTemplate','ESC13 Template',     NODE_TMPL),
        (12.6, 'Issuance\nPolicy OID','Policy Object',       NODE_CA),
        (16.2, 'Tier-0\nTarget',      'Domain Admins',       '#991b1b'),
    ]
    nw, nh = 2.0, 1.1

    for nx, ny_label, sub, col in chain_nodes:
        box = FancyBboxPatch(
            (nx - nw/2, chain_y - nh/2), nw, nh,
            boxstyle="round,pad=0.06",
            facecolor=col, edgecolor='#1e293b',
            linewidth=2.0, zorder=3
        )
        ax.add_patch(box)
        ax.text(nx, chain_y + 0.15, ny_label,
                ha='center', va='center', fontsize=10.5,
                fontweight='bold', color='white', zorder=4,
                linespacing=1.1)
        ax.text(nx, chain_y - 0.35, sub,
                ha='center', va='center', fontsize=8,
                color='white', alpha=0.85, zorder=4)

    # ---- Step arrows between chain nodes ----
    steps = [
        (1.8, 5.4, 'STEP 1\nMemberOf', EDGE_COLOR),
        (5.4, 9.0, 'STEP 2\nEnroll (DACL)', EDGE_COLOR),
        (9.0, 12.6, 'STEP 3\nLinksPolicy', HIGHLIGHT_RED),
        (12.6, 16.2, 'STEP 4\nPAC Elevate', HIGHLIGHT_RED),
    ]
    for sx, ex, lab, col in steps:
        ax.annotate('', xy=(ex - nw/2 - 0.05, chain_y),
                    xytext=(sx + nw/2 + 0.05, chain_y),
                    arrowprops=dict(
                        arrowstyle='-|>,head_length=0.35,head_width=0.2',
                        color=col, lw=2.5))
        mid_x = (sx + ex) / 2
        ax.text(mid_x, chain_y + 0.85, lab,
                ha='center', va='center', fontsize=8.5,
                color=col, fontweight='bold', linespacing=1.15,
                bbox=dict(boxstyle='round,pad=0.12', facecolor='white',
                          edgecolor=col, lw=1.0, alpha=0.95))

    # ---- TOOL COMPARISON BELOW (3 columns) ----
    comp_y_top = 3.6
    col_w = 4.8
    col_h = 3.0
    col_xs = [3.0, 9.0, 15.0]
    col_labels = [
        ('Certipy (Heuristic)', HIGHLIGHT_RED, '#fef2f2'),
        ('BloodHound (BFS)',    GOLD,          '#fffbeb'),
        ('CertGraph GNN (Ours)', HIGHLIGHT_GREEN, '#ecfdf5'),
    ]
    col_details = [
        [
            '[BLIND SPOT] No OID linkage check',
            'Static signature matching only',
            'Misses Steps 3-4 entirely',
            'ESC13 Detection: MISSED',
            'Macro-F1: 77.91%',
        ],
        [
            '[STATE EXPLOSION] 2^k BFS paths',
            'Shortest-path traversal',
            'Exponential on deep nesting',
            'ESC13 Detection: PARTIAL',
            'Macro-F1: 84.22%',
        ],
        [
            '[LEARNED ATTENTION] α weights',
            'Relational multi-head GAT',
            'Captures LinksPolicy via attention',
            'ESC13 Detection: FULL (100%)',
            'Macro-F1: 97.18%',
        ],
    ]

    for i, (cx, (title, border_col, bg_col), details) in enumerate(
            zip(col_xs, col_labels, col_details)):
        # Column box
        cbox = FancyBboxPatch(
            (cx - col_w/2, comp_y_top - col_h), col_w, col_h,
            boxstyle="round,pad=0.08",
            facecolor=bg_col, edgecolor=border_col,
            linewidth=1.8, zorder=2
        )
        ax.add_patch(cbox)

        # Title bar
        tbar = FancyBboxPatch(
            (cx - col_w/2, comp_y_top - 0.55), col_w, 0.55,
            boxstyle="round,pad=0.04",
            facecolor=border_col, edgecolor='none', zorder=3
        )
        ax.add_patch(tbar)
        ax.text(cx, comp_y_top - 0.28, title,
                ha='center', va='center', fontsize=10,
                fontweight='bold', color='white', zorder=4)

        # Detail bullets
        for j, detail in enumerate(details):
            dy = comp_y_top - 0.85 - j * 0.42
            weight = 'bold' if j >= 3 else 'normal'
            fs = 9 if j >= 3 else 8.5
            ax.text(cx - col_w/2 + 0.25, dy, '• ' + detail,
                    ha='left', va='center', fontsize=fs,
                    color=DARK_SLATE, fontweight=weight, zorder=4)

        # Arrow from chain to column
        # Draw down arrow from the attack chain
        target_node_x = chain_nodes[0][0] if i == 0 else (
            chain_nodes[2][0] if i == 1 else chain_nodes[4][0])
        ax.annotate('', xy=(cx, comp_y_top + 0.02),
                    xytext=(target_node_x, chain_y - nh/2 - 0.05),
                    arrowprops=dict(
                        arrowstyle='-|>,head_length=0.3,head_width=0.18',
                        color=border_col, lw=1.5,
                        connectionstyle="arc3,rad=0.0",
                        linestyle='dashed'))

    plt.tight_layout(pad=0.3)
    out = f'{OUTPUT_DIR}/esc13_benchmark_graph.png'
    plt.savefig(out, bbox_inches='tight', dpi=300, transparent=True)
    plt.close()
    print(f'Saved: {out}')


if __name__ == '__main__':
    create_methodology_graph()
    create_esc13_benchmark_graph()
    print('Done — both graph diagrams created.')
