"""Generate three figures corrected against the formal schema and saved measurements.

No illustrative performance trajectories or unmeasured deployment claims are used.
Run from any directory with the project's Python environment.
"""
from pathlib import Path
import hashlib
import json
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'manuscript/figures'
DATA = ROOT / 'thesis_research/results/lineage_constraints/2026-11-10/interdiction_recheck_statistics/results.json'
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 8, 'pdf.fonttype': 42})
BLUE = '#183b56'


def box(ax, xy, width, height, text, size=8, color='#edf3f7'):
    ax.add_patch(FancyBboxPatch(xy, width, height, boxstyle='round,pad=0.015',
                               facecolor=color, edgecolor=BLUE, linewidth=.8))
    ax.text(xy[0]+width/2, xy[1]+height/2, text, ha='center', va='center', fontsize=size)


def save(fig, name):
    fig.savefig(OUT/(name+'.pdf'), bbox_inches='tight', pad_inches=.04)
    fig.savefig(OUT/(name+'.png'), dpi=220, bbox_inches='tight', pad_inches=.04)
    plt.close(fig)


def main():
    fig, ax = plt.subplots(figsize=(3.45, 2.2))
    ax.set(xlim=(0, 1), ylim=(0, 1)); ax.axis('off')
    ax.text(.5, .96, 'Identity graph: six node types', ha='center', weight='bold')
    for i, label in enumerate(['User', 'Group', 'Computer', 'Certificate\nTemplate', 'EnterpriseCA', 'Domain']):
        x=.015+(i % 3)*.33; y=.72-(i//3)*.2
        box(ax,(x,y),.30,.15,label,7)
    ax.text(.5,.44,'Ten relation types',ha='center',weight='bold')
    names=['MemberOf','GenericAll','GenericWrite','WriteOwner','WriteDacl',
           'Enroll','ExtendedRight','EnablesEnrollment','IssuedBy','TrustedForNTAuth']
    for i,name in enumerate(names):
        ax.text(.025+(i//5)*.50,.35-(i%5)*.075,name,fontsize=7.5)
    save(fig,'verified_identity_schema')

    fig,ax=plt.subplots(figsize=(7.05,2.45))
    ax.set(xlim=(0,1),ylim=(0,1));ax.axis('off')
    for y,text in [(.67,'Directory changes\n5136'),(.39,'CA issuance + exports\n4887; issuer/request bridge'),(.11,'KDC outcomes\n4768; issuer/serial/thumbprint')]:
        box(ax,(.025,y),.27,.20,text,7.5)
        ax.add_patch(FancyArrowPatch((.31,y+.10),(.35,.51),arrowstyle='-|>',mutation_scale=9,color=BLUE))
    box(ax,(.36,.32),.28,.38,'Issuer-scoped contract\n\nRetain compatible candidates\nCheck identifiers and order\nRevise on late conflicts',7.7)
    box(ax,(.72,.56),.25,.25,'Supported investigation\nPossible / definite / conflict\nAuthentication outcome',7.3)
    box(ax,(.72,.15),.25,.25,'Budgeted remediation\nBlockable permission edges\nAssigned disruption budget',7.3)
    for y in (.68,.28):
        ax.add_patch(FancyArrowPatch((.65,.51),(.70,y),arrowstyle='-|>',mutation_scale=9,color=BLUE))
    ax.text(.50,.965,'Evidence collection does not depend on a neural-positive prediction',ha='center',weight='bold',fontsize=8)
    ax.text(.50,.03,'Raw-source integrity and justified time bounds are explicit assumptions.',ha='center',fontsize=7)
    save(fig,'verified_evidence_pipeline')

    data=json.loads(DATA.read_text())['rows']
    fig,ax=plt.subplots(figsize=(3.45,2.55))
    for label,mean,sd,marker,color,offset in [
        ('Static greedy','greedy_mean_pct','greedy_population_sd_pct','o','#607d8b',-.14),
        ('Adaptive sequential','corrected_mean_pct','corrected_population_sd_pct','s',BLUE,.14)]:
        ax.errorbar([r['budget']+offset for r in data],[r[mean] for r in data],
                    yerr=[r[sd] for r in data],fmt=marker+'-',capsize=2.5,color=color,
                    markersize=3.5,linewidth=1,label=label)
    ax.set(xlabel='Assigned disruption budget',ylabel='Disconnected pairs (%)',
           xticks=[6,12,18,24],ylim=(45,114),xlim=(4,26))
    ax.axhline(100,color='#aaa',linestyle=':',linewidth=.6)
    ax.grid(axis='y',alpha=.18);ax.spines[['top','right']].set_visible(False)
    ax.legend(loc='lower right',fontsize=7,frameon=False)
    fig.tight_layout(pad=.4)
    save(fig,'verified_interdiction_results')
    files=[p for p in OUT.glob('verified_*') if p.suffix in ('.pdf','.png')]
    (OUT/'verified_figures_manifest.json').write_text(json.dumps({
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'measurement_source':str(DATA.relative_to(ROOT)),
        'measurement_sha256':hashlib.sha256(DATA.read_bytes()).hexdigest(),
        'output_sha256':{p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
    },indent=2)+'\n')


if __name__=='__main__':
    main()
