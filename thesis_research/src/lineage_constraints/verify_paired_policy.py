"""Independent signed-input and matched-policy checks for live interventions.

This verifies concrete controlled contrasts. It does not generalize necessity
to other templates, patch levels, principals, or policy configurations.
"""

import argparse
from collections import defaultdict
import hashlib
import json
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def read(path):return json.loads(path.read_text())


def verify(directory,judgement,output):
    if output.exists():raise FileExistsError(output)
    adjudication=read(judgement)
    blocks=defaultdict(dict)
    trials={r["trial"]:r for r in adjudication["trials"]}
    verified_requests=[]
    for path in sorted(directory.glob("r*")):
        binding_path=path/"request_binding.json"
        if not binding_path.exists() or path.name not in trials:continue
        binding=read(binding_path)
        raw=(path/"request.csr").read_bytes()
        if hashlib.sha256(raw).hexdigest()!=binding["request_sha256"]:raise ValueError("CSR hash differs")
        request=x509.load_pem_x509_csr(raw)
        # Explicit verification records the actual CSR hash algorithm. Legacy
        # Windows certreq defaults to SHA-1; do not call it SHA-256 evidence.
        request.public_key().verify(request.signature,request.tbs_certrequest_bytes,padding.PKCS1v15(),request.signature_hash_algorithm)
        certificate_bytes=(path/"issued_certificate.cer").read_bytes()
        try:certificate=x509.load_der_x509_certificate(certificate_bytes)
        except ValueError:certificate=x509.load_pem_x509_certificate(certificate_bytes)
        fmt=serialization.PublicFormat.SubjectPublicKeyInfo
        csr_key=request.public_key().public_bytes(serialization.Encoding.DER,fmt)
        if csr_key!=certificate.public_key().public_bytes(serialization.Encoding.DER,fmt):raise ValueError("Issued certificate key differs from fixed CSR")
        verified_requests.append({"trial":path.name,"csr_sha256":binding["request_sha256"],
            "csr_signature_hash":request.signature_hash_algorithm.name,"rsa_signature_verified":True,
            "certificate_public_key_matches_request":True})
        context=json.loads(read(path/"00_domain_context.json")["stdout"])
        if binding["requested_upn"].casefold()!="administrator@"+context["dns_root"].casefold():continue
        policy=json.loads(read(path/"04_assigned_state_effective_policy.json")["stdout"])
        condition=trials[path.name]["condition"]
        blocks[binding["block"]][condition]={"trial":path.name,"csr":binding["request_sha256"],
            "public_key_sha256":hashlib.sha256(csr_key).hexdigest(),"policy":policy,"adjudication":trials[path.name]}
    results=[]
    required={"baseline_admin_san","enabled_admin_san","rollback_before_enroll"}
    for block,values in sorted(blocks.items()):
        if set(values)!=required:
            results.append({"block":block,"complete":False,"conditions_present":sorted(values)})
            continue
        same_request=len({v["csr"] for v in values.values()})==1
        same_key=len({v["public_key_sha256"] for v in values.values()})==1
        other_policies=[{k:v for k,v in row["policy"].items() if k!="name_flag"} for row in values.values()]
        same_policy=all(p==other_policies[0] for p in other_policies)
        original=values["baseline_admin_san"]["policy"]["name_flag"]
        one_bit=(values["enabled_admin_san"]["policy"]["name_flag"]==(original|1) and
                 values["rollback_before_enroll"]["policy"]["name_flag"]==original and not original&1)
        outcomes={k:v["adjudication"]["observed_outcome"] for k,v in values.items()}
        supported=(same_request and same_key and same_policy and one_bit and
            outcomes["enabled_admin_san"]=="privileged_certificate_use" and
            outcomes["baseline_admin_san"]==outcomes["rollback_before_enroll"]=="self_certificate_use")
        results.append({"block":block,"complete":True,"identical_signed_request":same_request,"identical_public_key":same_key,
            "other_recorded_effective_policy_fields_equal":same_policy,"single_name_flag_bit_intervention":one_bit,
            "observed_outcomes":outcomes,"controlled_necessity_supported":bool(supported),
            "scope":"Necessity for this privileged certificate outcome under the matched recorded inputs and controlled cache protocol only"})
    report={"scope":"Signed CSR/key and recorded policy verification; conditional matched intervention evidence, not universal policy causality",
            "adjudication_input_sha256":hashlib.sha256(judgement.read_bytes()).hexdigest(),
            "request_checks":verified_requests,"blocks":results,"complete_blocks":sum(r["complete"] for r in results),
            "supported_controlled_contrasts":sum(r.get("controlled_necessity_supported",False) for r in results),
            "verifier_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(report,indent=2,sort_keys=True)+"\n")
    print(json.dumps({k:report[k] for k in ("complete_blocks","supported_controlled_contrasts")},indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("directory",type=Path);parser.add_argument("adjudication",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args();verify(args.directory,args.adjudication,args.output)
