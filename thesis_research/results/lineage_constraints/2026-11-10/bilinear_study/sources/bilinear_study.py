"""Family-disjoint audit of the literal bilinear two-layer attention model.

Labels are an explicit resolved-permission ESC1 abstraction. Whole input graphs
are filtered by typed WL hashes across splits; this excludes isomorphic inputs
under the declared encoding, but does not establish independent local motifs.
"""
import argparse
from collections import defaultdict,deque
import copy
from datetime import datetime,timezone
import gzip
import hashlib
import json
from pathlib import Path
import platform
import random
import time
import sklearn

import networkx as nx
import numpy as np
from sklearn.metrics import accuracy_score,f1_score,precision_score,recall_score
import torch
from torch.nn import functional as F

from .literal_bilinear import LiteralBilinearGNN

ROOT=Path(__file__).resolve().parents[3]


def digest(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def reference(case,closure=False):
    n=len(case["x"]);sources={i for i,x in enumerate(case["x"]) if x[10]==1};target=case["target"]
    if closure:
        reach=np.eye(n,dtype=bool)
        for r,u,v in case["edges"]:
            if r==0:reach[u,v]=True
        for k in range(n):reach|=reach[:,k,None]&reach[None,k,:]
        seen={j for s in sources for j in np.where(reach[s])[0]}
    else:
        adjacency=defaultdict(list)
        for r,u,v in case["edges"]:
            if r==0:adjacency[u].append(v)
        seen=set(sources);queue=deque(sources)
        while queue:
            for v in adjacency[queue.popleft()]:
                if v not in seen:seen.add(v);queue.append(v)
    allow=any(r==1 and u in seen and v==target for r,u,v in case["edges"])
    deny=any(r==2 and u in seen and v==target for r,u,v in case["edges"])
    flags=all(case["x"][target][i]==1 for i in (0,1,3))
    return int(flags and allow and not deny)


def typed_hash(case):
    g=nx.DiGraph()
    for i,(x,kind) in enumerate(zip(case["x"],case["types"],strict=True)):
        g.add_node(i,kind=str((kind,x[10],x[11],x[0],x[1],x[3])))
    labels=defaultdict(list)
    for r,u,v in case["edges"]:labels[(u,v)].append(r)
    for (u,v),rs in labels.items():g.add_edge(u,v,kind=",".join(map(str,sorted(rs))))
    return nx.weisfeiler_lehman_graph_hash(g,node_attr="kind",edge_attr="kind",iterations=5)


def family(rng,depth,identifier,background=0):
    types=[0,0];features=[];edges=[]
    def node(kind):types.append(kind);return len(types)-1
    chain=[];previous=0
    for _ in range(depth):
        v=node(1);edges.append((0,previous,v));chain.append(v);previous=v
    reachable=[0]+chain
    for _ in range(rng.randint(4,12)):
        v=node(1);parent=rng.choice(reachable);edges.append((0,parent,v));reachable.append(v)
    unreach=[1]
    for _ in range(rng.randint(5,14)):
        v=node(1);parent=rng.choice(unreach);edges.append((0,parent,v));unreach.append(v)
        if rng.random()<.35 and len(unreach)>2:
            another=rng.choice(unreach[:-1]);edges.append((0,another,v))
    target=node(2);node(3)
    for _ in range(background):node(rng.choice((0,1,4)))
    for i,kind in enumerate(types):
        x=[0.]*16
        if kind==1:x[12]=1
        elif kind==2:x[14]=1
        elif kind==3:x[15]=1
        if i==0:x[10]=1
        if i==1:x[11]=1
        features.append(x)
    for k in (0,1,3):features[target][k]=1
    denied=rng.choice(unreach[1:]);edges.extend(((1,previous,target),(2,denied,target)))
    positive={"x":features,"types":types,"target":target,"edges":sorted(set(edges))}
    negative=copy.deepcopy(positive)
    intervention=rng.choice(("unreachable_allow","reachable_deny"))
    if intervention=="unreachable_allow":
        negative["edges"].remove((1,previous,target));negative["edges"].append((1,rng.choice(unreach[1:]),target))
    else:
        negative["edges"].remove((2,denied,target));negative["edges"].append((2,rng.choice(reachable),target))
    permutation=list(range(len(types)));rng.shuffle(permutation);inverse={old:new for new,old in enumerate(permutation)}
    pair=[]
    for label,row in ((1,positive),(0,negative)):
        row["x"]=[row["x"][old] for old in permutation];row["types"]=[row["types"][old] for old in permutation]
        row["edges"]=sorted((r,inverse[u],inverse[v]) for r,u,v in row["edges"]);row["target"]=inverse[row["target"]]
        row.update(label=label,family=identifier,variant="positive" if label else "negative",family_depth=depth,intervention=intervention)
        if reference(row)!=label or reference(row,True)!=label:raise AssertionError("Resolved permission label mismatch")
        row["typed_wl_hash"]=typed_hash(row)
        row["input_sha256"]=hashlib.sha256(json.dumps({k:row[k] for k in ("x","types","edges","target")},sort_keys=True).encode()).hexdigest()
        pair.append(row)
    return pair


def data(seed,protocol):
    seen=set();splits={};attempt_counts={}
    plans=(("train",protocol["train_families"],[0,1],0),("validation",protocol["validation_families"],[0,1],0),
           ("iid",protocol["test_families"],[0,1],0),("long_paths",protocol["test_families"],[2,4,8],0),
           ("larger_background",protocol["test_families"],[0,1],40))
    for index,(name,count,depths,background) in enumerate(plans):
        rng=random.Random(seed+index*1000000);rows=[];attempts=0
        while len(rows)<2*count:
            attempts+=1
            if attempts>count*100:raise RuntimeError("Insufficient distinct graph families")
            pair=family(rng,depths[(len(rows)//2)%len(depths)],f"{seed}:{name}:{len(rows)//2}",background)
            hashes={r["typed_wl_hash"] for r in pair}
            if len(hashes)!=2 or hashes&seen:continue
            seen.update(hashes);rows.extend(pair)
        splits[name]=rows;attempt_counts[name]=attempts
    return splits,attempt_counts


def batch(rows):
    b=len(rows);n=max(len(r["x"]) for r in rows)
    x=torch.zeros(b,n,16);a=torch.zeros(b,3,n,n,dtype=torch.bool);types=torch.zeros(b,n,dtype=torch.long)
    valid=torch.zeros(b,n,dtype=torch.bool);targets=torch.zeros(b,dtype=torch.long);labels=torch.zeros(b,dtype=torch.long)
    for i,row in enumerate(rows):
        size=len(row["x"]);x[i,:size]=torch.tensor(row["x"]);types[i,:size]=torch.tensor(row["types"]);valid[i,:size]=True
        targets[i]=row["target"];labels[i]=row["label"]
        for r,u,v in row["edges"]:a[i,r,u,v]=True
    return (x,a,types,valid,targets),labels


def predict(model,rows,batch_size=32):
    model.eval();scores=[]
    with torch.no_grad():
        for index in range(0,len(rows),batch_size):
            inputs,_=batch(rows[index:index+batch_size]);scores.extend(torch.softmax(model(*inputs),-1)[:,1].tolist())
    return scores


def metrics(rows,scores):
    labels=np.asarray([r["label"] for r in rows]);scores=np.asarray(scores);predictions=scores>=.5
    pairs=defaultdict(list)
    for r,p in zip(rows,predictions,strict=True):pairs[r["family"]].append(int(p)==r["label"])
    if any(len(v)!=2 for v in pairs.values()):raise AssertionError("Incomplete paired evaluation")
    ece=0
    for i in range(10):
        selection=(scores>=i/10)&(scores<((i+1)/10) if i<9 else scores<=1)
        if selection.any():ece+=selection.mean()*abs(scores[selection].mean()-labels[selection].mean())
    return {"cases":len(rows),"families":len(pairs),"accuracy":float(accuracy_score(labels,predictions)),"macro_f1":float(f1_score(labels,predictions,average="macro",zero_division=0)),
        "precision":float(precision_score(labels,predictions,zero_division=0)),"recall":float(recall_score(labels,predictions,zero_division=0)),
        "false_positive":int(((labels==0)&predictions).sum()),"false_negative":int(((labels==1)&~predictions).sum()),
        "brier":float(np.mean((scores-labels)**2)),"ece_10_equal_width_bins":float(ece),"pair_both_correct":float(np.mean([all(v) for v in pairs.values()]))}


def freeze(path):
    if path.exists():raise FileExistsError(path)
    from . import literal_bilinear
    sources=[Path(__file__),Path(literal_bilinear.__file__)]
    dump(path,{"declared_utc":datetime.now(timezone.utc).isoformat(),"seeds":[62003,63001,64007],"epochs":30,"train_families":300,"validation_families":100,"test_families":150,
        "batch_size":32,"hidden":32,"heads":4,"layers":2,"learning_rate":.003,"weight_decay":.0001,"augment_probabilities":[0,.3],
        "selection":"Minimum validation cross entropy, threshold .5 fixed; test sets never used for model selection",
        "split_contract":"Typed five-round WL input hashes and family IDs disjoint across every split; conservative isomorphism filter, not independent local motif guarantee",
        "scope":"Literal fully trained bilinear relational attention in a resolved-permission ESC1 abstraction; no Windows exploit or enterprise prevalence labels",
        "source_sha256":{str(p.relative_to(ROOT)):digest(p) for p in sources},"python":platform.python_version(),"torch":torch.__version__,"networkx":nx.__version__,"numpy":np.__version__,"sklearn":sklearn.__version__})


def run(protocol_path,output):
    protocol=json.loads(protocol_path.read_text())
    for name,expected in protocol["source_sha256"].items():
        if digest(ROOT/name)!=expected:raise ValueError("Frozen source changed")
    torch.set_num_threads(2);torch.use_deterministic_algorithms(True)
    output.mkdir(parents=True,exist_ok=False);dump(output/"protocol.json",protocol);(output/"sources").mkdir()
    for name in protocol["source_sha256"]:(output/"sources"/Path(name).name).write_bytes((ROOT/name).read_bytes())
    reports=[]
    for seed in protocol["seeds"]:
        splits,attempts=data(seed,protocol)
        with gzip.open(output/f"{seed}_cases.json.gz","wt") as target:json.dump(splits,target)
        dump(output/f"{seed}_split_audit.json",{"attempts":attempts,"rows":{k:len(v) for k,v in splits.items()},"all_typed_hashes_disjoint":True})
        for gated in (False,True):
            for probability in protocol["augment_probabilities"]:
                name=f"{seed}_{'bilinear' if gated else 'additive'}_aug{probability}";torch.manual_seed(seed)
                model=LiteralBilinearGNN(gated=gated,hidden=protocol["hidden"],heads=protocol["heads"])
                initial_hash=hashlib.sha256(b"".join(v.detach().numpy().tobytes() for v in model.state_dict().values())).hexdigest()
                optimizer=torch.optim.Adam(model.parameters(),lr=protocol["learning_rate"],weight_decay=protocol["weight_decay"])
                best_nll=float("inf");best=None;history=[];started=time.perf_counter()
                for epoch in range(protocol["epochs"]):
                    model.train();order=list(range(len(splits["train"])));rng=random.Random(seed+epoch);rng.shuffle(order)
                    for index in range(0,len(order),protocol["batch_size"]):
                        selected=[splits["train"][i] for i in order[index:index+protocol["batch_size"]]];inputs,labels=batch(selected)
                        x,a,types,valid,targets=inputs
                        draws=torch.tensor([rng.random() for _ in selected]);augment=(draws<probability)&(labels==1)
                        if augment.any():a[augment,1]=False;labels[augment]=0
                        optimizer.zero_grad();loss=F.cross_entropy(model(x,a,types,valid,targets),labels);loss.backward();optimizer.step()
                    scores=np.clip(predict(model,splits["validation"]),1e-7,1-1e-7);y=np.array([r["label"] for r in splits["validation"]])
                    nll=float(np.mean(-y*np.log(scores)-(1-y)*np.log(1-scores)));history.append({"epoch":epoch,"validation_nll":nll})
                    if nll<best_nll:best_nll=nll;best=copy.deepcopy(model.state_dict());selected_epoch=epoch
                model.load_state_dict(best);torch.save(best,output/(name+"_checkpoint.pt"))
                report={"name":name,"seed":seed,"gated":gated,"augmentation_probability":probability,"selected_epoch":selected_epoch,"history":history,"initial_parameters_sha256":initial_hash,"test_sets":{}}
                for split in ("iid","long_paths","larger_background"):
                    scores=predict(model,splits[split]);report["test_sets"][split]=metrics(splits[split],scores)
                    dump(output/(name+"_"+split+"_predictions.json"),[{"family":r["family"],"variant":r["variant"],"label":r["label"],"input_sha256":r["input_sha256"],"typed_wl_hash":r["typed_wl_hash"],"score":score,"prediction":int(score>=.5)} for r,score in zip(splits[split],scores,strict=True)])
                report["training_and_evaluation_seconds"]=time.perf_counter()-started;reports.append(report);dump(output/"results.json",reports)
                print(json.dumps({"name":name,"selected_epoch":selected_epoch,"test_sets":report["test_sets"]}),flush=True)
    dump(output/"manifest.json",{str(p.relative_to(output)):digest(p) for p in output.rglob("*") if p.is_file()})


if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    f=sub.add_parser("freeze");f.add_argument("protocol",type=Path)
    r=sub.add_parser("run");r.add_argument("protocol",type=Path);r.add_argument("output",type=Path)
    args=p.parse_args();freeze(args.protocol) if args.action=="freeze" else run(args.protocol,args.output)
