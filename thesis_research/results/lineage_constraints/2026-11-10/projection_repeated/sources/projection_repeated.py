"""Repeated alternating-order timings for the same-task projection contract."""
import argparse
import hashlib
import json
from pathlib import Path
import platform
import statistics
import time

import networkx as nx
from . import projection_contract as projection


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__),Path(projection.__file__),Path(projection.legacy.__file__)]
    protocol={"seeds":[52021,53003,54001],"nodes":[100,1000,5000],"repetitions":5,"budget":12,
        "timing_contract":"Alternate full-first/projected-first, include projection in each projected timing, no cached graph preprocessing across repetitions; host is shared with Windows lab VM",
        "python":platform.python_version(),"networkx":nx.__version__,"platform":platform.platform(),
        "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(output/"sources").mkdir()
    for p in sources:(output/"sources"/p.name).write_bytes(p.read_bytes())
    rows=[]
    for seed in protocol["seeds"]:
        for n in protocol["nodes"]:
            g,pairs=projection.make_graph(n,seed+n);repetitions=[]
            def full():
                start=time.perf_counter();r=projection.legacy.stackelberg_backward_causal_mincut(g,pairs,12)
                return time.perf_counter()-start,r
            def reduced():
                start=time.perf_counter();small=projection.project(g,pairs);projected=time.perf_counter()
                r=projection.legacy.stackelberg_backward_causal_mincut(small,pairs,12)
                return time.perf_counter()-start,r,projected-start,len(small),small.number_of_edges()
            for repetition in range(protocol["repetitions"]):
                if repetition%2==0:whole=full();small=reduced()
                else:small=reduced();whole=full()
                if abs(whole[1][0]-small[1][0])>1e-9:raise AssertionError("Reported outcome differs")
                repetitions.append({"order":"full_first" if repetition%2==0 else "projection_first","full_seconds":whole[0],"projection_inclusive_seconds":small[0],
                    "projection_only_seconds":small[2],"full_result":list(whole[1]),"projected_result":list(small[1]),"ratio":whole[0]/small[0]})
            rows.append({"seed":seed,"nodes":n,"edges":g.number_of_edges(),"pairs":len(pairs),"projected_nodes":small[3],"projected_edges":small[4],"dropped_pairs":0,
                "median_ratio":statistics.median(r["ratio"] for r in repetitions),"repetitions":repetitions})
            (output/"results.json").write_text(json.dumps(rows,indent=2)+"\n")
            print(json.dumps({k:v for k,v in rows[-1].items() if k!="repetitions"}),flush=True)
    summaries=[]
    for n in protocol["nodes"]:
        group=[row for row in rows if row["nodes"]==n];r=[r for row in group for r in row["repetitions"]]
        summaries.append({"nodes":n,"seeds":len(group),"timing_pairs":len(r),"query_pairs_per_graph":group[0]["pairs"],
            "projected_nodes_min":min(v["projected_nodes"] for v in group),"projected_nodes_max":max(v["projected_nodes"] for v in group),
            "median_full_ms":1000*statistics.median(v["full_seconds"] for v in r),"median_projection_inclusive_ms":1000*statistics.median(v["projection_inclusive_seconds"] for v in r),
            "median_ratio":statistics.median(v["ratio"] for v in r),"min_ratio":min(v["ratio"] for v in r),"max_ratio":max(v["ratio"] for v in r)})
    (output/"summary.json").write_text(json.dumps(summaries,indent=2)+"\n")
    (output/"manifest.json").write_text(json.dumps({str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()},indent=2)+"\n")
    print(json.dumps(summaries,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);args=p.parse_args();run(args.output)
