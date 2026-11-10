"""Frozen factorial studies of bridge faults and independently observed order.

These are controlled component studies, not a new Windows testbed. This generator
does not import the earlier simulator. Latent truth is saved separately from
the detector input. Earlier confirmation cases are used only as a labeled
post-hoc diagnostic and are never called a fresh holdout for the new method.
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import random
import time

from .engine import Observation, TimeRange
from .repair import reason_with_bridge_budget
from .temporal import Constraint, TemporalNetwork

ROOT = Path(__file__).resolve().parents[3]


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n")


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def restore(raw):
    return Observation(**{**raw, "time": TimeRange(**raw["time"])})


def freeze(path, per_cell):
    if path.exists():
        raise FileExistsError(path)
    sources = [Path(__file__), Path(__file__).with_name("engine.py"),
               Path(__file__).with_name("repair.py"), Path(__file__).with_name("temporal.py")]
    protocol = {
        "schema": 1, "declared_utc": datetime.now(timezone.utc).isoformat(),
        "seeds": [7103, 8111, 9109, 10111, 11113], "per_cell_per_seed": per_cell,
        "repair_grid": {"certificates": [1, 4, 8], "missing_raw_thumbprint_probability": [0, 0.5, 1],
                        "corrupt_target_bridge_records": [0, 1, 2], "budgets": [0, 1, 2]},
        "temporal_grid": {"interval_width": [0, 2, 5], "order_observation_probability": [0, 0.5, 1],
                          "negative_control": [False, True]},
        "repair_task": "Trusted raw issuance/KDC records; up to k faulty optional bridge records, not k faulty sources",
        "temporal_task": "Integer-bounded continuous-time component study; observed order is an additional input channel",
        "scope": "Locally frozen synthetic study; no external registration, enterprise prevalence, or Windows generalization claim",
        "source_sha256": {str(p.relative_to(ROOT)): digest(p) for p in sources},
    }
    path.parent.mkdir(parents=True, exist_ok=True)
    dump(path, protocol)


def repair_case(seed, index, ncert, missing, faults):
    rng = random.Random(f"independent-fault-grid:{seed}:{index}:{ncert}:{missing}:{faults}")
    cid = f"repair:{seed}:{ncert}:{missing}:{faults}:{index}"
    target = rng.randrange(ncert)
    records, physical = [], []
    for j in range(ncert):
        issuer, serial = f"ca-{j // 3}", f"{j % 3 + 1:x}"
        thumb, skid = f"{j + 20:040x}", f"{j % 2 + 80:040x}"
        rid = f"{cid}:i{j}"
        issue = Observation(rid, "issuance", TimeRange(10 + j, 10 + j), issuer, str(j + 1),
                            serial if rng.random() > 0.3 else "", thumb if rng.random() >= missing else "", skid,
                            "template", f"user{j}")
        physical.append({"record_id": rid, "issuer": issuer, "serial": serial, "thumbprint": thumb, "skid": skid})
        records.append(issue)
        exported = f"{900 + j:040x}" if j == target and faults else thumb
        bridge = Observation(f"{cid}:b{j}", "bridge", TimeRange(0, 0), issuer, str(j + 1), serial, exported, skid, "template", f"user{j}")
        records.append(bridge)
        if j == target and faults == 2:
            records.append(Observation(f"{cid}:b{j}-copy", "bridge", TimeRange(0, 0), issuer, str(j + 1), serial, exported, skid, "template", f"user{j}"))
    selected = physical[target]
    auth = Observation(cid + ":a", "authentication", TimeRange(30, 30), selected["issuer"],
                       serial=selected["serial"], thumbprint=selected["thumbprint"], skid=selected["skid"], success=rng.random() >= 0.2)
    records.append(auth)
    rng.shuffle(records)
    return {"case_id": cid, "records": [asdict(r) for r in records], "auth_id": auth.record_id,
            "ncert": ncert, "missing": missing, "faults": faults}, {
        "case_id": cid, "physical_certificates": physical, "selected_id": selected["record_id"],
        "success": auth.success, "true_id": selected["record_id"] if auth.success else None}


def temporal_case(seed, index, width, observed, negative):
    rng = random.Random(f"independent-order-grid:{seed}:{index}:{width}:{observed}:{negative}")
    cid = f"temporal:{seed}:{width}:{observed}:{int(negative)}:{index}"
    opened, closed = sorted((rng.randrange(7), rng.randrange(7)))
    actual = {"o": opened, "i": rng.randrange(7), "r": closed}
    bounds = {k: [max(0, v-rng.randrange(width+1)), min(6, v+rng.randrange(width+1))] for k, v in actual.items()}
    edges = []
    # This simulates an independent operation-order channel. It is not an edge
    # inferred by sorting reported timestamps or by reading truth at inference.
    for a, b in (("o", "i"), ("i", "r"), ("o", "r")):
        if rng.random() < observed:
            earlier, later = (a, b) if actual[a] <= actual[b] else (b, a)
            edges.append({"left": earlier, "right": later, "upper": 0, "evidence_id": f"observed-order:{a}:{b}", "strict": False})
    if negative:
        # Explicit false sensor: positive cycle contradiction independent of the
        # random sample, so abstention is testable even at zero order coverage.
        edges += [{"left": "o", "right": "i", "upper": -1, "evidence_id": "bad-sensor:1", "strict": False},
                  {"left": "i", "right": "o", "upper": -1, "evidence_id": "bad-sensor:2", "strict": False}]
    return {"case_id": cid, "bounds": bounds, "orders": edges, "width": width,
            "observed": observed, "negative_control": negative}, {
        "case_id": cid, "actual_times": actual, "true_overlap": opened <= actual["i"] <= closed}


def count_repair(counter, label, possible, certain, hypotheses):
    true_id = label["true_id"]
    counter.update(cases=1, true_links=int(true_id is not None), candidates=len(possible),
                   retained_true_links=int(true_id is not None and true_id in possible),
                   certain_links=int(certain is not None),
                   correct_certain_links=int(certain is not None and certain == true_id),
                   false_certain_links=int(certain is not None and certain != true_id),
                   hypotheses=hypotheses)


def run(protocol_path, output):
    protocol = json.loads(protocol_path.read_text())
    for name, expected in protocol["source_sha256"].items():
        if digest(ROOT / name) != expected:
            raise ValueError(f"Frozen source changed: {name}")
    output.mkdir(parents=True, exist_ok=False)
    dump(output / "protocol.json", protocol)
    snapshots = output / "sources"
    snapshots.mkdir()
    for name in protocol["source_sha256"]:
        (snapshots / Path(name).name).write_bytes((ROOT/name).read_bytes())
    aggregate, by_cell, temporal_counts = defaultdict(Counter), defaultdict(Counter), defaultdict(Counter)
    started = time.perf_counter()
    with (output/"inputs.jsonl").open("w") as inputs, (output/"truth.jsonl").open("w") as truths, (output/"predictions.jsonl").open("w") as predictions:
        def save(handle, row):
            handle.write(json.dumps(row, sort_keys=True) + "\n")
        for seed in protocol["seeds"]:
            grid = protocol["repair_grid"]
            for ncert in grid["certificates"]:
                for missing in grid["missing_raw_thumbprint_probability"]:
                    for faults in grid["corrupt_target_bridge_records"]:
                        for index in range(protocol["per_cell_per_seed"]):
                            case, label = repair_case(seed, index, ncert, missing, faults)
                            save(inputs, case); save(truths, label)
                            records = [restore(r) for r in case["records"]]
                            previous_candidates = set()
                            for budget in grid["budgets"]:
                                d = reason_with_bridge_budget(records, (), case["auth_id"], budget)
                                assert previous_candidates <= set(d.possible_issuance_ids)
                                previous_candidates = set(d.possible_issuance_ids)
                                method = f"bridge_budget_{budget}"
                                row = {"case_id": case["case_id"], "method": method, "possible": d.possible_issuance_ids,
                                       "certain": d.certain_issuance_id, "hypotheses": d.hypotheses_checked,
                                       "witnesses": d.candidate_witnesses}
                                save(predictions, row)
                                cell = f"faults={faults},missing={missing},ncert={ncert}/{method}"
                                count_repair(aggregate[method], label, row["possible"], row["certain"], row["hypotheses"])
                                count_repair(by_cell[cell], label, row["possible"], row["certain"], row["hypotheses"])
                                if faults <= budget and label["true_id"]:
                                    assert label["true_id"] in row["possible"], "Within-budget retention failed"
                            # Strong information-ablation comparator: discard all
                            # optional exports rather than tolerating k faults.
                            d = reason_with_bridge_budget([r for r in records if r.kind != "bridge"], (), case["auth_id"], 0)
                            row = {"case_id": case["case_id"], "method": "ignore_all_bridges", "possible": d.possible_issuance_ids,
                                   "certain": d.certain_issuance_id, "hypotheses": 1, "witnesses": d.candidate_witnesses}
                            save(predictions, row)
                            count_repair(aggregate[row["method"]], label, row["possible"], row["certain"], 1)
                            count_repair(by_cell[f"faults={faults},missing={missing},ncert={ncert}/{row['method']}"], label, row["possible"], row["certain"], 1)
            grid = protocol["temporal_grid"]
            for width in grid["interval_width"]:
                for observed in grid["order_observation_probability"]:
                    for negative in grid["negative_control"]:
                        for index in range(protocol["per_cell_per_seed"]):
                            case, label = temporal_case(seed, index, width, observed, negative)
                            save(inputs, case); save(truths, label)
                            for method in ("point_time", "interval_boxes", "interval_and_order"):
                                if method == "point_time":
                                    mid = {k: sum(v)/2 for k, v in case["bounds"].items()}
                                    status = "definite_overlap" if mid["o"] <= mid["i"] <= mid["r"] else "impossible_overlap"
                                else:
                                    orders = [Constraint(**c) for c in case["orders"]] if method == "interval_and_order" else []
                                    network = TemporalNetwork(case["bounds"], orders)
                                    status = network.overlap("o", "i", "r")
                                save(predictions, {"case_id": case["case_id"], "method": method, "status": status})
                                key = f"width={width},order={observed},negative={int(negative)}/{method}"
                                temporal_counts[key].update(cases=1, true_overlaps=int(label["true_overlap"]),
                                    definite=int(status == "definite_overlap"),
                                    correct_definite=int(status == "definite_overlap" and label["true_overlap"]),
                                    false_definite=int(status == "definite_overlap" and not label["true_overlap"]),
                                    inconsistent=int(status == "inconsistent_evidence"))
    result = {"scope": protocol["scope"], "repair_aggregate": dict(aggregate), "repair_by_cell": dict(by_cell),
              "temporal_by_cell": dict(temporal_counts), "wall_seconds": time.perf_counter()-started}
    dump(output/"results.json", result)
    dump(output/"manifest.json", {"protocol_file_sha256": digest(protocol_path),
        "artifact_sha256": {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob('*')) if p.is_file()}})
    print(json.dumps({"repair": result["repair_aggregate"], "wall_seconds": result["wall_seconds"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    sub = parser.add_subparsers(dest="action", required=True)
    f = sub.add_parser("freeze"); f.add_argument("protocol", type=Path); f.add_argument("--per-cell", type=int, default=20)
    r = sub.add_parser("run"); r.add_argument("protocol", type=Path); r.add_argument("output", type=Path)
    args = parser.parse_args()
    if args.action == "freeze":
        if args.per_cell < 1:
            parser.error("Positive per-cell count required")
        freeze(args.protocol, args.per_cell)
    else:
        run(args.protocol, args.output)
