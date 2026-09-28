"""
High-Resolution, Publication-Grade Generator for:
Figure 2.2: Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_esc13_diagram(output_path):
    # Set overall canvas size and resolution: 16.5 x 6.8 inches at 300 DPI
    fig, ax = plt.subplots(figsize=(16.5, 6.8), dpi=300)
    ax.set_xlim(0, 16.5)
    ax.set_ylim(0, 6.8)
    ax.axis('off')

    # Card dimensions
    w = 2.05
    h = 2.10
    y_center = 4.25
    y_box = y_center - h / 2  # 3.20

    # 5 Node definitions with curated colors
    nodes = [
        {
            'x': 1.65,
            'bg': '#f8fafc',
            'border': '#1d4ed8',
            'badge': 'IDENTITY PRINCIPAL',
            'badge_bg': '#dbeafe',
            'badge_fg': '#1e40af',
            'title': 'Low-Priv User',
            'role': '(Compromised Foothold)',
            'code': 'sAMAccountName: jsmith',
            'sub': 'Domain Users Group'
        },
        {
            'x': 4.80,
            'bg': '#f8fafc',
            'border': '#c2410c',
            'badge': 'SECURITY GROUP',
            'badge_bg': '#ffedd5',
            'badge_fg': '#9a3412',
            'title': 'Enroller Group',
            'role': '(Intermediate Group)',
            'code': 'CN=CertEnrollers',
            'sub': 'Granted Template DACL'
        },
        {
            'x': 7.95,
            'bg': '#f8fafc',
            'border': '#7e22ce',
            'badge': 'CERTIFICATE TEMPLATE',
            'badge_bg': '#f3e8ff',
            'badge_fg': '#6b21a8',
            'title': 'ESC13 Template',
            'role': '(ADCS Schema v2 Template)',
            'code': 'msPKI-Certificate-Policy',
            'sub': 'Policy OID Extension'
        },
        {
            'x': 11.10,
            'bg': '#f8fafc',
            'border': '#15803d',
            'badge': 'ISSUANCE POLICY OID',
            'badge_bg': '#dcfce7',
            'badge_fg': '#166534',
            'title': 'Policy OID Object',
            'role': '(Linked to Tier-0 Group)',
            'code': 'msPKI-Cert-Policy-OID',
            'sub': 'Maps to Group SID'
        },
        {
            'x': 14.25,
            'bg': '#f8fafc',
            'border': '#b91c1c',
            'badge': 'TIER-0 CROWN JEWEL',
            'badge_bg': '#fee2e2',
            'badge_fg': '#991b1b',
            'title': 'Domain Admins',
            'role': '(High-Value Target Asset)',
            'code': 'SID: S-1-5-21-...-512',
            'sub': 'Enterprise Dominance'
        }
    ]

    # Draw Nodes with Drop Shadow and Structured Internal Layout
    for n in nodes:
        xc = n['x']
        # 1. Subtle drop shadow
        shadow = patches.FancyBboxPatch(
            (xc - w/2 + 0.06, y_box - 0.05), w, h,
            boxstyle="round,pad=0.03,rounding_size=0.16",
            facecolor='#94a3b8', alpha=0.18, edgecolor='none', zorder=1
        )
        ax.add_patch(shadow)

        # 2. Main Card Body
        card = patches.FancyBboxPatch(
            (xc - w/2, y_box), w, h,
            boxstyle="round,pad=0.03,rounding_size=0.16",
            facecolor=n['bg'], edgecolor=n['border'], linewidth=1.8, zorder=2
        )
        ax.add_patch(card)

        # 3. Top Category Badge Header
        badge_w = w - 0.28
        badge_h = 0.32
        badge_y = y_box + h - 0.42
        badge = patches.FancyBboxPatch(
            (xc - badge_w/2, badge_y), badge_w, badge_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=n['badge_bg'], edgecolor=n['border'], linewidth=0.9, zorder=3
        )
        ax.add_patch(badge)
        ax.text(xc, badge_y + badge_h/2, n['badge'],
                ha='center', va='center', fontsize=7.2, weight='bold',
                color=n['badge_fg'], zorder=4)

        # 4. Main Title
        ax.text(xc, y_box + h - 0.74, n['title'],
                ha='center', va='center', fontsize=10.2, weight='bold',
                color='#0f172a', zorder=4)

        # 5. Role / Description
        ax.text(xc, y_box + h - 1.02, n['role'],
                ha='center', va='center', fontsize=7.8, style='normal',
                color='#475569', zorder=4)

        # 6. Technical / LDAP detail badge at bottom of card
        detail_w = w - 0.24
        detail_h = 0.34
        detail_y = y_box + 0.46
        detail_box = patches.FancyBboxPatch(
            (xc - detail_w/2, detail_y), detail_w, detail_h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=0.8, zorder=3
        )
        ax.add_patch(detail_box)
        ax.text(xc, detail_y + detail_h/2, n['code'],
                ha='center', va='center', fontsize=7.0, family='monospace', weight='bold',
                color='#1e293b', zorder=4)

        # 7. Sub-attribute label
        ax.text(xc, y_box + 0.24, n['sub'],
                ha='center', va='center', fontsize=6.9, style='italic',
                color='#64748b', zorder=4)

    # 4 Transition Edges with Arrows & Step Badges
    # Generous gap: 3.15 - 2.05 = 1.10 units
    edges = [
        {
            'x_start': nodes[0]['x'] + w/2 + 0.08,
            'x_end': nodes[1]['x'] - w/2 - 0.08,
            'color': '#1d4ed8',
            'step_num': 'STEP 1',
            'step_name': 'MemberOf',
            'desc_1': 'Group Nesting',
            'desc_2': '(Inherited Access)'
        },
        {
            'x_start': nodes[1]['x'] + w/2 + 0.08,
            'x_end': nodes[2]['x'] - w/2 - 0.08,
            'color': '#c2410c',
            'step_num': 'STEP 2',
            'step_name': 'Enroll Rights',
            'desc_1': 'Enrollment ACE',
            'desc_2': '(DACL Permission)'
        },
        {
            'x_start': nodes[2]['x'] + w/2 + 0.08,
            'x_end': nodes[3]['x'] - w/2 - 0.08,
            'color': '#7e22ce',
            'step_num': 'STEP 3',
            'step_name': 'LinksPolicy',
            'desc_1': 'Policy Link',
            'desc_2': '(OID Reference)'
        },
        {
            'x_start': nodes[3]['x'] + w/2 + 0.08,
            'x_end': nodes[4]['x'] - w/2 - 0.08,
            'color': '#b91c1c',
            'step_num': 'STEP 4',
            'step_name': 'PAC Elevation',
            'desc_1': 'SID Injection',
            'desc_2': '(Kerberos S4U2Self)'
        }
    ]

    for e in edges:
        xs = e['x_start']
        xe = e['x_end']
        xm = (xs + xe) / 2
        y_arrow = y_center

        # Arrow stroke with polished styling
        ax.annotate(
            '', xy=(xe, y_arrow), xytext=(xs, y_arrow),
            arrowprops=dict(
                arrowstyle="-|>,head_width=0.40,head_length=0.65",
                color=e['color'], lw=2.4
            ),
            zorder=5
        )

        # Step Pill above arrow
        pill_w = 0.82
        pill_h = 0.44
        pill_y = y_arrow + 0.26
        pill = patches.FancyBboxPatch(
            (xm - pill_w/2, pill_y), pill_w, pill_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor='#ffffff', edgecolor=e['color'], linewidth=1.3, zorder=6
        )
        ax.add_patch(pill)
        ax.text(xm, pill_y + pill_h*0.72, e['step_num'],
                ha='center', va='center', fontsize=6.2, weight='bold',
                color='#64748b', zorder=7)
        ax.text(xm, pill_y + pill_h*0.28, e['step_name'],
                ha='center', va='center', fontsize=7.2, weight='bold',
                color=e['color'], zorder=7)

        # Mechanism label below arrow
        ax.text(xm, y_arrow - 0.26, e['desc_1'],
                ha='center', va='center', fontsize=6.8, weight='bold',
                color='#334155', zorder=6)
        ax.text(xm, y_arrow - 0.44, e['desc_2'],
                ha='center', va='center', fontsize=6.4, style='italic',
                color='#64748b', zorder=6)

    # Professional Title & Context Header
    ax.text(8.25, 6.45, 'Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory',
            ha='center', va='center', fontsize=13.5, weight='bold', color='#0f172a')
    ax.text(8.25, 6.08, 'Transitive Privilege Traversal: Foothold Identity $\\longrightarrow$ Intermediate Enroller $\\longrightarrow$ Certificate Template $\\longrightarrow$ Issuance Policy $\\longrightarrow$ Tier-0 Domain Dominance',
            ha='center', va='center', fontsize=8.6, color='#475569')

    # Explanatory Bottom Callout: 3-column structured architecture container
    callout_w = 15.5
    callout_h = 2.10
    callout_x = (16.5 - callout_w) / 2
    callout_y = 0.35

    # Callout drop shadow
    callout_shadow = patches.FancyBboxPatch(
        (callout_x + 0.06, callout_y - 0.05), callout_w, callout_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        facecolor='#94a3b8', alpha=0.14, edgecolor='none', zorder=1
    )
    ax.add_patch(callout_shadow)

    # Callout main box
    callout_box = patches.FancyBboxPatch(
        (callout_x, callout_y), callout_w, callout_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.4, zorder=2
    )
    ax.add_patch(callout_box)

    # Callout Header Badge
    tag_box = patches.FancyBboxPatch(
        (callout_x + 0.35, callout_y + callout_h - 0.36), 3.4, 0.28,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor='#1e293b', edgecolor='none', zorder=3
    )
    ax.add_patch(tag_box)
    ax.text(callout_x + 0.35 + 1.7, callout_y + callout_h - 0.22,
            'ATTACK CHAIN EXPLOITATION MECHANISM & IMPACT', ha='center', va='center',
            fontsize=7.2, weight='bold', color='#ffffff', zorder=4)

    # 3-Column Structured Breakdown
    col_w = 4.70
    col_gap = 0.35
    col_y_top = callout_y + callout_h - 0.55
    col_h = 1.35

    columns_data = [
        {
            'x': callout_x + 0.35,
            'title': 'Phase 1: Transitive Access Path',
            'color': '#1d4ed8',
            'lines': [
                '• Foothold Credential: Adversary compromises a low-priv user (e.g., via Phishing or Kerberoasting).',
                '• Group Nesting: User belongs to an intermediate security group (e.g., Contractors or IT-Staff).',
                '• Template DACL: Intermediate group holds explicit Enrollment ACE permissions over the template.'
            ]
        },
        {
            'x': callout_x + 0.35 + col_w + col_gap,
            'title': 'Phase 2: Relational Policy Linkage',
            'color': '#7e22ce',
            'lines': [
                '• CSR Submission: Actor requests certificate from the ESC13 ADCS template.',
                '• Policy OID Embedded: ADCS signs CSR and embeds msPKI-Certificate-Policy into certificate.',
                '• Directory Mapping: Policy OID links directly to an administrative security group object.'
            ]
        },
        {
            'x': callout_x + 0.35 + (col_w + col_gap)*2,
            'title': 'Phase 3: Tier-0 Domain Dominance',
            'color': '#b91c1c',
            'lines': [
                '• KDC Authentication: Actor authenticates using Kerberos PKINIT or S4U2Self extension.',
                '• PAC Group Injection: KDC resolves policy OID to Tier-0 group SID (S-1-5-21-...-512).',
                '• Immediate Elevation: Unprivileged actor receives full Domain Admin token across the forest.'
            ]
        }
    ]

    for col in columns_data:
        cx = col['x']
        # Column container card
        col_box = patches.FancyBboxPatch(
            (cx, callout_y + 0.18), col_w, col_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor='#ffffff', edgecolor='#e2e8f0', linewidth=1.0, zorder=3
        )
        ax.add_patch(col_box)

        # Column Title
        ax.text(cx + 0.20, col_y_top - 0.12, col['title'],
                ha='left', va='center', fontsize=8.0, weight='bold',
                color=col['color'], zorder=4)

        # Divider line
        ax.plot([cx + 0.20, cx + col_w - 0.20], [col_y_top - 0.26, col_y_top - 0.26],
                color='#e2e8f0', lw=0.8, zorder=4)

        # Lines of text
        ly = col_y_top - 0.44
        for line in col['lines']:
            # Word-wrapped inside column width
            ax.text(cx + 0.20, ly, line,
                    ha='left', va='top', fontsize=6.8, color='#334155', linespacing=1.2,
                    wrap=True, zorder=4)
            ly -= 0.32

    plt.tight_layout()
    plt.savefig(output_path, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"Successfully generated {output_path}")

if __name__ == '__main__':
    generate_esc13_diagram('/home/hs32/Desktop/GOAD/thesis_paper/figures/esc13_attack_path_diagram.png')
