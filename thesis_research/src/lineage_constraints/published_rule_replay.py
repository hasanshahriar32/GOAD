"""SQLite semantic proxy for a published SAN/principal association analytic.

This is NOT a Splunk execution or an exact SPL runtime reproduction. It exposes
required fields and candidate associations, with unsupported multivalue records
reported explicitly. It neither treats the published analytic as a certificate
identity proof nor assigns attack labels to archived scenario names.
"""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sqlite3
import xml.etree.ElementTree as ET

ROOT = Path(__file__).resolve().parents[3]
SOURCE = "https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/"


def read_events(path):
    raw = path.read_text(encoding="utf-8-sig")
    try:
        root = ET.fromstring(raw)
    except ET.ParseError:
        root = ET.fromstring("<Events>"+raw+"</Events>")
    events = [root] if root.tag.rsplit("}", 1)[-1] == "Event" else list(root)
    rows = []
    for event in events:
        system = next(c for c in event if c.tag.rsplit("}", 1)[-1] == "System")
        meta = {c.tag.rsplit("}", 1)[-1]: c.text or "" for c in system}
        fields = {c.attrib["Name"]: c.text or "" for c in event.iter()
                  if c.tag.rsplit("}", 1)[-1] == "Data" and "Name" in c.attrib}
        rows.append({"event_id": meta["EventID"], "record_id": meta["Computer"]+":"+meta["EventRecordID"], "fields": fields})
    return rows


def replay(events, normalize_principal=False):
    """Candidate-set proxy, without SPL max=1 truncation or search scheduling."""
    ca, kdc, unsupported = [], [], []
    for event in events:
        fields, rid = event["fields"], event["record_id"]
        if event["event_id"] == "4887":
            attrs = fields.get("Attributes", "")
            if not re.search(r"SAN:.*upn", attrs, re.I | re.S) or "certificatetemplate:" not in attrs.casefold():
                continue
            names = re.findall(r"upn=([^\r\n&]+)", attrs, re.I)[:10]
            if len(names) != 1:
                unsupported.append(rid)
                continue
            name = names[0].lower()
            if normalize_principal:
                name = name.split("@", 1)[0].rsplit("\\", 1)[-1]
            ca.append((rid, name))
        elif event["event_id"] == "4768" and fields.get("CertThumbprint"):
            name = fields.get("TargetUserName", "")
            if normalize_principal:
                name = name.lower().split("@", 1)[0].rsplit("\\", 1)[-1]
            kdc.append((rid, name, fields.get("Status", "")))
    with sqlite3.connect(":memory:") as db:
        db.executescript("CREATE TABLE ca(id TEXT, principal TEXT); CREATE TABLE kdc(id TEXT, principal TEXT, status TEXT);")
        db.executemany("INSERT INTO ca VALUES (?,?)", ca)
        db.executemany("INSERT INTO kdc VALUES (?,?,?)", kdc)
        pairs = [dict(zip(("issuance_record_id", "auth_record_id", "auth_status"), row)) for row in
                 db.execute("SELECT ca.id,kdc.id,kdc.status FROM ca JOIN kdc ON ca.principal=kdc.principal ORDER BY ca.id,kdc.id")]
    return {"eligible_issuances": len(ca), "certificate_auth_records": len(kdc), "pairs": pairs,
            "unsupported_multivalue_or_missing_upn_records": unsupported}


def run(output):
    if output.exists():
        raise FileExistsError(output)
    paths = sorted((ROOT/"thesis_research/data/live_goad_traces").glob("trace_*.xml"))
    paths.append(ROOT/"thesis_research/data/lineage_live/2026-11-10/split_actor_02/trace_split_actor_delayed_pkinit.xml")
    result = {
        "source": {"url": SOURCE, "analytic_id": "f0306acf-a6ab-437a-bbc6-8628f8d5c97e", "version_checked": 10,
                   "updated": "2026-05-13", "accessed": "2026-11-10"},
        "scope": "Published-rule candidate association proxy in SQLite; NOT Splunk execution or attack detection accuracy",
        "implemented_conditions": ["4887 with textual SAN/UPN and template attribute", "4768 with certificate thumbprint", "principal string association"],
        "differences": ["Candidate-set output: no join max=1 truncation, runtime scheduling, macros, or risk actions",
                        "Multivalue UPN records are excluded and listed, rather than guessing SPL semantics",
                        "The separate normalized-principal mode is an explicit adaptation, not the published query",
                        "This analytic's association objective differs from exact certificate linkage; no overall precision/recall comparison is inferred"],
        "files": [],
        "source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),
    }
    for path in paths:
        events = read_events(path)
        result["files"].append({"path": str(path.relative_to(ROOT)), "input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                                "raw_events": len(events), "literal_principal_proxy": replay(events),
                                "normalized_principal_adaptation": replay(events, True)})
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(result, indent=2, sort_keys=True)+"\n")
    print(json.dumps([{ "path": row["path"], "eligible": row["literal_principal_proxy"]["eligible_issuances"],
                       "literal_pairs": len(row["literal_principal_proxy"]["pairs"]),
                       "adapted_pairs": len(row["normalized_principal_adaptation"]["pairs"])} for row in result["files"]], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(); parser.add_argument("output", type=Path)
    run(parser.parse_args().output)
