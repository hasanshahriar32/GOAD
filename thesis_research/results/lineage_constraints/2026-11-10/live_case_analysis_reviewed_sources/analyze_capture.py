"""Reconstruct an outcome-checked controlled capture and audit time assumptions."""

import argparse
from dataclasses import asdict, replace
from datetime import datetime
import hashlib
import json
from pathlib import Path
import xml.etree.ElementTree as ET

from cryptography import x509
from cryptography.x509.oid import NameOID

from scripts.capture_trace7_split_actor_delayed_pkinit import adjudicate_capture
from .clock_audit import audit_operation_bracket
from .engine import LineageEngine, MutationWindow, TimeRange
from .goad import read_bridge, read_trace


def local(tag):
    return tag.rsplit("}", 1)[-1]


def analyze(capture, inventory_path, output):
    if output.exists():
        raise FileExistsError(output)
    capture_manifest = json.loads((capture / "capture_manifest.json").read_text())
    for name, expected in capture_manifest["output_sha256"].items():
        if hashlib.sha256((capture / name).read_bytes()).hexdigest() != expected:
            raise ValueError(f"Capture artifact changed: {name}")
    if hashlib.sha256((capture / "capture_source.py").read_bytes()).hexdigest() != capture_manifest["source_sha256"]:
        raise ValueError("The frozen capture source does not match the executed-source hash")
    judgement = adjudicate_capture(capture)
    if not judgement["successful_controlled_case"] or not capture_manifest.get("original_state_restored"):
        raise ValueError("The controlled case did not pass the required outcome/restoration checks")
    inventory = json.loads(inventory_path.read_text())
    dc = inventory["hosts"]["dc03"]
    ca = inventory["hosts"]["srv03"]
    offsets = {"dc03": dc["clock_offset_intersection_seconds"], "srv03": ca["clock_offset_intersection_seconds"]}
    for bounds in offsets.values():
        if len(bounds) != 2 or bounds[0] > bounds[1]:
            raise ValueError("The inventory has inconsistent clock samples")
    templates = dc["inventory"]["templates"]
    aliases, by_dn = {}, {}
    for template in templates:
        oid = template.get("msPKI-Cert-Template-OID")
        if oid:
            for key in (template["Name"], template["DistinguishedName"], oid):
                aliases[key] = oid
            by_dn[template["DistinguishedName"].casefold()] = template
    public_bytes = (capture / "issued_certificate.cer").read_bytes()
    try:
        cert = x509.load_der_x509_certificate(public_bytes)
    except ValueError:
        cert = x509.load_pem_x509_certificate(public_bytes)
    issuer = cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
    trace_path = capture / "trace_split_actor_delayed_pkinit.xml"
    observations, event_counts = read_trace(trace_path, issuer)
    bridges = list(read_bridge(capture / "srv03_ca_db_bridge.csv", issuer))
    mutation_rows = []
    for event in ET.parse(trace_path).getroot():
        system = next(c for c in event if local(c.tag) == "System")
        meta = {local(c.tag): c.text or "" for c in system}
        if meta.get("EventID") != "5136":
            continue
        fields = {c.attrib["Name"]: c.text or "" for c in event.iter() if local(c.tag) == "Data"}
        if fields.get("AttributeLDAPDisplayName", "").casefold() != "mspki-certificate-name-flag" or fields.get("OperationType") != "%%14674":
            continue
        dn = fields.get("ObjectDN", "").casefold()
        if dn not in by_dn:
            continue
        stamp = next(c.attrib["SystemTime"] for c in system if local(c.tag) == "TimeCreated")
        mutation_rows.append({"record_id": ":".join((meta["Computer"], meta["Channel"], meta["EventRecordID"])),
                              "record_number": int(meta["EventRecordID"]), "dn": dn,
                              "timestamp": datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp(),
                              "flags": int(fields["AttributeValue"])})
    mutation_rows.sort(key=lambda r: r["record_number"])
    open_rows, pairs = {}, []
    state = {dn: int(t["msPKI-Certificate-Name-Flag"]) for dn, t in by_dn.items()}
    for row in mutation_rows:
        was_enabled = bool(state[row["dn"]] & 1)
        enabled = bool(row["flags"] & 1)
        if enabled and not was_enabled:
            open_rows[row["dn"]] = row
        elif was_enabled and not enabled and row["dn"] in open_rows:
            pairs.append((open_rows.pop(row["dn"]), row))
        state[row["dn"]] = row["flags"]

    def time_for(timestamp, source, mode):
        if mode == "point_timestamps":
            return TimeRange(timestamp, timestamp)
        if mode == "assumed_two_second_error":
            return TimeRange.around(timestamp, 2)
        lower, upper = offsets[source]
        return TimeRange(timestamp - upper, timestamp - lower)

    modes = {}
    dc_name = dc["inventory"]["computer"].casefold()
    for mode in ("point_timestamps", "assumed_two_second_error", "pre_capture_calibration_assuming_constant_offset"):
        engine = LineageEngine(aliases)
        for opened, closed in pairs:
            template = by_dn[opened["dn"]]["msPKI-Cert-Template-OID"]
            engine.add(MutationWindow("window:" + opened["record_id"], template,
                                      time_for(opened["timestamp"], "dc03", mode),
                                      time_for(closed["timestamp"], "dc03", mode),
                                      (opened["record_id"], closed["record_id"])))
        for record in observations:
            host = record.record_id.split(":", 1)[0].split(".", 1)[0].casefold()
            source = "dc03" if host == dc_name else "srv03"
            engine.add(replace(record, time=time_for(record.time.lower, source, mode)))
        for bridge in bridges:
            engine.add(bridge)
        modes[mode] = [asdict(d) for d in engine.decisions.values()]
    audits = []
    for phase, row in (("01_mutation", pairs[0][0]), ("04_rollback", pairs[0][1])) if pairs else ():
        control = json.loads((capture / f"{phase}.json").read_text())
        audit = audit_operation_bracket(row["timestamp"], control["local_before"], control["local_after"], *offsets["dc03"])
        audit.update({"phase": phase, "event_record_id": row["record_id"]})
        audits.append(audit)
    clock_compatible = bool(audits) and all(a["compatible"] for a in audits)
    result = {
        "scope": "One controlled case; not a detection-rate or external-generalization estimate",
        "outcome_adjudication": judgement, "event_counts": event_counts,
        "exact_template_inventory_mapping_used": aliases,
        "paired_template_mutation_windows": len(pairs), "conditional_reasoner_outputs": modes,
        "pre_capture_clock_model_audit": audits,
        "strict_temporal_attribution_permitted": clock_compatible,
        "timing_interpretation": ("Not falsified by these operation checks; assumptions still apply" if clock_compatible else
                                  "The pre-capture clock model is incompatible with at least one controlled operation. Conditional reasoner output must not be presented as a guaranteed timing attribution."),
        "input_sha256": {str(p): hashlib.sha256(p.read_bytes()).hexdigest() for p in
                         (capture / "capture_manifest.json", capture / "adjudication.json", trace_path, inventory_path)},
        "analysis_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    output.parent.mkdir(parents=True, exist_ok=True)
    root = Path(__file__).resolve().parents[3]
    sources = [Path(__file__), Path(__file__).with_name("engine.py"), Path(__file__).with_name("goad.py"),
               Path(__file__).with_name("clock_audit.py"), root / "scripts/capture_trace7_split_actor_delayed_pkinit.py"]
    snapshots = output.parent / (output.stem + "_sources")
    snapshots.mkdir(exist_ok=False)
    result["implementation_sha256"] = {}
    for source in sources:
        frozen = snapshots / source.name
        frozen.write_bytes(source.read_bytes())
        result["implementation_sha256"][str(source.relative_to(root))] = hashlib.sha256(frozen.read_bytes()).hexdigest()
    result["source_snapshot_directory"] = str(snapshots)
    output.write_text(json.dumps(result, indent=2, sort_keys=True) + "\n")
    print(json.dumps({"outcome_checked": judgement["successful_controlled_case"], "windows": len(pairs),
                      "strict_temporal_attribution_permitted": clock_compatible,
                      "conditional_outputs": {k: [(d["status"], d["exposure"]) for d in v] for k, v in modes.items()}}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("capture", type=Path)
    parser.add_argument("--inventory", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    analyze(args.capture, args.inventory, args.output)
