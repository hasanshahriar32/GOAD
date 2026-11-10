"""Evidence-consistent certificate lineage with revisable, bounded-time claims.

This is a research prototype. 'Resolved' means uniquely supported among the
recorded candidates under declared clock bounds, not cryptographic attestation
or proof of a malicious Windows exploit. No external dependencies are required.
"""

from dataclasses import asdict, dataclass, field
import json
import math
from typing import Optional


def text(value: str) -> str:
    return (value or "").strip().casefold()


def hex_key(value: str, *, serial: bool = False) -> str:
    key = "".join((value or "").split()).replace(":", "").lower()
    if key.startswith("0x"):
        key = key[2:]
    if key and any(c not in "0123456789abcdef" for c in key):
        raise ValueError(f"Non-hexadecimal certificate identifier: {value!r}")
    return (key.lstrip("0") or "0") if serial and key else key


@dataclass(frozen=True)
class TimeRange:
    lower: float
    upper: float

    def __post_init__(self):
        if not (math.isfinite(self.lower) and math.isfinite(self.upper)) or self.lower > self.upper:
            raise ValueError("Time bounds must be finite and ordered")

    @classmethod
    def around(cls, timestamp: float, error: float = 0.0):
        if error < 0:
            raise ValueError("Clock error must be nonnegative")
        return cls(timestamp - error, timestamp + error)


@dataclass(frozen=True)
class Observation:
    record_id: str
    kind: str  # issuance, authentication, or bridge
    time: TimeRange
    issuer: str = ""
    request_id: str = ""
    serial: str = ""
    thumbprint: str = ""
    skid: str = ""
    template: str = ""
    principal: str = ""
    success: Optional[bool] = True
    preauth_type: Optional[int] = 16

    def __post_init__(self):
        if not self.record_id or self.kind not in {"issuance", "authentication", "bridge"}:
            raise ValueError("A record needs an ID and a supported kind")
        hex_key(self.serial, serial=True)
        hex_key(self.thumbprint)
        hex_key(self.skid)

    def identity(self) -> dict:
        return {"issuer": text(self.issuer), "serial": hex_key(self.serial, serial=True),
                "thumbprint": hex_key(self.thumbprint), "skid": hex_key(self.skid)}


@dataclass(frozen=True)
class MutationWindow:
    record_id: str
    template: str
    opened: TimeRange
    closed: TimeRange
    evidence_ids: tuple[str, ...] = ()

    def __post_init__(self):
        if not self.record_id or not self.template or self.opened.lower > self.closed.upper:
            raise ValueError("A mutation window needs an exact object and a feasible interval")


@dataclass(frozen=True)
class Decision:
    auth_id: str
    status: str
    issuance_id: Optional[str] = None
    candidate_ids: tuple[str, ...] = ()
    evidence_ids: tuple[str, ...] = ()
    exposure: str = "unresolved"
    window_ids: tuple[str, ...] = ()
    principal_divergence: Optional[bool] = None


@dataclass(frozen=True)
class DecisionUpdate:
    previous: Optional[Decision]
    current: Decision

    @property
    def retracts_resolved_link(self):
        return self.previous is not None and self.previous.status == "resolved" and (
            self.current.status != "resolved" or self.current.issuance_id != self.previous.issuance_id)


@dataclass
class _Profile:
    issuance: Observation
    fields: dict[str, set[str]]
    template: str
    principal: str
    evidence: set[str] = field(default_factory=set)
    conflict: bool = False


class LineageEngine:
    """Maintain conservative lineage decisions as evidence arrives or is removed.

    Recomputing after each update is intentional in this correctness prototype.
    Decisions are relative to retained evidence; there is no completeness claim
    about records that were never collected. Records are retained until removed.
    """

    def __init__(self, template_aliases: Optional[dict[str, str]] = None):
        self.records: dict[str, Observation] = {}
        self.windows: dict[str, MutationWindow] = {}
        self.decisions: dict[str, Decision] = {}
        self.template_aliases = {text(k): text(v) for k, v in (template_aliases or {}).items()}

    def _template(self, value: str) -> str:
        return self.template_aliases.get(text(value), text(value))

    def add(self, record: Observation | MutationWindow) -> list[DecisionUpdate]:
        target = self.windows if isinstance(record, MutationWindow) else self.records
        old = target.get(record.record_id)
        if old is not None and old != record:
            raise ValueError(f"Conflicting payload for immutable record ID {record.record_id}")
        if old == record:
            return []
        target[record.record_id] = record
        return self.recompute()

    def remove(self, record_id: str) -> list[DecisionUpdate]:
        self.records.pop(record_id, None)
        self.windows.pop(record_id, None)
        self.decisions.pop(record_id, None)
        return self.recompute()

    def _profiles(self) -> list[_Profile]:
        bridge_index: dict[tuple[str, str], list[Observation]] = {}
        for record in self.records.values():
            if record.kind == "bridge" and record.issuer and record.request_id:
                bridge_index.setdefault((text(record.issuer), record.request_id), []).append(record)
        profiles = []
        for issuance in sorted(self.records.values(), key=lambda r: r.record_id):
            if issuance.kind != "issuance" or issuance.success is not True:
                continue
            profile = _Profile(issuance, {k: {v} if v else set() for k, v in issuance.identity().items()},
                               self._template(issuance.template), text(issuance.principal), {issuance.record_id})
            for bridge in bridge_index.get((text(issuance.issuer), issuance.request_id), []):
                for name, value in bridge.identity().items():
                    if value:
                        profile.fields[name].add(value)
                for name, value in (("template", self._template(bridge.template)),
                                    ("principal", text(bridge.principal))):
                    existing = getattr(profile, name)
                    if existing and value and existing != value:
                        profile.conflict = True
                    elif value:
                        setattr(profile, name, value)
                profile.evidence.add(bridge.record_id)
            profile.conflict |= any(len(values) > 1 for values in profile.fields.values())
            profiles.append(profile)
        return profiles

    def _exposure(self, profile: _Profile) -> tuple[str, tuple[str, ...], tuple[str, ...]]:
        if not profile.template:
            return "unknown_template", (), ()
        possible, definite = [], []
        issue_time = profile.issuance.time
        for window in self.windows.values():
            if self._template(window.template) != profile.template:
                continue
            if window.opened.lower <= issue_time.upper and issue_time.lower <= window.closed.upper:
                possible.append(window)
                if window.opened.upper <= issue_time.lower and issue_time.upper <= window.closed.lower:
                    definite.append(window)
        chosen = definite or possible
        state = "definite_overlap" if definite else ("possible_overlap" if possible else "no_observed_overlap")
        ids = tuple(sorted(w.record_id for w in chosen))
        evidence = tuple(sorted({e for w in chosen for e in w.evidence_ids}))
        return state, ids, evidence

    def _decide(self, auth: Observation, profiles: list[_Profile]) -> Decision:
        if auth.success is not True:
            return Decision(auth.record_id, "failed_or_unknown_authentication")
        if auth.preauth_type not in (15, 16, 17):
            return Decision(auth.record_id, "not_certificate_authentication")
        identity = auth.identity()
        identifiers_missing = not any(identity[k] for k in ("serial", "thumbprint", "skid"))
        candidates: list[tuple[_Profile, bool, bool]] = []
        conflicts = []
        for profile in profiles:
            fields = profile.fields
            # A known issuer mismatch rules out even an equal serial.
            if identity["issuer"] and fields["issuer"] and identity["issuer"] not in fields["issuer"]:
                continue
            shared = {k for k in ("serial", "thumbprint", "skid")
                      if identity[k] and identity[k] in fields[k]}
            if profile.issuance.time.lower > auth.time.upper:
                continue
            mismatch = any(identity[k] and fields[k] and identity[k] not in fields[k]
                           for k in ("issuer", "serial", "thumbprint", "skid"))
            if profile.conflict:
                if shared or not mismatch:
                    conflicts.append(profile.issuance.record_id)
                continue
            if mismatch:
                continue
            # An incomplete, non-contradicted issuance remains a weak candidate;
            # absence of its identifiers must not manufacture uniqueness.
            # SKID identifies a key and can be reused across renewed certificates.
            strong = "thumbprint" in shared or ("serial" in shared and bool(identity["issuer"] and fields["issuer"]))
            definite_time = profile.issuance.time.upper <= auth.time.lower
            candidates.append((profile, strong, definite_time))
        candidate_ids = tuple(sorted({p.issuance.record_id for p, _, _ in candidates} | set(conflicts)))
        if conflicts:
            return Decision(auth.record_id, "conflicting_evidence", candidate_ids=candidate_ids)
        if not candidates:
            return Decision(auth.record_id, "no_consistent_candidate")
        if identifiers_missing:
            return Decision(auth.record_id, "missing_identifiers", candidate_ids=candidate_ids)
        if len(candidates) > 1:
            return Decision(auth.record_id, "ambiguous", candidate_ids=candidate_ids)
        profile, strong, definite_time = candidates[0]
        if not strong:
            return Decision(auth.record_id, "insufficient_identity", candidate_ids=candidate_ids)
        if not definite_time:
            return Decision(auth.record_id, "uncertain_order", candidate_ids=candidate_ids)
        exposure, windows, window_evidence = self._exposure(profile)
        evidence = tuple(sorted(profile.evidence | {auth.record_id} | set(window_evidence)))
        divergence = (profile.principal != text(auth.principal)) if profile.principal and auth.principal else None
        return Decision(auth.record_id, "resolved", profile.issuance.record_id, candidate_ids,
                        evidence, exposure, windows, divergence)

    def recompute(self) -> list[DecisionUpdate]:
        profiles = self._profiles()
        updates = []
        for auth in sorted(self.records.values(), key=lambda r: r.record_id):
            if auth.kind != "authentication":
                continue
            decision = self._decide(auth, profiles)
            previous = self.decisions.get(auth.record_id)
            if decision != previous:
                updates.append(DecisionUpdate(previous, decision))
                self.decisions[auth.record_id] = decision
        return updates

    def checkpoint(self) -> str:
        return json.dumps({"schema": 1, "template_aliases": self.template_aliases,
                           "records": [asdict(r) for r in sorted(self.records.values(), key=lambda x: x.record_id)],
                           "windows": [asdict(w) for w in sorted(self.windows.values(), key=lambda x: x.record_id)]}, sort_keys=True)

    @classmethod
    def restore(cls, checkpoint: str):
        state = json.loads(checkpoint)
        if state.get("schema") != 1:
            raise ValueError("Unknown checkpoint schema")
        engine = cls(state["template_aliases"])
        for raw in state["records"]:
            item = dict(raw)
            item["time"] = TimeRange(**item["time"])
            record = Observation(**item)
            if record.record_id in engine.records:
                raise ValueError("Duplicate checkpoint record ID")
            engine.records[record.record_id] = record
        for raw in state["windows"]:
            item = dict(raw)
            item["opened"] = TimeRange(**item["opened"])
            item["closed"] = TimeRange(**item["closed"])
            item["evidence_ids"] = tuple(item["evidence_ids"])
            window = MutationWindow(**item)
            if window.record_id in engine.windows:
                raise ValueError("Duplicate checkpoint window ID")
            engine.windows[window.record_id] = window
        engine.recompute()
        return engine
