"""Whole-source deletion hypotheses for correlated optional export failures.

The caller supplies an explicit failure-domain partition for every bridge row.
File copies are not independent sources. Raw CA/KDC anchors remain trusted.
All hypotheses, including unresolved and contradictory retained sets, contribute
to uncertainty; no world is discarded merely to obtain a certain answer.
"""
from itertools import combinations
from math import comb

from .engine import LineageEngine


def reason_with_source_budget(records,windows,auth_id,source_by_bridge,budget=1,max_hypotheses=10000):
    if type(budget) is not int or budget<0:raise ValueError("Nonnegative source fault budget required")
    records=tuple(records);windows=tuple(windows)
    ids=[r.record_id for r in records]
    if len(ids)!=len(set(ids)):raise ValueError("Duplicate observation IDs")
    bridges={r.record_id for r in records if r.kind=="bridge"}
    if set(source_by_bridge)!=bridges or any(not isinstance(v,str) or not v for v in source_by_bridge.values()):
        raise ValueError("Every optional bridge needs exactly one explicit failure-domain label")
    groups=sorted(set(source_by_bridge.values()))
    count=sum(comb(len(groups),n) for n in range(min(budget,len(groups))+1))
    if count>max_hypotheses:raise ValueError("Declared source hypotheses exceed limit")
    outcomes=[];witnesses={}
    for n in range(min(budget,len(groups))+1):
        for dropped in combinations(groups,n):
            engine=LineageEngine();engine.records={r.record_id:r for r in records if r.kind!="bridge" or source_by_bridge[r.record_id] not in dropped}
            engine.windows={w.record_id:w for w in windows};engine.recompute()
            if auth_id not in engine.decisions:raise ValueError("Requested authentication absent")
            decision=engine.decisions[auth_id]
            for candidate in decision.candidate_ids:witnesses.setdefault(candidate,list(dropped))
            outcomes.append({"dropped_sources":list(dropped),"status":decision.status,"issuance_id":decision.issuance_id,"candidate_ids":list(decision.candidate_ids)})
    initial=outcomes[0]["issuance_id"]
    certain=initial if initial and all(r["status"]=="resolved" and r["issuance_id"]==initial for r in outcomes) else None
    return {"status":"certain_link" if certain else "uncertain","certain_issuance_id":certain,"possible_issuance_ids":sorted(witnesses),
            "candidate_source_witnesses":witnesses,"hypotheses_checked":len(outcomes),"source_groups":groups,"outcomes":outcomes}
