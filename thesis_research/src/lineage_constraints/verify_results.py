"""Independent audit of saved labels/projections and aggregate edge metrics.

This script imports no detector or simulator. It recomputes randomized labels
from saved latent histories and checks claimed metrics against per-case output.
"""

import argparse
from collections import Counter, defaultdict
import hashlib
import json
from pathlib import Path


def read_rows(path):
    return [json.loads(line) for line in path.read_text().splitlines() if line.strip()]


def verify(directory):
    result = json.loads((directory / "results.json").read_text())
    protocol = json.loads((directory / "protocol.json").read_text())
    inputs = {r["case_id"]: r for r in read_rows(directory / "cases.jsonl")}
    labels = {r["case_id"]: r for r in read_rows(directory / "labels.jsonl")}
    if set(inputs) != set(labels):
        raise AssertionError("Input/label case IDs differ")
    independently_checked = 0
    for cid, label in labels.items():
        latent = label["latent_truth"]
        if not latent:
            continue
        certificates = {c["record_id"]: c for c in latent["physical_certificates"]}
        selected = certificates[latent["selected_issuance_id"]]
        window = latent["mutation_window"]
        expected_id = selected["record_id"] if latent["authentication_succeeded"] else None
        expected_exposure = bool(latent["authentication_succeeded"] and selected["template"] == window["template"]
                                 and window["opened_at"] <= selected["issued_at"] <= window["closed_at"])
        if (label["true_issuance_id"], label["true_exposure"]) != (expected_id, expected_exposure):
            raise AssertionError("Saved random-case label does not follow latent history")
        keys = {(c["issuer"], c["serial"]) for c in certificates.values()}
        if len(keys) != len(certificates):
            raise AssertionError("Simulator reused a serial inside one issuer")
        for record in inputs[cid]["records"]:
            if record["kind"] == "issuance":
                actual = certificates[record["record_id"]]["issued_at"]
            elif record["kind"] == "authentication":
                actual = latent["authenticated_at"]
            else:
                continue
            if not record["time"]["lower"] <= actual <= record["time"]["upper"]:
                raise AssertionError("Physical event lies outside the supplied clock bounds")
        independently_checked += 1

    totals = defaultdict(Counter)
    by_family = defaultdict(Counter)
    seen = set()
    for row in read_rows(directory / "predictions.jsonl"):
        cid, method = row["case_id"], row["method"]
        if (cid, method) in seen:
            raise AssertionError("Duplicate prediction row")
        seen.add((cid, method))
        label = labels[cid]
        predicted = row["predicted_issuance_ids"]
        if len(set(predicted)) != len(predicted):
            raise AssertionError("Duplicate predicted edges")
        correct = int(label["true_issuance_id"] is not None and label["true_issuance_id"] in predicted)
        counts = Counter(cases=1, predicted_edges=len(predicted), correct_edges=correct,
                         false_edges=len(predicted) - correct, true_observed_edges=int(label["true_issuance_id"] is not None),
                         singletons=int(len(predicted) == 1), wrong_singletons=int(len(predicted) == 1 and not correct),
                         definite_exposure_edges=len(row["definite_exposure_ids"]),
                         false_definite_exposure_edges=sum(not (label["true_exposure"] and eid == label["true_issuance_id"])
                                                          for eid in row["definite_exposure_ids"]))
        counts["possible_edges"] = len(row["possible_issuance_ids"])
        counts["possible_sets_containing_truth"] = int(label["true_issuance_id"] is not None and label["true_issuance_id"] in row["possible_issuance_ids"])
        family = cid.split(":")[1]
        by_family[(family, method)].update(counts)
        if not label["assumption_violation"] and family != "randomized_mix":
            totals[method].update(counts)
    if len(seen) != len(inputs) * len(protocol["methods"]):
        raise AssertionError("Incomplete method/case coverage")
    for method, counts in totals.items():
        for key, value in counts.items():
            if result["aggregate_excluding_forgery"][method][key] != value:
                raise AssertionError(f"Aggregate mismatch: {method}/{key}")
    for (family, method), counts in by_family.items():
        for key, value in counts.items():
            if result["by_family"][family][method][key] != value:
                raise AssertionError(f"Family mismatch: {family}/{method}/{key}")
    manifest = json.loads((directory / "manifest.json").read_text())
    for name, expected in manifest["result_sha256"].items():
        if hashlib.sha256((directory / name).read_bytes()).hexdigest() != expected:
            raise AssertionError(f"Output hash mismatch: {name}")
    return {"cases_checked": len(inputs), "prediction_rows_checked": len(seen),
            "independent_random_history_labels_checked": independently_checked, "status": "passed"}


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    print(json.dumps(verify(parser.parse_args().directory), indent=2))
