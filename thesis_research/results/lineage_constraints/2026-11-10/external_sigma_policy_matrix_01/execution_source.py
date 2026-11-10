"""Execute unmodified upstream Sigma rules using actual pySigma/SQLite code.

Run in the isolated tools environment with pysigma-backend-sqlite installed.
Rule matches are event predicates, not independently adjudicated attack labels.
"""

import argparse
from datetime import datetime, timezone
import hashlib
import importlib.metadata
import json
from pathlib import Path
import shutil
import sqlite3
import subprocess
import time
import xml.etree.ElementTree as ET

from sigma.collection import SigmaCollection
from sigma.backends.sqlite import sqliteBackend
import yaml

ROOT = Path(__file__).resolve().parents[3]
RULES = (
    "win_security_adcs_certificate_template_configuration_vulnerability.yml",
    "win_security_adcs_certificate_template_configuration_vulnerability_eku.yml",
    "win_security_petitpotam_susp_tgt_request.yml",
)


def digest(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def flatten(path):
    content = path.read_text(encoding="utf-8-sig")
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        root = ET.fromstring("<Events>"+content+"</Events>")
    events = [root] if root.tag.rsplit("}", 1)[-1] == "Event" else list(root)
    result = []
    for event in events:
        if event.tag.rsplit("}", 1)[-1] != "Event":
            continue
        system = next(c for c in event if c.tag.rsplit("}", 1)[-1] == "System")
        record = {c.tag.rsplit("}", 1)[-1]: c.text or "" for c in system}
        record.update({c.attrib["Name"]: c.text or "" for c in event.iter()
                       if c.tag.rsplit("}", 1)[-1] == "Data" and "Name" in c.attrib})
        record["EventID"] = int(record["EventID"])
        record["evidence_id"] = ":".join(record.get(k, "") for k in ("Computer", "Channel", "EventRecordID"))
        result.append(record)
    return result


def quoted(field):
    return '"'+field.replace('"', '""')+'"'


def evaluate(records, compiled, fields):
    fields = sorted(set(fields) | {k for r in records for k in r})
    with sqlite3.connect(":memory:") as db:
        db.execute("CREATE TABLE logs ("+",".join(quoted(k) for k in fields)+")")
        db.executemany("INSERT INTO logs VALUES ("+",".join("?" for _ in fields)+")",
                       [[r.get(k) for k in fields] for r in records])
        matches = {}
        for rid, queries in compiled.items():
            selected = set()
            for query in queries:
                cursor = db.execute(query)
                names = [c[0] for c in cursor.description]
                for row in cursor:
                    selected.add(dict(zip(names, row))["evidence_id"])
            matches[rid] = sorted(selected)
        return matches


def run(checkout, output, paths):
    output.mkdir(parents=True, exist_ok=False)
    frozen = output/"upstream_rules"
    frozen.mkdir()
    commit = subprocess.check_output(["git", "-C", str(checkout), "rev-parse", "HEAD"], text=True).strip()
    if subprocess.check_output(["git", "-C", str(checkout), "status", "--porcelain"]):
        raise ValueError("The upstream rules checkout has local modifications")
    compiled, metadata, fields = {}, [], {"evidence_id"}
    for name in RULES:
        path = checkout/"rules/windows/builtin/security"/name
        raw = path.read_text()
        spec = yaml.safe_load(raw)
        collection = SigmaCollection.from_yaml(raw)
        queries = sqliteBackend(table="logs", collate_nocase=True).convert(collection)
        compiled[spec["id"]] = queries
        fields |= set(collection.rules[0].detection.detections[k].detection_items[j].field
                      for k in collection.rules[0].detection.detections
                      for j in range(len(collection.rules[0].detection.detections[k].detection_items))
                      if hasattr(collection.rules[0].detection.detections[k].detection_items[j], "field")
                      and collection.rules[0].detection.detections[k].detection_items[j].field)
        shutil.copyfile(path, frozen/name)
        metadata.append({"id": spec["id"], "title": spec["title"], "status": spec.get("status"),
                         "sha256": digest(path), "path": str(path.relative_to(checkout)), "queries": queries})
    for path in checkout.glob("LICENSE*"):
        if path.is_file():
            shutil.copyfile(path, frozen/path.name)
    # Execution/mapping controls are separate from real evidence and scores.
    controls = [
        {"evidence_id": "fixture:subject", "EventID": 4898, "TemplateContent": "CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT"},
        {"evidence_id": "fixture:eku", "EventID": 4899, "NewTemplateContent": "CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT 1.3.6.1.5.5.7.3.2"},
        {"evidence_id": "fixture:machine", "EventID": 4768, "TargetUserName": "DC03$", "CertThumbprint": "aa", "IpAddress": "192.0.2.1"},
        {"evidence_id": "fixture:local", "EventID": 4768, "TargetUserName": "DC03$", "CertThumbprint": "aa", "IpAddress": "::1"},
        {"evidence_id": "fixture:human", "EventID": 4768, "TargetUserName": "user", "CertThumbprint": "aa", "IpAddress": "192.0.2.1"},
    ]
    control_matches = evaluate(controls, compiled, fields)
    expected = {
        "5ee3a654-372f-11ec-8d3d-0242ac130003": ["fixture:eku", "fixture:subject"],
        "bfbd3291-de87-4b7c-88a2-d6a5deb28668": ["fixture:eku"],
        "6a53d871-682d-40b6-83e0-b7c1a6c4e3a5": ["fixture:machine"],
    }
    if control_matches != expected:
        raise AssertionError({"expected": expected, "actual": control_matches})
    results = []
    for path in paths:
        started = time.perf_counter()
        records = flatten(path)
        loaded = time.perf_counter()
        matches = evaluate(records, compiled, fields)
        results.append({"path": str(path), "input_sha256": digest(path), "events": len(records),
                        "event_ids_present": sorted({r["EventID"] for r in records}), "matches": matches,
                        "xml_projection_seconds": loaded-started, "query_and_load_seconds": time.perf_counter()-loaded})
    result = {
        "scope": "Actual upstream Sigma rules converted by actual pySigma SQLite backend and executed by SQLite; event-predicate matches, not attack recall",
        "upstream": "https://github.com/SigmaHQ/sigma", "upstream_commit": commit,
        "executed_utc": datetime.now(timezone.utc).isoformat(), "rules": metadata,
        "mapping": "Raw XML System/EventData fields, EventID as integer, absent rule fields NULL; SQLite ASCII case-insensitive comparison enabled",
        "versions": {name: importlib.metadata.version(name) for name in ("pysigma", "pysigma-backend-sqlite", "PyYAML")},
        "sqlite_version": sqlite3.sqlite_version, "execution_controls": {"passed": True, "matches": control_matches},
        "files": results, "source_sha256": digest(Path(__file__)),
        "task_boundaries": ["Template rules require 4898/4899 telemetry; absence is a coverage gap, not proof of a missed applicable detection",
                            "The machine-account rule is scoped to machine targets; human Administrator authentication is not its intended target",
                            "These are Sigma/SQLite runs, not Splunk or HADES executions"],
    }
    (output/"results.json").write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    subprocess.run(["uv", "pip", "freeze", "--python", __import__("sys").executable], stdout=(output/"dependencies.txt").open("w"), check=True)
    (output/"execution_source.py").write_bytes(Path(__file__).read_bytes())
    manifest = {str(p.relative_to(output)): digest(p) for p in sorted(output.rglob("*")) if p.is_file()}
    (output/"manifest.json").write_text(json.dumps(manifest, indent=2)+"\n")
    print(json.dumps({"rules": len(metadata), "files": len(results), "execution_controls": "passed",
                      "total_real_event_matches": sum(len(ids) for r in results for ids in r["matches"].values())}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--checkout", type=Path, required=True); parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--xml", nargs="*", type=Path)
    args = parser.parse_args()
    paths = args.xml or sorted((ROOT/"thesis_research/data/live_goad_traces").glob("trace_*.xml")) + [ROOT/"thesis_research/data/lineage_live/2026-11-10/split_actor_02/trace_split_actor_delayed_pkinit.xml"]
    run(args.checkout, args.output, paths)
