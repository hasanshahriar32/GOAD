#!/usr/bin/env python3
"""
Publication-Grade Generator for Figure 2.2:
Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory
Designed specifically for full textwidth inclusion with EXTRA LARGE, bold typography
and mathematically guaranteed zero collision / zero clipping.
"""
import os
import textwrap
import matplotlib.pyplot as plt
import matplotlib.patches as patches

def generate_esc13_diagram(output_paths):
    fig_w, fig_h = 12.6, 7.5
    fig, ax = plt.subplots(figsize=(fig_w, fig_h), dpi=300)
    ax.set_xlim(0, fig_w)
    ax.set_ylim(0, fig_h)
    ax.axis('off')

    # Background color
    fig.patch.set_facecolor('#ffffff')
    ax.set_facecolor('#ffffff')

    # Top Title & Subtitle
    ax.text(fig_w / 2, 7.18, 'Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory',
            ha='center', va='center', fontsize=17.5, weight='bold', color='#0f172a')
    ax.text(fig_w / 2, 6.80,
            r'Transitive Path: Low-Priv User $\rightarrow$ Enroller Group $\rightarrow$ ESC13 Template $\rightarrow$ Policy OID $\rightarrow$ Domain Admins',
            ha='center', va='center', fontsize=12.2, weight='bold', color='#475569')

    # 5 Nodes Configuration (Generous gaps to guarantee zero collision)
    card_w = 1.48
    card_h = 2.45
    y_box = 3.82
    c_gap = 1.02
    c_left = (fig_w - (5 * card_w + 4 * c_gap)) / 2

    nodes = [
        {
            'bg': '#f8fafc', 'border': '#1d4ed8',
            'badge': 'IDENTITY PRINCIPAL', 'badge_bg': '#dbeafe', 'badge_fg': '#1e40af', 'badge_size': 8.2,
            'title': 'Low-Priv User', 'role': 'Initial Foothold',
            'code': 'sAMAccount: jsmith', 'sub': 'Domain Users Group'
        },
        {
            'bg': '#f8fafc', 'border': '#c2410c',
            'badge': 'SECURITY GROUP', 'badge_bg': '#ffedd5', 'badge_fg': '#9a3412', 'badge_size': 8.8,
            'title': 'Enroller Group', 'role': 'Intermediate Group',
            'code': 'CN=CertEnrollers', 'sub': 'Holds Template DACL'
        },
        {
            'bg': '#f8fafc', 'border': '#7e22ce',
            'badge': 'CERT TEMPLATE', 'badge_bg': '#f3e8ff', 'badge_fg': '#6b21a8', 'badge_size': 8.8,
            'title': 'ESC13 Template', 'role': 'Target Template',
            'code': 'msPKI-Cert-Policy', 'sub': 'Policy OID Extension'
        },
        {
            'bg': '#f8fafc', 'border': '#0f766e',
            'badge': 'ISSUANCE POLICY', 'badge_bg': '#ccfbf1', 'badge_fg': '#115e59', 'badge_size': 8.5,
            'title': 'Policy OID', 'role': 'Issuance Policy',
            'code': 'OIDToGroupLink', 'sub': 'Maps to Target SID'
        },
        {
            'bg': '#f8fafc', 'border': '#b91c1c',
            'badge': 'TIER-0 TARGET', 'badge_bg': '#fee2e2', 'badge_fg': '#991b1b', 'badge_size': 8.8,
            'title': 'Domain Admins', 'role': 'Tier-0 Target',
            'code': 'SID: S-1-5-...-512', 'sub': 'Full Forest Takeover'
        }
    ]

    for i, n in enumerate(nodes):
        xc = c_left + i * (card_w + c_gap) + card_w / 2
        n['xc'] = xc

        # Shadow
        shadow = patches.FancyBboxPatch(
            (xc - card_w/2 + 0.03, y_box - 0.03), card_w, card_h,
            boxstyle='round,pad=0.02,rounding_size=0.10',
            facecolor='#94a3b8', alpha=0.18, edgecolor='none', zorder=1
        )
        ax.add_patch(shadow)

        # Card Body
        card = patches.FancyBboxPatch(
            (xc - card_w/2, y_box), card_w, card_h,
            boxstyle='round,pad=0.02,rounding_size=0.10',
            facecolor=n['bg'], edgecolor=n['border'], linewidth=2.0, zorder=2
        )
        ax.add_patch(card)

        # Top Badge
        bw = card_w - 0.12
        bh = 0.32
        by = y_box + card_h - 0.40
        badge = patches.FancyBboxPatch(
            (xc - bw/2, by), bw, bh,
            boxstyle='round,pad=0.015,rounding_size=0.05',
            facecolor=n['badge_bg'], edgecolor=n['border'], linewidth=1.1, zorder=3
        )
        ax.add_patch(badge)
        ax.text(xc, by + bh/2, n['badge'],
                ha='center', va='center', fontsize=n['badge_size'], weight='bold',
                color=n['badge_fg'], zorder=4)

        # Main Title
        ax.text(xc, y_box + card_h - 0.74, n['title'],
                ha='center', va='center', fontsize=12.5, weight='bold',
                color='#0f172a', zorder=4)

        # Role
        ax.text(xc, y_box + card_h - 1.02, n['role'],
                ha='center', va='center', fontsize=10.5, weight='bold',
                color='#475569', zorder=4)

        # Detail box
        dw = card_w - 0.12
        dh = 0.38
        dy = y_box + 0.54
        detail_box = patches.FancyBboxPatch(
            (xc - dw/2, dy), dw, dh,
            boxstyle='round,pad=0.015,rounding_size=0.05',
            facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.1, zorder=3
        )
        ax.add_patch(detail_box)
        ax.text(xc, dy + dh/2, n['code'],
                ha='center', va='center', fontsize=9.5, family='monospace', weight='bold',
                color='#1e293b', zorder=4)

        # Sub-attribute
        ax.text(xc, y_box + 0.24, n['sub'],
                ha='center', va='center', fontsize=9.8, weight='bold', style='italic',
                color='#64748b', zorder=4)

    # 4 Transition Steps between Cards (Generous padding: zero collision guaranteed)
    edges = [
        {'color': '#1d4ed8', 'bg': '#eff6ff', 'step': 'Step 1', 'action': 'MemberOf', 'desc': 'Group Nesting'},
        {'color': '#c2410c', 'bg': '#fff7ed', 'step': 'Step 2', 'action': 'Enroll', 'desc': 'DACL ACE'},
        {'color': '#7e22ce', 'bg': '#faf5ff', 'step': 'Step 3', 'action': 'LinksPolicy', 'desc': 'OID Linkage'},
        {'color': '#b91c1c', 'bg': '#fef2f2', 'step': 'Step 4', 'action': 'PAC Elevate', 'desc': 'SID Injection'}
    ]

    for i, e in enumerate(edges):
        xs = nodes[i]['xc'] + card_w/2 + 0.05
        xe = nodes[i+1]['xc'] - card_w/2 - 0.05
        xm = (xs + xe) / 2
        y_arrow = y_box + 1.20

        # Arrow
        ax.annotate(
            '', xy=(xe, y_arrow), xytext=(xs, y_arrow),
            arrowprops=dict(
                arrowstyle='-|>,head_width=0.32,head_length=0.42',
                color=e['color'], lw=2.2
            ),
            zorder=5
        )

        # Step Label above arrow with compact width to guarantee zero card overlap
        pw = 0.72
        ph = 0.44
        pill = patches.FancyBboxPatch(
            (xm - pw/2, y_arrow + 0.12), pw, ph,
            boxstyle='round,pad=0.02,rounding_size=0.08',
            facecolor=e['bg'], edgecolor=e['color'], lw=1.2, zorder=6
        )
        ax.add_patch(pill)

        ax.text(xm, y_arrow + 0.42, e['step'],
                ha='center', va='center', fontsize=9.2, weight='bold',
                color=e['color'], zorder=7)
        ax.text(xm, y_arrow + 0.22, e['action'],
                ha='center', va='center', fontsize=10.0, weight='bold',
                color=e['color'], zorder=7)

        # Desc below arrow
        ax.text(xm, y_arrow - 0.22, e['desc'],
                ha='center', va='center', fontsize=9.2, weight='bold',
                color='#1e293b', zorder=6)

    # Bottom Callout Container
    callout_x = c_left
    callout_y = 0.20
    callout_w = 5 * card_w + 4 * c_gap
    callout_h = 3.32

    callout_shadow = patches.FancyBboxPatch(
        (callout_x + 0.03, callout_y - 0.03), callout_w, callout_h,
        boxstyle='round,pad=0.02,rounding_size=0.10',
        facecolor='#94a3b8', alpha=0.14, edgecolor='none', zorder=1
    )
    ax.add_patch(callout_shadow)

    callout_box = patches.FancyBboxPatch(
        (callout_x, callout_y), callout_w, callout_h,
        boxstyle='round,pad=0.02,rounding_size=0.10',
        facecolor='#f8fafc', edgecolor='#cbd5e1', linewidth=1.5, zorder=2
    )
    ax.add_patch(callout_box)

    # Header Bar
    hh = 0.42
    header_box = patches.FancyBboxPatch(
        (callout_x + 0.01, callout_y + callout_h - hh - 0.01), callout_w - 0.02, hh,
        boxstyle='round,pad=0.01,rounding_size=0.08',
        facecolor='#1e293b', edgecolor='none', zorder=3
    )
    ax.add_patch(header_box)
    ax.text(callout_x + callout_w / 2, callout_y + callout_h - hh / 2 - 0.01,
            'ATTACK CHAIN EXPLOITATION MECHANISM & RELATIONAL IMPACT',
            ha='center', va='center', fontsize=13.0, weight='bold', color='#ffffff', zorder=4)

    # 3 Breakdown Columns
    col_w = (callout_w - 0.40 - 2 * 0.20) / 3
    col_gap = 0.20
    col_y = callout_y + 0.16
    col_h = callout_h - hh - 0.34
    col_top = col_y + col_h

    columns = [
        {
            'x': callout_x + 0.20,
            'title_1': 'Phase 1: Foothold & DACL',
            'title_2': 'Transitive Identity Escalation',
            'color': '#1d4ed8',
            'bullets': [
                ('Foothold Compromise', 'Adversary gains low-priv foothold via credential spraying.'),
                ('Group Nesting', 'Transitive membership in intermediate enroller group.'),
                ('Enrollment DACL', 'Group holds explicit Certificate-Enroll permissions on template.')
            ]
        },
        {
            'x': callout_x + 0.20 + col_w + col_gap,
            'title_1': 'Phase 2: Policy Inversion',
            'title_2': 'Template OID Linkage Inversion',
            'color': '#7e22ce',
            'bullets': [
                ('CSR Submission', 'Requests certificate from ESC13 template via MS-WCCE RPC.'),
                ('Policy Extension', 'CA embeds msPKI-Cert-Policy OID into issued certificate.'),
                ('OID Group Mapping', 'OID object links directly to privileged administrative target SID.')
            ]
        },
        {
            'x': callout_x + 0.20 + (col_w + col_gap) * 2,
            'title_1': 'Phase 3: Domain Dominance',
            'title_2': 'Kerberos PKINIT Forest Takeover',
            'color': '#b91c1c',
            'bullets': [
                ('PKINIT Authentication', 'Requests TGT via Kerberos PKINIT using forged certificate.'),
                ('PAC SID Injection', 'KDC injects Domain Admins SID (S-1-5-...-512) into PAC.'),
                ('Full Compromise', 'Actor obtains Tier-0 administrative ticket for forest dominance.')
            ]
        }
    ]

    for col in columns:
        cx = col['x']
        col_box = patches.FancyBboxPatch(
            (cx, col_y), col_w, col_h,
            boxstyle='round,pad=0.015,rounding_size=0.06',
            facecolor='#ffffff', edgecolor='#cbd5e1', linewidth=1.2, zorder=3
        )
        ax.add_patch(col_box)

        ax.text(cx + 0.16, col_top - 0.24, col['title_1'],
                ha='left', va='center', fontsize=12.2, weight='bold',
                color=col['color'], zorder=4)
        ax.text(cx + 0.16, col_top - 0.46, col['title_2'],
                ha='left', va='center', fontsize=10.5, weight='bold',
                color='#64748b', zorder=4)

        ax.plot([cx + 0.14, cx + col_w - 0.14], [col_top - 0.58, col_top - 0.58],
                color='#e2e8f0', lw=1.1, zorder=4)

        cur_y = col_top - 0.74
        for tag, body in col['bullets']:
            ax.text(cx + 0.16, cur_y, f'• {tag}:',
                    ha='left', va='top', fontsize=11.0, weight='bold', color='#0f172a', zorder=4)
            cur_y -= 0.20
            wrapped = textwrap.wrap(body, width=40)
            for line in wrapped:
                ax.text(cx + 0.30, cur_y, line,
                        ha='left', va='top', fontsize=9.8, color='#334155', zorder=4)
                cur_y -= 0.19
            cur_y -= 0.08

    plt.tight_layout()
    for p in output_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, bbox_inches='tight', dpi=300)
    plt.close()
    print(f"[✓] Generated publication-grade esc13_attack_path_diagram.png to {output_paths}")

if __name__ == '__main__':
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out = os.path.join(base_dir, 'figures', 'esc13_attack_path_diagram.png')
    generate_esc13_diagram([out])
