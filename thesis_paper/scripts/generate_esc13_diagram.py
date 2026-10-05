#!/usr/bin/env python3
"""
Publication-Grade Generator for Figure 2.2:
Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory
Designed specifically for full textwidth inclusion with EXTRA LARGE, bold typography.
"""
import os
import textwrap
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_esc13_diagram(output_paths):
    fig_w, fig_h = 13.8, 8.8
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Background color
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Top Titles
    ax.text(6.9, 8.45, 'Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory',
            ha='center', va='center', fontsize=18.5, weight='bold', color='#0f172a')
    ax.text(6.9, 8.05,
            r'Transitive Path: Low-Priv Foothold $\longrightarrow$ Intermediate Group $\longrightarrow$ Certificate Template $\longrightarrow$ Issuance Policy OID $\longrightarrow$ Tier-0 Domain Admins',
            ha='center', va='center', fontsize=13.2, weight='bold', color='#475569')

    # 5 Nodes Configuration
    card_w = 1.92
    card_h = 2.65
    y_center = 6.25
    y_box = y_center - card_h / 2  # 4.925

    # Centers calculation:
    # 5 cards of 1.92 = 9.60 width.
    # Total span = 12.80.
    # 4 gaps = (12.80 - 9.60) / 4 = 0.80 each.
    # Margins: left = 0.50, right = 0.50.
    c0 = 0.50 + card_w / 2                        # 1.46
    c1 = c0 + card_w + 0.80                       # 4.18
    c2 = c1 + card_w + 0.80                       # 6.90 (exact center)
    c3 = c2 + card_w + 0.80                       # 9.62
    c4 = c3 + card_w + 0.80                       # 12.34

    nodes = [
        {
            'x': c0,
            'bg': '#f8fafc',
            'border': '#1d4ed8',
            'badge': 'IDENTITY PRINCIPAL',
            'badge_bg': '#dbeafe',
            'badge_fg': '#1e40af',
            'title': 'Low-Priv User',
            'role': '(Compromised Foothold)',
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
            'role': '(Intermediate Principal)',
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
            'role': '(ADCS Schema v2)',
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
            'title': 'Policy OID Object',
            'role': '(Linked to Tier-0 Group)',
            'code': 'msDS-OIDToGroupLink',
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
            'role': '(High-Value Target Asset)',
            'code': 'SID: S-1-5-...-512',
            'sub': 'Full Forest Takeover'
        }
    ]

    # Draw Nodes
    for n in nodes:
        xc = n['x']
        # Shadow
        shadow = patches.FancyBboxPatch(
            (xc - card_w/2 + 0.05, y_box - 0.04), card_w, card_h,
            boxstyle="round,pad=0.02,rounding_size=0.14",
            facecolor='#94a3b8', alpha=0.18, edgecolor='none', zorder=1
        )
        ax.add_patch(shadow)

        # Card Body
        card = patches.FancyBboxPatch(
            (xc - card_w/2, y_box), card_w, card_h,
            boxstyle="round,pad=0.02,rounding_size=0.14",
            facecolor=n['bg'], edgecolor=n['border'], linewidth=2.0, zorder=2
        )
        ax.add_patch(card)

        # Top Badge
        badge_w = card_w - 0.16
        badge_h = 0.42
        badge_y = y_box + card_h - 0.48
        badge = patches.FancyBboxPatch(
            (xc - badge_w/2, badge_y), badge_w, badge_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor=n['badge_bg'], edgecolor=n['border'], linewidth=1.1, zorder=3
        )
        ax.add_patch(badge)
        ax.text(xc, badge_y + badge_h/2, n['badge'],
                ha='center', va='center', fontsize=11.2, weight='bold',
                color=n['badge_fg'], zorder=4)

        # Main Title
        ax.text(xc, y_box + card_h - 0.90, n['title'],
                ha='center', va='center', fontsize=16.0, weight='bold',
                color='#0f172a', zorder=4)

        # Role / Description
        ax.text(xc, y_box + card_h - 1.25, n['role'],
                ha='center', va='center', fontsize=12.2, weight='bold',
                color='#475569', zorder=4)

        # Code / LDAP Detail Box
        detail_w = card_w - 0.16
        detail_h = 0.44
        detail_y = y_box + 0.52
        detail_box = patches.FancyBboxPatch(
            (xc - detail_w/2, detail_y), detail_w, detail_h,
            boxstyle="round,pad=0.02,rounding_size=0.06",
            facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
        )
        ax.add_patch(detail_box)
        code_font = 11.5 if len(n['code']) > 16 else 12.2
        ax.text(xc, detail_y + detail_h/2, n['code'],
                ha='center', va='center', fontsize=code_font, family='monospace', weight='bold',
                color='#1e293b', zorder=4)

        # Sub-attribute
        ax.text(xc, y_box + 0.24, n['sub'],
                ha='center', va='center', fontsize=11.5, weight='bold', style='italic',
                color='#64748b', zorder=4)

    # 4 Transition Edges
    edges = [
        {
            'idx': 0,
            'color': '#1d4ed8',
            'step_num': 'STEP 1',
            'step_name': 'MemberOf',
            'desc_1': 'Group Nesting',
            'desc_2': 'LDAP Token'
        },
        {
            'idx': 1,
            'color': '#c2410c',
            'step_num': 'STEP 2',
            'step_name': 'Enroll',
            'desc_1': 'DACL ACE',
            'desc_2': 'MS-WCCE RPC'
        },
        {
            'idx': 2,
            'color': '#7e22ce',
            'step_num': 'STEP 3',
            'step_name': 'LinksPolicy',
            'desc_1': 'OID Linkage',
            'desc_2': 'Template Flag'
        },
        {
            'idx': 3,
            'color': '#b91c1c',
            'step_num': 'STEP 4',
            'step_name': 'PAC Elevate',
            'desc_1': 'SID Injection',
            'desc_2': 'Kerberos PKINIT'
        }
    ]

    for e in edges:
        i = e['idx']
        xs = nodes[i]['x'] + card_w/2 + 0.05
        xe = nodes[i+1]['x'] - card_w/2 - 0.05
        xm = (xs + xe) / 2
        y_arrow = y_center

        # Arrow
        ax.annotate(
            '', xy=(xe, y_arrow), xytext=(xs, y_arrow),
            arrowprops=dict(
                arrowstyle="-|>,head_width=0.50,head_length=0.70",
                color=e['color'], lw=3.0
            ),
            zorder=5
        )

        # Step Pill above arrow
        pill_w = 0.88
        pill_h = 0.54
        pill_y = y_arrow + 0.16
        pill = patches.FancyBboxPatch(
            (xm - pill_w/2, pill_y), pill_w, pill_h,
            boxstyle="round,pad=0.02,rounding_size=0.08",
            facecolor='#ffffff', edgecolor=e['color'], linewidth=1.6, zorder=6
        )
        ax.add_patch(pill)
        ax.text(xm, pill_y + pill_h*0.72, e['step_num'],
                ha='center', va='center', fontsize=11.0, weight='bold',
                color='#64748b', zorder=7)
        ax.text(xm, pill_y + pill_h*0.28, e['step_name'],
                ha='center', va='center', fontsize=12.8, weight='bold',
                color=e['color'], zorder=7)

        # Concise description below arrow
        ax.text(xm, y_arrow - 0.28, e['desc_1'],
                ha='center', va='center', fontsize=12.2, weight='bold',
                color='#1e293b', zorder=6)
        ax.text(xm, y_arrow - 0.48, e['desc_2'],
                ha='center', va='center', fontsize=11.2, weight='bold', style='italic',
                color='#64748b', zorder=6)

    # Bottom Callout Container
    callout_x = 0.50
    callout_y = 0.25
    callout_w = 12.80
    callout_h = 4.10

    # Shadow
    callout_shadow = patches.FancyBboxPatch(
        (callout_x + 0.05, callout_y - 0.04), callout_w, callout_h,
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

    # Header Badge
    badge_title_w = 6.80
    tag_box = patches.FancyBboxPatch(
        (callout_x + 0.30, callout_y + callout_h - 0.46), badge_title_w, 0.40,
        boxstyle="round,pad=0.02,rounding_size=0.06",
        facecolor='#1e293b', edgecolor='none', zorder=3
    )
    ax.add_patch(tag_box)
    ax.text(callout_x + 0.30 + badge_title_w/2, callout_y + callout_h - 0.26,
            'ATTACK CHAIN EXPLOITATION MECHANISM & RELATIONAL IMPACT',
            ha='center', va='center', fontsize=12.8, weight='bold', color='#ffffff', zorder=4)

    # 3 Structured Breakdown Columns
    col_w = 3.90
    col_gap = 0.25
    col_y = callout_y + 0.18
    col_h = 3.35
    col_top = col_y + col_h

    columns = [
        {
            'x': callout_x + 0.25,
            'title': 'Phase 1: Transitive Foothold & DACL',
            'color': '#1d4ed8',
            'bullets': [
                ("Foothold Compromise", "Adversary gains execution as a low-privileged identity principal (e.g., via password spraying or Kerberoasting)."),
                ("Group Nesting", "Low-priv user is a transitive nested member of an intermediate security group (e.g., CN=CertEnrollers)."),
                ("Enrollment DACL", "Intermediate group holds explicit Certificate-Enroll ACE permissions over the vulnerable template.")
            ]
        },
        {
            'x': callout_x + 0.25 + col_w + col_gap,
            'title': 'Phase 2: Relational Policy Linkage',
            'color': '#7e22ce',
            'bullets': [
                ("CSR Submission", "Adversary requests an X.509 certificate from the ESC13 template via MS-WCCE RPC interface."),
                ("Policy Extension", "ADCS issues certificate embedding msPKI-Certificate-Policy OID in the Certificate Policies extension."),
                ("Directory Mapping", "Target OID object defines msDS-OIDToGroupLink referencing high-privileged administrative groups.")
            ]
        },
        {
            'x': callout_x + 0.25 + (col_w + col_gap)*2,
            'title': 'Phase 3: Tier-0 Domain Dominance',
            'color': '#b91c1c',
            'bullets': [
                ("PKINIT Auth", "Actor performs Kerberos PKINIT / S4U2Self authentication presenting the signed certificate."),
                ("PAC SID Injection", "KDC evaluates OID-to-group linkage and injects Domain Admins SID (S-1-5-...-512) into PAC."),
                ("Forest Takeover", "Actor obtains a Tier-0 Kerberos TGT with full forest administrative compromise.")
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

        # Title
        ax.text(cx + 0.16, col_top - 0.26, col['title'],
                ha='left', va='center', fontsize=14.0, weight='bold',
                color=col['color'], zorder=4)

        # Divider line
        ax.plot([cx + 0.16, cx + col_w - 0.16], [col_top - 0.46, col_top - 0.46],
                color='#e2e8f0', lw=1.2, zorder=4)

        # Bullets with guaranteed clearance and no overflow
        cur_y = col_top - 0.54
        for tag, text in col['bullets']:
            ax.text(cx + 0.16, cur_y, f"• {tag}:",
                    ha='left', va='top', fontsize=12.6, weight='bold', color='#0f172a', zorder=4)
            cur_y -= 0.25
            wrapped = textwrap.fill(text, width=39)
            ax.text(cx + 0.34, cur_y, wrapped,
                    ha='left', va='top', fontsize=12.0, color='#334155',
                    linespacing=1.22, zorder=4)
            n_lines = wrapped.count('\n') + 1
            cur_y -= (n_lines * 0.23 + 0.14)

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

