"""Match external Sigma/Certipy outputs to the actual tested template object.

Configuration-risk matches and certificate-use outcomes remain separate tasks.
Matches on other loaded templates are preserved as background, not called false
positives for a rule that correctly reports risky configuration elsewhere.
"""

import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

from .adjudicate_policy_matrix import events


def run(matrix,sigma_directory,adjudication,output):
    if output.exists():raise FileExistsError(output)
    manifest=json.loads((sigma_directory/"manifest.json").read_text())
    for name,expected in manifest.items():
        if hashlib.sha256((sigma_directory/name).read_bytes()).hexdigest()!=expected:raise ValueError("External output hash mismatch")
    sigma=json.loads((sigma_directory/"results.json").read_text())
    labels={r["trial"]:r for r in json.loads(adjudication.read_text())["trials"]}
    rows=[];totals=defaultdict(Counter)
    for record in sigma["files"]:
        path=Path(record["path"])
        trial=path.parent.name
        context=json.loads(json.loads((matrix/trial/"00_domain_context.json").read_text())["stdout"])
        template=context.get("template_name","CGPubPositive")
        selected=set()
        for event in events(path):
            if event["fields"].get("TemplateInternalName")==template:
                host,rid=event["id"].rsplit(":",1)
                selected.add(host+":Security:"+rid)
        relevant={rule:sorted(set(ids)&selected) for rule,ids in record["matches"].items()}
        background={rule:len(set(ids)-selected) for rule,ids in record["matches"].items()}
        label=labels[trial]
        tool=label.get("actual_certipy_template_result",{})
        vulnerability_keys=sorted(tool.get("[!] Vulnerabilities",{}))
        row={"trial":trial,"condition":label["condition"],"assigned_name_flag":label["assigned_name_flag"],
             "sigma_tested_template_matches":relevant,"sigma_other_object_match_counts":background,
             "actual_certipy_esc1_flagged":"ESC1" in vulnerability_keys,"actual_certipy_vulnerability_keys":vulnerability_keys,
             "verified_certificate_use":label["successful_exact_certificate_use"],"verified_administrator_use":label["successful_administrator_use"]}
        rows.append(row)
        totals[label["condition"]].update(trials=1,certipy_esc1=int(row["actual_certipy_esc1_flagged"]),
            sigma_subject_rule=int(bool(relevant.get("5ee3a654-372f-11ec-8d3d-0242ac130003"))),
            sigma_eku_rule=int(bool(relevant.get("bfbd3291-de87-4b7c-88a2-d6a5deb28668"))),
            verified_privileged_uses=int(row["verified_administrator_use"]))
    result={"scope":"Executed external configuration-risk predicates on the exact tested template, separately from observed certificate use; not cross-task detection accuracy",
        "upstream_commit":sigma["upstream_commit"],"versions":sigma["versions"],"by_condition":dict(totals),"trials":rows,
        "input_sha256":{str(p):hashlib.sha256(p.read_bytes()).hexdigest() for p in (adjudication,sigma_directory/"manifest.json")},
        "analysis_source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.parent.mkdir(parents=True,exist_ok=True);output.write_text(json.dumps(result,indent=2,sort_keys=True)+"\n")
    print(json.dumps(result["by_condition"],indent=2))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("matrix",type=Path);parser.add_argument("sigma_directory",type=Path);parser.add_argument("adjudication",type=Path);parser.add_argument("output",type=Path)
    args=parser.parse_args();run(args.matrix,args.sigma_directory,args.adjudication,args.output)
