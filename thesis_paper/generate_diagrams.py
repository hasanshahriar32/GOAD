"""
Generate publication-quality diagrams for the thesis:
1. adcs_attack_graph_schema.png
2. esc13_attack_path_diagram.png
3. certgraph_architecture_diagram.png
4. neuro_symbolic_pipeline.png
"""
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

plt.rcParams['font.family'] = 'DejaVu Sans'
plt.rcParams['font.size'] = 11

OUTPUT_DIR = '/home/hs32/Desktop/GOAD/thesis_paper/figures'

# ─────────────────────────────────────────────────────────────
# 1. ADCS ATTACK GRAPH SCHEMA
# ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(10, 6), dpi=300)
ax.set_xlim(0, 10)
ax.set_ylim(0, 6)
ax.axis('off')

# Node types and coordinates
nodes = {
    'User': (1.8, 4.5, '#2b5c8f', 'User Node\n(Privileged & Low-Priv)'),
    'Computer': (1.8, 1.5, '#3a7d44', 'Computer Node\n(Workstations & DCs)'),
    'Group': (5.0, 4.8, '#d95f02', 'Group Node\n(Security Groups & Tier 0)'),
    'Template': (5.0, 1.8, '#7570b3', 'Certificate Template\n(ADCS Schema v1-v4)'),
    'EnterpriseCA': (8.2, 3.2, '#e7298a', 'Enterprise CA\n(Root/Subordinate CA)')
}

# Draw nodes
for name, (x, y, color, label) in nodes.items():
    box = patches.FancyBboxPatch((x-1.0, y-0.5), 2.0, 1.0,
                                 boxstyle="round,pad=0.1,rounding_size=0.2",
                                 facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.9)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', color='white', weight='bold', fontsize=9.5)

# Edges with labels
edges = [
    ((2.8, 4.6), (4.0, 4.8), 'MemberOf', '#333333', 0.2),
    ((2.8, 4.2), (4.0, 2.2), 'Enroll / WriteDacl', '#b2182b', -0.15),
    ((2.8, 1.6), (4.0, 1.7), 'Enroll / GenericAll', '#b2182b', 0.1),
    ((5.0, 4.3), (5.0, 2.3), 'Owns / WriteOwner', '#d95f02', 0.0),
    ((6.0, 1.9), (7.2, 2.9), 'PublishedTo', '#2166ac', -0.15),
    ((6.0, 4.7), (7.3, 3.5), 'ManageCA / CertManager', '#b2182b', 0.15),
    ((4.0, 2.0), (2.8, 4.0), 'LinksPolicy (ESC13)', '#762a83', 0.25),
]

for (x1, y1), (x2, y2), label, color, offset_y in edges:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                                color=color, lw=2.0, shrinkA=5, shrinkB=5))
    mid_x, mid_y = (x1 + x2) / 2, (y1 + y2) / 2 + offset_y
    ax.text(mid_x, mid_y, label, ha='center', va='center',
            fontsize=8.5, weight='bold', color=color,
            bbox=dict(boxstyle="round,pad=0.2", facecolor='white', edgecolor='none', alpha=0.85))

plt.title('Heterogeneous Active Directory Certificate Services (ADCS) Graph Schema',
          fontsize=13, weight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/adcs_attack_graph_schema.png', bbox_inches='tight')
plt.close()

# ─────────────────────────────────────────────────────────────
# 2. ESC13 ATTACK PATH DIAGRAM
# ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 4.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 4.5)
ax.axis('off')

steps = [
    (1.2, 2.2, '#2b5c8f', 'Low-Priv User\n(Compromised Actor)'),
    (3.5, 2.2, '#d95f02', 'Enroller Group\n(Contractors / Domain Users)'),
    (6.0, 2.2, '#7570b3', 'ESC13 Template\n(msPKI-Certificate-Policy)'),
    (8.5, 2.2, '#1b7837', 'Issuance Policy OID\n(OID Linked to Tier-0 Group)'),
    (10.2, 2.2, '#d73027', 'Domain Admin\n(High-Value Asset)')
]

for x, y, color, label in steps:
    box = patches.FancyBboxPatch((x-0.9, y-0.6), 1.8, 1.2,
                                 boxstyle="round,pad=0.1,rounding_size=0.2",
                                 facecolor=color, edgecolor='black', linewidth=1.5, alpha=0.9)
    ax.add_patch(box)
    ax.text(x, y, label, ha='center', va='center', color='white', weight='bold', fontsize=8.5)

step_edges = [
    ((2.1, 2.2), (2.6, 2.2), 'Step 1:\nMemberOf', '#333333'),
    ((4.4, 2.2), (5.1, 2.2), 'Step 2:\nEnroll Rights', '#b2182b'),
    ((6.9, 2.2), (7.6, 2.2), 'Step 3:\nLinksPolicy', '#762a83'),
    ((9.4, 2.2), (9.7, 2.2), 'Step 4:\nElevation', '#d73027')
]

for (x1, y1), (x2, y2), label, color in step_edges:
    ax.annotate('', xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6",
                                color=color, lw=2.2))
    ax.text((x1 + x2)/2, y1 + 0.9, label, ha='center', va='center',
            fontsize=8.5, weight='bold', color=color)

# Explanatory subtitle
ax.text(5.5, 0.4,
        'Path Exploitation Mechanism: Enrollment in Template with issuance policy link maps certificate OID to Tier-0 group SID,\n'
        'granting immediate Domain Admin token creation via Kerberos S4U2Self extension.',
        ha='center', va='center', fontsize=9, style='italic',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#f7f7f7', edgecolor='#cccccc'))

plt.title('Two-Hop ESC13 Privilege Escalation Attack Chain in Active Directory',
          fontsize=12.5, weight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/esc13_attack_path_diagram.png', bbox_inches='tight')
plt.close()

# ─────────────────────────────────────────────────────────────
# 3. CERTGRAPH ARCHITECTURE DIAGRAM
# ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(12, 6.5), dpi=300)
ax.set_xlim(0, 12)
ax.set_ylim(0, 6.5)
ax.axis('off')

# Architectural blocks
blocks = [
    (1.5, 3.5, 2.2, 5.0, '#f0f0f0', 'Input HeteroData Graph\n' + '-'*25 + '\nNodes: Users, Computers,\nGroups, Templates, CAs\nNode Features: $X_v \\in \\mathbb{R}^{d_v}$\nEdges: Relational Adjacency $\\mathcal{E}_r$'),
    (4.5, 3.5, 2.2, 5.0, '#e0f3f8', 'Layer 1: Hetero-GAT Conv\n' + '-'*25 + '\nMulti-Head Attention (K=4)\nRelational Aggregation:\n$h_v^{(1)} = \\sigma(\\sum_{r} \\sum_u \\alpha_{vu}^r W_r h_u^{(0)})$\n+ Residual Skip: $h_v^{(1)} + W_{skip} h_v^{(0)}$\nLayerNorm + Dropout(0.2)'),
    (7.5, 3.5, 2.2, 5.0, '#e0f3f8', 'Layer 2: Hetero-GAT Conv\n' + '-'*25 + '\nMulti-Head Attention (K=4)\n2-Hop Path Context Integration\nTarget Template Focus\n+ Residual Skip Connection\nNon-linear Activation (ELU)'),
    (10.5, 3.5, 2.0, 5.0, '#fee0d2', 'Classification Head\n' + '-'*25 + '\nExtract $h_{template} \\in \\mathbb{R}^{64}$\nLinear(64 $\\to$ 32) + ReLU\nLinear(32 $\\to$ 7 classes)\nSoftmax Distribution:\nESC1, 2, 3, 4, 9, 13, Safe')
]

for x, y, w, h, color, text in blocks:
    box = patches.FancyBboxPatch((x-w/2, y-h/2), w, h,
                                 boxstyle="round,pad=0.1,rounding_size=0.2",
                                 facecolor=color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.5, family='monospace', weight='bold')

# Connect blocks with arrows
arrow_pairs = [((2.6, 3.5), (3.4, 3.5)), ((5.6, 3.5), (6.4, 3.5)), ((8.6, 3.5), (9.5, 3.5))]
for p1, p2 in arrow_pairs:
    ax.annotate('', xy=p2, xytext=p1,
                arrowprops=dict(arrowstyle="->,head_width=0.5,head_length=0.7",
                                color='#2b5c8f', lw=3.0))

# Sub-annotation highlighting skip connection necessity
ax.text(6.0, 0.4,
        'CRITICAL ARCHITECTURAL GUARANTEE: Residual skip connections prevent representation collapse ($h_v^{(l+1)} \\to 0$)\n'
        'for directed source-only nodes (Users, Computers) with zero in-degree during relational message passing.',
        ha='center', va='center', fontsize=9, weight='bold', color='#b2182b',
        bbox=dict(boxstyle="round,pad=0.3", facecolor='#fee8c8', edgecolor='#b2182b', lw=1.2))

plt.title('CertGraph Heterogeneous Graph Attention Network (Hetero-GAT) Pipeline',
          fontsize=13, weight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/certgraph_architecture_diagram.png', bbox_inches='tight')
plt.close()

# ─────────────────────────────────────────────────────────────
# 4. NEURO-SYMBOLIC HYBRID PIPELINE
# ─────────────────────────────────────────────────────────────
fig, ax = plt.subplots(figsize=(11, 5.5), dpi=300)
ax.set_xlim(0, 11)
ax.set_ylim(0, 5.5)
ax.axis('off')

# Stages
stages = [
    (1.5, 3.8, 2.2, 1.8, '#d9d9d9', 'Enterprise Active Directory\nRaw BloodHound / SharpHound\nDomain JSON Export\n(Users, Groups, Templates)'),
    (4.5, 3.8, 2.4, 2.2, '#ccebc5', 'TIER 1: Neural Screening\n(CertGraph Hetero-GAT)\n' + '-'*20 + '\nFast contextual scoring\nInference: <25ms per 1k nodes\nPrioritizes high-risk templates'),
    (8.2, 3.8, 2.6, 2.2, '#fed9a6', 'TIER 2: Symbolic Verification\n(BloodHound BFS / Cypher)\n' + '-'*20 + '\nExact path traversal check\nVerifies DACL / Enrollment chain\nImmune to shortcut learning (84% HN)'),
    (5.5, 1.0, 4.5, 1.4, '#fbb4ae', 'Automated Remediation / Mitigation Action\n' + '-'*35 + '\nTargeted edge-severing: Revoke enrollment ACL,\nUnlink malicious issuance policy, Tier-0 isolation')
]

for x, y, w, h, color, text in stages:
    box = patches.FancyBboxPatch((x-w/2, y-h/2), w, h,
                                 boxstyle="round,pad=0.1,rounding_size=0.2",
                                 facecolor=color, edgecolor='black', linewidth=1.5)
    ax.add_patch(box)
    ax.text(x, y, text, ha='center', va='center', fontsize=8.5, family='monospace', weight='bold')

# Arrows
ax.annotate('', xy=(3.3, 3.8), xytext=(2.6, 3.8),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='black', lw=2))
ax.annotate('', xy=(6.9, 3.8), xytext=(5.7, 3.8),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='black', lw=2))
ax.text(6.3, 4.3, 'Top-K Suspect\nTemplates', ha='center', va='center', fontsize=8, weight='bold', color='#2b5c8f')

# Downward arrow to mitigation
ax.annotate('', xy=(5.5, 1.7), xytext=(8.2, 2.7),
            arrowprops=dict(arrowstyle="->,head_width=0.4,head_length=0.6", color='#b2182b', lw=2.5,
                            connectionstyle="arc3,rad=-0.2"))
ax.text(7.6, 2.0, 'Confirmed\nExploitable Path', ha='center', va='center', fontsize=8, weight='bold', color='#b2182b')

plt.title('Two-Tier Neuro-Symbolic Architecture for Autonomous Active Directory Defense',
          fontsize=12.5, weight='bold', pad=15)
plt.tight_layout()
plt.savefig(f'{OUTPUT_DIR}/neuro_symbolic_pipeline.png', bbox_inches='tight')
plt.close()

print("All 4 publication diagrams successfully generated in", OUTPUT_DIR)
