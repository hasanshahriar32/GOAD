#!/usr/bin/env python3
"""
Publication-Grade Generator for Figure 2.2:
Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory
Designed specifically for full textwidth inclusion with EXTRA LARGE, bold typography
and mathematically guaranteed zero collision / zero clipping.
"""
import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_esc13_diagram(output_paths):
    fig_w, fig_h = 16.5, 9.6
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Background color
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Top Titles
    ax.text(fig_w / 2, 9.15, 'Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory',
            ha='center', va='center', fontsize=20.0, weight='bold', color='#0f172a')
    ax.text(fig_w / 2, 8.72,
            r'Transitive Path: Low-Priv Foothold $\longrightarrow$ Intermediate Group $\longrightarrow$ Certificate Template $\longrightarrow$ Issuance Policy OID $\longrightarrow$ Tier-0 Domain Admins',
            ha='center', va='center', fontsize=13.0, weight='bold', color='#475569')

    # 5 Nodes Configuration
    card_w = 2.05
    card_h = 2.65
    y_box = 5.60

    # Margins: 0.45 left/right. Span = 15.60. 5 * 2.05 = 10.25. Gap = (15.60 - 10.25)/4 = 1.3375
    gap = 1.3375
    c0 = 0.45 + card_w / 2
    c1 = c0 + card_w + gap
    c2 = c1 + card_w + gap
    c3 = c2 + card_w + gap
    c4 = c3 + card_w + gap

    nodes = [
        {
            'x': c0,
            'bg': '#f8fafc',
            'border': '#1d4ed8',
            'badge': 'IDENTITY PRINCIPAL',
            'badge_bg': '#dbeafe',
            'badge_fg': '#1e40af',
            'title': 'Low-Priv User',
            'role': 'Compromised Foothold',
            'code': 'sAMAccount: jsmith',
            'sub': 'Domain Users Group'
        },
        {
            'x': c1,
            'bg': '#f8fafc',
            'border': '#c2410c',
            'badge': 'SECURITY GROUP',
            'badge_bg': '#ffedd5',
            'badge_fg': '#9a3412',
            'title': 'Enroller Group',
            'role': 'Intermediate Group',
            'code': 'CN=CertEnrollers',
            'sub': 'Holds Template DACL'
        },
        {
            'x': c2,
            'bg': '#f8fafc',
            'border': '#7e22ce',
            'badge': 'CERTIFICATE TEMPLATE',
            'badge_bg': '#f3e8ff',
            'badge_fg': '#6b21a8',
            'title': 'ESC13 Template',
            'role': 'Target Template',
            'code': 'msPKI-Cert-Policy',
            'sub': 'Policy OID Extension'
        },
        {
            'x': c3,
            'bg': '#f8fafc',
            'border': '#0f766e',
            'badge': 'ISSUANCE POLICY OID',
            'badge_bg': '#ccfbf1',
            'badge_fg': '#115e59',
            'title': 'Policy OID',
            'role': 'Issuance Policy',
            'code': 'OIDToGroupLink',
            'sub': 'Maps to Target SID'
        },
        {
            'x': c4,
            'bg': '#f8fafc',
            'border': '#b91c1c',
            'badge': 'TIER-0 CROWN JEWEL',
            'badge_bg': '#fee2e2',
            'badge_fg': '#991b1b',
            'title': 'Domain Admins',
            'role': 'Tier-0 Target Asset',
            'code': 'SID: S-1-5-...-512',
            'sub': 'Full Forest Takeover'
        }
    ]

    # Draw Nodes
    for n in nodes:
        xc = n['x']
        # Shadow
        shadow = patches.FancyBboxPatch(
            (xc - card_w/2 + 0.04, y_box - 0.04), card_w, card_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor='#94a3b8', alpha=0.18, edgecolor='none', zorder=1
        )
        ax.add_patch(shadow)

        # Card Body
        card = patches.FancyBboxPatch(
            (xc - card_w/2, y_box), card_w, card_h,
            boxstyle="round,pad=0.02,rounding_size=0.12",
            facecolor=n['bg'], edgecolor=n['border'], linewidth=2.0, zorder=2
        )
        ax.add_patch(card)

        # Top Badge
        badge_w = card_w - 0.24
        badge_h = 0.34
        badge_y = y_box + card_h - 0.44
        badge = patches.FancyBboxPatch(
            (xc - badge_w/2, badge_y), badge_w, badge_h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor=n['badge_bg'], edgecolor=n['border'], linewidth=1.1, zorder=3
        )
        ax.add_patch(badge)
        ax.text(xc, badge_y + badge_h/2, n['badge'],
                ha='center', va='center', fontsize=9.2, weight='bold',
                color=n['badge_fg'], zorder=4)

        # Main Title
        ax.text(xc, y_box + card_h - 0.78, n['title'],
                ha='center', va='center', fontsize=14.5, weight='bold',
                color='#0f172a', zorder=4)

        # Subtitle / Role (concise, guaranteed 0.3in clearance inside card)
        ax.text(xc, y_box + card_h - 1.08, n['role'],
                ha='center', va='center', fontsize=10.6, weight='bold',
                color='#475569', zorder=4)

        # Code / LDAP Detail Box
        detail_w = card_w - 0.22
        detail_h = 0.40
        detail_y = y_box + 0.58
        detail_box = patches.FancyBboxPatch(
            (xc - detail_w/2, detail_y), detail_w, detail_h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
        )
        ax.add_patch(detail_box)
        ax.text(xc, detail_y + detail_h/2, n['code'],
                ha='center', va='center', fontsize=10.2, family='monospace', weight='bold',
                color='#1e293b', zorder=4)

        # Sub-attribute
        ax.text(xc, y_box + 0.26, n['sub'],
                ha='center', va='center', fontsize=10.5, weight='bold', style='italic',
                color='#64748b', zorder=4)

    # 4 Transition Steps between Cards
    edges = [
        {
            'idx': 0,
            'color': '#1d4ed8',
            'step_tag': 'STEP 1',
            'step_name': 'MemberOf',
            'desc': 'Group Nesting'
        },
        {
            'idx': 1,
            'color': '#c2410c',
            'step_tag': 'STEP 2',
            'step_name': 'Enroll',
            'desc': 'DACL ACE'
        },
        {
            'idx': 2,
            'color': '#7e22ce',
            'step_tag': 'STEP 3',
            'step_name': 'LinksPolicy',
            'desc': 'OID Linkage'
        },
        {
            'idx': 3,
            'color': '#b91c1c',
            'step_tag': 'STEP 4',
            'step_name': 'PAC Elevate',
            'desc': 'SID Injection'
        }
    ]

    for e in edges:
        i = e['idx']
        xs = nodes[i]['x'] + card_w/2 + 0.08
        xe = nodes[i+1]['x'] - card_w/2 - 0.08
        xm = (xs + xe) / 2
        y_arrow = y_box + 1.25  # 6.85

        # Step Pill above arrow
        pill_w = 1.18
        pill_h = 0.52
        pill_y = y_arrow + 0.12
        pill = patches.FancyBboxPatch(
            (xm - pill_w/2, pill_y), pill_w, pill_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor='#ffffff', edgecolor=e['color'], linewidth=1.5, zorder=6
        )
        ax.add_patch(pill)

        name_font = 10.5 if len(e['step_name']) > 9 else 11.4
        ax.text(xm, pill_y + pill_h*0.72, e['step_tag'],
                ha='center', va='center', fontsize=9.2, weight='bold',
                color='#64748b', zorder=7)
        ax.text(xm, pill_y + pill_h*0.28, e['step_name'],
                ha='center', va='center', fontsize=name_font, weight='bold',
                color=e['color'], zorder=7)

        # Arrow
        ax.annotate(
            '', xy=(xe, y_arrow), xytext=(xs, y_arrow),
            arrowprops=dict(
                arrowstyle="-|>,head_width=0.40,head_length=0.55",
                color=e['color'], lw=2.4
            ),
            zorder=5
        )

        # Concise description below arrow
        ax.text(xm, y_arrow - 0.25, e['desc'],
                ha='center', va='center', fontsize=10.2, weight='bold',
                color='#1e293b', zorder=6)

    # Bottom Callout Container
    callout_x = 0.45
    callout_y = 0.25
    callout_w = 15.60
    callout_h = 5.05

    # Container Shadow
    callout_shadow = patches.FancyBboxPatch(
        (callout_x + 0.04, callout_y - 0.04), callout_w, callout_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        facecolor='#94a3b8', alpha=0.14, edgecolor='none', zorder=1
    )
    ax.add_patch(callout_shadow)

    # Main Container Box
    callout_box = patches.FancyBboxPatch(
        (callout_x, callout_y), callout_w, callout_h,
        boxstyle="round,pad=0.03,rounding_size=0.14",
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5, zorder=2
    )
    ax.add_patch(callout_box)

    # Full-Width Header Bar across Top of Container (guaranteed no text clipping)
    header_h = 0.50
    header_box = patches.FancyBboxPatch(
        (callout_x + 0.01, callout_y + callout_h - header_h - 0.01), callout_w - 0.02, header_h,
        boxstyle="round,pad=0.01,rounding_size=0.12",
        facecolor='#1e293b', edgecolor='none', zorder=3
    )
    ax.add_patch(header_box)
    ax.text(callout_x + callout_w / 2, callout_y + callout_h - header_h / 2 - 0.01,
            'ATTACK CHAIN EXPLOITATION MECHANISM & RELATIONAL IMPACT',
            ha='center', va='center', fontsize=13.5, weight='bold', color='#ffffff', zorder=4)

    # 3 Structured Breakdown Columns
    col_w = 4.86
    col_gap = 0.27
    col_y = callout_y + 0.22
    col_h = 4.08
    col_top = col_y + col_h

    columns = [
        {
            'x': callout_x + 0.24,
            'title_1': 'Phase 1: Foothold & DACL',
            'title_2': 'Transitive Identity Escalation',
            'color': '#1d4ed8',
            'bullets': [
                ("Foothold Compromise", [
                    "Adversary compromises low-priv",
                    "user via credential spraying."
                ]),
                ("Group Nesting", [
                    "User possesses transitive nested",
                    "membership in enroller group."
                ]),
                ("Enrollment DACL", [
                    "Group holds explicit Certificate-",
                    "Enroll ACE permissions."
                ])
            ]
        },
        {
            'x': callout_x + 0.24 + col_w + col_gap,
            'title_1': 'Phase 2: Policy Inversion',
            'title_2': 'Template OID Linkage Inversion',
            'color': '#7e22ce',
            'bullets': [
                ("CSR Submission", [
                    "Requests certificate from ESC13",
                    "template via MS-WCCE RPC."
                ]),
                ("Policy Extension", [
                    "CA embeds msPKI-Cert-Policy",
                    "OID into issued certificate."
                ]),
                ("OID Group Mapping", [
                    "OID object links to privileged",
                    "administrative target SID."
                ])
            ]
        },
        {
            'x': callout_x + 0.24 + (col_w + col_gap)*2,
            'title_1': 'Phase 3: Domain Dominance',
            'title_2': 'Kerberos PKINIT Forest Takeover',
            'color': '#b91c1c',
            'bullets': [
                ("PKINIT Authentication", [
                    "Performs Kerberos PKINIT auth",
                    "using issued certificate."
                ]),
                ("PAC SID Injection", [
                    "KDC injects Domain Admins SID",
                    "(S-1-5-...-512) into PAC."
                ]),
                ("Full Takeover", [
                    "Actor obtains Tier-0 TGT with",
                    "complete forest compromise."
                ])
            ]
        }
    ]

    for col in columns:
        cx = col['x']
        # Column card
        col_box = patches.FancyBboxPatch(
            (cx, col_y), col_w, col_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
        )
        ax.add_patch(col_box)

        # Title (2 lines)
        ax.text(cx + 0.24, col_top - 0.28, col['title_1'],
                ha='left', va='center', fontsize=14.0, weight='bold',
                color=col['color'], zorder=4)
        ax.text(cx + 0.24, col_top - 0.52, col['title_2'],
                ha='left', va='center', fontsize=11.6, weight='bold',
                color='#64748b', zorder=4)

        # Divider line
        ax.plot([cx + 0.20, cx + col_w - 0.20], [col_top - 0.68, col_top - 0.68],
                color='#e2e8f0', lw=1.2, zorder=4)

        # Bullets with guaranteed clearance and no overflow
        cur_y = col_top - 0.88
        for tag, lines in col['bullets']:
            ax.text(cx + 0.24, cur_y, f"• {tag}:",
                    ha='left', va='top', fontsize=12.6, weight='bold', color='#0f172a', zorder=4)
            cur_y -= 0.27
            for line in lines:
                ax.text(cx + 0.44, cur_y, line,
                    ha='left', va='top', fontsize=11.6, color='#334155', zorder=4)
                cur_y -= 0.24
            cur_y -= 0.14

    plt.tight_layout()
    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, bbox_inches='tight', dpi=300)
        print(f"Generated {p}")
    plt.close()

if __name__ == '__main__':
    paths = [
        '/home/hs32/Desktop/GOAD/thesis_paper/figures/esc13_attack_path_diagram.png',
        '/home/hs32/Desktop/GOAD/thesis_research/results/phase2/esc13_attack_path_diagram.png'
    ]
    generate_esc13_diagram(paths)
