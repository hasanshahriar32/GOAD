"""Exact-rank/paired reanalysis of the metadata-preserving rerun."""
import argparse
from collections import Counter
from fractions import Fraction
import hashlib
import json
from pathlib import Path

import numpy as np
from scipy import stats
from .audit_legacy_statistics import holm


def exact_rank(differences):
    values=[d for d in differences if d]
    if not values:return {'p_value':1.,'nonzero_pairs':0,'sign_assignments':1}
    groups=Counter(abs(d) for d in values);ranks={};before=0
    for value,count in sorted(groups.items()):ranks[value]=2*before+count+1;before+=count
    weights=[ranks[abs(d)] for d in values];observed=abs(sum(w if d>0 else -w for w,d in zip(weights,values)))
    distribution=Counter({0:1})
    for weight in weights:
        following=Counter()
        for total,count in distribution.items():following[total+weight]+=count;following[total-weight]+=count
        distribution=following
    assignments=1<<len(values)
    assert sum(distribution.values())==assignments
    tail=sum(count for total,count in distribution.items() if abs(total)>=observed)
    return {'p_value':tail/assignments,'nonzero_pairs':len(values),'sign_assignments':assignments,'tail_assignments':tail,
        'method':'Exact conditional sign flips via integer subset-sum counts; tied ranks from exact rational disconnection fractions; zero differences omitted'}


def run(directory,output):
    output.mkdir(parents=True,exist_ok=False)
    rows=json.loads((directory/'per_case.json').read_text());graphs={g['id']:g for g in json.loads((directory/'graphs.json').read_text())}
    results=[];pvalues={}
    for budget in (6,12,18,24):
        selected=[r for r in rows if r['budget']==budget]
        a=np.array([r['corrected']['pct'] for r in selected]);b=np.array([r['static_greedy']['pct'] for r in selected])
        differences=[]
        for row in selected:
            n=len(graphs[row['graph_id']]['pairs'])
            successes_a=round(row['corrected']['pct']*n/100);successes_b=round(row['static_greedy']['pct']*n/100)
            differences.append(Fraction(successes_a-successes_b,n))
        exact=exact_rank(differences);t=stats.ttest_rel(a,b)
        result={'budget':budget,'graphs':len(selected),'corrected_mean_pct':float(a.mean()),'corrected_population_sd_pct':float(a.std()),
            'greedy_mean_pct':float(b.mean()),'greedy_population_sd_pct':float(b.std()),'mean_gain_percentage_points':float((a-b).mean()),
            'corrected_mean_cut_edges':float(np.mean([len(r['corrected']['cut']) for r in selected])),
            'corrected_population_sd_cut_edges':float(np.std([len(r['corrected']['cut']) for r in selected])),
            'greedy_mean_cut_edges':float(np.mean([r['static_greedy']['edges'] for r in selected])),
            'paired_t_statistic':float(t.statistic),'paired_t_p':float(t.pvalue),'exact_signed_rank':exact,
            'changed_legacy_objective_cases':sum(abs(r['legacy']['pct']-r['corrected']['pct'])>1e-9 for r in selected)}
        pvalues[str(budget)+'/t']=float(t.pvalue);pvalues[str(budget)+'/rank']=exact['p_value'];results.append(result)
    adjusted=holm(pvalues)
    for r in results:r.update(holm_t_p=adjusted[str(r['budget'])+'/t'],holm_exact_rank_p=adjusted[str(r['budget'])+'/rank'])
    source=Path(__file__);report={'scope':'Exploratory paired reanalysis of the same 30 synthetic graphs; eight-test family across four budgets and two procedures, not enterprise effectiveness',
        'standard_deviation':'Population denominator over the finite evaluated graph set, matching the historical table convention',
        'input_sha256':{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (directory/'manifest.json',directory/'per_case.json',directory/'graphs.json')},
        'source_sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'rows':results}
    (output/'executed_source.py').write_bytes(source.read_bytes());(output/'results.json').write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
    (output/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in output.iterdir() if p.is_file()},indent=2)+'\n')
    print(json.dumps(results,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.directory,a.output)
