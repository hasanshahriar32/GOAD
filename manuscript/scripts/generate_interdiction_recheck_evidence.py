"""Generate the primary remediation table from the corrected full rerun."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/'thesis_research/results/lineage_constraints/2026-11-10'


def p_format(value):
    text=f'{value:.4g}'
    if 'e' in text:
        coefficient,exponent=text.split('e');return coefficient+r' \times 10^{'+str(int(exponent))+'}'
    return text


def main():
    inputs=[ROOT/'thesis_research/results/phase2/defense_results.json',RESULTS/'interdiction_recheck_statistics/results.json',RESULTS/'interdiction_recheck_verification.json']
    old,corrected,verification=[json.loads(p.read_text()) for p in inputs]
    assert verification['historical_static_greedy_percentages_reproduced']==120
    rows=[]
    for key,label in [('random_revocation','Random cut'),('degree_centrality','Degree centrality'),('greedy_capacity_disruption','Static greedy')]:
        values=[old['empirical_metrics'][key][str(b)] for b in [6,12,18,24]]
        rows.append(label+' & '+' & '.join(f"${r['paths_severed_mean']:.1f} \\pm {r['paths_severed_std']:.1f}\\%$" for r in values)+r' \\')
    values=corrected['rows']
    rows.append('Metadata-preserving adaptive & '+' & '.join(f"${r['corrected_mean_pct']:.1f} \\pm {r['corrected_population_sd_pct']:.1f}\\%$" for r in values)+r' \\')
    rows.append(r'\midrule')
    for key,label in [('paired_t_p','Paired $t$, raw $p$'),('exact_signed_rank','Exact signed rank, raw $p$'),('holm_t_p','Holm paired $t$'),('holm_exact_rank_p','Holm signed rank')]:
        numbers=[r[key]['p_value'] if key=='exact_signed_rank' else r[key] for r in values]
        rows.append(label+' & '+' & '.join('$'+p_format(x)+'$' for x in numbers)+r' \\')
    text=r'''\begin{table}[ht]
\centering
\caption{Remediation on the same 30 generated identity graphs. The adaptive row uses full edge-attribute restoration. Mean and population SD describe the finite evaluated set. Tests compare the corrected adaptive policy with static greedy; Holm correction covers four budgets and two test procedures.}
\label{tab:stackelberg_results}
\small
\resizebox{\textwidth}{!}{%
\begin{tabular}{l@{\hspace{12pt}}c@{\hspace{18pt}}c@{\hspace{18pt}}c@{\hspace{18pt}}c}
\toprule
Policy & Budget 6 & Budget 12 & Budget 18 & Budget 24 \\
\midrule
'''+ '\n'.join(rows)+r'''
\bottomrule
\end{tabular}%
}
\end{table}
'''
    path=ROOT/'manuscript/generated/interdiction_recheck_evidence.tex';path.write_text(text)
    path.with_name('interdiction_recheck_evidence_manifest.json').write_text(json.dumps({'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        'input_sha256':{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},'output_sha256':hashlib.sha256(path.read_bytes()).hexdigest()},indent=2)+'\n')


if __name__=='__main__':main()
