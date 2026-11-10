"""Independent NetworkX labels, split audits and checkpoint reproduction."""
import argparse
from collections import defaultdict
import gzip
import hashlib
import json
from pathlib import Path
import statistics

import networkx as nx
import numpy as np
import torch
from .bilinear_study import LiteralBilinearGNN,predict,metrics,typed_hash


def independent_label(case):
    g=nx.DiGraph();g.add_nodes_from(range(len(case["x"])))
    g.add_edges_from((u,v) for r,u,v in case["edges"] if r==0)
    seen=set()
    for i,x in enumerate(case["x"]):
        if x[10]==1:seen|=nx.descendants(g,i)|{i}
    target=case["target"]
    allow=any(r==1 and u in seen and v==target for r,u,v in case["edges"])
    deny=any(r==2 and u in seen and v==target for r,u,v in case["edges"])
    return int(allow and not deny and all(case["x"][target][i]==1 for i in (0,1,3)))


def verify(directory,output):
    if output.exists():raise FileExistsError(output)
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    for name,expected in json.loads((directory/"manifest.json").read_text()).items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:raise AssertionError("Artifact hash differs")
    protocol=json.loads((directory/"protocol.json").read_text());reports=json.loads((directory/"results.json").read_text())
    for name,expected in protocol["source_sha256"].items():
        if hashlib.sha256((directory/"sources"/Path(name).name).read_bytes()).hexdigest()!=expected:raise AssertionError("Frozen executed source differs")
    if len(reports)!=12:raise AssertionError("Incomplete factorial study")
    cases_by_seed={};labels_checked=0;prediction_count=0;pooled=defaultdict(list);per_seed=defaultdict(list)
    for seed in protocol["seeds"]:
        with gzip.open(directory/f"{seed}_cases.json.gz","rt") as source:splits=json.load(source)
        seen=set();families=set()
        for split,rows in splits.items():
            hashes={r["typed_wl_hash"] for r in rows};group={r["family"] for r in rows}
            if seen&hashes or families&group or len(hashes)!=len(rows):raise AssertionError("Family/input overlap across splits")
            seen|=hashes;families|=group
            for row in rows:
                if independent_label(row)!=row["label"]:raise AssertionError("Independent permission label differs")
                if typed_hash(row)!=row["typed_wl_hash"]:raise AssertionError("Typed graph encoding differs")
                encoded=json.dumps({k:row[k] for k in ("x","types","edges","target")},sort_keys=True).encode()
                if hashlib.sha256(encoded).hexdigest()!=row["input_sha256"]:raise AssertionError("Input hash differs")
                labels_checked+=1
        cases_by_seed[seed]=splits
        initial={r["initial_parameters_sha256"] for r in reports if r["seed"]==seed}
        if len(initial)!=1:raise AssertionError("Initial trainable parameters differ across arms")
    for report in reports:
        selected=min(report["history"],key=lambda v:v["validation_nll"])["epoch"]
        if selected!=report["selected_epoch"]:raise AssertionError("Validation checkpoint selection differs")
        model=LiteralBilinearGNN(gated=report["gated"],hidden=protocol["hidden"],heads=protocol["heads"])
        model.load_state_dict(torch.load(directory/(report["name"]+"_checkpoint.pt"),weights_only=True,map_location="cpu"))
        arm=("bilinear" if report["gated"] else "additive")+"/aug="+str(report["augmentation_probability"])
        for split,summary in report["test_sets"].items():
            inputs=cases_by_seed[report["seed"]][split];scores=predict(model,inputs)
            saved=json.loads((directory/(report["name"]+"_"+split+"_predictions.json")).read_text())
            for case,score,row in zip(inputs,scores,saved,strict=True):
                if row["input_sha256"]!=case["input_sha256"] or row["label"]!=case["label"] or row["prediction"]!=int(score>=.5) or abs(score-row["score"])>1e-6:raise AssertionError("Checkpoint prediction differs")
                prediction_count+=1
            computed=metrics(inputs,scores)
            if any(abs(computed[k]-summary[k])>1e-8 for k in computed):raise AssertionError("Aggregate metric differs")
            pooled[(arm,split)].extend(saved);per_seed[(arm,split)].append(summary["accuracy"])
    matched_classifications={}
    for seed in protocol["seeds"]:
        for split in ("iid","long_paths","larger_background"):
            signatures=[]
            for implementation in ("additive","bilinear"):
                for probability in protocol["augment_probabilities"]:
                    rows=json.loads((directory/f"{seed}_{implementation}_aug{probability}_{split}_predictions.json").read_text())
                    signatures.append([(r["input_sha256"],r["prediction"]) for r in rows])
            matched_classifications[f"{seed}/{split}"]=all(s==signatures[0] for s in signatures)
    aggregate={}
    for (arm,split),rows in pooled.items():
        values=per_seed[(arm,split)]
        aggregate[arm+"/"+split]={"accuracy_mean":statistics.mean(values),"accuracy_sample_sd":statistics.stdev(values),
            "accuracy_by_seed":values,"pooled":metrics(rows,[r["score"] for r in rows])}
    result={"status":"passed","labels_checked_independently":labels_checked,"checkpoint_predictions_reproduced":prediction_count,"runs":len(reports),
        "split_contract_checked":"Typed whole-graph WL and family disjointness within each seed; does not establish disjoint local motifs or population independence",
        "by_arm_and_split":aggregate,"verifier_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "all_arms_have_identical_classifications_by_seed_and_cohort":matched_classifications,
        "input_manifest_sha256":hashlib.sha256((directory/"manifest.json").read_bytes()).hexdigest()}
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n");print(json.dumps({k:result[k] for k in ("status","labels_checked_independently","checkpoint_predictions_reproduced","runs")},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("output",type=Path);args=p.parse_args();verify(args.directory,args.output)
