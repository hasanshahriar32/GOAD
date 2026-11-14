"""Render evidence tables using the manuscript's existing table conventions."""

from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path
from evidence_table_layout import style_evidence_tables

ROOT = Path(__file__).resolve().parents[2]
RESULTS = ROOT / "thesis_research/results/lineage_constraints/2026-11-10"


def read(name):
    return json.loads((RESULTS/name).read_text())


def table(caption, label, columns, header, rows):
    return ("\\begin{table*}[ht]\n\\centering\n\\caption{" + caption + "}\n\\label{" + label + "}\n\\small\n"
            "\\begin{tabular}{" + columns + "}\n\\toprule\n" + header + " \\\\\n\\midrule\n" +
            "\n".join(" & ".join(map(str, row)) + " \\\\" for row in rows) +
            "\n\\bottomrule\n\\end{tabular}\n\\end{table*}\n")


def main():
    for directory, key in (("confirmation", "result_sha256"), ("robustness", "artifact_sha256")):
        expected = read(directory + "/manifest.json")[key]["results.json"]
        if hashlib.sha256((RESULTS/directory/"results.json").read_bytes()).hexdigest() != expected:
            raise ValueError("Saved result hash mismatch: " + directory)
    confirmation = read("confirmation/results.json")["by_family"]["randomized_mix"]
    methods = [("legacy_or_keys", "Identifier OR"), ("issuer_serial", "Issuer--serial"),
               ("conjunctive_window300", "Conjunctive, 300 s"), ("conjunctive_point", "Conjunctive, point"),
               ("constraint_lineage", "CIPG constraint reference")]
    rows = []
    for key, label in methods:
        r = confirmation[key]
        rows.append([label, f"{100*r['edge_recall']:.2f}", f"{100*r['possible_set_recall']:.2f}",
                     r["definite_exposure_edges"]-r["false_definite_exposure_edges"], r["false_definite_exposure_edges"]])
    text = "% Generated from hash-verified saved research artifacts; do not hand-edit.\n"
    text += table("Confirmation on 2,000 synthetic histories: 1,804 true observed links and 539 true mutation overlaps. Link coverage is a percentage; overlap entries are edge counts. These are attribution outcomes, not exploit detection rates.",
                  "tab:lineage_confirmation", "lrrrr", "Method & Definite links & Possible links & True overlap & False overlap", rows)
    study = read("robustness/results.json")
    totals = defaultdict(Counter)
    for key, values in study["temporal_by_cell"].items():
        cell, method = key.split("/")
        if "negative=0" in cell:
            rate = cell.split(",")[1].split("=")[1]
            totals[(rate, method)].update(values)
    rows = []
    for rate in ("0", "0.5", "1"):
        for method, label in (("point_time", "Point time"), ("interval_boxes", "Interval boxes"), ("interval_and_order", "Intervals + observed order")):
            r = totals[(rate, method)]
            rows.append([rate, label, r["true_overlaps"], r["correct_definite"], r["false_definite"]])
    text += table("Temporal component study, 300 histories per observation rate. The order-aware method receives an additional explicit sensor channel; no cross-host ordering is inferred from record numbers. Each row is evaluated on the same cases as the other methods at that rate.",
                  "tab:order_component", "rlrrr", "Order rate & Method & True overlaps & Recovered & False claims", rows)
    rows = []
    for method, label in (("bridge_budget_0", "$k=0$"), ("bridge_budget_1", "$k=1$"), ("bridge_budget_2", "$k=2$"), ("ignore_all_bridges", "Ignore optional exports")):
        r = study["repair_aggregate"][method]
        rows.append([label, r["retained_true_links"], r["correct_certain_links"], r["false_certain_links"], r["hypotheses"]])
    text += table("Bridge-fault component study: 2,700 histories, 2,180 successful observed links. Fault counts range from zero to two; budgets below the true count include outside-assumption controls. Candidate retention and certain-link coverage are reported separately.",
                  "tab:bridge_component", "lrrrr", "Method & Retained true links & Certain true links & Wrong certain & Hypotheses", rows)
    paired_path = RESULTS/"paired_policy_external_comparison.json"
    independent_path = RESULTS/"independent_2019_external_comparison.json"
    if paired_path.exists():
        rows = []
        for os_label,source in (("2016",paired_path),("2019",independent_path)):
            if not source.exists():continue
            paired=json.loads(source.read_text())
            for condition, label in (("baseline_admin_san", "Baseline/admin request"),
                                     ("enabled_admin_san", "Subject bit enabled"),
                                     ("rollback_before_enroll", "Rollback before request"),
                                     ("benign_self_enrollment", "Legitimate self request")):
                r = paired["by_condition"][condition]
                rows.append([os_label,label,r["trials"],r["verified_privileged_uses"],r["certipy_esc1"],r["sigma_eku_rule"]])
        text += table("Paired interventions in Windows 2016 and an independent Windows 2019 forest: three blocks per environment, with identical signed administrative CSR/key within each block. All 24 certificate-use outcomes are checked and baseline readback is restored. External columns concern configuration risk on the exact template, not attack intent. The 2019 build is 17763.4974.",
                      "tab:paired_live_policy", "llrrrr", "OS & Condition & Trials & Admin uses & ESC1 & Risky EKU", rows)
    path = ROOT/"manuscript/generated/lineage_evidence.tex"
    path.parent.mkdir(exist_ok=True)
    path.write_text(style_evidence_tables(text))
    inputs = [RESULTS/"confirmation/results.json", RESULTS/"robustness/results.json"]
    if paired_path.exists():
        inputs += [paired_path]
    if independent_path.exists():inputs += [independent_path]
    (path.parent/"lineage_evidence_manifest.json").write_text(json.dumps({"layout_sha256": hashlib.sha256((Path(__file__).parent/"evidence_table_layout.py").read_bytes()).hexdigest(),
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
        "input_sha256": {str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in inputs},
        "output_sha256": hashlib.sha256(path.read_bytes()).hexdigest()}, indent=2)+"\n")
    print(path)


if __name__ == "__main__":
    main()
