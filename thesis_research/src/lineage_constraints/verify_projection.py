"""Reproduce graph/pair outcomes and timing summaries without retiming claims."""
import argparse
import hashlib
import json
from pathlib import Path
import statistics

import networkx as nx
from .projection_contract import make_graph,project,legacy


def verify(directory,output):
    if output.exists():raise FileExistsError(output)
    for name,expected in json.loads((directory/"manifest.json").read_text()).items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:raise AssertionError("Artifact differs")
    protocol=json.loads((directory/"protocol.json").read_text())
    for name,expected in protocol["source_sha256"].items():
        if hashlib.sha256(Path(name).read_bytes()).hexdigest()!=expected:raise AssertionError("Executed source no longer matches")
    rows=json.loads((directory/"results.json").read_text());summaries=json.loads((directory/"summary.json").read_text());pairs_checked=0
    for row in rows:
        g,pairs=make_graph(row["nodes"],row["seed"]+row["nodes"]);small=project(g,pairs)
        if len(pairs)!=row["pairs"] or len(small)!=row["projected_nodes"] or row["dropped_pairs"]:raise AssertionError("Task projection differs")
        for s,t in pairs:
            if nx.has_path(g,s,t)!=nx.has_path(small,s,t):raise AssertionError("Pair reachability differs")
            pairs_checked+=1
        full=legacy.stackelberg_backward_causal_mincut(g,pairs,protocol["budget"])
        reduced=legacy.stackelberg_backward_causal_mincut(small,pairs,protocol["budget"])
        if len(row["repetitions"])!=protocol["repetitions"]:raise AssertionError("Repetition count differs")
        for r in row["repetitions"]:
            if list(full)!=r["full_result"] or list(reduced)!=r["projected_result"]:raise AssertionError("Saved solver outcomes differ")
            if min(r["full_seconds"],r["projection_inclusive_seconds"],r["projection_only_seconds"])<=0:raise AssertionError("Invalid timing")
            if abs(r["ratio"]-r["full_seconds"]/r["projection_inclusive_seconds"])>1e-10:raise AssertionError("Ratio differs")
    for summary in summaries:
        observations=[r for row in rows if row["nodes"]==summary["nodes"] for r in row["repetitions"]]
        expected={"median_full_ms":1000*statistics.median(r["full_seconds"] for r in observations),
                  "median_projection_inclusive_ms":1000*statistics.median(r["projection_inclusive_seconds"] for r in observations),
                  "median_ratio":statistics.median(r["ratio"] for r in observations)}
        if any(abs(summary[k]-v)>1e-10 for k,v in expected.items()):raise AssertionError("Timing summary differs")
    result={"status":"passed","graph_tasks":len(rows),"queried_pairs_reconstructed":pairs_checked,"timing_pairs_checked":sum(len(r["repetitions"]) for r in rows),
            "scope":"Reconstructed queries, solver outcomes and recorded timing arithmetic; does not reproduce elapsed wall-clock durations",
            "verifier_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("output",type=Path);a=p.parse_args();verify(a.directory,a.output)
