"""Matched audit of the existing two-layer NumPy implementations.

No model equations, layer counts, or original artifacts are modified. The
factorial separates augmentation from the named implementation contrast. Tests
use an explicit ESC1 effective-permission abstraction, not Windows ground truth.
"""
import argparse
import copy
from collections import Counter,defaultdict,deque
import hashlib
import json
from pathlib import Path
import random
import time

import numpy as np
from scipy.special import softmax

from thesis_research.src.phase2_certgraph import gated_shortcut_cure as legacy

ROOT=Path(__file__).resolve().parents[3]
FIELDS=("X","A_mem","A_allow","A_deny","A_write","A_oid","t_idx")


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
def fingerprint(s):
    h=hashlib.sha256()
    for k in FIELDS:
        v=np.asarray(s[k]);h.update(k.encode());h.update(str(v.shape).encode());h.update(v.tobytes())
    return h.hexdigest()


def reachable_bfs(s):
    seen={int(i) for i in np.where(s["X"][:,10]==1)[0]};q=deque(seen)
    while q:
        for j in np.where(s["A_mem"][q.popleft()]>0)[0]:
            if int(j) not in seen:seen.add(int(j));q.append(int(j))
    return seen


def esc1_reference(s,method="bfs"):
    if method=="bfs":seen=reachable_bfs(s)
    else:
        n=len(s["X"]);closure=(s["A_mem"]>0)|np.eye(n,dtype=bool)
        for k in range(n):closure|=closure[:,k,None]&closure[None,k,:]
        seen=set(np.where(closure[np.where(s["X"][:,10]==1)[0]].any(axis=0))[0])
    t=s["t_idx"];x=s["X"][t]
    allow=any(s["A_allow"][i,t]>0 for i in seen)
    deny=any(s["A_deny"][i,t]>0 for i in seen)
    return 0 if x[0]==x[1]==x[3]==1 and allow and not deny else 6


def family(seed,depth,index):
    rng=np.random.default_rng(seed*10000+depth*100+index)
    n=6+depth+int(rng.integers(0,5));t=n-2;admin=n-3
    x=np.zeros((n,16),dtype=np.float32);x[0,10]=1;x[admin,11]=1
    x[t,[0,1,3,14]]=1;x[t,9]=.5;x[n-1,15]=1
    s={"X":x,"t_idx":t}
    for name in FIELDS[1:-1]:s[name]=np.zeros((n,n),dtype=np.float32)
    source=0
    for j in range(depth):
        target=j+1;s["X"][target,12]=1;s["A_mem"][source,target]=1;source=target
    s["A_allow"][source,t]=1
    negative=copy.deepcopy(s)
    intervention="admin_only_enrollment" if index%2==0 else "explicit_deny"
    if index%2==0:
        negative["A_allow"][:]=0;negative["A_allow"][admin,t]=1
    else:negative["A_deny"][0,t]=1
    permutation=rng.permutation(n)
    result=[]
    for label,row in ((0,s),(6,negative)):
        row["X"]=row["X"][permutation]
        for name in FIELDS[1:-1]:row[name]=row[name][np.ix_(permutation,permutation)]
        row["t_idx"]=int(np.where(permutation==t)[0][0]);row["y"]=label
        if esc1_reference(row)!=label or esc1_reference(row,"closure")!=label:raise AssertionError("Independent permission references disagree")
        row.update(family=f"{seed}:{depth}:{index}",depth=depth,intervention=intervention)
        result.append(row)
    return result


def forward(model,s):return model.forward(*(s[k] for k in FIELDS))[0]


def metrics(rows):
    return {"cases":len(rows),"exact_class_accuracy":sum(r["prediction"]==r["label"] for r in rows)/len(rows),
            "escalation_flag_accuracy":sum((r["prediction"]!=6)==(r["label"]!=6) for r in rows)/len(rows),
            "false_positive":sum(r["prediction"]!=6 and r["label"]==6 for r in rows),
            "false_negative":sum(r["prediction"]==6 and r["label"]!=6 for r in rows)}


def freeze(path):
    if path.exists():raise FileExistsError(path)
    dump(path,{"seeds":[12011,13001,14009],"epochs":40,"train":1400,"validation":350,"families_per_depth":50,
        "test_depths":[0,1,2,4,8],"augment_probabilities":[0,.3],"selection":"Minimum validation NLL; no test-selected checkpoint",
        "test_label_contract":"ESC1 client-auth + supplied subject + no approval, effective allow reachable from low-privileged source, no reachable explicit deny; resolved permissions, CA trust assumed. Deep reachable membership remains positive.",
        "limitations":"Fixed membership transforms and hand-initialized projections in inherited implementations; implementation contrast includes initialization differences. Synthetic legacy training archetypes repeat across splits. This is a diagnostic, not a pure gate-effect or enterprise generalization estimate.",
        "source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in (Path(__file__),Path(legacy.__file__))}})


def run(protocol_path,output):
    protocol=json.loads(protocol_path.read_text())
    for name,expected in protocol["source_sha256"].items():
        if digest(ROOT/name)!=expected:raise ValueError("Frozen source differs")
    output.mkdir(parents=True,exist_ok=False);dump(output/"protocol.json",protocol)
    (output/"sources").mkdir()
    for name in protocol["source_sha256"]:(output/"sources"/Path(name).name).write_bytes((ROOT/name).read_bytes())
    reports=[]
    for seed in protocol["seeds"]:
        train=[legacy.generate_multi_hop_ad_graph(legacy.ESC_CLASSES[i%7],seed=seed+i) for i in range(protocol["train"])]
        val=[legacy.generate_multi_hop_ad_graph(legacy.ESC_CLASSES[i%7],seed=seed+5000+i) for i in range(protocol["validation"])]
        test=[s for d in protocol["test_depths"] for i in range(protocol["families_per_depth"]) for s in family(seed,d,i)]
        dump(output/f"{seed}_test_inputs.json",[{**{k:(v.tolist() if isinstance(v,np.ndarray) else v) for k,v in s.items()},"input_sha256":fingerprint(s)} for s in test])
        split_audit={"train_unique_inputs":len({fingerprint(s) for s in train}),"validation_unique_inputs":len({fingerprint(s) for s in val}),
                     "train_validation_input_overlap":len({fingerprint(s) for s in train}&{fingerprint(s) for s in val}),"test_cases":len(test)}
        for implementation,cls in (("additive",legacy.CertGraphAdditive),("feature_channel_gate",legacy.CertGraphGated)):
            for probability in protocol["augment_probabilities"]:
                name=f"{seed}_{implementation}_aug{probability}"
                model=cls(seed=seed);best=None;best_nll=float("inf");history=[];start=time.perf_counter()
                for epoch in range(protocol["epochs"]):
                    order=list(range(len(train)));random.Random(seed+epoch).shuffle(order)
                    augmentation=random.Random(seed+100000+epoch)
                    for index in order:
                        s=train[index];values=[s[k] for k in FIELDS];label=s["y"]
                        draw=augmentation.random()
                        if draw<probability and label!=6:
                            values=[v.copy() if isinstance(v,np.ndarray) else v for v in values]
                            relation="A_allow" if label in (0,1,2,4) else "A_write" if label==3 else "A_oid"
                            values[FIELDS.index(relation)][:]=0;label=6
                        model.train_step(*values,label,lr=.015)
                    nll=float(np.mean([-np.log(softmax(forward(model,s))[s["y"]]+1e-12) for s in val]))
                    history.append({"epoch":epoch,"validation_nll":nll})
                    if nll<best_nll:best_nll=nll;best=copy.deepcopy(model);selected=epoch
                np.savez_compressed(output/(name+"_checkpoint.npz"),**{k:v for k,v in vars(best).items() if isinstance(v,np.ndarray)})
                rows=[{"family":s["family"],"depth":s["depth"],"intervention":s["intervention"],"input_sha256":fingerprint(s),"label":s["y"],
                       "prediction":int(np.argmax(forward(best,s))),"probabilities":softmax(forward(best,s)).tolist()} for s in test]
                dump(output/(name+"_predictions.json"),rows)
                by_depth={str(d):metrics([r for r in rows if r["depth"]==d]) for d in protocol["test_depths"]}
                report={"name":name,"seed":seed,"implementation":implementation,"augmentation_probability":probability,"selected_epoch":selected,
                        "history":history,"split_audit":split_audit,"overall":metrics(rows),"by_depth":by_depth,"training_seconds":time.perf_counter()-start}
                reports.append(report);dump(output/"results.json",reports)
                print(json.dumps({k:report[k] for k in ("name","overall","by_depth")}),flush=True)
    dump(output/"manifest.json",{str(p.relative_to(output)):digest(p) for p in sorted(output.rglob("*")) if p.is_file() and p.name!="manifest.json"})


if __name__=="__main__":
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest="action",required=True)
    f=sub.add_parser("freeze");f.add_argument("protocol",type=Path)
    r=sub.add_parser("run");r.add_argument("protocol",type=Path);r.add_argument("output",type=Path)
    args=parser.parse_args()
    if args.action=="freeze":freeze(args.protocol)
    else:run(args.protocol,args.output)
