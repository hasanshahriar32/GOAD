"""Read-only projection of archived GOAD XML and CA CSV into observations.

The caller supplies the CA issuer namespace for this single-CA export. Clock
bounds are sensitivity assumptions, not measured synchronization guarantees.
No exploit labels are inferred from filenames, and no live lab is operated.
"""

from collections import Counter
import csv
from datetime import datetime
from pathlib import Path
import re
import xml.etree.ElementTree as ET

from .engine import LineageEngine, Observation, TimeRange


def _local(tag):
    return tag.rsplit("}", 1)[-1]


def _integer(value):
    try:
        return int(value, 0)
    except (ValueError, TypeError):
        return None


def read_trace(path: Path, issuer_namespace: str, clock_error: float = 0.0):
    content = path.read_text(encoding="utf-8-sig")
    try:
        root = ET.fromstring(content)
    except ET.ParseError:
        # Concatenated Event roots are also accepted; malformed XML still fails.
        root = ET.fromstring("<Events>" + content + "</Events>")
    events = [root] if _local(root.tag) == "Event" else [c for c in root if _local(c.tag) == "Event"]
    observations, counts = [], Counter()
    for event in events:
        system = next(c for c in event if _local(c.tag) == "System")
        meta = {_local(c.tag): c.text or "" for c in system}
        eid = meta.get("EventID", "")
        counts[eid] += 1
        if eid not in ("4887", "4768"):
            continue
        fields = {c.attrib["Name"]: c.text or "" for c in event.iter()
                  if _local(c.tag) == "Data" and "Name" in c.attrib}
        stamp = next(c.attrib["SystemTime"] for c in system if _local(c.tag) == "TimeCreated")
        timestamp = datetime.fromisoformat(stamp.replace("Z", "+00:00")).timestamp()
        record_id = ":".join((meta.get("Computer", ""), meta.get("Channel", ""), meta.get("EventRecordID", "")))
        if not meta.get("EventRecordID"):
            raise ValueError("Archived event lacks a stable record ID")
        if eid == "4887":
            template = re.search(r"(?:^|\n)CertificateTemplate:([^\r\n]+)", fields.get("Attributes", ""), re.I)
            observations.append(Observation(
                record_id, "issuance", TimeRange.around(timestamp, clock_error),
                issuer=issuer_namespace, request_id=fields.get("RequestId", ""),
                serial=fields.get("CertificateSerialNumber", ""),
                thumbprint=fields.get("CertificateThumbprint", ""), skid=fields.get("SubjectKeyIdentifier", ""),
                template=fields.get("CertificateTemplate", "") or (template.group(1) if template else ""),
                principal=fields.get("Requester", ""),
            ))
        elif any(fields.get(k) for k in ("CertSerialNumber", "CertThumbprint")):
            status = _integer(fields.get("Status"))
            observations.append(Observation(
                record_id, "authentication", TimeRange.around(timestamp, clock_error),
                issuer=fields.get("CertIssuerName", ""), serial=fields.get("CertSerialNumber", ""),
                thumbprint=fields.get("CertThumbprint", ""), principal=fields.get("TargetUserName", ""),
                success=(status == 0) if status is not None else None,
                preauth_type=_integer(fields.get("PreAuthType")),
            ))
    return observations, dict(counts)


def read_bridge(path: Path, issuer_namespace: str):
    with path.open(encoding="utf-8-sig", newline="") as source:
        for row in csv.DictReader(source):
            def value(key):
                v = row.get(key, "") or ""
                return "" if v == "EMPTY" else v
            request = value("Issued Request ID")
            yield Observation(
                f"bridge:{issuer_namespace}:{request}", "bridge", TimeRange(0, 0), issuer_namespace, request,
                value("Serial Number"), value("Certificate Hash"), value("Issued Subject Key Identifier"),
                value("Certificate Template"), value("Requester Name"),
            )


def replay_archive(directory: Path, clock_error: float = 0.0):
    issuer = "CertGraph-Lab-CA"
    bridges = list(read_bridge(directory / "srv03_ca_db_bridge.csv", issuer))
    rows = []
    for path in sorted(directory.glob("trace_*.xml")):
        records, counts = read_trace(path, issuer, clock_error)
        engine = LineageEngine()
        for record in records + bridges:
            engine.add(record)
        rows.append({
            "filename": path.name, "raw_events": sum(counts.values()), "event_counts": counts,
            "certificate_auth_records": sum(r.kind == "authentication" for r in records),
            "failed_certificate_auth_records": sum(r.kind == "authentication" and r.success is False for r in records),
            "decision_status_counts": dict(Counter(d.status for d in engine.decisions.values())),
            "decisions": [d.__dict__ for d in engine.decisions.values()],
        })
    return {
        "evidence_scope": "Archived observations only; no independently adjudicated attack labels or recall estimate.",
        "assumptions": {"single_CA_issuer_context": issuer, "clock_error_seconds_per_record": clock_error,
                        "measured_clock_bound": False, "mutation_attribution_evaluated": False},
        "traces": rows,
    }
