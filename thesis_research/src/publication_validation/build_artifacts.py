"""Render manuscript tables/figures exclusively from completed saved runs."""
import hashlib,json,statistics
from pathlib import Path
import numpy as np
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from common import ROOT,write_json

RESULTS=ROOT/'thesis_research/results/publication_validation'
PAPER=ROOT/'thesis_paper/journal_manuscript'
OUT=PAPER/'generated'
MODELS=['CertGraph','Feature MLP','Graph-count MLP','Graph-count RF']

def pm(values,scale=100):
    a=np.array(values)*scale
    return f'{a.mean():.2f} $\\pm$ {a.std(ddof=1):.2f}'

def table(name,caption,label,headers,rows,cols=None,wide=False):
    env='table*' if wide else 'table'
    s='\\begin{'+env+'}[t]\n\\centering\n\\caption{'+caption+'}\n\\label{'+label+'}\n\\footnotesize\n'
    s+='\\begin{tabular}{'+(cols or 'l'+'r'*(len(headers)-1))+'}\n\\toprule\n'
    s+=' & '.join(headers)+' \\\\\n\\midrule\n'
    s+=''.join(' & '.join(row)+' \\\\\n' for row in rows)
    s+='\\bottomrule\n\\end{tabular}\n\\end{'+env+'}\n'
    (OUT/f'{name}.tex').write_text(s)

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    legacy=json.loads((RESULTS/'legacy/results.json').read_text())
    cf=json.loads((RESULTS/'counterfactual/results.json').read_text())
    assert {(r['seed'],r['condition']) for r in legacy['runs']}=={(s,c) for s in [11,29,47] for c in ['mixed_training','no_hn_training']}
    assert {r['seed'] for r in cf['runs']}=={11,29,47}
    for r in cf['runs']: assert len(r['test_sets'])==4 and r['oracle_agreement']
    lr=lambda c,m,k:[r['models'][m][k] for r in legacy['runs'] if r['condition']==c]
    cr=lambda split,m,k:[r['test_sets'][split]['models'][m][k] for r in cf['runs']]
    rows=[]
    for m in MODELS+['Generator diagnostic','Legacy direct-edge rules']:
        rows.append([m,pm(lr('mixed_training',m,'macro_f1')),pm(lr('no_hn_training',m,'macro_f1'))])
    table('legacy','Seven-class synthetic holdouts: macro-F1 (percent), mean $\\pm$ sample standard deviation over three seeds. Each test has 350 graphs. The generator diagnostic is post hoc.','tab:legacy',['Method','Mixed training','No-HN training'],rows)
    rows=[]
    for m in MODELS+['Symbolic reference']:
        rows.append([m]+[pm(cr(s,m,'accuracy')) for s in ['iid','long_paths','larger_graphs','remote_membership']])
    table('counterfactual','Paired prerequisite benchmark: accuracy (percent), mean $\\pm$ sample standard deviation over three seeds. IID, long-path, and larger-graph sets each contain 150 families per seed; remote membership contains 100. The reference also defines the labels.','tab:counterfactual',['Method','IID','Long paths','Larger graphs','Remote membership'],rows,wide=True)
    rows=[]
    for m in MODELS+['Symbolic reference']:
        rows.append([m]+[pm(cr(s,m,'pair_both_correct')) for s in ['iid','long_paths','larger_graphs','remote_membership']])
    table('pairs','Families with both variants classified correctly (percent), mean $\\pm$ sample standard deviation. Each pair contains one positive and one negative.','tab:pairs',['Method','IID','Long paths','Larger graphs','Remote membership'],rows,wide=True)
    rows=[]
    for m in MODELS:
        rows.append([m,pm(lr('mixed_training',m,'hard_negative_specificity')),pm(lr('no_hn_training',m,'hard_negative_specificity'))])
    table('hard_negatives','Specificity on flag-bearing safe examples in the seven-class test (percent). These are a diagnostic subset, not an independently collected negative population.','tab:hn',['Method','Mixed training','No-HN training'],rows)
    rows=[]
    for m in MODELS:
        h=lambda k:[r['test_sets']['iid']['hybrid'][m][k] for r in cf['runs']]
        cost=[r['test_sets']['iid']['timings'][m+' + reference']['median_ms'] for r in cf['runs']]
        rows.append([m,pm(h('recall')),pm(h('candidate_fraction')),pm(cost,1)])
    rows.append(['Reference only','100.00','100.00',pm([r['test_sets']['iid']['timings']['Symbolic reference']['median_ms'] for r in cf['runs']],1)])
    rows.append(['Flags + reference','100.00','85.00',pm([r['test_sets']['iid']['timings']['Necessary flags + reference']['median_ms'] for r in cf['runs']],1)])
    table('cascade','IID screening followed by exact checking within the abstraction. Corpus latency covers 300 graphs in memory. Values are mean $\\pm$ sample standard deviation of per-seed medians; they are not deployment latency.','tab:cascade',['Screen','Recall (\\%)','Checked (\\%)','Time (ms)'],rows,wide=True)
    # A compact figure with reproducible values and error bars across seeds.
    plt.rcParams.update({'font.family':'DejaVu Sans','font.size':9,'pdf.fonttype':42})
    fig,axes=plt.subplots(1,2,figsize=(7.0,2.65),layout='constrained')
    labels=['GNN','Local MLP','Count MLP','Count RF']
    x=np.arange(4)
    for ax,metric,title in [(axes[0],'accuracy','Individual-case accuracy'),(axes[1],'pair_both_correct','Both variants correct')]:
        for j,(split,label,color) in enumerate([('iid','IID','#2878a0'),('larger_graphs','Larger graphs','#d58a22'),('remote_membership','Remote membership','#6f627f')]):
            a=np.array([cr(split,m,metric) for m in MODELS])*100
            ax.bar(x+(j-1)*.24,a.mean(1),width=.23,label=label,color=color,yerr=a.std(1,ddof=1),capsize=2)
        ax.set_xticks(x,labels);ax.set_ylim(0,105);ax.set_title(title);ax.set_ylabel('Percent');ax.spines[['top','right']].set_visible(False)
    handles,labels=axes[0].get_legend_handles_labels()
    fig.legend(handles,labels,fontsize=8,loc='lower center',bbox_to_anchor=(.5,-.09),ncol=3,frameon=False)
    fig.savefig(OUT/'paired_results.pdf',bbox_inches='tight');fig.savefig(OUT/'paired_results.png',dpi=300,bbox_inches='tight');plt.close(fig)
    summary={'legacy':{},'counterfactual':{},'iid_cascade':{}}
    for c in ['mixed_training','no_hn_training']:
        summary['legacy'][c]={m:{k:float(np.mean(lr(c,m,k))) for k in ['macro_f1','hard_negative_specificity']} for m in MODELS+['Generator diagnostic']}
    for s in ['iid','long_paths','larger_graphs','remote_membership']:
        summary['counterfactual'][s]={m:{k:float(np.mean(cr(s,m,k))) for k in ['accuracy','pair_both_correct','recall','specificity']} for m in MODELS+['Symbolic reference']}
    for m in MODELS:
        summary['iid_cascade'][m]={k:float(np.mean([r['test_sets']['iid']['hybrid'][m][k] for r in cf['runs']])) for k in ['recall','candidate_fraction']}
    write_json(OUT/'summary.json',summary)
    write_json(OUT/'table_provenance.json',{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in [RESULTS/'legacy/results.json',RESULTS/'counterfactual/results.json']})
    print(json.dumps(summary,indent=2))
if __name__=='__main__':main()
