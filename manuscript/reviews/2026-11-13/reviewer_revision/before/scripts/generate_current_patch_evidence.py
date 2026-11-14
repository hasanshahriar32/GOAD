"""Render the measured current-patch request-form matrix in existing style."""
import hashlib
import json
from pathlib import Path
from evidence_table_layout import style_evidence_tables

from generate_lineage_evidence import table

ROOT=Path(__file__).resolve().parents[2]
RESULTS=ROOT/"thesis_research/results/lineage_constraints/2026-11-10"


def main():
    rows=[]; inputs=[]
    for form,label in (("upn","UPN"),("sid","UPN + SID URL")):
        review=RESULTS/f"current_patch_{form}_01_review"
        for name,expected in json.loads((review/"manifest.json").read_text()).items():
            if hashlib.sha256((review/name).read_bytes()).hexdigest()!=expected:raise ValueError(name)
        adjudication=review/"adjudication.json"; external=RESULTS/f"current_patch_{form}_01_external.json"
        inputs.extend([review/"manifest.json",adjudication,external,review/"provenance.json"])
        trials=json.loads(adjudication.read_text())["trials"]
        risk=json.loads(external.read_text())["by_condition"]
        for condition,short in (("baseline_admin_san","Baseline"),("enabled_admin_san","Enabled"),
                                ("rollback_before_enroll","Rollback first"),("benign_self_enrollment","Self request")):
            selected=[t for t in trials if t["condition"]==condition]
            if len(selected)!=3:raise ValueError("Incomplete current-patch cell")
            r=risk[condition]
            if r["postrollback_enumerations"]!=3:raise ValueError("Missing postrollback enumeration")
            counts=[sum(t["observed_outcome"]==value for t in selected) for value in
                    ("self_certificate_use","privileged_certificate_use","certificate_authentication_rejected")]
            if sum(counts)!=3:raise ValueError("Unadjudicated outcome")
            rows.append([label,short,*counts,r["certipy_esc1"],r["postrollback_certipy_esc1"]])
    text=table("Windows 2019 build 17763.9376: three trials per cell, with baseline restored and actual Certipy enumeration repeated before authentication. Reject denotes a certificate-bound KDC rejection; ESC1 columns are configuration findings before request and after rollback. Eighteen missing per-trial CA exports are supplemented by a separately recorded later read-only CA snapshot; original captures remain unchanged.",
               "tab:current_patch_policy","llrrrrr","Request form & Condition & Self & Admin & Reject & ESC1 pre & ESC1 post",rows)
    path=ROOT/"manuscript/generated/current_patch_evidence.tex";path.write_text(style_evidence_tables(text))
    path.with_name("current_patch_evidence_manifest.json").write_text(json.dumps({"layout_sha256": hashlib.sha256((Path(__file__).parent/"evidence_table_layout.py").read_bytes()).hexdigest(),
        "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256":{str(p.relative_to(ROOT)):hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "output_sha256":hashlib.sha256(path.read_bytes()).hexdigest()},indent=2)+"\n")


if __name__=="__main__":main()
