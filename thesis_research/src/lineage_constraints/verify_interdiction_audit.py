"""Independent bitset reachability and exhaustive-budget verification."""
import argparse
import hashlib
import json
from pathlib import Path


def severed(nodes,edges,pairs,removed):
    ids={v:i for i,v in enumerate(nodes)};reach=[1<<i for i in range(len(nodes))]
    for u,v,_ in edges:
        if (u,v) not in removed:reach[ids[u]]|=1<<ids[v]
    for k in range(len(nodes)):
        for i in range(len(nodes)):
            if reach[i]>>k&1:reach[i]|=reach[k]
    return sum(not (reach[ids[u]]>>ids[v]&1) for u,v in pairs)


def verify(directory,output):
    if output.exists():raise FileExistsError(output)
    manifest=json.loads((directory/"manifest.json").read_text())
    for name,expected in manifest.items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:raise AssertionError("Artifact differs")
    rows=json.loads((directory/"results.json").read_text());subsets=0
    for row in rows:
        nodes,edges,pairs=row["nodes"],row["edges"],row["pairs"]
        available=[(u,v,a["cost"]) for u,v,a in edges if a["blockable"]];best=(severed(nodes,edges,pairs,set()),0)
        for mask in range(1<<len(available)):
            selected=[e for i,e in enumerate(available) if mask>>i&1];cost=sum(e[2] for e in selected)
            if cost>row["budget"]:continue
            subsets+=1;answer=severed(nodes,edges,pairs,{e[:2] for e in selected})
            best=max(best,(answer,-cost))
        if best!=(row["exact"]["severed_pairs"],-row["exact"]["cost"]):raise AssertionError("Exact result differs from independent oracle")
        fixed=row["metadata_preserving_adaptive"];cut=set(map(tuple,fixed["cut"]))
        if severed(nodes,edges,pairs,cut)!=fixed["severed_pairs"]:raise AssertionError("Heuristic outcome differs")
        if any(not a["blockable"] for u,v,a in edges if (u,v) in cut):raise AssertionError("Immutable permission revoked")
        if sum(a["cost"] for u,v,a in edges if (u,v) in cut)!=fixed["cost"] or fixed["cost"]>row["budget"]:raise AssertionError("Cost differs")
    result={"status":"passed","cases":len(rows),"independent_feasible_subsets":subsets,"verifier_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(result,indent=2)+"\n");print(json.dumps(result,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("output",type=Path);a=p.parse_args();verify(a.directory,a.output)
