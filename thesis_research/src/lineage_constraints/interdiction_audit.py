"""Check a metadata-preserving adaptive heuristic against exact small cuts.

This is a reachability/disruption heuristic, not an equilibrium or branch-and-cut
solver. Original code/results remain intact as a separately measured comparator.
"""
import argparse
from collections import Counter
import copy
import hashlib
import itertools
import json
from pathlib import Path
import random
import time

import networkx as nx
from thesis_research.src.phase2_certgraph import run_real_stackelberg_eval as legacy


def count(g,pairs):return sum(not nx.has_path(g,s,t) for s,t in pairs)


def adaptive(g,pairs,budget):
    current=g.copy();cuts=[];cost=0
    while True:
        active=[(s,t) for s,t in pairs if nx.has_path(current,s,t)]
        participation=Counter()
        for s,t in active:
            p=nx.shortest_path(current,s,t);participation.update(zip(p,p[1:]))
        best=None;score=-1
        for (u,v),frequency in participation.items():
            attrs=dict(current[u][v]);c=attrs.get("cost",1)
            if not attrs.get("blockable",True) or cost+c>budget:continue
            before=count(current,active);current.remove_edge(u,v)
            gain=count(current,active)-before
            # Restore every edge attribute, including relation and immutability.
            current.add_edge(u,v,**attrs)
            choke=2 if attrs.get("rel") in ("enrolls","write_dacl","escalates_to") or v.startswith("Template") or v.startswith("Group_0") else 1
            value=(gain*10*choke+frequency*choke)/c
            if value>score:best=(u,v,c);score=value
        if best is None:break
        u,v,c=best;current.remove_edge(u,v);cuts.append((u,v));cost+=c
    return {"severed_pairs":count(current,pairs),"cut":cuts,"cost":cost}


def exact(g,pairs,budget):
    edges=[(u,v) for u,v,a in g.edges(data=True) if a.get("blockable",True)]
    best={"severed_pairs":count(g,pairs),"cut":[],"cost":0};checked=0
    for mask in range(1<<len(edges)):
        cut=[e for i,e in enumerate(edges) if mask>>i&1];cost=sum(g[u][v]["cost"] for u,v in cut)
        if cost>budget:continue
        checked+=1;residual=g.copy();residual.remove_edges_from(cut);severed=count(residual,pairs)
        if (severed,-cost)>(best["severed_pairs"],-best["cost"]):best={"severed_pairs":severed,"cut":cut,"cost":cost}
    return {**best,"feasible_subsets":checked}


def graph(seed,index):
    rng=random.Random(seed+index);g=nx.DiGraph();g.add_nodes_from("n"+str(i) for i in range(7))
    base=[(0,2),(2,5),(1,3),(3,6),(0,4),(1,4),(4,5),(4,6)]
    extra=[(u,v) for u in range(7) for v in range(7) if u!=v and (u,v) not in base];rng.shuffle(extra)
    for u,v in base+extra[:4]:g.add_edge("n"+str(u),"n"+str(v),cost=rng.choice((1,2,3)),blockable=rng.random()<.8,rel=rng.choice(("member_of","enrolls","write_dacl")))
    return g,[("n"+str(s),"n"+str(t)) for s in (0,1) for t in (5,6)]


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(legacy.__file__)];protocol={"seeds":[42017,43003,44017],"cases_per_seed":10,"budgets":[3,6],
        "objective":"Maximize severed terminal-pair count with cost as exact-optimum tie break; lambda=0; integer assigned costs",
        "scope":"Small synthetic graph optimality audit, not enterprise disruption or a Stackelberg equilibrium guarantee",
        "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(output/"sources").mkdir()
    for p in sources:(output/"sources"/p.name).write_bytes(p.read_bytes())
    rows=[]
    for seed in protocol["seeds"]:
        for index in range(protocol["cases_per_seed"]):
            g,pairs=graph(seed,index)
            for budget in protocol["budgets"]:
                started=time.perf_counter();opt=exact(g,pairs,budget);fixed=adaptive(g,pairs,budget)
                old=legacy.stackelberg_backward_causal_mincut(g,pairs,budget);greedy=legacy.greedy_capacity_disruption(g,pairs,budget)
                old_count=round(old[0]*len(pairs)/100);greedy_count=round(greedy[0]*len(pairs)/100)
                if fixed["cost"]>budget or fixed["severed_pairs"]>opt["severed_pairs"]:raise AssertionError("Feasibility/optimum violated")
                if any(not g[u][v]["blockable"] for u,v in fixed["cut"]):raise AssertionError("Immutable edge cut")
                rows.append({"seed":seed,"case":index,"budget":budget,"nodes":list(g),"edges":[[u,v,a] for u,v,a in g.edges(data=True)],"pairs":pairs,
                    "exact":opt,"metadata_preserving_adaptive":fixed,"legacy_adaptive_severed":old_count,"static_greedy_severed":greedy_count,
                    "seconds":time.perf_counter()-started})
    summary={"cases":len(rows),"fixed_matches_optimal_count":sum(r["metadata_preserving_adaptive"]["severed_pairs"]==r["exact"]["severed_pairs"] for r in rows),
        "legacy_matches_optimal_count":sum(r["legacy_adaptive_severed"]==r["exact"]["severed_pairs"] for r in rows),
        "static_matches_optimal_count":sum(r["static_greedy_severed"]==r["exact"]["severed_pairs"] for r in rows),
        "maximum_fixed_pair_gap":max(r["exact"]["severed_pairs"]-r["metadata_preserving_adaptive"]["severed_pairs"] for r in rows),"scope":protocol["scope"]}
    for name,data in (("results.json",rows),("summary.json",summary)):(output/name).write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
    (output/"manifest.json").write_text(json.dumps({str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()},indent=2)+"\n")
    print(json.dumps(summary,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);args=p.parse_args();run(args.output)
