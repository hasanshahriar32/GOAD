"""Execute a versioned synthetic challenge and archived-data projection.

python -m thesis_research.src.lineage_constraints.evaluate --output <new-dir>
"""

import argparse
from collections import Counter, defaultdict
from dataclasses import asdict
import hashlib
import json
from pathlib import Path
import platform
import time

from .baselines import enriched_issuances, predict
from .engine import LineageEngine
from .goad import replay_archive
from .simulator import FAMILIES, generate_case


ROOT = Path(__file__).resolve().parents[3]
METHODS = ("legacy_or_keys", "issuer_serial", "conjunctive_point", "conjunctive_window300", "constraint_lineage")


def dump(path, value):
    path.write_text(json.dumps(value, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def metrics(counts):
    d = dict(counts)
    d["edge_precision"] = counts["correct_edges"] / counts["predicted_edges"] if counts["predicted_edges"] else None
    d["edge_recall"] = counts["correct_edges"] / counts["true_observed_edges"] if counts["true_observed_edges"] else None
    d["singleton_coverage"] = counts["singletons"] / counts["cases"] if counts["cases"] else None
    d["singleton_error_rate"] = counts["wrong_singletons"] / counts["singletons"] if counts["singletons"] else None
    d["possible_set_recall"] = counts["possible_sets_containing_truth"] / counts["true_observed_edges"] if counts["true_observed_edges"] else None
    return d


def run(output, seeds, per_family, random_per_seed):
    output.mkdir(parents=True, exist_ok=False)
    all_metrics = defaultdict(Counter)
    family_metrics = defaultdict(Counter)
    seed_metrics = defaultdict(Counter)
    random_seed_metrics = defaultdict(Counter)
    statuses = Counter()
    stream_audit = Counter()
    runtime = Counter()
    protocol = {
        "schema": 1, "seeds": seeds, "cases_per_family_per_seed": per_family, "families": FAMILIES,
        "random_mixture_cases_per_seed": random_per_seed,
        "methods": METHODS, "task": "Observed issuance-to-successful-certificate-authentication linkage",
        "scope": "Stratified synthetic challenge plus archive replay; not enterprise prevalence or attack detection accuracy.",
        "negative_control": "outside_model_forgery violates the trusted-record assumption and is excluded from the main aggregate",
        "clock_model": "Independent per-record bounded intervals; true simulated times are inside bounds except explicitly injected consistency faults.",
        "baselines": "Executed local correlation algorithms; no claim that Certipy, BloodHound, Splunk, or HADES was run.",
        "python": platform.python_version(),
    }
    dump(output / "protocol.json", protocol)
    with (output / "cases.jsonl").open("w") as inputs, (output / "labels.jsonl").open("w") as labels, (output / "predictions.jsonl").open("w") as predictions:
        for seed in seeds:
            for family in FAMILIES:
                for index in range(random_per_seed if family == "randomized_mix" else per_family):
                    case = generate_case(seed, family, index)
                    inputs.write(json.dumps({"case_id": case.case_id, "records": [asdict(r) for r in case.records],
                                             "windows": [asdict(w) for w in case.windows]}, sort_keys=True) + "\n")
                    labels.write(json.dumps({"case_id": case.case_id, "true_issuance_id": case.truth_issuance_id,
                                             "true_exposure": case.truth_exposure,
                                             "latent_truth": case.latent_truth,
                                             "assumption_violation": case.assumption_violation}, sort_keys=True) + "\n")
                    started = time.perf_counter()
                    engine = LineageEngine()
                    for window in case.windows:
                        engine.add(window)
                    retractions = 0
                    for record in case.records:
                        updates = engine.add(record)
                        retractions += sum(u.retracts_resolved_link for u in updates)
                    decision = engine.decisions[case.auth_id]
                    runtime["constraint_lineage_seconds"] += time.perf_counter() - started
                    statuses[decision.status] += 1
                    restored = LineageEngine.restore(engine.checkpoint())
                    if restored.decisions != engine.decisions:
                        raise AssertionError("Checkpoint changed decisions")
                    reverse = LineageEngine()
                    for window in case.windows:
                        reverse.add(window)
                    for record in reversed(case.records):
                        reverse.add(record)
                    if reverse.decisions != engine.decisions:
                        raise AssertionError("Arrival order changed final decisions")
                    stream_audit["checkpoint_cases_verified"] += 1
                    stream_audit["reverse_order_cases_verified"] += 1
                    stream_audit["retracted_provisional_links"] += retractions
                    for method in METHODS:
                        if method == "constraint_lineage":
                            chosen = [decision.issuance_id] if decision.status == "resolved" else []
                        else:
                            started = time.perf_counter()
                            chosen = predict(case.records, method)
                            runtime[method + "_seconds"] += time.perf_counter() - started
                        correct = int(case.truth_issuance_id is not None and case.truth_issuance_id in chosen)
                        possible_ids = list(decision.candidate_ids) if method == "constraint_lineage" else chosen
                        counts = Counter(cases=1, predicted_edges=len(chosen), correct_edges=correct,
                                         false_edges=len(chosen) - correct,
                                         true_observed_edges=int(case.truth_issuance_id is not None),
                                         singletons=int(len(chosen) == 1),
                                         wrong_singletons=int(len(chosen) == 1 and not correct))
                        counts["possible_edges"] = len(possible_ids)
                        counts["possible_sets_containing_truth"] = int(case.truth_issuance_id is not None and case.truth_issuance_id in possible_ids)
                        # Assess overclaiming of a definite mutation overlap.
                        if method == "constraint_lineage":
                            exposed = chosen if decision.exposure == "definite_overlap" else []
                        else:
                            exposed = []
                            for issue in enriched_issuances(case.records):
                                midpoint = (issue.time.lower + issue.time.upper) / 2
                                if issue.record_id in chosen and any(
                                    issue.template == w.template
                                    and (w.opened.lower + w.opened.upper) / 2 <= midpoint <= (w.closed.lower + w.closed.upper) / 2
                                    for w in case.windows):
                                    exposed.append(issue.record_id)
                        counts["definite_exposure_edges"] = len(exposed)
                        counts["false_definite_exposure_edges"] = sum(
                            not (case.truth_exposure and eid == case.truth_issuance_id) for eid in exposed)
                        family_metrics[(family, method)].update(counts)
                        if family == "randomized_mix":
                            random_seed_metrics[(seed, method)].update(counts)
                        elif not case.assumption_violation:
                            all_metrics[method].update(counts)
                            seed_metrics[(seed, method)].update(counts)
                        predictions.write(json.dumps({"case_id": case.case_id, "method": method,
                                                      "predicted_issuance_ids": chosen,
                                                      "possible_issuance_ids": possible_ids,
                                                      "status": decision.status if method == "constraint_lineage" else "baseline_edge_set",
                                                      "definite_exposure_ids": exposed}, sort_keys=True) + "\n")
    result = {
        "aggregate_excluding_forgery": {k: metrics(v) for k, v in all_metrics.items()},
        "by_family": {family: {m: metrics(family_metrics[(family, m)]) for m in METHODS} for family in FAMILIES},
        "by_seed": {str(s): {m: metrics(seed_metrics[(s, m)]) for m in METHODS} for s in seeds},
        "randomized_by_seed": {str(s): {m: metrics(random_seed_metrics[(s, m)]) for m in METHODS} for s in seeds},
        "constraint_statuses_including_negative_control": dict(statuses),
        "stream_audit": dict(stream_audit), "execution_wall_seconds_by_method": dict(runtime),
    }
    dump(output / "results.json", result)
    archive = ROOT / "thesis_research/data/live_goad_traces"
    dump(output / "goad_point_time.json", replay_archive(archive, clock_error=0))
    dump(output / "goad_two_second_bounds.json", replay_archive(archive, clock_error=2))
    source_files = list(Path(__file__).parent.glob("*.py"))
    source_files += list(archive.glob("trace_*.xml")) + [archive / "srv03_ca_db_bridge.csv"]
    dump(output / "manifest.json", {"sha256": {
        str(p.relative_to(ROOT)): hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(source_files)
    }, "result_sha256": {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in sorted(output.iterdir()) if p.is_file()}})
    print(json.dumps(result["aggregate_excluding_forgery"], indent=2))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", nargs="+", type=int, default=[101, 211, 307, 401, 503])
    parser.add_argument("--per-family", type=int, default=40)
    parser.add_argument("--random-per-seed", type=int, default=400)
    args = parser.parse_args()
    if args.per_family < 1 or args.random_per_seed < 1 or len(set(args.seeds)) != len(args.seeds):
        parser.error("Use positive case counts and distinct seeds")
    run(args.output.resolve(), args.seeds, args.per_family, args.random_per_seed)


if __name__ == "__main__":
    main()
