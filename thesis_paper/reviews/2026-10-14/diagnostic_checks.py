"""Exploratory journal-readiness checks, not a new independent benchmark.
Run from repo root: .venv/bin/python thesis_paper/reviews/2026-10-14/diagnostic_checks.py
Does not train models or change original results. Predictions never read labels.
Rules were constructed after inspecting the generator; success tests benchmark
simplicity, NOT real ADCS security correctness or out-of-sample generalization.
"""
from pathlib import Path
import sys, json, hashlib, platform
from collections import Counter
ROOT = Path(__file__).resolve().parents[3]
sys.path.insert(0, str(ROOT / 'thesis_research/src/phase2_certgraph'))
import torch
import torch_geometric
import numpy as np
from scipy.stats import ttest_rel
from generator import generate_dataset, ESC_CLASSES
from bfs_baseline import BloodHoundBFSBaseline

def facts(d, ti):
    x = d['Template'].x[ti].tolist()
    def lp(rel):
        e = d['User', rel, 'Template'].edge_index
        return bool((d['User'].x[e[0, e[1] == ti], 5] < .5).any())
    e = d['Template','linked_to','Group'].edge_index
    hv = bool((d['Group'].x[e[1, e[0] == ti], 0] > .5).any())
    return x, lp('enrolls'), lp('write_dacl'), hv

def diagnostic(d, ti):
    x, enroll, write, hv = facts(d, ti)
    ess,nma,nse,ca,ap,cra,ras,ipo,vacl,_ = x
    if vacl: return 'ESC4' if write else 'Safe'
    if ess and ca and nma and not ras: return 'ESC1' if enroll else 'Safe'
    if ap and nma: return 'ESC2'
    if (cra or (ras and ca)) and nma: return 'ESC3'
    if nse and ca: return 'ESC9'
    if ipo and ca: return 'ESC13' if enroll and hv else 'Safe'
    return 'Safe'

def digest(sample):
    d,c,ti = sample
    h=hashlib.sha256()
    h.update(str(ti).encode())
    for n in sorted(d.node_types):
        h.update(n.encode()); h.update(d[n].x.numpy().tobytes())
    for e in sorted(d.edge_types):
        h.update(str(e).encode()); h.update(d[e].edge_index.numpy().tobytes())
    return h.hexdigest()

def summary(ds):
    base=BloodHoundBFSBaseline()
    errors=Counter()
    for d,c,ti in ds:
        p=ESC_CLASSES[base.predict_sample(d,ti)]
        if p != c: errors[c+' -> '+p] += 1
    return {'n':len(ds), 'diagnostic_correct':sum(diagnostic(d,ti)==c for d,c,ti in ds),
            'existing_symbolic_errors':dict(errors),
            'existing_symbolic_correct':len(ds)-sum(errors.values())}

def main():
    ds=generate_dataset(700, seed=42)
    test=generate_dataset(600,seed=1041)
    hn=[s for s in test if s[1]=='Safe' and any(s[0]['Template'].x[s[2],i] == 1 for i in (0,7,8))]
    comparison=generate_dataset(200,seed=100)
    hashes={digest(s) for s in ds}
    cv=json.loads((ROOT/'thesis_research/results/phase2/cv_results.json').read_text())
    compact={k:{f:v[f] for f in ['f1_mean','f1_std','p_value_vs_certgraph'] if f in v} for k,v in cv.items()}
    out={'scope':'Exploratory diagnostic on current source; no model retraining; generator-aware rules, not an independent security oracle',
         'environment':{'python':platform.python_version(),'torch':torch.__version__,'pyg':torch_geometric.__version__},
         'cv_corpus':summary(ds),'hard_negatives':summary(hn),
         'always_safe_correct_on_hn':len(hn),
         'unique_target_vectors':len({tuple(d['Template'].x[ti].tolist()) for d,c,ti in ds}),
         'unique_target_vectors_by_class':{c:len({tuple(d['Template'].x[ti].tolist()) for d,k,ti in ds if k==c}) for c in ESC_CLASSES},
         'current_tool_comparison_exact_overlap':sum(digest(s) in hashes for s in comparison),
         'saved_cv':compact}
    # No-self-loop attention can still depend on target through attention weights.
    target=torch.tensor(0.,requires_grad=True)
    sources=torch.tensor([-1.,1.])
    a=torch.softmax(torch.nn.functional.leaky_relu(sources+target,negative_slope=.2),0)
    result=(a*sources).sum(); result.backward()
    out['theorem1_counterexamples']={'no_self_loop_target_derivative':target.grad.item(),
        'rectangular_skip_W1':[[1.],[0.]],'rectangular_skip_W2':[[0.,1.]],
        'each_nonzero_singular_value':1.,'W2_times_W1':0.,
        'scalar_residual_cancellation':'F(x)=-x, W_skip=1 => F(x)+W_skip*x=0; derivative=0'}
    print(json.dumps(out,indent=2))

if __name__=='__main__': main()
