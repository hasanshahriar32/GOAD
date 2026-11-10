"""Recompute saved fold/pair statistics, exact sign flips and Holm correction."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

import numpy as np
import scipy
from scipy import stats

ROOT=Path(__file__).resolve().parents[3]


def exact_signed_rank(differences):
    d=np.asarray(differences);d=d[d!=0]
    if len(d)>22:raise ValueError("Exact reference limited to 22 nonzero pairs")
    if not len(d):return {"p_value":1.,"nonzero_pairs":0,"sign_assignments":1}
    weights=np.rint(2*stats.rankdata(abs(d))).astype(np.int64)
    observed=abs(int(np.dot(np.sign(d).astype(np.int64),weights)));tail=0;assignments=1<<len(d)
    for start in range(0,assignments,65536):
        ids=np.arange(start,min(start+65536,assignments),dtype=np.uint32)
        bits=((ids[:,None]>>np.arange(len(d),dtype=np.uint32))&1).astype(np.int64)
        scores=2*(bits@weights)-weights.sum();tail+=int((abs(scores)>=observed).sum())
    return {"p_value":tail/assignments,"nonzero_pairs":len(d),"sign_assignments":assignments,"tail_assignments":tail,
            "method":"Two-sided exact conditional signed-rank sign-flip enumeration, zeros omitted, doubled ranks retain ties exactly"}


def holm(values):
    ordered=sorted(values,key=values.get);answer={};previous=0
    for i,key in enumerate(ordered):previous=max(previous,min(1.,values[key]*(len(values)-i)));answer[key]=previous
    return answer


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    files=[ROOT/"thesis_research/results/phase2/ablation_results.json",ROOT/"thesis_research/results/phase2/defense_results.json"]
    protocol={"declared_utc":datetime.now(timezone.utc).isoformat(),"scope":"Exploratory reanalysis of historical saved fold/topology values, not new independent Windows evidence",
        "holm_family":"All four budgets times paired t and exact signed-rank permutation tests: eight tests; historical asymptotic Wilcoxon retained separately",
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"input_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in files},
        "numpy":np.__version__,"scipy":scipy.__version__}
    (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(output/"executed_source.py").write_bytes(Path(__file__).read_bytes())
    ablation,defense=[json.loads(p.read_text()) for p in files]
    full=ablation["CertGraph (Full)"]["f1_per_fold"];no_skip=ablation["CertGraph (No Skip)"]["f1_per_fold"]
    t=stats.ttest_rel(full,no_skip)
    folds={"folds":len(full),"full_mean":float(np.mean(full)),"no_skip_mean":float(np.mean(no_skip)),"full_population_sd":float(np.std(full)),
           "no_skip_population_sd":float(np.std(no_skip)),"t_statistic":float(t.statistic),"p_value":float(t.pvalue),"degrees_of_freedom":len(full)-1}
    rows=[];pvalues={}
    for budget in ("6","12","18","24"):
        a=np.array(defense["empirical_metrics"]["stackelberg_coadaptive_mincut"][budget]["paths_severed_per_topology"])
        b=np.array(defense["empirical_metrics"]["greedy_capacity_disruption"][budget]["paths_severed_per_topology"])
        t=stats.ttest_rel(a,b);w=stats.wilcoxon(a,b);exact=exact_signed_rank(a-b)
        saved=defense["statistical_significance"][budget]
        if abs(t.pvalue-saved["paired_ttest_stackelberg_vs_greedy"]["p_value"])>1e-12 or abs(w.pvalue-saved["wilcoxon_stackelberg_vs_greedy"]["p_value"])>1e-12:raise AssertionError("Historical statistics do not reproduce")
        row={"budget":int(budget),"topologies":len(a),"paired_mean_gain_percentage_points":float((a-b).mean()),"nonzero_differences":int(np.count_nonzero(a-b)),
             "positive_differences":int((a>b).sum()),"negative_differences":int((a<b).sum()),"paired_t_p":float(t.pvalue),"legacy_asymptotic_wilcoxon_p":float(w.pvalue),"exact_signed_rank":exact}
        rows.append(row);pvalues[budget+"/paired_t"]=float(t.pvalue);pvalues[budget+"/exact_signed_rank"]=exact["p_value"]
    adjusted=holm(pvalues)
    for row in rows:
        budget=str(row["budget"]);row["holm_adjusted_paired_t_p"]=adjusted[budget+"/paired_t"];row["holm_adjusted_exact_signed_rank_p"]=adjusted[budget+"/exact_signed_rank"]
    result={"status":"passed","historical_statistics_reproduced":True,"skip_ablation":folds,"interdiction":rows,
            "caution":"Fold overlap, graph-generator assumptions and signed-rank sign symmetry limit inference; assigned costs are not measured business disruption"}
    (output/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    (output/"manifest.json").write_text(json.dumps({str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()},indent=2)+"\n")
    print(json.dumps({"status":"passed","budget24":rows[-1],"skip_ablation":folds},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);args=p.parse_args();run(args.output)
