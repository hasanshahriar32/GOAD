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
    fig, ax = plt.subplots(figsize=(12.0, 6.8), dpi=300)
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 6.8)
    ax.axis('off')

    BOX_BG = '#ffffff'
    HDR_BG = '#f1f5f9'
    BORDER_COLOR = '#1e293b'
    BORDER_LW = 1.2
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    EDGE_COLOR = '#334155'
    ATTACK_COLOR = '#991b1b'

    # Nodes with comfortable spacing and enlarged sizes
    nodes = {
        'User': {
            'pos': (2.1, 4.6),
            'w': 2.8, 'h': 1.6,
            'title': 'User Principal',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{User}}$',
            'cls': 'objectClass: user',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_u}$'
        },
        'Computer': {
            'pos': (2.1, 1.8),
            'w': 2.8, 'h': 1.6,
            'title': 'Computer Object',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{Comp}}$',
            'cls': 'objectClass: computer',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_c}$'
        },
        'Group': {
            'pos': (6.3, 4.6),
            'w': 3.0, 'h': 1.6,
            'title': 'Security Group',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{Group}}$',
            'cls': 'objectClass: group',
            'feat': r'Feature Vector $\mathbf{x}_v \in \mathbb{R}^{d_g}$'
        },
        'Template': {
            'pos': (6.3, 1.8),
            'w': 3.2, 'h': 1.65,
            'title': 'Certificate Template',
            'glyph': r'$\mathbf{v} \in \mathcal{V}_{\mathrm{Tmpl}}$',
            'cls': 'class: pKICertificateTemplate',
            'feat': r'Attr Vector $\mathbf{x}_v \in \mathbb{R}^{10}$ (EKU, Flags)'
        },
        'EnterpriseCA': {
            'pos': (10.6, 3.2),
            'w': 2.6, 'h': 1.6,
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

        h_strip = 0.42
        hdr = patches.Rectangle(
            (x - w/2, y + h/2 - h_strip), w, h_strip,
            facecolor=HDR_BG, edgecolor=BORDER_COLOR, linewidth=BORDER_LW, zorder=4
        )
        ax.add_patch(hdr)

        ax.text(x, y + h/2 - h_strip/2, n['title'], ha='center', va='center',
                fontsize=11.5, weight='bold', color=TEXT_MAIN, zorder=5)

        ax.text(x, y + 0.12, n['glyph'], ha='center', va='center',
                fontsize=11.0, color=TEXT_MAIN, zorder=5)
        ax.text(x, y - 0.18, n['cls'], ha='center', va='center',
                fontsize=9.5, family='monospace', color=TEXT_MUTED, zorder=5)
        ax.text(x, y - 0.48, n['feat'], ha='center', va='center',
                fontsize=9.0, style='italic', color=TEXT_MUTED, zorder=5)

    def draw_edge(x1, y1, x2, y2, label, rad=0.0, is_attack=False, is_dashed=False,
                  label_pos=0.5, label_offset=(0, 0)):
        color = ATTACK_COLOR if is_attack else EDGE_COLOR
        ls = '--' if is_dashed else '-'
        lw = 1.6 if is_attack else 1.3

        arrow = patches.FancyArrowPatch(
            (x1, y1), (x2, y2),
            connectionstyle=f"arc3,rad={rad}",
            arrowstyle="-|>,head_length=7,head_width=4.5",
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
                fontsize=9.5, weight='bold',
                color=color,
                bbox=dict(boxstyle="square,pad=0.22", fc='#ffffff',
                          ec=color, lw=0.9, zorder=6))

    # 1. User -> Group: MemberOf (Horizontal)
    draw_edge(3.5, 4.6, 4.80, 4.6, "MemberOf", label_pos=0.5)

    # 2. Group -> Group: MemberOf (Transitive nesting self-arc on top)
    gx, gy = nodes['Group']['pos']
    loop = patches.FancyArrowPatch(
        (gx - 0.65, gy + 0.8), (gx + 0.65, gy + 0.8),
        connectionstyle="arc3,rad=-0.8",
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=EDGE_COLOR, linewidth=1.3, zorder=2
    )
    ax.add_patch(loop)
    ax.text(gx, gy + 1.45, "MemberOf (Transitive Nesting)", ha='center', va='center',
            fontsize=9.5, weight='bold', color=EDGE_COLOR,
            bbox=dict(boxstyle="square,pad=0.20", fc='#ffffff', ec=EDGE_COLOR, lw=0.8, zorder=6))

    # 3. User -> Template: Enroll / WriteDacl (Direct diagonal edge)
    draw_edge(3.5, 4.0, 4.70, 2.5, "Enroll / WriteDacl", rad=0.08, label_pos=0.45)

    # 4. Computer -> Template: Enroll / GenericAll (Horizontal)
    draw_edge(3.5, 1.8, 4.70, 1.8, "Enroll / GenericAll", label_pos=0.5)

    # 5. Group -> Template: GenericAll / WriteOwner (Vertical, Left Lane x=5.35)
    draw_edge(5.35, 3.8, 5.35, 2.625, "GenericAll / WriteOwner", label_pos=0.5)

    # 6. Template -> Group: LinksPolicy (ESC13) (Vertical, Right Lane x=7.25)
    draw_edge(7.25, 2.625, 7.25, 3.8, "LinksPolicy (ESC13)",
              is_attack=True, is_dashed=True, label_pos=0.5)

    # 7. Template -> EnterpriseCA: PublishedTo
    draw_edge(7.90, 2.15, 9.30, 2.85, "PublishedTo", label_pos=0.5)

    # 8. Group -> EnterpriseCA: ManageCA / CertManager
    draw_edge(7.80, 4.40, 9.30, 3.75, "ManageCA / CertManager", label_pos=0.45, label_offset=(0, 0.22))

    # Bottom Legend
    leg_box = patches.Rectangle(
        (0.6, 0.22), 10.8, 0.48,
        facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=0.9, zorder=2
    )
    ax.add_patch(leg_box)

    ax.text(0.8, 0.46, r"$\mathbf{Graph \; Metagraph \; Schema:}$",
            fontsize=10.0, weight='bold', color=TEXT_MAIN, va='center')

    ax.plot([2.7, 3.1], [0.46, 0.46], color=EDGE_COLOR, lw=1.5)
    ax.text(3.2, 0.46, r"Standard AD Relation ($\mathcal{E}_{\mathrm{AD}}$)",
            fontsize=9.5, color=TEXT_MUTED, va='center')

    ax.plot([5.5, 5.9], [0.46, 0.46], color=EDGE_COLOR, lw=1.5, ls=':')
    ax.text(6.0, 0.46, r"Administrative ACL ($\mathcal{E}_{\mathrm{DACL}}$)",
            fontsize=9.5, color=TEXT_MUTED, va='center')

    ax.plot([8.2, 8.6], [0.46, 0.46], color=ATTACK_COLOR, lw=1.8, ls='--')
    ax.text(8.7, 0.46, r"ESC13 Policy Inversion Link ($\mathcal{E}_{\mathrm{ESC13}}$)",
            fontsize=9.5, weight='bold', color=ATTACK_COLOR, va='center')

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/adcs_attack_graph_schema.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Generated publication-grade adcs_attack_graph_schema.png")


# =============================================================================
# 2. ESC13 ATTACK PATH DIAGRAM (Figure 2.2)
# =============================================================================
def generate_esc13_diagram():
    fig, ax = plt.subplots(figsize=(12.0, 5.6), dpi=300)
    ax.set_xlim(0, 12.0)
    ax.set_ylim(0, 5.6)
    ax.axis('off')

    BOX_BG = '#ffffff'
    HDR_BG = '#f1f5f9'
    BORDER_COLOR = '#1e293b'
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#475569'
    ARROW_COLOR = '#1e293b'
    TARGET_BORDER = '#991b1b'
    TARGET_HDR = '#fef2f2'

    y_nodes = 4.10
    w_node = 1.60
    h_node = 1.80

    chain = [
        {
            'x': 1.10,
            'stage': 'Compromised User',
            'sub': 'Initial Foothold',
            'props': [
                ('Type', 'User Principal'),
                ('sAMAccount', 'jsmith'),
                ('Context', 'Domain User'),
                ('Privilege', 'Low-Priv / Unauth')
            ],
            'is_target': False
        },
        {
            'x': 3.50,
            'stage': 'Enroller Group',
            'sub': 'Intermediate Principal',
            'props': [
                ('Type', 'Security Group'),
                ('CN', 'CertEnrollers'),
                ('Membership', 'Nested User Member'),
                ('Permission', 'Certificate-Enroll')
            ],
            'is_target': False
        },
        {
            'x': 5.90,
            'stage': 'ESC13 Template',
            'sub': 'Target Template Object',
            'props': [
                ('Type', 'pKICertTemplate'),
                ('SchemaVer', 'v2 (Editable)'),
                ('PolicyAttr', 'msPKI-Cert-Policy'),
                ('Approval', 'No Manager Approval')
            ],
            'is_target': False
        },
        {
            'x': 8.30,
            'stage': 'Issuance Policy',
            'sub': 'OID Linkage Object',
            'props': [
                ('Type', 'msPKI-Enterprise-OID'),
                ('OID Value', '1.3.6.1.4.1.311...'),
                ('Mapping', 'msDS-OIDToGroupLink'),
                ('LinkedSID', 'S-1-5-21...-512')
            ],
            'is_target': False
        },
        {
            'x': 10.70,
            'stage': 'Domain Admins',
            'sub': 'Tier-0 Target Asset',
            'props': [
                ('Type', 'Administrative Group'),
                ('RID', '512 (Domain Admins)'),
                ('Impact', 'Kerberos PAC Injection'),
                ('Dominance', 'Full Forest Takeover')
            ],
            'is_target': True
        }
    ]

    for item in chain:
        x = item['x']
        y = y_nodes
        b_col = TARGET_BORDER if item['is_target'] else BORDER_COLOR
        h_col = TARGET_HDR if item['is_target'] else HDR_BG
        lw = 1.3 if item['is_target'] else 1.0

        box = patches.Rectangle(
            (x - w_node/2, y - h_node/2), w_node, h_node,
            facecolor=BOX_BG, edgecolor=b_col, linewidth=lw, zorder=3
        )
        ax.add_patch(box)

        h_hdr = 0.42
        hdr = patches.Rectangle(
            (x - w_node/2, y + h_node/2 - h_hdr), w_node, h_hdr,
            facecolor=h_col, edgecolor=b_col, linewidth=lw, zorder=4
        )
        ax.add_patch(hdr)

        ax.text(x, y + h_node/2 - 0.15, item['stage'], ha='center', va='center',
                fontsize=7.8, weight='bold', color=TARGET_BORDER if item['is_target'] else TEXT_MAIN, zorder=5)
        ax.text(x, y + h_node/2 - 0.31, item['sub'], ha='center', va='center',
                fontsize=6.6, style='italic', color=TEXT_MUTED, zorder=5)

        y_text = y + 0.26
        for k, v in item['props']:
            ax.text(x - w_node/2 + 0.08, y_text, f"{k}:", ha='left', va='center',
                fontsize=6.4, weight='bold', color=TEXT_MAIN, zorder=5)
            ax.text(x + w_node/2 - 0.08, y_text, v, ha='right', va='center',
                fontsize=6.4, family='monospace' if 'SID' in v or '1.3' in v or '512' in v else 'STIXGeneral',
                color=TEXT_MUTED, zorder=5)
            y_text -= 0.25

    steps = [
        {'x1': 1.10 + w_node/2 + 0.02, 'x2': 3.50 - w_node/2 - 0.02, 'step': 'Step 1', 'action': 'MemberOf', 'proto': 'LDAP Nesting'},
        {'x1': 3.50 + w_node/2 + 0.02, 'x2': 5.90 - w_node/2 - 0.02, 'step': 'Step 2', 'action': 'Enroll', 'proto': 'MS-WCCE RPC'},
        {'x1': 5.90 + w_node/2 + 0.02, 'x2': 8.30 - w_node/2 - 0.02, 'step': 'Step 3', 'action': 'LinksPolicy', 'proto': 'OID Linkage'},
        {'x1': 8.30 + w_node/2 + 0.02, 'x2': 10.70 - w_node/2 - 0.02, 'step': 'Step 4', 'action': 'PAC Elevation', 'proto': 'Kerberos PKINIT'}
    ]

    for s in steps:
        mid_x = (s['x1'] + s['x2']) / 2
        arrow = patches.FancyArrowPatch(
            (s['x1'], y_nodes), (s['x2'], y_nodes),
            arrowstyle="-|>,head_length=5,head_width=3.5",
            color=ARROW_COLOR, linewidth=1.1, zorder=2
        )
        ax.add_patch(arrow)

        ax.text(mid_x, y_nodes + 0.28, s['step'], ha='center', va='center',
                fontsize=6.5, weight='bold', color=TEXT_MAIN,
                bbox=dict(boxstyle="square,pad=0.15", fc='#f1f5f9', ec='#94a3b8', lw=0.5, zorder=4))
        ax.text(mid_x, y_nodes - 0.26, s['action'], ha='center', va='center',
                fontsize=6.2, weight='bold', color=TEXT_MAIN)
        ax.text(mid_x, y_nodes - 0.44, s['proto'], ha='center', va='center',
                fontsize=5.8, style='italic', color=TEXT_MUTED)

    seq_border = patches.Rectangle(
        (0.30, 0.35), 11.40, 2.30,
        facecolor='none', edgecolor='#94a3b8', linewidth=0.7, linestyle=':', zorder=1
    )
    ax.add_patch(seq_border)

    ax.text(0.50, 2.45, "Exploitation Protocol & Active Directory State Progression:",
            fontsize=8.0, weight='bold', color=TEXT_MAIN)

    phases = [
        {
            'x': 0.50, 'w': 3.45,
            'title': 'Phase I: Identity & Group Traversal',
            'proto': 'Protocol: LDAP (TCP 389 / 636)',
            'desc': (
                "• Adversary enumerates token groups for compromised foothold jsmith.\n"
                "• Transitive group nesting resolves membership in CertEnrollers.\n"
                "• Unprivileged security context allows read traversal of ADCS schema."
            )
        },
        {
            'x': 4.25, 'w': 3.50,
            'title': 'Phase II: Template Abuse & OID Linkage',
            'proto': 'Protocol: MS-WCCE / RPC (TCP 135 / Ephemeral)',
            'desc': (
                "• Actor requests certificate via ESC13-Template.\n"
                "• CA signs X.509 certificate embedding msPKI-Certificate-Policy.\n"
                "• Policy OID directly maps to Domain Admins via msDS-OIDToGroupLink."
            )
        },
        {
            'x': 8.05, 'w': 3.45,
            'title': 'Phase III: Kerberos PKINIT & PAC Elevation',
            'proto': 'Protocol: Kerberos MS-KILE (TCP/UDP 88)',
            'desc': (
                "• Attacker authenticates to KDC using forged certificate via PKINIT.\n"
                "• KDC expands Issuance Policy OID into Tier-0 SID (S-1-5-21...-512).\n"
                "• SID injected directly into PAC authorization data; full forest takeover."
            )
        }
    ]

    for p in phases:
        px, pw = p['x'], p['w']
        py = 1.30
        ph = 1.45

        pbox = patches.Rectangle(
            (px, py - ph/2), pw, ph,
            facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.8, zorder=2
        )
        ax.add_patch(pbox)

        phdr = patches.Rectangle(
            (px, py + ph/2 - 0.32), pw, 0.32,
            facecolor='#e2e8f0', edgecolor='#cbd5e1', linewidth=0.8, zorder=3
        )
        ax.add_patch(phdr)

        ax.text(px + pw/2, py + ph/2 - 0.16, p['title'], ha='center', va='center',
                fontsize=7.4, weight='bold', color=TEXT_MAIN, zorder=4)
        ax.text(px + 0.12, py + ph/2 - 0.48, p['proto'], ha='left', va='center',
                fontsize=6.6, weight='bold', color='#334155', zorder=4)
        ax.text(px + 0.12, py - 0.18, p['desc'], ha='left', va='center',
                fontsize=6.4, color=TEXT_MAIN, zorder=4, linespacing=1.3)

    plt.tight_layout()
    plt.savefig(f'{OUTPUT_DIR}/esc13_attack_path_diagram.png', bbox_inches='tight', dpi=300)
    plt.close()
    print("Generated publication-grade esc13_attack_path_diagram.png")


# =============================================================================
# 3. CERTGRAPH HETERO-GAT ARCHITECTURE DIAGRAM (Figure 3.1)
# =============================================================================
def generate_certgraph_arch():
    fig, ax = plt.subplots(figsize=(13.6, 6.8), dpi=300)
    ax.set_xlim(0, 13.6)
    ax.set_ylim(0, 6.8)
    ax.axis('off')

    BOX_BG = '#ffffff'
    BORDER_COLOR = '#1e293b'
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    ACCENT_RED = '#991b1b'

    col_h = 5.6
    col_y = 3.5

    # Section 1: Input Heterogeneous Graph
    s1_w = 2.8
    s1_xc = 1.7
    box1 = patches.Rectangle(
        (s1_xc - s1_w/2, col_y - col_h/2), s1_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box1)

    hdr1 = patches.Rectangle(
        (s1_xc - s1_w/2, col_y + col_h/2 - 0.48), s1_w, 0.48,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr1)
    ax.text(s1_xc, col_y + col_h/2 - 0.24, "1. Input Heterogeneous Graph", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(s1_xc, col_y + 2.05, r"$\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{T}_V, \mathcal{T}_E)$",
            ha='center', va='center', fontsize=10.5, weight='bold', color=TEXT_MAIN)

    # Network schematic
    g_nodes = [
        (s1_xc - 0.7, col_y + 1.25, 'U', 'o', '#e2e8f0'),
        (s1_xc + 0.7, col_y + 1.35, 'G', '^', '#e2e8f0'),
        (s1_xc - 0.6, col_y + 0.35, 'C', 's', '#e2e8f0'),
        (s1_xc + 0.1, col_y + 0.70, 'T', 'D', '#fee2e2'),
        (s1_xc + 0.8, col_y + 0.25, 'CA', 'h', '#e2e8f0'),
    ]
    ax.plot([s1_xc - 0.7, s1_xc + 0.7], [col_y + 1.25, col_y + 1.35], color='#64748b', lw=1.2, zorder=3)
    ax.plot([s1_xc - 0.7, s1_xc + 0.1], [col_y + 1.25, col_y + 0.70], color='#64748b', lw=1.2, zorder=3)
    ax.plot([s1_xc + 0.7, s1_xc + 0.1], [col_y + 1.35, col_y + 0.70], color='#64748b', lw=1.2, zorder=3)
    ax.plot([s1_xc - 0.6, s1_xc + 0.1], [col_y + 0.35, col_y + 0.70], color='#64748b', lw=1.2, zorder=3)
    ax.plot([s1_xc + 0.1, s1_xc + 0.8], [col_y + 0.70, col_y + 0.25], color='#64748b', lw=1.2, zorder=3)

    for gx, gy, glbl, gshape, gcol in g_nodes:
        ax.plot(gx, gy, marker=gshape, markersize=16, color=gcol,
                markeredgecolor=BORDER_COLOR, markeredgewidth=1.2, zorder=4)
        ax.text(gx, gy, glbl, ha='center', va='center', fontsize=8.5, weight='bold', color=TEXT_MAIN, zorder=5)

    ax.text(s1_xc, col_y - 0.45, "5 Entity Node Types:\nUser, Comp, Group, Tmpl, CA",
            ha='center', va='center', fontsize=9.2, color=TEXT_MUTED, linespacing=1.25)

    proj_box = patches.Rectangle(
        (s1_xc - 1.2, col_y - 2.35), 2.4, 1.25,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.9, zorder=3
    )
    ax.add_patch(proj_box)
    ax.text(s1_xc, col_y - 1.35, "Linear Projections:", ha='center', va='center',
            fontsize=9.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s1_xc, col_y - 1.75, r"$\mathbf{z}_u = W_{\mathrm{src}}^{(r)} \mathbf{h}_u^{(l-1)}$",
            ha='center', va='center', fontsize=9.2, color=TEXT_MAIN, zorder=4)
    ax.text(s1_xc, col_y - 2.08, r"$\mathbf{z}_v = W_{\mathrm{dst}}^{(r)} \mathbf{h}_v^{(l-1)}$",
            ha='center', va='center', fontsize=9.2, color=TEXT_MAIN, zorder=4)

    arrow1 = patches.FancyArrowPatch(
        (s1_xc + s1_w/2, col_y), (3.65, col_y),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=BORDER_COLOR, linewidth=1.3, zorder=5
    )
    ax.add_patch(arrow1)

    # Section 2: Hetero-GAT Layer 1
    s2_w = 3.0
    s2_xc = 5.2
    box2 = patches.Rectangle(
        (s2_xc - s2_w/2, col_y - col_h/2), s2_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box2)

    hdr2 = patches.Rectangle(
        (s2_xc - s2_w/2, col_y + col_h/2 - 0.48), s2_w, 0.48,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr2)
    ax.text(s2_xc, col_y + col_h/2 - 0.24, "2. Hetero-GAT Layer 1", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)

    # MHA block
    mha_box = patches.Rectangle(
        (s2_xc - 1.35, col_y + 0.15), 2.7, 2.05,
        facecolor='#f8fafc', edgecolor='#94a3b8', linewidth=0.9, zorder=3
    )
    ax.add_patch(mha_box)
    ax.text(s2_xc, col_y + 1.85, "Relational Multi-Head Attention", ha='center', va='center',
            fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y + 1.45, r"Heads $K=4$, $\; d_{\mathrm{head}} = 16$",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, zorder=4)
    ax.text(s2_xc, col_y + 0.95,
            r"$e_{vu}^{(k,r)} = \operatorname{LeakyReLU}\left(\mathbf{a}_k^T [\mathbf{z}_v \| \mathbf{z}_u]\right)$",
            ha='center', va='center', fontsize=9.0, color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y + 0.45,
            r"$\alpha_{vu}^{(k,r)} = \operatorname{Softmax}_{\mathcal{N}_r(v)}\left(e_{vu}^{(k,r)}\right)$",
            ha='center', va='center', fontsize=9.0, color=TEXT_MAIN, zorder=4)

    # Aggregation block
    agg_box = patches.Rectangle(
        (s2_xc - 1.35, col_y - 1.25), 2.7, 1.25,
        facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=0.9, zorder=3
    )
    ax.add_patch(agg_box)
    ax.text(s2_xc, col_y - 0.40, r"$\mathbf{\mu}_{v,r}^{(1)} = \bigoplus_{k=1}^K \sum_{u} \alpha_{vu}^{(k,r)} \mathbf{z}_u^{(k,r)}$",
            ha='center', va='center', fontsize=9.2, color=TEXT_MAIN, zorder=4)
    ax.text(s2_xc, col_y - 0.85, "ELU Activation + LayerNorm",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, zorder=4)

    # Residual skip connection
    skip_arrow = patches.FancyArrowPatch(
        (s2_xc - 1.25, col_y - 1.50), (s2_xc + 1.25, col_y - 1.50),
        connectionstyle="arc3,rad=-0.25",
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color='#334155', linewidth=1.3, linestyle='--', zorder=5
    )
    ax.add_patch(skip_arrow)
    ax.text(s2_xc, col_y - 1.95, r"$\mathbf{h}_v^{(1)} \leftarrow \mathbf{h}_v^{(1)} + W_{\mathrm{skip}} \mathbf{h}_v^{(0)}$",
            ha='center', va='center', fontsize=9.0, weight='bold', color='#1e293b',
            bbox=dict(boxstyle="square,pad=0.25", fc='#ffffff', ec='#334155', lw=0.8, zorder=6))
    ax.text(s2_xc, col_y - 2.45, "Theorem 1: Avoids Source Collapse",
            ha='center', va='center', fontsize=8.5, style='italic', color=TEXT_MUTED, zorder=6)

    arrow2 = patches.FancyArrowPatch(
        (s2_xc + s2_w/2, col_y), (7.35, col_y),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=BORDER_COLOR, linewidth=1.3, zorder=5
    )
    ax.add_patch(arrow2)

    # Section 3: Hetero-GAT Layer 2 & Readout
    s3_w = 3.0
    s3_xc = 8.9
    box3 = patches.Rectangle(
        (s3_xc - s3_w/2, col_y - col_h/2), s3_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box3)

    hdr3 = patches.Rectangle(
        (s3_xc - s3_w/2, col_y + col_h/2 - 0.48), s3_w, 0.48,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr3)
    ax.text(s3_xc, col_y + col_h/2 - 0.24, "3. Layer 2 & Target Readout", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)

    # Layer 2 Conv block
    l2_box = patches.Rectangle(
        (s3_xc - 1.35, col_y + 0.15), 2.7, 2.05,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.9, zorder=3
    )
    ax.add_patch(l2_box)
    ax.text(s3_xc, col_y + 1.85, "2-Hop Topological Convolution", ha='center', va='center',
            fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y + 1.30, "Aggregates multi-hop DACL chains\nand policy linkage contexts",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, linespacing=1.25, zorder=4)
    ax.text(s3_xc, col_y + 0.55, r"Additive Skip: $\mathbf{h}_v^{(2)} \leftarrow \mathbf{h}_v^{(2)} + W_{\mathrm{skip}}^{(2)} \mathbf{h}_v^{(1)}$",
            ha='center', va='center', fontsize=8.6, color='#1e293b', zorder=4)

    # Readout box
    read_box = patches.Rectangle(
        (s3_xc - 1.35, col_y - 2.45), 2.7, 2.35,
        facecolor='#ffffff', edgecolor='#94a3b8', linewidth=0.9, zorder=3
    )
    ax.add_patch(read_box)
    ax.text(s3_xc, col_y - 0.45, "Template Node Readout", ha='center', va='center',
            fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y - 0.95, r"Target Entity: $v \in \mathcal{V}_{\mathrm{Tmpl}}$",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, zorder=4)
    ax.text(s3_xc, col_y - 1.45, r"Embedding: $\mathbf{h}_t \in \mathbb{R}^{64}$",
            ha='center', va='center', fontsize=9.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s3_xc, col_y - 2.00, "Isolated Vulnerability Latent State",
            ha='center', va='center', fontsize=8.5, style='italic', color=TEXT_MUTED, zorder=4)

    arrow3 = patches.FancyArrowPatch(
        (s3_xc + s3_w/2, col_y), (11.05, col_y),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=BORDER_COLOR, linewidth=1.3, zorder=5
    )
    ax.add_patch(arrow3)

    # Section 4: Classification Head & Probability Output
    s4_w = 2.4
    s4_xc = 12.3
    box4 = patches.Rectangle(
        (s4_xc - s4_w/2, col_y - col_h/2), s4_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box4)

    hdr4 = patches.Rectangle(
        (s4_xc - s4_w/2, col_y + col_h/2 - 0.48), s4_w, 0.48,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr4)
    ax.text(s4_xc, col_y + col_h/2 - 0.24, "4. Classification Head", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(s4_xc, col_y + 1.95, "MLP Projection Head:", ha='center', va='center',
            fontsize=9.2, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(s4_xc, col_y + 1.55, r"$\mathrm{Linear}(64 \to 32) \to \mathrm{ReLU}$",
            ha='center', va='center', fontsize=8.5, color=TEXT_MUTED, zorder=4)
    ax.text(s4_xc, col_y + 1.20, r"$\mathrm{Dropout}(0.2) \to \mathrm{Linear}(32 \to 7)$",
            ha='center', va='center', fontsize=8.5, color=TEXT_MUTED, zorder=4)
    ax.text(s4_xc, col_y + 0.82, r"$\hat{\mathbf{y}} = \operatorname{Softmax}(\mathbf{z}_{\mathrm{cls}}) \in \Delta^6$",
            ha='center', va='center', fontsize=8.8, weight='bold', color=TEXT_MAIN, zorder=4)

    # Classes list
    esc_labels = [
        ("Safe", "#059669", "Benign"),
        ("ESC1", ACCENT_RED, "Enrollee Supplies SAN"),
        ("ESC2", ACCENT_RED, "Any Purpose EKU"),
        ("ESC3", ACCENT_RED, "Cert Request Agent"),
        ("ESC4", ACCENT_RED, "DACL / WriteOwner"),
        ("ESC9", ACCENT_RED, "No Security Extension"),
        ("ESC13", ACCENT_RED, "Policy OID Group Link"),
    ]

    list_y_start = col_y + 0.35
    row_h = 0.38
    for idx, (lbl, col, desc) in enumerate(esc_labels):
        ry = list_y_start - (idx * row_h)
        badge = patches.Rectangle(
            (s4_xc - 1.05, ry - 0.15), 0.68, 0.30,
            facecolor='#fef2f2' if col == ACCENT_RED else '#f0fdf4',
            edgecolor=col, linewidth=0.9, zorder=3
        )
        ax.add_patch(badge)
        ax.text(s4_xc - 0.71, ry, lbl, ha='center', va='center',
                fontsize=8.5, weight='bold', color=col, zorder=4)
        ax.text(s4_xc - 0.25, ry, desc, ha='left', va='center',
                fontsize=7.8, color=TEXT_MAIN, zorder=4)

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
    fig, ax = plt.subplots(figsize=(14.0, 7.2), dpi=300)
    ax.set_xlim(0, 14.0)
    ax.set_ylim(0, 7.2)
    ax.axis('off')

    BOX_BG = '#ffffff'
    BORDER_COLOR = '#1e293b'
    TEXT_MAIN = '#0f172a'
    TEXT_MUTED = '#334155'
    WARN_RED = '#991b1b'
    SUCC_GREEN = '#047857'

    col_h = 5.8
    col_y = 3.9

    # 1. AD Graph Ingestion (Column 1)
    b1_w = 2.85
    b1_xc = 1.7
    box1 = patches.Rectangle(
        (b1_xc - b1_w/2, col_y - col_h/2), b1_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box1)

    hdr1 = patches.Rectangle(
        (b1_xc - b1_w/2, col_y + col_h/2 - 0.50), b1_w, 0.50,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr1)
    ax.text(b1_xc, col_y + col_h/2 - 0.25, "1. AD Graph Ingestion", ha='center', va='center',
            fontsize=11.0, weight='bold', color=TEXT_MAIN, zorder=4)

    # Ingestion details
    ax.text(b1_xc, col_y + 1.95, "Telemetry Extraction:", ha='center', va='center',
            fontsize=10.0, weight='bold', color=TEXT_MAIN)
    ax.text(b1_xc, col_y + 1.35,
            "• Live LDAP & RPC Audits\n• BloodHound / SharpHound\n• Active Directory PKI Schema",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, linespacing=1.3)

    # HeteroData details
    ax.text(b1_xc, col_y + 0.35, "HeteroData Mapping:", ha='center', va='center',
            fontsize=10.0, weight='bold', color=TEXT_MAIN)
    ax.text(b1_xc, col_y - 0.30,
            r"$\mathcal{G} = (\mathcal{V}, \mathcal{E}, \mathcal{T}_V, \mathcal{T}_E)$" "\n"
            r"$|\mathcal{V}| > 10^5, \; |\mathcal{E}| > 10^6$" "\nTransitive DACLs & Groups",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, linespacing=1.3)

    ingest_box = patches.Rectangle(
        (b1_xc - 1.25, col_y - 2.50), 2.50, 1.30,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.9, zorder=3
    )
    ax.add_patch(ingest_box)
    ax.text(b1_xc, col_y - 1.55, "Continuous Auditor:", ha='center', va='center',
            fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(b1_xc, col_y - 2.05, "Dynamic Delta Sync\nLDAP USN Tracking",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, linespacing=1.25, zorder=4)

    arrow1 = patches.FancyArrowPatch(
        (b1_xc + b1_w/2, col_y + 0.40), (3.80, col_y + 0.40),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=BORDER_COLOR, linewidth=1.3, zorder=5
    )
    ax.add_patch(arrow1)
    ax.text(3.45, col_y + 0.70, "AD Graph", ha='center', va='center', fontsize=9.0, weight='bold', color=TEXT_MAIN)

    # 2. Tier 1: Inductive Screening (Column 2)
    b2_w = 3.10
    b2_xc = 5.40
    box2 = patches.Rectangle(
        (b2_xc - b2_w/2, col_y - col_h/2), b2_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box2)

    hdr2 = patches.Rectangle(
        (b2_xc - b2_w/2, col_y + col_h/2 - 0.50), b2_w, 0.50,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr2)
    ax.text(b2_xc, col_y + col_h/2 - 0.25, "2. Tier 1: Inductive Screening", ha='center', va='center',
            fontsize=11.0, weight='bold', color=TEXT_MAIN, zorder=4)

    # GNN Inference
    ax.text(b2_xc, col_y + 1.95, "CertGraph Hetero-GAT:", ha='center', va='center',
            fontsize=10.0, weight='bold', color=TEXT_MAIN)
    ax.text(b2_xc, col_y + 1.30,
            r"• Forward: $\hat{\mathbf{y}}_t = \mathrm{CertGraph}(G, t) \in \Delta^6$" "\n"
            r"• Risk: $S_{\mathrm{risk}}(t) = 1.0 - \hat{y}_t[\mathrm{Safe}]$" "\n"
            r"• Latency: $<25$ ms per 1,000 nodes",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, linespacing=1.3)

    # Candidate Filter
    ax.text(b2_xc, col_y + 0.35, "Candidate Filter:", ha='center', va='center',
            fontsize=10.0, weight='bold', color=TEXT_MAIN)
    ax.text(b2_xc, col_y - 0.30,
            r"• Prunes $>95\%$ benign templates" "\n"
            r"• Emits Top-$K$ suspect queue: $\mathcal{Q}_{\mathrm{suspect}}$" "\n"
            r"• Prevents state explosion in verifier",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, linespacing=1.3)

    speed_box = patches.Rectangle(
        (b2_xc - 1.35, col_y - 2.50), 2.70, 1.30,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.9, zorder=3
    )
    ax.add_patch(speed_box)
    ax.text(b2_xc, col_y - 1.55, "Throughput Performance:", ha='center', va='center',
            fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(b2_xc, col_y - 2.05, "Full Directory Sweep in <2.4s\nO(V + E) GPU Inference",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, linespacing=1.25, zorder=4)

    arrow2 = patches.FancyArrowPatch(
        (b2_xc + b2_w/2, col_y + 0.40), (7.50, col_y + 0.40),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=BORDER_COLOR, linewidth=1.3, zorder=5
    )
    ax.add_patch(arrow2)
    ax.text(7.22, col_y + 0.70, "Top-K", ha='center', va='center', fontsize=9.0, weight='bold', color=TEXT_MAIN)
    ax.text(7.22, col_y + 0.15, "Suspects", ha='center', va='center', fontsize=8.5, color=TEXT_MUTED)

    # 3. Tier 2: Symbolic Verification (Column 3)
    b3_w = 3.10
    b3_xc = 9.10
    box3 = patches.Rectangle(
        (b3_xc - b3_w/2, col_y - col_h/2), b3_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box3)

    hdr3 = patches.Rectangle(
        (b3_xc - b3_w/2, col_y + col_h/2 - 0.50), b3_w, 0.50,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr3)
    ax.text(b3_xc, col_y + col_h/2 - 0.25, "3. Tier 2: Symbolic Verification", ha='center', va='center',
            fontsize=11.0, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(b3_xc, col_y + 1.95, "Deterministic Sound Traversal:", ha='center', va='center',
            fontsize=10.0, weight='bold', color=TEXT_MAIN)
    ax.text(b3_xc, col_y + 1.30,
            r"• 2-hop authorization subgraph query" "\n"
            r"• Horn: $\mathrm{Exploit}(t) = \mathrm{Verify}(G, V_{\mathrm{low}}, t)$" "\n"
            r"• Validates DACLs, OIDs & enroll rights",
            ha='center', va='center', fontsize=9.0, color=TEXT_MUTED, linespacing=1.3)

    ax.text(b3_xc, col_y + 0.35, "Soundness Oracle Decision:", ha='center', va='center',
            fontsize=10.0, weight='bold', color=TEXT_MAIN)

    # Branch 1: Hard Negative
    p_false_box = patches.Rectangle(
        (b3_xc - 1.35, col_y - 0.60), 2.70, 0.70,
        facecolor='#f0fdf4', edgecolor=SUCC_GREEN, linewidth=1.0, zorder=3
    )
    ax.add_patch(p_false_box)
    ax.text(b3_xc, col_y - 0.38, r"$\mathbf{Hard \; Negative \; (Safe)}$" "\nFalse Alarm Suppressed / Logged",
            ha='center', va='center', fontsize=8.5, weight='bold', color=SUCC_GREEN, linespacing=1.2)

    # Branch 2: Valid Exploit Path
    p_true_box = patches.Rectangle(
        (b3_xc - 1.35, col_y - 2.50), 2.70, 1.30,
        facecolor='#fef2f2', edgecolor=WARN_RED, linewidth=1.0, zorder=3
    )
    ax.add_patch(p_true_box)
    ax.text(b3_xc, col_y - 1.55, r"$\mathbf{Valid \; Exploit \; Path}$",
            ha='center', va='center', fontsize=9.5, weight='bold', color=WARN_RED, zorder=4)
    ax.text(b3_xc, col_y - 2.05, "Sound Mathematical Proof Tree\nTriggers Automated Remediation",
            ha='center', va='center', fontsize=8.8, color=WARN_RED, linespacing=1.25, zorder=4)

    arrow3 = patches.FancyArrowPatch(
        (b3_xc + b3_w/2, col_y - 1.85), (11.35, col_y - 1.85),
        arrowstyle="-|>,head_length=7,head_width=4.5",
        color=WARN_RED, linewidth=1.4, zorder=5
    )
    ax.add_patch(arrow3)
    ax.text(11.0, col_y - 1.45, "Verified\nProof", ha='center', va='center',
            fontsize=8.8, weight='bold', color=WARN_RED, linespacing=1.1)

    # 4. Tier 3: Autonomous Remediation (Column 4)
    b4_w = 2.55
    b4_xc = 12.60
    box4 = patches.Rectangle(
        (b4_xc - b4_w/2, col_y - col_h/2), b4_w, col_h,
        facecolor=BOX_BG, edgecolor=BORDER_COLOR, linewidth=1.1, zorder=2
    )
    ax.add_patch(box4)

    hdr4 = patches.Rectangle(
        (b4_xc - b4_w/2, col_y + col_h/2 - 0.50), b4_w, 0.50,
        facecolor='#f1f5f9', edgecolor=BORDER_COLOR, linewidth=1.1, zorder=3
    )
    ax.add_patch(hdr4)
    ax.text(b4_xc, col_y + col_h/2 - 0.25, "4. Autonomous Remediation", ha='center', va='center',
            fontsize=10.5, weight='bold', color=TEXT_MAIN, zorder=4)

    ax.text(b4_xc, col_y + 1.95, "Policy Optimization:", ha='center', va='center',
            fontsize=9.8, weight='bold', color=TEXT_MAIN)
    ax.text(b4_xc, col_y + 1.30,
            r"• Stackelberg Game / ADESDP" "\n"
            r"• Minimal cut: $\min \operatorname{Impact}(E_{\mathrm{cut}})$" "\n"
            r"• s.t. $\mathrm{NoPath}(G \setminus E_{\mathrm{cut}})$",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, linespacing=1.3)

    ax.text(b4_xc, col_y + 0.35, "Targeted LDAP Actuation:", ha='center', va='center',
            fontsize=9.8, weight='bold', color=TEXT_MAIN)
    ax.text(b4_xc, col_y - 0.30,
            "• Revokes rogue enrollment ACEs\n• Unlinks vulnerable policy OIDs\n• Zero operational disruption",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, linespacing=1.3)

    rem_box = patches.Rectangle(
        (b4_xc - 1.15, col_y - 2.50), 2.30, 1.30,
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=0.9, zorder=3
    )
    ax.add_patch(rem_box)
    ax.text(b4_xc, col_y - 1.55, "Remediation Outcome:", ha='center', va='center',
            fontsize=9.5, weight='bold', color=TEXT_MAIN, zorder=4)
    ax.text(b4_xc, col_y - 2.05, "Edge Cut: $E_{\mathrm{cut}} \subseteq \mathcal{E}$\nOptimal ACL Revocation",
            ha='center', va='center', fontsize=8.8, color=TEXT_MUTED, linespacing=1.25, zorder=4)

    # Closed-Loop Feedback Bus: Routes from bottom of Col 4 back to bottom of Col 1
    fb_y = 0.55
    fb_points = [
        (b4_xc, col_y - col_h/2),
        (b4_xc, fb_y),
        (b1_xc, fb_y),
        (b1_xc, col_y - col_h/2)
    ]
    ax.plot([p[0] for p in fb_points], [p[1] for p in fb_points],
            color='#1e293b', linestyle='--', linewidth=1.5, zorder=4)

    ax.scatter([b1_xc], [col_y - col_h/2], marker='^', s=70, color='#1e293b', zorder=5)

    fb_badge = patches.Rectangle(
        (7.0 - 2.8, fb_y - 0.22), 5.6, 0.44,
        facecolor='#ffffff', edgecolor='#1e293b', linewidth=1.0, zorder=5
    )
    ax.add_patch(fb_badge)
    ax.text(7.0, fb_y, "Closed-Loop Feedback: State Ingestion Delta Sync Post-Remediation",
            ha='center', va='center', fontsize=9.2, weight='bold', color='#1e293b', zorder=6)

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
