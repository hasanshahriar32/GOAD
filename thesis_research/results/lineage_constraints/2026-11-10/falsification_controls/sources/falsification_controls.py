"""Two explicit contract counterexamples, not an accuracy benchmark."""
import argparse
from dataclasses import asdict
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

from . import engine,repair,temporal,source_faults
from .engine import Observation,TimeRange
from .temporal import TemporalNetwork,Constraint


def correlated_case():
    records=[Observation("true-issue","issuance",TimeRange(0,0),issuer="CA",request_id="1",principal="lab\\alice"),
             Observation("other-issue","issuance",TimeRange(1,1),issuer="CA",request_id="2",principal="lab\\bob"),
             Observation("auth","authentication",TimeRange(3,3),issuer="CA",serial="aa",thumbprint="ff",principal="administrator")]
    for request,serial,thumb,principal in (("1","bb","ee","lab\\alice"),("2","aa","ff","lab\\bob")):
        for repeat in range(3):records.append(Observation(f"bad-export:{request}:{repeat}","bridge",TimeRange(0,0),issuer="CA",request_id=request,serial=serial,thumbprint=thumb,principal=principal))
    mapping={r.record_id:"one-exporter-failure-domain" for r in records if r.kind=="bridge"}
    return records,mapping


def order_case():
    bounds={name:(0,3) for name in ("opened","issued","closed")}
    false=[Constraint("opened","issued",0,"sensor:opened-before-issued"),Constraint("issued","closed",0,"sensor:issued-before-closed")]
    network=TemporalNetwork(bounds,false)
    return {"latent_times":{"opened":0,"closed":1,"issued":2},"truth_overlap":False,
            "bounds":bounds,"false_order_evidence":[asdict(r) for r in false],
            "boxes_only":TemporalNetwork(bounds).overlap("opened","issued","closed"),
            "false_but_consistent_order":network.overlap("opened","issued","closed"),"network_consistent":network.consistent,
            "scope":"Declared source-truth assumption is violated; STN consistency cannot authenticate an order sensor"}


def run(output):
    output.mkdir(parents=True,exist_ok=False)
    sources=[Path(__file__)]+[Path(module.__file__) for module in (engine,repair,temporal,source_faults)]
    protocol={"declared_utc":datetime.now(timezone.utc).isoformat(),"controls":["self_consistent_false_order","six_correlated_bridge_rows_from_one_source"],
        "scope":"Deterministic falsification controls, not independent histories or enterprise detection rates",
        "source_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in sources}}
    (output/"protocol.json").write_text(json.dumps(protocol,indent=2)+"\n");(output/"sources").mkdir()
    for p in sources:(output/"sources"/p.name).write_bytes(p.read_bytes())
    records,mapping=correlated_case();small=repair.reason_with_bridge_budget(records,(),"auth",budget=2)
    sufficient=repair.reason_with_bridge_budget(records,(),"auth",budget=6)
    grouped=source_faults.reason_with_source_budget(records,(),"auth",mapping,budget=1)
    order=order_case();order["false_order_evidence"]=[{**r,"upper":str(r["upper"])} for r in order["false_order_evidence"]]
    if small.certain_issuance_id!="other-issue" or "true-issue" in small.possible_issuance_ids:raise AssertionError("Correlated control no longer exposes underspecified record budget")
    if "true-issue" not in sufficient.possible_issuance_ids or sufficient.certain_issuance_id:raise AssertionError("Sufficient record-budget reference differs")
    if "true-issue" not in grouped["possible_issuance_ids"] or grouped["certain_issuance_id"]:raise AssertionError("Source-budget uncertainty contract differs")
    if not order["network_consistent"] or order["false_but_consistent_order"]!="definite_overlap":raise AssertionError("False order control differs")
    result={"order_control":order,"correlated_source_control":{"latent_true_issuance":"true-issue","raw_anchor_truth_assumed":True,
        "faulty_source_count":1,"faulty_record_count":6,"raw_records":[asdict(r) for r in records],"source_partition":mapping,
        "record_budget_2_outside_assumption":asdict(small),"record_budget_6_within_assumption":asdict(sufficient),"source_budget_1_within_assumption":grouped,
        "scope":"One faulty source is six faulty records; budgets count different units. Grouped hypotheses require trustworthy partition metadata and do not authenticate raw anchors."}}
    (output/"results.json").write_text(json.dumps(result,indent=2)+"\n")
    (output/"manifest.json").write_text(json.dumps({str(p.relative_to(output)):hashlib.sha256(p.read_bytes()).hexdigest() for p in output.rglob("*") if p.is_file()},indent=2)+"\n")
    print(json.dumps({"false_order_accepted_as_definite":True,"record_budget_2_wrong_certain_link":small.certain_issuance_id,
        "record_budget_6_hypotheses":sufficient.hypotheses_checked,"source_budget_1_hypotheses":grouped["hypotheses_checked"],"source_budget_candidate_retention":True},indent=2))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("output",type=Path);args=p.parse_args();run(args.output)
