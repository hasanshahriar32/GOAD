"""Compare whole-graph and path-preserving projection on identical pair tasks.

Any original s-to-t path lies in descendants(s) intersect ancestors(t), so the
union projection preserves reachability for every subset of retained edge cuts.
All endpoints and edge attributes are retained, including initially unconnected
pairs. This differs from a depth-limited cone that drops queried source pairs.
"""
import argparse
import hashlib
import json
from pathlib import Path
import random
import time

import networkx as nx
from thesis_research.src.phase2_certgraph import run_real_stackelberg_eval as legacy


def project(g,pairs):
    nodes={v for p in pairs for v in p}
    forward={s:nx.descendants(g,s)|{s} for s,_ in pairs}
    backward={t:nx.ancestors(g,t)|{t} for _,t in pairs}
    for s,t in pairs:nodes|=forward[s]&backward[t]
    return g.subgraph(nodes).copy()


def make_graph(n,seed):
    rng=random.Random(seed);g=nx.DiGraph();users=int(.65*n);groups=int(.25*n);templates=max(4,int(.01*n))
    for prefix,count in (("User_",users),("Group_",groups),("Template_",templates)):
        g.add_nodes_from(prefix+str(i) for i in range(count))
    g.add_node("Group_Target")
    g.add_nodes_from("Background_"+str(i) for i in range(n-len(g)))
    def add(u,v,rel,cost):g.add_edge(u,v,rel=rel,cost=cost,blockable=True)
    for i in range(users):add(f"User_{i}",f"Group_{rng.randrange(groups)}","member_of",round(rng.uniform(2.5,3.5),2))
    for i in range(1,groups):add(f"Group_{i}",f"Group_{rng.randrange(i)}","member_of",round(rng.uniform(2.5,3.5),2))
    for t in range(templates):
        for _ in range(rng.randint(2,4)):add(f"Group_{rng.randrange(groups)}",f"Template_{t}","enrolls",round(rng.uniform(1,1.5),2))
    for t in range(3):add(f"Template_{t}","Group_Target","escalates_to",round(rng.uniform(1,1.5),2))
    add("Group_0","Template_0","enrolls",1.2)
    return g,[(f"User_{i}","Group_Target") for i in range(max(1,int(.1*users)))]


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(legacy.__file__)]
    protocol={"seeds":[52021,53003,54001],"nodes":[100,1000,5000],"budget":12,
        "solver":"Same unmodified historical adaptive heuristic on both inputs; its metadata bug remains part of this controlled comparison",
        "scope":"Pair-task-preserving projection diagnostic on hierarchical synthetic graphs; no enterprise distribution or universal speedup claim",
        "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(output/"sources").mkdir()
    for p in sources:(output/"sources"/p.name).write_bytes(p.read_bytes())
    rows=[]
    for seed in protocol["seeds"]:
        for n in protocol["nodes"]:
            g,pairs=make_graph(n,seed+n)
            start=time.perf_counter();small=project(g,pairs);projection_seconds=time.perf_counter()-start
            start=time.perf_counter();full_result=legacy.stackelberg_backward_causal_mincut(g,pairs,12);full_seconds=time.perf_counter()-start
            start=time.perf_counter();projected_result=legacy.stackelberg_backward_causal_mincut(small,pairs,12);solve_seconds=time.perf_counter()-start
            if any(nx.has_path(g,s,t)!=nx.has_path(small,s,t) for s,t in pairs):raise AssertionError("Projection changed queried reachability")
            # Algorithm tie breaks can depend on retained iteration order; report
            # outcomes, rather than assuming equal paths imply equal heuristic cuts.
            row={"seed":seed,"nodes":len(g),"edges":g.number_of_edges(),"pairs":len(pairs),"projected_nodes":len(small),"projected_edges":small.number_of_edges(),
                "dropped_pairs":0,"full_result":list(full_result),"projected_result":list(projected_result),"same_pair_count_outcome":abs(full_result[0]-projected_result[0])<1e-9,
                "full_seconds":full_seconds,"projection_seconds":projection_seconds,"projected_solve_seconds":solve_seconds,
                "inclusive_speed_ratio":full_seconds/(projection_seconds+solve_seconds)}
            rows.append(row);(output/"results.json").write_text(json.dumps(rows,indent=2)+"\n");print(json.dumps(row),flush=True)
    (output/"manifest.json").write_text(json.dumps({str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()},indent=2)+"\n")


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);a=p.parse_args();run(a.output)
