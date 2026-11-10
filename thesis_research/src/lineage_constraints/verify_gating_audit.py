"""Verify saved checkpoint predictions, effective-permission labels and reports."""
import argparse
from collections import defaultdict
import json
from pathlib import Path

import numpy as np
from scipy.special import softmax

from .gating_audit import ROOT,digest,esc1_reference,metrics,forward,FIELDS
from thesis_research.src.phase2_certgraph import gated_shortcut_cure as legacy


def verify(directory,output):
    if output.exists():raise FileExistsError(output)
    for name,expected in json.loads((directory/"manifest.json").read_text()).items():
        if digest(directory/name)!=expected:raise AssertionError("Artifact hash mismatch: "+name)
    protocol=json.loads((directory/"protocol.json").read_text())
    reports=json.loads((directory/"results.json").read_text());checked=0;pooled=defaultdict(list)
    if len(reports)!=12:raise AssertionError("Incomplete factorial study")
    for report in reports:
        rows=json.loads((directory/(report["name"]+"_predictions.json")).read_text())
        inputs=json.loads((directory/(str(report["seed"])+"_test_inputs.json")).read_text())
        cls=legacy.CertGraphAdditive if report["implementation"]=="additive" else legacy.CertGraphGated
        model=cls(seed=report["seed"])
        with np.load(directory/(report["name"]+"_checkpoint.npz"),allow_pickle=False) as checkpoint:
            for name in checkpoint.files:setattr(model,name,checkpoint[name])
        if report["selected_epoch"]!=min(report["history"],key=lambda h:h["validation_nll"])["epoch"]:raise AssertionError("Checkpoint selection mismatch")
        for row,s in zip(rows,inputs,strict=True):
            for key in FIELDS[:-1]:s[key]=np.asarray(s[key],dtype=np.float32)
            label=esc1_reference(s,"closure")
            if label!=row["label"]:raise AssertionError("Independent closure label differs")
            probability=softmax(forward(model,s))
            if int(np.argmax(probability))!=row["prediction"] or not np.allclose(probability,row["probabilities"],atol=1e-7):raise AssertionError("Checkpoint prediction mismatch")
            checked+=1
        if metrics(rows)!=report["overall"]:raise AssertionError("Aggregate mismatch")
        for depth in protocol["test_depths"]:
            if metrics([r for r in rows if r["depth"]==depth])!=report["by_depth"][str(depth)]:raise AssertionError("Stratum mismatch")
        pooled[(report["implementation"],report["augmentation_probability"])].extend(rows)
    summary={"checked_predictions":checked,"runs":len(reports),"status":"passed",
             "pooled":{f"{name}/aug={probability}":metrics(rows) for (name,probability),rows in pooled.items()},
             "verifier_sha256":digest(Path(__file__)),"input_manifest_sha256":digest(directory/"manifest.json")}
    output.write_text(json.dumps(summary,indent=2,sort_keys=True)+"\n");print(json.dumps(summary,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("directory",type=Path);p.add_argument("output",type=Path)
    args=p.parse_args();verify(args.directory,args.output)
