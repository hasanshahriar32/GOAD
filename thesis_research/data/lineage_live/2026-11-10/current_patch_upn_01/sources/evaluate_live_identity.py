"""Evaluate identity linkage/divergence from logs, CA exports and SID evidence.

Detector inputs exclude public issued-certificate bytes, private keys, expected
outcomes, and adjudicator labels. This identity-only ablation intentionally makes
no audit-clock or necessary-causation claim. Outcome labels are read only after
predictions have been computed.
"""

import argparse
from collections import Counter,defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import time

from .adjudicate_policy_matrix import events
from .engine import LineageEngine,Observation,TimeRange,text
from .goad import read_trace


def identity_prediction(path):
    context=json.loads(json.loads((path/"00_domain_context.json").read_text())["stdout"])
    issuer=context.get("ca_name","CertGraph-Lab-CA")
    raw_events=events(path/"events.xml")
    records,counts=read_trace(path/"events.xml",issuer)
    # _profiles performs scoped enrichment without looking at event time.
    aliases={}
    policy_path=path/"04_assigned_state.json"
    if policy_path.exists():
        policy=json.loads(json.loads(policy_path.read_text())["stdout"])
        name=context.get("template_name","CGPubPositive")
        # Use the collected directory object's explicit OID/name mapping. An
        # unexplained template-name disagreement must still cause abstention.
        if policy.get("template_oid") and policy.get("dn","").casefold().startswith("cn="+name.casefold()+","):
            aliases[policy["template_oid"]]=name
    engine=LineageEngine(aliases)
    engine.records={r.record_id:r for r in records}
    bridge_stdout=json.loads((path/"99_ca_bridge.json").read_text())["stdout"]
    for row in csv.DictReader(io.StringIO(bridge_stdout)):
        request=row.get("Issued Request ID")
        if not request:continue
        r=Observation("bridge:"+issuer+":"+request,"bridge",TimeRange(0,0),issuer,request,
                      row.get("Serial Number", ""),row.get("Certificate Hash", ""),template=row.get("Certificate Template", ""),principal=row.get("Requester Name", ""))
        engine.records[r.record_id]=r
    aliases=defaultdict(set);alias_evidence=defaultdict(list)
    for event in raw_events:
        fields=event["fields"]
        if event["event_id"]==4624 and fields.get("TargetUserSid") and fields.get("TargetDomainName") and fields.get("TargetUserName"):
            alias=text(fields["TargetDomainName"]+"\\"+fields["TargetUserName"])
            aliases[alias].add(fields["TargetUserSid"]);alias_evidence[alias].append(event["id"])
    profiles=engine._profiles()
    raw_auth={r["id"]:r["fields"] for r in raw_events if r["event_id"]==4768}
    predictions=[]
    for auth in records:
        if auth.kind!="authentication" or auth.success is not True or auth.preauth_type not in (15,16,17):continue
        a=auth.identity();candidates=[];conflicts=[]
        for profile in profiles:
            fields=profile.fields
            if a["issuer"] and fields["issuer"] and a["issuer"] not in fields["issuer"]:continue
            mismatch=any(a[k] and fields[k] and a[k] not in fields[k] for k in a)
            shared={k for k in ("serial","thumbprint","skid") if a[k] and a[k] in fields[k]}
            if profile.conflict:
                if shared or not mismatch:conflicts.append(profile.issuance.record_id)
                continue
            if mismatch:continue
            strong="thumbprint" in shared or ("serial" in shared and bool(a["issuer"] and fields["issuer"]))
            candidates.append((profile,strong))
        p={"auth_id":auth.record_id,"identity_candidates":[v[0].issuance.record_id for v in candidates],
           "status":"identity_unresolved","privileged_identity_divergence":None,"temporal_attribution":"not_evaluated"}
        if len(candidates)==1 and candidates[0][1] and not conflicts:
            profile=candidates[0][0]
            raw_id=auth.record_id.replace(":Security:",":")
            target_sid=raw_auth[raw_id].get("TargetSid")
            requester=text(profile.principal)
            known=aliases.get(requester,set())
            p.update(status="unique_identity_link",issuance_id=profile.issuance.record_id,requester_sid_candidates=sorted(known),
                     requester_alias_evidence=alias_evidence.get(requester,[]),target_sid=target_sid)
            if len(known)==1 and target_sid:
                requester_sid=next(iter(known))
                p["privileged_identity_divergence"]=bool(target_sid==context["admin_sid"] and requester_sid!=target_sid)
            else:p["principal_status"]="insufficient_or_conflicting_sid_evidence"
        predictions.append(p)
    return predictions,len(records)


def run(matrix,adjudication,output):
    if output.exists():raise FileExistsError(output)
    predictions=[];runtime=[]
    for path in sorted(matrix.glob("r*")):
        if not (path/"events.xml").exists() or not (path/"99_ca_bridge.json").exists():continue
        started=time.perf_counter();rows,count=identity_prediction(path)
        predictions.extend({"trial":path.name,**r} for r in rows)
        runtime.append({"trial":path.name,"input_projection_and_reasoning_seconds":time.perf_counter()-started,"certificate_records":count})
    # Read outcome labels only after all detector predictions exist.
    labels={r["trial"]:r for r in json.loads(adjudication.read_text())["trials"]}
    counts=Counter()
    for p in predictions:
        label=labels[p["trial"]]
        auth_id=p["auth_id"].replace(":Security:",":")
        if auth_id not in label.get("successful_kdc_event_ids",[]):continue
        counts["outcome_checked_authentications"]+=1
        counts["unique_identity_links"]+=p["status"]=="unique_identity_link"
        predicted=p["privileged_identity_divergence"]
        if predicted is None:counts["principal_abstentions"]+=1
        elif predicted:
            counts["correct_privileged_divergences" if label["successful_administrator_use"] else "false_privileged_divergences"]+=1
        elif label["successful_administrator_use"]:counts["missed_privileged_divergences"]+=1
        else:counts["correct_nonprivileged_outcomes"]+=1
    result={"scope":"Log/CA-export/SID identity-only ablation; no timing, necessary-causation, or attack-intent guarantee",
            "counts":dict(counts),"predictions":predictions,"timing":runtime,
            "detector_inputs":"events.xml, CA database stdout, observed directory template OID/name mapping and domain Admin SID; public certificate/CSR and outcome labels excluded from inference",
            "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
            "adjudication_sha256":hashlib.sha256(adjudication.read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result["counts"],indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("matrix",type=Path);parser.add_argument("adjudication",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args();run(args.matrix,args.adjudication,args.output)
