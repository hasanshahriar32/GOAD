"""
Publication-Grade Research Paper Diagram Generator
Strictly conforms to top-tier peer-reviewed security & AI publication standards
(IEEE S&P / USENIX Security / ACM CCS / NeurIPS / ICLR):
- Palette: Monochromatic charcoal and deep slate (#0f172a, #1e293b, #334155, #f8fafc)
  with a single restrained semantic accent (#991b1b) for attack paths/vulnerabilities.
- Typography: Authentic academic serif (STIXGeneral / Times-compatible) with LaTeX math notation.
- Graphical Content: Authentic schematics (graph nodes, tensors, multi-head attention slices,
  residual skip pathways, probability distributions, decision forks, closed-loop actuation).
- Zero cartoon drop shadows, zero empty whitespace voids.
- Impeccable geometry, alignment, and label clearances (zero collisions or clipping).
"""

import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

OUTPUT_DIR = '/home/hs32/Desktop/GOAD/thesis_paper/figures'
os.makedirs(OUTPUT_DIR, exist_ok=True)

# Configure Matplotlib for authentic Academic Publishing
plt.rcParams['font.family'] = 'STIXGeneral'
plt.rcParams['mathtext.fontset'] = 'stix'
plt.rcParams['font.size'] = 11.0
plt.rcParams['text.color'] = '#0f172a'
plt.rcParams['axes.edgecolor'] = '#334155'
plt.rcParams['axes.linewidth'] = 1.0


# =============================================================================
# 1. ADCS ATTACK GRAPH SCHEMA (Figure 2.1)
# =============================================================================
def generate_adcs_schema():
    fig, ax = plt.subplots(figsize=(12.2, 6.8), dpi=300)
    ax.set_xlim(0, 12.2)
    ax.set_ylim(0, 6.8)
    ax.axis('off')

    BOX_BG = '#ffffff'
    HDR_BG = '#f1f5f9'
    BORDER_COLOR = '#1e293b'
    BORDER_LW = 1.6
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    EDGE_COLOR = '#334155'
    ATTACK_COLOR = '#991b1b'

    # Nodes with comfortable spacing and enlarged sizes
    nodes = {
        'User': {
            'pos': (1.50, 4.60),
            'w': 2.60, 'h': 1.85,
            'title': 'User Principal',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{User}}$',
            'cls': 'objectClass: user',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_u}$'
        },
        'Computer': {
            'pos': (1.50, 1.75),
            'w': 2.60, 'h': 1.85,
            'title': 'Computer Object',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{Comp}}$',
            'cls': 'objectClass: computer',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_c}$'
        },
        'Group': {
            'pos': (5.40, 4.60),
            'w': 3.20, 'h': 1.85,
            'title': 'Security Group',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{Group}}$',
            'cls': 'objectClass: group',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_g}$'
        },
        'Template': {
            'pos': (5.40, 1.75),
            'w': 3.40, 'h': 1.85,
            'title': 'Certificate Template',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{Tmpl}}$',
            'cls': 'class: pKICertificateTemplate',
            'feat': r'Attr Vector $\mathbf{x}_v \in \mathbb{R}^{10}$ (EKU, Flags)'
        },
        'EnterpriseCA': {
            'pos': (10.35, 3.15),
            'w': 3.15, 'h': 1.85,
            'title': 'Enterprise CA',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{CA}}$',
            'cls': 'class: pKIEnrollmentService',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_{\mathrm{ca}}}$'
        }
    }

    # Draw Nodes
    for k, n in nodes.items():
        x, y = n['pos']
        w, h = n['w'], n['h']

        box = patches.Rectangle(
            (x - w/2, y - h/2), w, h,
            facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=BORDER_LW, zorder=3
        )
        ax.add_patch(box)

        h_strip = 0.50
        hdr = patches.Rectangle(
            (x - w/2, y + h/2 - h_strip), w, h_strip,
            facecolor=HDR_BG, edgecolor=BORDER_COLOR, linewidth=BORDER_LW, zorder=4
        )
        ax.add_patch(hdr)

        ax.text(x, y + h/2 - h_strip/2, n['title'], ha='center', va='center',
                fontsize=16.5, weight='bold', color=TEXT_MAIN, zorder=5)

        ax.text(x, y + 0.16, n['glyph'], ha='center', va='center',
                fontsize=14.5, weight='bold', color=TEXT_MAIN, zorder=5)
        ax.text(x, y - 0.22, n['cls'], ha='center', va='center',
                fontsize=12.2, family='monospace', weight='bold', color=TEXT_MUTED, zorder=5)
        ax.text(x, y - 0.58, n['feat'], ha='center', va='center',
                fontsize=12.0, style='italic', weight='bold', color=TEXT_MUTED, zorder=5)

    def draw_edge(x1, y1, x2, y2, label, rad=0.0, is_attack=False, is_dashed=False,
                  label_pos=0.5, label_offset=(0, 0)):
        color = ATTACK_COLOR if is_attack else EDGE_COLOR
        ls = '--' if is_dashed else '-'
        lw = 2.4 if is_attack else 1.9

        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=9.5,head_width=6.5",
            color=color, linestyle=ls, linewidth=lw, zorder=2
        )
        ax.add_patch(arrow)

        mx = x1 + (x2 - x1) * label_pos + label_offset[0]
        my = y1 + (y2 - y1) * label_pos + label_offset[1]

        if rad != 0.0:
            dx = x2 - x1
            dy = y2 - y1
            dist = np.hypot(dx, dy)
            if dist > 0:
                nx = -dy / dist
                ny = dx / dist
                mx += nx * (rad * dist * 0.35)
                my += ny * (rad * dist * 0.35)

        ax.text(mx, my, label, ha='center', va='center',
                fontsize=13.0, weight='bold',
                color=color,
                bbox=dict(boxstyle="square,pad=0.28", fc='#ffffff',
                          ec=color, lw=1.2, zorder=6))

    # 1. User -> Group: MemberOf (Horizontal)
    draw_edge(2.80, 4.60, 3.80, 4.60, "MemberOf", label_pos=0.5)

    # 2. Group -> Group: MemberOf (Transitive nesting self-arc on top)
    gx, gy = nodes['Group']['pos']
    loop = patches.FancyArrowPatch(
        (gx - 0.75, gy + 0.925), (gx + 0.75, gy + 0.925),
        connectionstyle="arc3,rad=-0.8",
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=EDGE_COLOR, linewidth=1.9, zorder=2
    )
    ax.add_patch(loop)
    ax.text(gx, gy + 1.64, "MemberOf (Transitive Nesting)", ha='center', va='center',
            fontsize=13.2, weight='bold', color=EDGE_COLOR,
            bbox=dict(boxstyle="square,pad=0.28", fc='#ffffff', ec=EDGE_COLOR, lw=1.1, zorder=6))

    # 3. User -> Template: Enroll / WriteDacl (Direct diagonal edge)
    draw_edge(2.80, 3.85, 3.70, 2.35, "Enroll /\nWriteDacl", rad=0.0, label_pos=0.34, label_offset=(-0.12, 0.16))

    # 4. Computer -> Template: Enroll / GenericAll (Horizontal)
    draw_edge(2.80, 1.75, 3.70, 1.75, "Enroll /\nGenericAll", label_pos=0.5)

    # 5. Group -> Template: GenericAll / WriteOwner (Vertical, Left Lane x=4.60)
    draw_edge(4.60, 3.675, 4.60, 2.675, "GenericAll /\nWriteOwner", label_pos=0.5)

    # 6. Template -> Group: LinksPolicy (ESC13) (Vertical, Right Lane x=6.20)
    draw_edge(6.20, 2.675, 6.20, 3.675, "LinksPolicy\n(ESC13)",
              is_attack=True, is_dashed=True, label_pos=0.5)

    # 7. Template -> EnterpriseCA: PublishedTo
    draw_edge(7.10, 2.05, 8.75, 2.75, "PublishedTo", label_pos=0.50)

    # 8. Group -> EnterpriseCA: ManageCA / CertManager
    draw_edge(7.00, 4.30, 8.75, 3.65, "ManageCA /\nCertManager", label_pos=0.50, label_offset=(0, 0.20))

    # Bottom Legend
    leg_box = patches.Rectangle(
        (0.40, 0.15), 11.40, 0.60,
        facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.2, zorder=2
    )
    ax.add_patch(leg_box)

    ax.text(0.60, 0.45, r"$\mathbf{Graph \; Metagraph \; Schema:}$",
            fontsize=13.5, weight='bold', color=TEXT_MAIN, va='center')

    ax.plot([3.00, 3.40], [0.45, 0.45], color=EDGE_COLOR, lw=2.2)
    ax.text(3.50, 0.45, r"Standard AD Relation ($\mathcal{E}_{\mathrm{AD}}$)",
            fontsize=12.5, weight='bold', color=TEXT_MUTED, va='center')

    ax.plot([6.05, 6.45], [0.45, 0.45], color=EDGE_COLOR, lw=2.2, ls=':')
    ax.text(6.55, 0.45, r"Administrative ACL ($\mathcal{E}_{\mathrm{DACL}}$)",
            fontsize=12.5, weight='bold', color=TEXT_MUTED, va='center')

    ax.plot([8.95, 9.35], [0.45, 0.45], color=ATTACK_COLOR, lw=2.4, ls='--')
    ax.text(9.45, 0.45, r"ESC13 Policy Inversion Link ($\mathcal{E}_{\mathrm{ESC13}}$)",
            fontsize=12.5, weight='bold', color=ATTACK_COLOR, va='center')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/adcs_attack_graph_schema.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Generated publication-grade adcs_attack_graph_schema.png")


# =============================================================================
# 2. ESC13 ATTACK PATH DIAGRAM (Figure 2.2)
# =============================================================================
def generate_esc13_diagram():
    import sys
    sys.path.insert(0, os.path.dirname(__file__))
    from generate_esc13_diagram import generate_esc13_diagram as _gen_esc13
    paths = [
        f'{OUTPUT_DIR}/esc13_attack_path_diagram.png',
        '/home/hs32/Desktop/GOAD/thesis_research/results/phase2/esc13_attack_path_diagram.png'
    ]
    _gen_esc13(paths)


# =============================================================================
# 3. CERTGRAPH HETERO-GAT ARCHITECTURE DIAGRAM (Figure 3.1)
# =============================================================================
def generate_certgraph_arch():
    fig, ax = plt.subplots(figsize=(15.6, 7.8), dpi=300)
    ax.set_xlim(0, 15.6)
    ax.set_ylim(0, 7.8)
    ax.axis('off')

    BOX_BG = '#ffffff'
    BORDER_COLOR = '#1e293b'
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    ACCENT_RED = '#991b1b'

    col_h = 6.6
    col_y = 3.9

    # Section 1: Input Hetero Graph
    s1_w = 3.00
    s1_xc = 2.05
    box1 = patches.Rectangle(
        (s1_xc - s1_w/2, col_y - col_h/2), s1_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box1)

    hdr1 = patches.Rectangle(
        (s1_xc - s1_w/2, col_y + col_h/2 - 0.56), s1_w, 0.56,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr1)
    ax.text(s1_xc, col_y + col_h/2 - 0.28, "1. Input Hetero Graph", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(s1_xc, col_y + 2.35, r"$\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{T}_V, \mathcal{T}_E)$",
            ha='center', va='center', fontsize=14.5, weight='bold', color=TEXT_MAIN)

    # Network schematic
    g_nodes = [
        (s1_xc - 0.85, col_y + 1.45, 'U', 'o', '#e2e8f0'),
        (s1_xc + 0.85, col_y + 1.55, 'G', '^', '#e2e8f0'),
        (s1_xc - 0.75, col_y + 0.40, 'C', 's', '#e2e8f0'),
        (s1_xc + 0.10, col_y + 0.85, 'T', 'D', '#fee2e2'),
        (s1_xc + 0.95, col_y + 0.30, 'CA', 'h', '#e2e8f0'),
    ]
    ax.plot([s1_xc - 0.85, s1_xc + 0.85], [col_y + 1.45, col_y + 1.55], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc - 0.85, s1_xc + 0.10], [col_y + 1.45, col_y + 0.85], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc + 0.85, s1_xc + 0.10], [col_y + 1.55, col_y + 0.85], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc - 0.75, s1_xc + 0.10], [col_y + 0.40, col_y + 0.85], color='#64748b', lw=1.6, zorder=3)
    ax.plot([s1_xc + 0.10, s1_xc + 0.95], [col_y + 0.85, col_y + 0.30], color='#64748b', lw=1.6, zorder=3)

    for gx, gy, glbl, gshape, gcol in g_nodes:
        ax.plot(gx, gy, marker=gshape, markersize=26, color=gcol,
                markeredgecolor=BORDER_COLOR, markeredgewidth=1.5, zorder=4)
        ax.text(gx, gy, glbl, ha='center', va='center', fontsize=13.0, weight='bold', color=TEXT_MAIN, zorder=5)

    ax.text(s1_xc, col_y - 0.50, "5 Entity Node Types:\nUser, Comp, Group, Tmpl, CA",
            ha='center', va='center', fontsize=12.5, weight='bold', color=TEXT_MUTED, linespacing=1.25)

    proj_box = patches.Rectangle(
        (s1_xc - 1.35, col_y - 2.85), 2.70, 1.80,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
    )
    ax.add_patch(proj_box)
    ax.text(s1_xc, col_y - 1.35, "Linear Projections:", ha='center', va='center',
            fontsize=13.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s1_xc, col_y - 1.90, r"$\mathbf{z}_u = W_{\mathrm{src}}^{(r)} \mathbf{h}_u^{(l-1)}$",
            ha='center', va='center', fontsize=13.0, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s1_xc, col_y - 2.45, r"$\mathbf{z}_v = W_{\mathrm{dst}}^{(r)} \mathbf{h}_v^{(l-1)}$",
            ha='center', va='center', fontsize=13.0, weight='bold', color=TEXT_MAIN, zorder=4)

    # Arrow 1
    arrow1 = patches.FancyArrowPatch(
        (s1_xc + s1_w/2, col_y), (4.12, col_y),
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=BORDER_COLOR, linewidth=2.2, zorder=5
    )
    ax.add_patch(arrow1)

    # Section 2: Hetero-GAT Layer 1
    s2_w = 3.30
    s2_xc = 5.77
    box2 = patches.Rectangle(
        (s2_xc - s2_w/2, col_y - col_h/2), s2_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box2)

    hdr2 = patches.Rectangle(
        (s2_xc - s2_w/2, col_y + col_h/2 - 0.56), s2_w, 0.56,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr2)
    ax.text(s2_xc, col_y + col_h/2 - 0.28, "2. Hetero-GAT Layer 1", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    # MHA block
    mha_box = patches.Rectangle(
        (s2_xc - 1.50, col_y + 0.15), 3.00, 2.35,
        facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.2, zorder=3
    )
    ax.add_patch(mha_box)
    ax.text(s2_xc, col_y + 2.15, "Relational Attention (MHA)", ha='center', va='center',
            fontsize=13.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y + 1.68, r"Heads $K=4$, $\; d_{\mathrm{head}} = 16$",
            ha='center', va='center', fontsize=12.5, weight='bold', color=TEXT_MUTED, zorder=4)
    ax.text(s2_xc, col_y + 1.10,
            r"$e_{vu}^{(k,r)} = \operatorname{LeakyReLU}\left(\mathbf{a}_k^T [\mathbf{z}_v \| \mathbf{z}_u]\right)$",
            ha='center', va='center', fontsize=12.5, color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y + 0.52,
            r"$\alpha_{vu}^{(k,r)} = \operatorname{Softmax}_{\mathcal{N}_r(v)}\left(e_{vu}^{(k,r)}\right)$",
            ha='center', va='center', fontsize=12.5, color=TEXT_MAIN, zorder=4)

    # Aggregation block
    agg_box = patches.Rectangle(
        (s2_xc - 1.50, col_y - 1.45), 3.00, 1.45,
        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
    )
    ax.add_patch(agg_box)
    ax.text(s2_xc, col_y - 0.45, r"$\mathbf{\mu}_{v,r}^{(1)} = \bigoplus_{k=1}^K \sum_{u} \alpha_{vu}^{(k,r)} \mathbf{z}_u^{(k,r)}$",
            ha='center', va='center', fontsize=12.8, color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y - 1.00, "ELU Activation + LayerNorm",
            ha='center', va='center', fontsize=12.2, weight='bold', color=TEXT_MUTED, zorder=4)

    # Dedicated Residual Update Card
    res_box = patches.Rectangle(
        (s2_xc - 1.50, col_y - 3.05), 3.00, 1.45,
        facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=1.2, zorder=3
    )
    ax.add_patch(res_box)
    ax.text(s2_xc, col_y - 1.85, "Residual Update & Skip:", ha='center', va='center',
            fontsize=12.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y - 2.35, r"$\mathbf{h}_v^{(1)} \leftarrow \mathbf{h}_v^{(1)} + W_{\mathrm{skip}} \mathbf{h}_v^{(0)}$",
            ha='center', va='center', fontsize=12.8, weight='bold', color='#1e293b', zorder=4)
    ax.text(s2_xc, col_y - 2.80, "Theorem 1: Avoids Source Collapse",
            ha='center', va='center', fontsize=11.5, weight='bold', style='italic', color=TEXT_MUTED, zorder=4)

    # Arrow 2
    arrow2 = patches.FancyArrowPatch(
        (s2_xc + s2_w/2, col_y), (7.99, col_y),
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=BORDER_COLOR, linewidth=2.2, zorder=5
    )
    ax.add_patch(arrow2)

    # Section 3: Layer 2 & Readout
    s3_w = 3.30
    s3_xc = 9.64
    box3 = patches.Rectangle(
        (s3_xc - s3_w/2, col_y - col_h/2), s3_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box3)

    hdr3 = patches.Rectangle(
        (s3_xc - s3_w/2, col_y + col_h/2 - 0.56), s3_w, 0.56,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr3)
    ax.text(s3_xc, col_y + col_h/2 - 0.28, "3. Layer 2 & Readout", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    # Layer 2 Conv block
    l2_box = patches.Rectangle(
        (s3_xc - 1.50, col_y + 0.15), 3.00, 2.35,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
    )
    ax.add_patch(l2_box)
    ax.text(s3_xc, col_y + 2.15, "2-Hop Topological Conv", ha='center', va='center',
            fontsize=13.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y + 1.50, "Aggregates multi-hop DACLs\nand policy linkage contexts",
            ha='center', va='center', fontsize=12.2, weight='bold', color=TEXT_MUTED, linespacing=1.25, zorder=4)
    ax.text(s3_xc, col_y + 0.65, r"Skip: $\mathbf{h}_v^{(2)} \leftarrow \mathbf{h}_v^{(2)} + W_{\mathrm{skip}}^{(2)} \mathbf{h}_v^{(1)}$",
            ha='center', va='center', fontsize=12.2, weight='bold', color='#1e293b', zorder=4)

    # Readout box
    read_box = patches.Rectangle(
        (s3_xc - 1.50, col_y - 2.85), 3.00, 2.80,
        facecolor='#ffffff', edgecolor='#94a3b8', linewidth=1.2, zorder=3
    )
    ax.add_patch(read_box)
    ax.text(s3_xc, col_y - 0.40, "Template Node Readout", ha='center', va='center',
            fontsize=13.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y - 1.00, r"Target Entity: $v \in \mathcal{V}_{\mathrm{Tmpl}}$",
            ha='center', va='center', fontsize=12.8, weight='bold', color=TEXT_MUTED, zorder=4)
    ax.text(s3_xc, col_y - 1.60, r"Embedding: $\mathbf{h}_t \in \mathbb{R}^{64}$",
            ha='center', va='center', fontsize=13.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y - 2.25, "Isolated Vulnerability\nLatent State",
            ha='center', va='center', fontsize=12.0, weight='bold', style='italic', color=TEXT_MUTED, linespacing=1.2, zorder=4)

    # Arrow 3
    arrow3 = patches.FancyArrowPatch(
        (s3_xc + s3_w/2, col_y), (11.85, col_y),
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=BORDER_COLOR, linewidth=2.2, zorder=5
    )
    ax.add_patch(arrow3)

    # Section 4: Classification Head
    s4_w = 3.20
    s4_xc = 13.45
    box4 = patches.Rectangle(
        (s4_xc - s4_w/2, col_y - col_h/2), s4_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box4)

    hdr4 = patches.Rectangle(
        (s4_xc - s4_w/2, col_y + col_h/2 - 0.56), s4_w, 0.56,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr4)
    ax.text(s4_xc, col_y + col_h/2 - 0.28, "4. Classification Head", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(s4_xc, col_y + 2.30, "MLP Projection Head:", ha='center', va='center',
            fontsize=13.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s4_xc, col_y + 1.80, r"$\mathrm{Linear}(64 \to 32) \to \mathrm{ReLU}$",
            ha='center', va='center', fontsize=12.2, weight='bold', color=TEXT_MUTED, zorder=4)
    ax.text(s4_xc, col_y + 1.35, r"$\mathrm{Dropout}(0.2) \to \mathrm{Linear}(32 \to 7)$",
            ha='center', va='center', fontsize=12.2, weight='bold', color=TEXT_MUTED, zorder=4)
    ax.text(s4_xc, col_y + 0.88, r"$\hat{\mathbf{y}} = \operatorname{Softmax}(\mathbf{z}_{\mathrm{cls}}) \in \Delta^6$",
            ha='center', va='center', fontsize=13.0, weight='bold', color=TEXT_MAIN, zorder=4)

    # Classes list
    esc_labels = [
        ("Safe", "#059669", "Benign"),
        ("ESC1", ACCENT_RED, "Enrollee Supplies SAN"),
        ("ESC2", ACCENT_RED, "Any Purpose EKU"),
        ("ESC3", ACCENT_RED, "Cert Request Agent"),
        ("ESC4", ACCENT_RED, "DACL / WriteOwner"),
        ("ESC9", ACCENT_RED, "No Security Extension"),
        ("ESC13", ACCENT_RED, "Policy OID Linkage"),
    ]

    list_y_start = col_y + 0.38
    row_h = 0.44
    for idx, (lbl, col, desc) in enumerate(esc_labels):
        ry = list_y_start - (idx * row_h)
        badge = patches.FancyBboxPatch(
            (s4_xc - 1.45, ry - 0.17), 0.82, 0.34,
            boxstyle="round,pad=0.03,rounding_size=0.06",
            facecolor='#fef2f2' if col == ACCENT_RED else '#f0fdf4',
            edgecolor=col, linewidth=1.2, zorder=3
        )
        ax.add_patch(badge)
        ax.text(s4_xc - 1.04, ry, lbl, ha='center', va='center',
                fontsize=11.8, weight='bold', color=col, zorder=4)
        ax.text(s4_xc - 0.48, ry, desc, ha='left', va='center',
                fontsize=11.8, weight='bold', color=TEXT_MAIN, zorder=4)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/certgraph_architecture_diagram.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Generated publication-grade certgraph_architecture_diagram.png")


# Alias for backwards compatibility
generate_certgraph_architecture = generate_certgraph_arch


# =============================================================================
# 4. TWO-TIER NEURO-SYMBOLIC PIPELINE (Figure 8.1)
# =============================================================================
def generate_neuro_symbolic_pipeline():
    fig, ax = plt.subplots(figsize=(16.8, 8.6), dpi=300)
    ax.set_xlim(0, 16.8)
    ax.set_ylim(0, 8.6)
    ax.axis('off')

    BOX_BG = '#ffffff'
    BORDER_COLOR = '#1e293b'
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    WARN_RED = '#991b1b'
    SUCC_GREEN = '#047857'

    col_h = 6.4
    col_y = 4.8

    b_w = 3.00
    col_xcs = [2.10, 6.30, 10.50, 14.70]

    # ================= 1. AD Graph Ingestion (Column 1) =================
    b1_xc = col_xcs[0]
    box1 = patches.Rectangle(
        (b1_xc - b_w/2, col_y - col_h/2), b_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box1)

    hdr1 = patches.Rectangle(
        (b1_xc - b_w/2, col_y + col_h/2 - 0.58), b_w, 0.58,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr1)
    ax.text(b1_xc, col_y + col_h/2 - 0.29, "1. AD Graph Ingestion", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(b1_xc, col_y + 2.20, "Telemetry Extraction:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b1_xc, col_y + 1.40,
            "• Live LDAP & RPC Audits\n• BloodHound / SharpHound\n• Active Directory PKI Schema",
            ha='center', va='center', fontsize=11.8, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    ax.text(b1_xc, col_y + 0.35, "HeteroData Mapping:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b1_xc, col_y - 0.45,
            r"$\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{T}_V, \mathcal{T}_E)$" "\n"
            r"$|\mathcal{V}| > 10^5, \; |\mathcal{E}| > 10^6$" "\nTransitive DACLs & Groups",
            ha='center', va='center', fontsize=11.8, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    ingest_box = patches.Rectangle(
        (b1_xc - 1.35, col_y - 2.85), 2.70, 1.55,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
    )
    ax.add_patch(ingest_box)
    ax.text(b1_xc, col_y - 1.75, "Continuous Auditor:", ha='center', va='center',
            fontsize=12.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(b1_xc, col_y - 2.30, "Dynamic Delta Sync\nLDAP USN Tracking",
            ha='center', va='center', fontsize=11.8, weight='bold', color=TEXT_MUTED, linespacing=1.25, zorder=4)

    # Gap 1: Transition 1 -> 2
    g1_c = 4.20
    arrow1_y = col_y + 0.35
    arrow1 = patches.FancyArrowPatch(
        (3.60, arrow1_y), (4.80, arrow1_y),
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=BORDER_COLOR, linewidth=2.0, zorder=5
    )
    ax.add_patch(arrow1)
    pill1 = patches.FancyBboxPatch(
        (g1_c - 0.46, arrow1_y + 0.22), 0.92, 0.40,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        facecolor='#f1f5f9', edgecolor='#64748b', linewidth=1.1, zorder=5
    )
    ax.add_patch(pill1)
    ax.text(g1_c, arrow1_y + 0.42, "AD Graph", ha='center', va='center',
            fontsize=11.5, weight='bold', color=TEXT_MAIN, zorder=6)

    # ================= 2. Tier 1: Inductive Screening (Column 2) =================
    b2_xc = col_xcs[1]
    box2 = patches.Rectangle(
        (b2_xc - b_w/2, col_y - col_h/2), b_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box2)

    hdr2 = patches.Rectangle(
        (b2_xc - b_w/2, col_y + col_h/2 - 0.58), b_w, 0.58,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr2)
    ax.text(b2_xc, col_y + col_h/2 - 0.29, "2. Tier 1: Screening", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(b2_xc, col_y + 2.20, "CertGraph Hetero-GAT:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b2_xc, col_y + 1.40,
            r"• Forward: $\hat{\mathbf{y}}_t = \mathrm{CertGraph}(G, t) \in \Delta^6$" "\n"
            r"• Risk: $S_{\mathrm{risk}}(t) = 1.0 - \hat{y}_t[\mathrm{Safe}]$" "\n"
            r"• Latency: $<25$ ms per 1,000 nodes",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    ax.text(b2_xc, col_y + 0.35, "Candidate Filter:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b2_xc, col_y - 0.45,
            r"• Prunes $>95\%$ benign templates" "\n"
            r"• Emits Top-$K$ suspect queue: $\mathcal{Q}_{\mathrm{suspect}}$" "\n"
            r"• Prevents state explosion in verifier",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    speed_box = patches.Rectangle(
        (b2_xc - 1.35, col_y - 2.85), 2.70, 1.55,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
    )
    ax.add_patch(speed_box)
    ax.text(b2_xc, col_y - 1.75, "Throughput Performance:", ha='center', va='center',
            fontsize=12.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(b2_xc, col_y - 2.30, "Full Directory Sweep in <2.4s\n$\mathcal{O}(|V| + |E|)$ GPU Inference",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MUTED, linespacing=1.25, zorder=4)

    # Gap 2: Transition 2 -> 3
    g2_c = 8.40
    arrow2_y = col_y + 0.35
    arrow2 = patches.FancyArrowPatch(
        (7.80, arrow2_y), (9.00, arrow2_y),
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=BORDER_COLOR, linewidth=2.0, zorder=5
    )
    ax.add_patch(arrow2)
    pill2 = patches.FancyBboxPatch(
        (g2_c - 0.48, arrow2_y + 0.18), 0.96, 0.48,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        facecolor='#f1f5f9', edgecolor='#64748b', linewidth=1.1, zorder=5
    )
    ax.add_patch(pill2)
    ax.text(g2_c, arrow2_y + 0.42, "Top-$K$\nSuspects", ha='center', va='center',
            fontsize=10.8, weight='bold', color=TEXT_MAIN, linespacing=1.15, zorder=6)

    # ================= 3. Tier 2: Symbolic Verification (Column 3) =================
    b3_xc = col_xcs[2]
    box3 = patches.Rectangle(
        (b3_xc - b_w/2, col_y - col_h/2), b_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box3)

    hdr3 = patches.Rectangle(
        (b3_xc - b_w/2, col_y + col_h/2 - 0.58), b_w, 0.58,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr3)
    ax.text(b3_xc, col_y + col_h/2 - 0.29, "3. Tier 2: Verification", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(b3_xc, col_y + 2.20, "Sound Traversal:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b3_xc, col_y + 1.40,
            r"• 2-hop authorization subgraph query" "\n"
            r"• Horn: $\mathrm{Exploit}(t) = \mathrm{Verify}(G, V_{\mathrm{low}}, t)$" "\n"
            r"• Checks DACLs, OIDs & enroll rights",
            ha='center', va='center', fontsize=11.2, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    ax.text(b3_xc, col_y + 0.35, "Soundness Decision:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)

    # Branch 1: Hard Negative
    p_false_box = patches.Rectangle(
        (b3_xc - 1.35, col_y - 0.85), 2.70, 0.95,
        facecolor='#f0fdf4', edgecolor=SUCC_GREEN, linewidth=1.3, zorder=3
    )
    ax.add_patch(p_false_box)
    ax.text(b3_xc, col_y - 0.38, r"$\mathbf{Hard \; Negative \; (Safe)}$",
            ha='center', va='center', fontsize=12.5, weight='bold', color=SUCC_GREEN, zorder=4)
    ax.text(b3_xc, col_y - 0.65, "False Alarm Suppressed / Logged",
            ha='center', va='center', fontsize=11.2, weight='bold', color=SUCC_GREEN, zorder=4)

    # Branch 2: Valid Exploit Path
    p_true_box = patches.Rectangle(
        (b3_xc - 1.35, col_y - 2.85), 2.70, 1.55,
        facecolor='#fef2f2', edgecolor=WARN_RED, linewidth=1.3, zorder=3
    )
    ax.add_patch(p_true_box)
    ax.text(b3_xc, col_y - 1.75, r"$\mathbf{Valid \; Exploit \; Path}$",
            ha='center', va='center', fontsize=13.5, weight='bold', color=WARN_RED, zorder=4)
    ax.text(b3_xc, col_y - 2.30, "Sound Mathematical Proof Tree\nTriggers Autonomous Remediation",
            ha='center', va='center', fontsize=11.2, weight='bold', color=WARN_RED, linespacing=1.25, zorder=4)

    # Gap 3: Transition 3 -> 4
    g3_c = 12.60
    arrow3_y = col_y - 2.05
    arrow3 = patches.FancyArrowPatch(
        (12.00, arrow3_y), (13.20, arrow3_y),
        arrowstyle="-|>,head_length=9.5,head_width=6.5",
        color=WARN_RED, linewidth=2.0, zorder=5
    )
    ax.add_patch(arrow3)
    pill3 = patches.FancyBboxPatch(
        (g3_c - 0.46, arrow3_y + 0.18), 0.92, 0.48,
        boxstyle="round,pad=0.03,rounding_size=0.08",
        facecolor='#fef2f2', edgecolor=WARN_RED, linewidth=1.2, zorder=5
    )
    ax.add_patch(pill3)
    ax.text(g3_c, arrow3_y + 0.42, "Verified\nProof", ha='center', va='center',
            fontsize=10.8, weight='bold', color=WARN_RED, linespacing=1.15, zorder=6)

    # ================= 4. Tier 3: Autonomous Remediation (Column 4) =================
    b4_xc = col_xcs[3]
    box4 = patches.Rectangle(
        (b4_xc - b_w/2, col_y - col_h/2), b_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.4, zorder=2
    )
    ax.add_patch(box4)

    hdr4 = patches.Rectangle(
        (b4_xc - b_w/2, col_y + col_h/2 - 0.58), b_w, 0.58,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.4, zorder=3
    )
    ax.add_patch(hdr4)
    ax.text(b4_xc, col_y + col_h/2 - 0.29, "4. Remediation", ha='center', va='center',
            fontsize=15.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(b4_xc, col_y + 2.20, "Policy Optimization:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b4_xc, col_y + 1.40,
            r"• Stackelberg Game / ADESDP" "\n"
            r"• Minimal cut: $\min \operatorname{Impact}(E_{\mathrm{cut}})$" "\n"
            r"• s.t. $\mathrm{NoPath}(G \setminus E_{\mathrm{cut}})$",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    ax.text(b4_xc, col_y + 0.35, "Targeted LDAP Actuation:", ha='center', va='center',
            fontsize=13.5, weight='bold', color=TEXT_MAIN)
    ax.text(b4_xc, col_y - 0.45,
            "• Revokes rogue enrollment ACEs\n• Unlinks vulnerable policy OIDs\n• Zero operational disruption",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MUTED, linespacing=1.35)

    rem_box = patches.Rectangle(
        (b4_xc - 1.35, col_y - 2.85), 2.70, 1.55,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
    )
    ax.add_patch(rem_box)
    ax.text(b4_xc, col_y - 1.75, "Remediation Outcome:", ha='center', va='center',
            fontsize=12.8, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(b4_xc, col_y - 2.30, r"Edge Cut: $E_{\mathrm{cut}} \subseteq \mathcal{E}$" "\nOptimal ACL Revocation",
            ha='center', va='center', fontsize=11.5, weight='bold', color=TEXT_MUTED, linespacing=1.25, zorder=4)

    # Closed-Loop Feedback Bus: Routes from bottom of Col 4 back to bottom of Col 1
    fb_y = 0.65
    fb_points = [
        (b4_xc, col_y - col_h/2),
        (b4_xc, fb_y),
        (b1_xc, fb_y),
        (b1_xc, col_y - col_h/2)
    ]
    ax.plot([p[0] for p in fb_points], [p[1] for p in fb_points],
            color='#1e293b', linestyle='--', linewidth=2.0, zorder=4)

    ax.scatter([b1_xc], [col_y - col_h/2], marker='^', s=120, color='#1e293b', zorder=5)

    mid_xc = (b1_xc + b4_xc) / 2
    fb_badge = patches.FancyBboxPatch(
        (mid_xc - 3.80, fb_y - 0.28), 7.60, 0.56,
        boxstyle="round,pad=0.04,rounding_size=0.10",
        facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.3, zorder=5
    )
    ax.add_patch(fb_badge)
    ax.text(mid_xc, fb_y, "Closed-Loop Feedback: State Ingestion Delta Sync Post-Remediation",
            ha='center', va='center', fontsize=13.0, weight='bold', color='#1e293b', zorder=6)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/neuro_symbolic_pipeline.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Generated publication-grade neuro_symbolic_pipeline.png")


if __name__ == '__main__':
    generate_adcs_schema()
    generate_esc13_diagram()
    generate_certgraph_arch()
    generate_neuro_symbolic_pipeline()
    print("All 4 publication diagrams generated successfully.")
