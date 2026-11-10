"""Artifact/latent-label audit plus independent temporal-world enumeration.

Imports neither study generator, lineage engine, repair wrapper nor STN solver.
The temporal study uses integer bounds and non-strict integer differences;
integrality supplies integer witnesses for feasibility and overlap violations.
This verifier does not certify completeness/optimality of repair candidate sets.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
from itertools import product
import json
from math import comb
from pathlib import Path


def rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def classify_by_worlds(case, orders):
    names = ("o", "i", "r")
    outcomes = []
    for values in product(*(range(case["bounds"][k][0], case["bounds"][k][1]+1) for k in names)):
        w = dict(zip(names, values))
        if all(w[c["left"]]-w[c["right"]] <= c["upper"] for c in orders):
            outcomes.append(w["o"] <= w["i"] <= w["r"])
    if not outcomes:
        return "inconsistent_evidence"
    return "definite_overlap" if all(outcomes) else "possible_overlap" if any(outcomes) else "impossible_overlap"


def verify(directory):
    manifest = json.loads((directory/"manifest.json").read_text())
    for name, expected in manifest["artifact_sha256"].items():
        assert hashlib.sha256((directory/name).read_bytes()).hexdigest() == expected, name
    protocol = json.loads((directory/"protocol.json").read_text())
    for name, expected in protocol["source_sha256"].items():
        assert hashlib.sha256((directory/"sources"/Path(name).name).read_bytes()).hexdigest() == expected
    inputs = {x["case_id"]: x for x in rows(directory/"inputs.jsonl")}
    labels = {x["case_id"]: x for x in rows(directory/"truth.jsonl")}
    assert inputs.keys() == labels.keys()
    predictions = rows(directory/"predictions.jsonl")
    aggregate, by_cell, temporal = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    seen, oracle, protected, recovery_cases = set(), {}, 0, 0
    for cid, case in inputs.items():
        label = labels[cid]
        if cid.startswith("temporal:"):
            actual = label["actual_times"]
            assert label["true_overlap"] == (actual["o"] <= actual["i"] <= actual["r"])
            assert all(case["bounds"][k][0] <= v <= case["bounds"][k][1] for k, v in actual.items())
            if not case["negative_control"]:
                assert all(actual[c["left"]]-actual[c["right"]] <= c["upper"] for c in case["orders"])
            oracle[cid] = {"interval_boxes": classify_by_worlds(case, []),
                           "interval_and_order": classify_by_worlds(case, case["orders"])}
        else:
            physical = {x["record_id"]: x for x in label["physical_certificates"]}
            selected = physical[label["selected_id"]]
            auth = next(r for r in case["records"] if r["record_id"] == case["auth_id"])
            assert label["true_id"] == (selected["record_id"] if auth["success"] else None)
            assert label["success"] == auth["success"]
            assert all(auth[k] == selected[k] for k in ("issuer", "serial", "thumbprint", "skid"))
            issuances = [r for r in case["records"] if r["kind"] == "issuance"]
            assert len(physical) == len(issuances) == case["ncert"]
            assert len({(x["issuer"], x["serial"]) for x in physical.values()}) == len(physical)
            for r in issuances:
                assert all(not r[k] or r[k] == physical[r["record_id"]][k]
                           for k in ("issuer", "serial", "thumbprint", "skid"))
            bad = 0
            for bridge in (r for r in case["records"] if r["kind"] == "bridge"):
                issue = next(r for r in issuances if (r["issuer"], r["request_id"]) == (bridge["issuer"], bridge["request_id"]))
                bad += bridge["thumbprint"] != physical[issue["record_id"]]["thumbprint"]
            assert bad == case["faults"]
    for row in predictions:
        cid, method = row["case_id"], row["method"]
        assert (cid, method) not in seen
        seen.add((cid, method))
        case, label = inputs[cid], labels[cid]
        if cid.startswith("temporal:"):
            if method in oracle[cid]:
                assert row["status"] == oracle[cid][method], (cid, method)
            else:
                assert method == "point_time"
                midpoint = {k: sum(v)/2 for k, v in case["bounds"].items()}
                assert (row["status"] == "definite_overlap") == (midpoint["o"] <= midpoint["i"] <= midpoint["r"])
            key = f"width={case['width']},order={case['observed']},negative={int(case['negative_control'])}/{method}"
            status = row["status"]
            temporal[key].update(cases=1, true_overlaps=int(label["true_overlap"]), definite=int(status == "definite_overlap"),
                correct_definite=int(status == "definite_overlap" and label["true_overlap"]),
                false_definite=int(status == "definite_overlap" and not label["true_overlap"]),
                inconsistent=int(status == "inconsistent_evidence"))
        else:
            assert method in {"bridge_budget_0", "bridge_budget_1", "bridge_budget_2", "ignore_all_bridges"}
            assert len(row["possible"]) == len(set(row["possible"]))
            bridges = {r["record_id"] for r in case["records"] if r["kind"] == "bridge"}
            if method.startswith("bridge_budget_"):
                budget = int(method.rsplit("_", 1)[1])
                assert row["hypotheses"] == sum(comb(len(bridges), k) for k in range(min(budget, len(bridges))+1))
                for witness in row["witnesses"].values():
                    assert set(witness) <= bridges and len(witness) <= budget
                if case["faults"] <= budget and label["true_id"]:
                    protected += 1
                    assert label["true_id"] in row["possible"]
            counts = Counter(cases=1, true_links=int(label["true_id"] is not None), candidates=len(row["possible"]),
                retained_true_links=int(label["true_id"] is not None and label["true_id"] in row["possible"]),
                certain_links=int(row["certain"] is not None), correct_certain_links=int(row["certain"] is not None and row["certain"] == label["true_id"]),
                false_certain_links=int(row["certain"] is not None and row["certain"] != label["true_id"]), hypotheses=row["hypotheses"])
            aggregate[method].update(counts)
            by_cell[f"faults={case['faults']},missing={case['missing']},ncert={case['ncert']}/{method}"].update(counts)
    nrepair = sum(cid.startswith("repair:") for cid in inputs)
    ntemporal = len(inputs)-nrepair
    assert len(seen) == nrepair*4 + ntemporal*3
    result = json.loads((directory/"results.json").read_text())
    assert dict(aggregate) == result["repair_aggregate"]
    assert dict(by_cell) == result["repair_by_cell"]
    assert dict(temporal) == result["temporal_by_cell"]
    return {"status": "passed", "repair_histories_checked": nrepair, "temporal_histories_checked": ntemporal,
            "prediction_rows_checked": len(seen), "temporal_oracle_queries_checked": ntemporal*2,
            "within_budget_true_link_checks": protected,
            "scope": "Independent labels/counts/hashes, complete temporal oracle on this grid, and within-budget retention; not repair-set optimality."}


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("directory", type=Path)
    print(json.dumps(verify(parser.parse_args().directory), indent=2))
