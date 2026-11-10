"""Detector-independent byte/CA/KDC adjudication of controlled policy trials.

Expected protocol outcomes are reported alongside observations, not used to
manufacture labels. Native RPC failures remain infrastructure outcomes.
"""

import argparse
from collections import Counter, defaultdict
import csv
import hashlib
import io
import json
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from asn1crypto.core import UTF8String
from cryptography import x509
from cryptography.hazmat.primitives import hashes


def hexkey(value):
    return "".join((value or "").split()).replace(":", "").lower().removeprefix("0x").lstrip("0") or "0"


def read(path):
    return json.loads(path.read_text())


def events(path):
    if not path.exists():
        return []
    rows = []
    for event in ET.parse(path).getroot():
        system = next(c for c in event if c.tag.rsplit("}",1)[-1] == "System")
        meta = {c.tag.rsplit("}",1)[-1]: c.text or "" for c in system}
        fields = {c.attrib["Name"]:c.text or "" for c in event.iter() if c.tag.rsplit("}",1)[-1] == "Data" and "Name" in c.attrib}
        rows.append({"event_id":int(meta["EventID"]),"id":meta["Computer"]+":"+meta["EventRecordID"],"fields":fields})
    return rows


def system_rejections(path,serial,thumbprint):
    """Require both public certificate identifiers in a KDC diagnostic."""
    if not path.exists():return []
    matched=[]
    for event in ET.parse(path).getroot():
        system=next(c for c in event if c.tag.rsplit("}",1)[-1]=="System")
        meta={c.tag.rsplit("}",1)[-1]:c.text or "" for c in system}
        providers=[c.attrib.get("Name","").casefold() for c in system if c.tag.rsplit("}",1)[-1]=="Provider"]
        if meta.get("EventID") not in ("39","40","41") or not any("kdc" in p or "kerberos-key-distribution" in p for p in providers):continue
        values={hexkey(c.text) for c in event.iter() if c.tag.rsplit("}",1)[-1]=="Data" and c.text}
        if hexkey(serial) in values and hexkey(thumbprint) in values:
            matched.append({"id":meta["Computer"]+":System:"+meta["EventRecordID"],"event_id":int(meta["EventID"])})
    return matched


def adjudicate(directory, trial):
    manifest=read(directory/"manifest.json")
    for name,expected in manifest.items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:
            raise ValueError("Trial hash mismatch: "+str(directory/name))
    outcome=read(directory/"outcome.json")
    required=("04_assigned_state.json","01_before_state.json","99_final_state.json","00_domain_context.json")
    if outcome.get("status")=="infrastructure_error" and any(not (directory/name).exists() for name in required):
        return {"trial":directory.name,"condition":trial["condition"],"expected_admin_certificate":trial["expected_admin_certificate"],
                "restored":bool(outcome.get("restored")),"observed_outcome":"infrastructure_error","error":outcome.get("error"),
                "successful_exact_certificate_use":False,"successful_administrator_use":False,"missing_setup_evidence":[name for name in required if not (directory/name).exists()]}
    assignment=json.loads(read(directory/"04_assigned_state.json")["stdout"])
    final=json.loads(read(directory/"99_final_state.json")["stdout"])
    original=json.loads(read(directory/"01_before_state.json")["stdout"])
    context=json.loads(read(directory/"00_domain_context.json")["stdout"])
    enroller_name=context.get("enroller_name","viserys.targaryen")
    enroller_sid=context.get("enroller_sid",context.get("viserys_sid"))
    requester=context.get("domain_netbios","ESSOS")+"\\"+enroller_name
    ca_name=context.get("ca_name","CertGraph-Lab-CA")
    template_name=context.get("template_name","CGPubPositive")
    mutator_name=context.get("mutator_name","khal.drogo")
    rows=events(directory/"events.xml")
    result={"trial":directory.name,"condition":trial["condition"],"expected_admin_certificate":trial["expected_admin_certificate"],
            "raw_events":len(rows),"event_ids":dict(Counter(r["event_id"] for r in rows)),
            "restored":final["name_flag"]==original["name_flag"] and outcome["restored"],
            "assigned_name_flag":assignment["name_flag"],"observed_outcome":"unverified",
            "successful_exact_certificate_use":False,"successful_administrator_use":False}
    for folder,key in (("06_certipy_find","actual_certipy_template_result"),("12_postrollback_certipy_find","actual_postrollback_certipy_template_result")):
        for path in (directory/folder).glob("*.json"):
            doc=read(path)
            if "Certificate Templates" in doc:
                for template in doc["Certificate Templates"].values():
                    if template.get("Template Name")==template_name:
                        result[key]={k:v for k,v in template.items() if k in
                            ("Template Name","Enabled","Enrollee Supplies Subject","Certificate Name Flag","Enrollment Flag","[!] Vulnerabilities","[+] User Enrollable Principals")}
    if outcome.get("native_submission_exit")==-2147023174:
        result["observed_outcome"]="infrastructure_rpc_unavailable"
        result["cleanup_error"]=outcome.get("cleanup_error")
        return result
    if outcome.get("status")=="infrastructure_error":
        result["observed_outcome"]="infrastructure_error"
        result["error"]=outcome.get("error")
        return result
    certpath=directory/"issued_certificate.cer"
    if not certpath.exists():
        result["observed_outcome"]="nonissuance_unverified"
        return result
    raw=certpath.read_bytes()
    try:cert=x509.load_der_x509_certificate(raw)
    except ValueError:cert=x509.load_pem_x509_certificate(raw)
    serial,thumb=format(cert.serial_number,"x"),cert.fingerprint(hashes.SHA1()).hex()
    upns=[]
    try:
        for item in cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value:
            if isinstance(item,x509.OtherName) and item.type_id.dotted_string=="1.3.6.1.4.1.311.20.2.3":
                upns.append(UTF8String.load(item.value).native.casefold())
    except x509.ExtensionNotFound:pass
    identity=read(directory/"certificate_identity.json")
    if hexkey(identity["serial"])!=hexkey(serial) or hexkey(identity["sha1"])!=hexkey(thumb):
        raise ValueError("Certificate identity metadata disagrees with public bytes")
    result.update(serial=serial,sha256=cert.fingerprint(hashes.SHA256()).hex(),upns=upns,
                  administrator_san_present=("administrator@"+context["dns_root"].casefold()) in upns)
    try:
        san=cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
        result["certificate_san_uris"]=san.get_values_for_type(x509.UniformResourceIdentifier)
    except x509.ExtensionNotFound:result["certificate_san_uris"]=[]
    try:
        extension=cert.extensions.get_extension_for_oid(x509.ObjectIdentifier("1.3.6.1.4.1.311.25.2")).value
        result["certificate_security_sid_values"]=sorted({s.decode("ascii") for s in re.findall(rb"S-\d-(?:\d+-)*\d+",extension.value)})
    except x509.ExtensionNotFound:result["certificate_security_sid_values"]=[]
    bridge=directory/"99_ca_bridge.json"
    ca_rows=[]
    if bridge.exists():
        stdout=read(bridge)["stdout"]
        ca_rows=[r for r in csv.DictReader(io.StringIO(stdout)) if
                 hexkey(r.get("Serial Number"))==hexkey(serial) and hexkey(r.get("Certificate Hash"))==hexkey(thumb)]
    request_ids={r.get("Issued Request ID") for r in ca_rows}
    issuance=[r for r in rows if r["event_id"]==4887 and r["fields"].get("RequestId") in request_ids
              and r["fields"].get("Requester","").casefold()==requester.casefold()]
    matching_auth=[r for r in rows if r["event_id"]==4768 and
                   hexkey(r["fields"].get("CertSerialNumber"))==hexkey(serial) and
                   hexkey(r["fields"].get("CertThumbprint"))==hexkey(thumb)]
    def principal_matches(fields):
        pairs=((context["admin_sid"],"administrator"),(enroller_sid,enroller_name.casefold()))
        return (fields.get("TargetDomainName","").casefold()==context["dns_root"].casefold() and
                any(fields.get("TargetSid")==sid and fields.get("TargetUserName","").casefold()==name for sid,name in pairs))
    successful=[r for r in matching_auth if r["fields"].get("Status") in ("0","0x0","0x00000000") and
                r["fields"].get("PreAuthType") in ("15","16","17") and
                r["fields"].get("CertIssuerName","").casefold()==ca_name.casefold() and principal_matches(r["fields"])]
    rejected=[r for r in matching_auth if r["fields"].get("Status") not in (None,"","0","0x0","0x00000000") and
              r["fields"].get("CertIssuerName","").casefold()==ca_name.casefold()]
    system_failed=system_rejections(directory/"kdc_system_events.xml",serial,thumb)
    principal_sids={r["fields"].get("TargetSid") for r in successful}
    mutator_values={r["fields"].get("AttributeValue") for r in rows if r["event_id"]==5136 and
                    r["fields"].get("ObjectDN","").casefold()==assignment["dn"].casefold() and
                    r["fields"].get("AttributeLDAPDisplayName","").casefold()=="mspki-certificate-name-flag" and
                    r["fields"].get("OperationType")=="%%14674" and
                    r["fields"].get("SubjectUserName","").casefold()==mutator_name.casefold() and
                    (r["fields"].get("SubjectUserSid")==context["mutator_sid"] if context.get("mutator_sid") else
                     r["fields"].get("SubjectUserSid","").startswith(context["domain_sid"]+"-"))}
    known_mutation_condition=trial["condition"] in ("baseline_admin_san","enabled_admin_san","benign_self_enrollment","rollback_before_enroll")
    needed_mutation=trial["condition"] in ("enabled_admin_san","benign_self_enrollment","rollback_before_enroll")
    mutation_checked=not needed_mutation or str(original["name_flag"]|1) in mutator_values
    restored_event_checked=not needed_mutation or str(original["name_flag"]) in mutator_values
    use_checked=(len(ca_rows)==1 and bool(issuance) and bool(successful))
    complete=(use_checked and result["restored"] and mutation_checked and restored_event_checked)
    admin=use_checked and context["admin_sid"] in principal_sids
    self_use=use_checked and enroller_sid in principal_sids
    result.update(matching_ca_rows=len(ca_rows),ca_issuance_event_ids=[r["id"] for r in issuance],
                  successful_kdc_event_ids=[r["id"] for r in successful],successful_target_sids=sorted(principal_sids),
                  rejected_kdc_event_ids=[r["id"] for r in rejected],
                  rejected_kdc_statuses=sorted({r["fields"]["Status"] for r in rejected}),
                  exact_certificate_kdc_system_rejections=system_failed,
                  mutation_actor_checked=mutation_checked if known_mutation_condition else None,
                  restoration_event_checked=restored_event_checked if known_mutation_condition else None,
                  controlled_mutation_chain_complete=bool(complete) if known_mutation_condition else None,
                  mutation_history_validation="legacy_condition_contract" if known_mutation_condition else "not_evaluated_for_this_condition",
                  successful_exact_certificate_use=bool(admin or self_use),successful_administrator_use=bool(admin),
                  observed_outcome="privileged_certificate_use" if admin else "self_certificate_use" if self_use else
                  "certificate_authentication_rejected" if (rejected or system_failed) and not successful and len(ca_rows)==1 and issuance else "issued_chain_incomplete")
    return result


def run(directory,output):
    if output.exists():raise FileExistsError(output)
    protocol=read(directory/"protocol.json")
    for name,expected in protocol["source_sha256"].items():
        frozen=directory/"sources"/Path(name).name
        if hashlib.sha256(frozen.read_bytes()).hexdigest()!=expected:raise ValueError("Frozen source changed")
    results=[]
    for trial in protocol["trials"]:
        path=directory/trial["id"]
        if (path/"manifest.json").exists():results.append(adjudicate(path,trial))
    by_condition=defaultdict(Counter)
    for r in results:
        by_condition[r["condition"]].update(attempts=1,restored=int(r["restored"]),
            verified_uses=int(r["successful_exact_certificate_use"]),privileged_uses=int(r["successful_administrator_use"]),
            infrastructure_errors=int(r["observed_outcome"].startswith("infrastructure_")))
    report={"scope":"Independent controlled outcome adjudication; no CIPG detector imports or enterprise-rate estimate",
            "trials_planned":len(protocol["trials"]),"trials_adjudicated":len(results),"by_condition":dict(by_condition),"trials":results,
            "adjudicator_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps(report["by_condition"],indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("directory",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args();run(args.directory,args.output)
