"""Frozen, equal-input identity/revision comparison with executed SQLite.

This tests a relational implementation boundary, not a full external PIDS.
Synthetic histories and prefix perturbations are not enterprise-rate estimates.
"""
import argparse
from collections import Counter,defaultdict
from dataclasses import asdict,replace
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import random
import sqlite3
import time

from .engine import LineageEngine,TimeRange
from .simulator import FAMILIES,generate_case
from .sql_lineage import SQLiteLineage

ROOT=Path(__file__).resolve().parents[3]


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,value):path.write_text(json.dumps(value,indent=2,sort_keys=True)+"\n")


def freeze(path):
    if path.exists():raise FileExistsError(path)
    sources=[Path(__file__),Path(__file__).with_name("sql_lineage.py"),Path(__file__).with_name("engine.py"),Path(__file__).with_name("simulator.py")]
    dump(path,{"schema":1,"declared_utc":datetime.now(timezone.utc).isoformat(),"seeds":[72019,73009,74017],
        "cases_per_named_family":20,"random_cases_per_seed":150,"families":list(FAMILIES),
        "projection":"Same canonical identity observations; all event intervals set to [0,0], no mutation windows, no temporal/exposure claims",
        "prefixes":"Seeded shuffled delivery; then remove/re-add one optional bridge if present; every prefix compared",
        "methods":["constraint_identity","sql_strong_join","sql_guarded"],
        "scope":"Equal-input relational identity and revision comparison; not HADES/Splunk execution, new independent generator, or a deployment-frequency estimate",
        "source_sha256":{str(p.relative_to(ROOT)):sha(p) for p in sources}})


def key(decisions,engine=False):
    return {aid:(d.status,tuple(d.candidate_ids if engine else d.candidates),d.issuance_id) for aid,d in decisions.items()}


def run(protocol_path,output):
    protocol=json.loads(protocol_path.read_text())
    for name,expected in protocol["source_sha256"].items():
        if sha(ROOT/name)!=expected:raise ValueError("Frozen source changed: "+name)
    output.mkdir(parents=True,exist_ok=False);dump(output/"protocol.json",protocol)
    snapshots=output/"sources";snapshots.mkdir()
    for name in protocol["source_sha256"]:(snapshots/Path(name).name).write_bytes((ROOT/name).read_bytes())
    totals=defaultdict(Counter);runtime=Counter();comparisons=0;case_count=0
    with (output/"cases.jsonl").open("w") as cases,(output/"predictions.jsonl").open("w") as predictions:
        for seed in protocol["seeds"]:
            for family in protocol["families"]:
                count=protocol["random_cases_per_seed"] if family=="randomized_mix" else protocol["cases_per_named_family"]
                for index in range(count):
                    case=generate_case(seed,family,index);case_count+=1
                    records=[replace(r,time=TimeRange(0,0)) for r in case.records]
                    rng=random.Random(f"sql-delivery:{seed}:{family}:{index}");rng.shuffle(records)
                    steps=[("add",r) for r in records]
                    optional=next((r for r in records if r.kind=="bridge"),None)
                    if optional:steps += [("remove",optional),("add",optional)]
                    cases.write(json.dumps({"case_id":case.case_id,"family":family,"seed":seed,
                        "assumption_violation":case.assumption_violation,"truth_issuance_id":case.truth_issuance_id,
                        "latent_truth":case.latent_truth,"steps":[{"operation":op,"record":asdict(r)} for op,r in steps]},sort_keys=True)+"\n")
                    engine=LineageEngine();sqls={"sql_strong_join":SQLiteLineage("strong_join"),"sql_guarded":SQLiteLineage("guarded")}
                    previous={m:{} for m in protocol["methods"]};observed={}
                    try:
                        for step,(operation,record) in enumerate(steps):
                            if operation=="add":observed[record.record_id]=record
                            else:observed.pop(record.record_id,None)
                            started=time.perf_counter()
                            getattr(engine,operation)(record if operation=="add" else record.record_id)
                            runtime["constraint_identity"]+=time.perf_counter()-started
                            outputs={"constraint_identity":key(engine.decisions,True)}
                            for method,sql in sqls.items():
                                started=time.perf_counter();decisions=getattr(sql,operation)(record if operation=="add" else record.record_id)
                                runtime[method]+=time.perf_counter()-started;outputs[method]=key(decisions)
                            if outputs["constraint_identity"]!=outputs["sql_guarded"]:raise AssertionError("Guarded SQL and reference differ: "+case.case_id)
                            comparisons+=len(outputs["constraint_identity"])
                            for method,values in outputs.items():
                                for aid,(status,candidates,chosen) in values.items():
                                    old=previous[method].get(aid)
                                    retracted=bool(old and old[0]=="resolved" and (status!="resolved" or old[2]!=chosen))
                                    row={"case_id":case.case_id,"step":step,"method":method,"auth_id":aid,"status":status,
                                        "candidates":candidates,"issuance_id":chosen,"retracts_resolved_link":retracted,
                                        "true_issuance_observed":case.truth_issuance_id in observed}
                                    predictions.write(json.dumps(row,sort_keys=True)+"\n")
                                    if step==len(steps)-1:
                                        group="outside_assumption" if case.assumption_violation else "main"
                                        totals[(group,method)].update(cases=1,resolved=int(status=="resolved"),
                                            correct_certain=int(chosen is not None and chosen==case.truth_issuance_id),
                                            wrong_certain=int(chosen is not None and chosen!=case.truth_issuance_id),
                                            successful_truth=int(case.truth_issuance_id is not None),
                                            candidate_retained=int(case.truth_issuance_id is not None and case.truth_issuance_id in candidates))
                                    totals[("prefix",method)].update(decisions=1,retractions=int(retracted),
                                        wrong_certain_with_true_issue_observed=int(chosen is not None and chosen!=case.truth_issuance_id and case.truth_issuance_id in observed))
                                previous[method]=values
                    finally:
                        for sql in sqls.values():sql.close()
    result={"cases":case_count,"prefix_decision_equivalence_checks":comparisons,"guarded_query_matches_reference_every_prefix":True,
        "by_group_method":{group+"/"+method:dict(values) for (group,method),values in totals.items()},
        "total_inference_seconds":dict(runtime),"sqlite_version":sqlite3.sqlite_version,"scope":protocol["scope"]}
    dump(output/"results.json",result)
    dump(output/"manifest.json",{str(p.relative_to(output)):sha(p) for p in output.rglob("*") if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();sub=p.add_subparsers(dest="action",required=True)
    f=sub.add_parser("freeze");f.add_argument("protocol",type=Path)
    r=sub.add_parser("run");r.add_argument("protocol",type=Path);r.add_argument("output",type=Path)
    args=p.parse_args()
    if args.action=="freeze":freeze(args.protocol)
    else:run(args.protocol,args.output)
