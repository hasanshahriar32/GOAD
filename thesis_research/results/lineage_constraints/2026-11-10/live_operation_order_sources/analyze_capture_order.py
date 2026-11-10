"""Controlled operation-order reconstruction, separate from audit-clock claims.

The channel is the frozen synchronous test orchestrator, not an ordering inferred
from CA/DC timestamps. This pilot result must not be presented as a passive-log
detector result or as proof of a necessary enabling configuration change.
"""

import argparse
import ast
import hashlib
import json
from pathlib import Path

from scripts.capture_trace7_split_actor_delayed_pkinit import adjudicate_capture
from .temporal import Constraint, TemporalNetwork


def analyze(capture, output):
    if output.exists():
        raise FileExistsError(output)
    manifest = json.loads((capture/"capture_manifest.json").read_text())
    for name, expected in manifest["output_sha256"].items():
        if hashlib.sha256((capture/name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Capture artifact changed: {name}")
    source = (capture/"capture_source.py").read_bytes()
    if hashlib.sha256(source).hexdigest() != manifest["source_sha256"]:
        raise ValueError("Executed-source hash mismatch")
    judgement = adjudicate_capture(capture)
    if not judgement["successful_controlled_case"] or not manifest.get("original_state_restored"):
        raise ValueError("An outcome-checked and restored controlled case is required")
    tree = ast.parse(source)
    function = next(n for n in tree.body if isinstance(n, ast.FunctionDef) and n.name == "run_capture")
    phases = []
    for statement in function.body:
        if isinstance(statement, ast.Assign) and isinstance(statement.value, ast.Call):
            call = statement.value
            if isinstance(call.func, ast.Name) and call.func.id == "checked_ps":
                phases.append(call.args[1].value)
    required = ["01_mutation", "02_csr", "03_submission", "04_rollback"]
    if phases[:4] != required:
        raise ValueError("The frozen source is outside the reviewed sequential capture protocol")
    steps = {name: json.loads((capture/f"{name}.json").read_text()) for name in required}
    if any(s["returncode"] != 0 for s in steps.values()):
        raise ValueError("A controlled phase failed")
    if "MUTATED" not in steps["01_mutation"]["stdout"] or "ROLLED_BACK" not in steps["04_rollback"]["stdout"]:
        raise ValueError("The control phases lack their success markers")
    # Effective operation variables have no Windows audit-time bounds at all.
    bounds = dict.fromkeys(("open", "submit_start", "issue", "submit_complete", "rollback_start", "close"))
    constraints = [
        Constraint("open", "submit_start", 0, "01_mutation:return-before-03_submission:invoke"),
        Constraint("submit_start", "issue", 0, "03_submission:synchronous-issuance-lower"),
        Constraint("issue", "submit_complete", 0, "03_submission:synchronous-issued-response"),
        Constraint("submit_complete", "rollback_start", 0, "03_submission:return-before-04_rollback:invoke"),
        Constraint("rollback_start", "close", 0, "04_rollback:synchronous-effective-write"),
    ]
    network = TemporalNetwork(bounds, constraints)
    status = network.overlap("open", "issue", "close")
    ablation = {}
    for edge in constraints:
        ablation[edge.evidence_id] = TemporalNetwork(bounds, [c for c in constraints if c != edge]).overlap("open", "issue", "close")
    result = {
        "scope": "One controlled operation-order pilot; additional orchestration evidence, not passive audit telemetry",
        "outcome_checked": True, "restoration_checked": True,
        "certificate_serial": judgement["certificate_identity"]["serial"],
        "ca_issuance_records": judgement["matching_ca_issuance_events"],
        "successful_kdc_records": judgement["matching_successful_kdc_events"],
        "operation_order_overlap": status,
        "clock_alignment_repaired": False,
        "necessary_enabling_mutation_established": False,
        "assumptions": [
            "The frozen synchronous orchestrator and saved responses truthfully describe this execution.",
            "Successful Set-ADObject return bounds the effective write on the tested DC.",
            "The exact new certificate was issued inside the synchronous certreq submission, not reused from an earlier request.",
            "The observed mutation and rollback correspond to the reviewed commands; no unseen intervening state change is ruled out globally.",
            "This establishes ordering of the controlled operations, not when the CA consumed template policy or whether the mutation was necessary.",
        ],
        "reviewed_source_phase_sequence": phases,
        "constraints": [{"left": c.left, "right": c.right, "upper": str(c.upper), "evidence_id": c.evidence_id} for c in constraints],
        "leave_one_order_edge_out": ablation,
        "capture_manifest_sha256": hashlib.sha256((capture/"capture_manifest.json").read_bytes()).hexdigest(),
        "executed_source_sha256": manifest["source_sha256"],
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    snapshots = output.parent/(output.stem+"_sources")
    snapshots.mkdir(exist_ok=False)
    root = Path(__file__).resolve().parents[3]
    sources = [Path(__file__), Path(__file__).with_name("temporal.py"), root/"scripts/capture_trace7_split_actor_delayed_pkinit.py"]
    result["analysis_sources_sha256"] = {}
    for path in sources:
        (snapshots/path.name).write_bytes(path.read_bytes())
        result["analysis_sources_sha256"][str(path.relative_to(root))] = hashlib.sha256(path.read_bytes()).hexdigest()
    output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps({k: result[k] for k in ("outcome_checked", "operation_order_overlap", "clock_alignment_repaired", "necessary_enabling_mutation_established")}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path); parser.add_argument("output", type=Path)
    args = parser.parse_args(); analyze(args.capture, args.output)
