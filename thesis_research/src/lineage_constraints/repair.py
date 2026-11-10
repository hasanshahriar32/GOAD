"""Bounded optional-CA-export hypotheses; the original engine is unchanged.

This is an exhaustive correctness reference, not a scalable repair algorithm.
Raw issuance/authentication observations are trusted. Up to k *bridge records*
may be discarded. Every subset of size <= k is considered, including the empty
subset; no hypothesis is preferred because it produces an attractive answer.
"""

from dataclasses import dataclass
from itertools import combinations
from math import comb

from .engine import LineageEngine


@dataclass(frozen=True)
class RepairDecision:
    status: str
    certain_issuance_id: str | None
    possible_issuance_ids: tuple[str, ...]
    certain_overlap: bool
    hypotheses_checked: int
    candidate_witnesses: dict[str, tuple[str, ...]]
    hypothesis_outcomes: tuple[dict, ...]


def reason_with_bridge_budget(records, windows, auth_id, budget=1,
                              template_aliases=None, max_hypotheses=10000):
    """Quantify over record-deletion hypotheses, including abstaining worlds.

    This is deliberately not minimum-cost/majority repair. Even inconsistent
    retained hypotheses remain uncertainty (the engine abstains). Increasing
    the budget cannot shrink possible candidates or create a new certain link.
    The budget is record-level, not a bound on compromised sources or fields.
    """
    if type(budget) is not int or budget < 0:
        raise ValueError("Use a nonnegative integer record fault budget")
    records, windows = tuple(records), tuple(windows)
    ids = [r.record_id for r in records]
    if len(ids) != len(set(ids)):
        raise ValueError("Duplicate record IDs are not independent hypotheses")
    bridge_ids = sorted(r.record_id for r in records if r.kind == "bridge")
    count = sum(comb(len(bridge_ids), n) for n in range(min(budget, len(bridge_ids)) + 1))
    if count > max_hypotheses:
        raise ValueError(f"{count} hypotheses exceed explicit limit {max_hypotheses}")
    witnesses, outcomes = {}, []
    for n in range(min(budget, len(bridge_ids)) + 1):
        for dropped in combinations(bridge_ids, n):
            engine = LineageEngine(template_aliases)
            # Batch a retained set: avoid measuring incremental update overhead.
            engine.records = {r.record_id: r for r in records if r.record_id not in dropped}
            engine.windows = {w.record_id: w for w in windows}
            engine.recompute()
            if auth_id not in engine.decisions:
                raise ValueError("The requested authentication is not present")
            decision = engine.decisions[auth_id]
            for candidate in decision.candidate_ids:
                witnesses.setdefault(candidate, dropped)
            outcomes.append({"dropped_bridge_ids": dropped, "status": decision.status,
                             "resolved_id": decision.issuance_id,
                             "candidate_ids": decision.candidate_ids,
                             "definite_overlap": decision.exposure == "definite_overlap"})
    first = outcomes[0]["resolved_id"]
    certain = first if first and all(x["status"] == "resolved" and x["resolved_id"] == first
                                     for x in outcomes) else None
    return RepairDecision("certain_link" if certain else "uncertain", certain,
                          tuple(sorted(witnesses)),
                          bool(certain and all(x["definite_overlap"] for x in outcomes)),
                          len(outcomes), witnesses, tuple(outcomes))
