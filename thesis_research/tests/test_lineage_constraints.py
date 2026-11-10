"""Counterexamples and independent endpoint checks for lineage reasoning."""

from dataclasses import replace
import itertools
from pathlib import Path
import unittest

from thesis_research.src.lineage_constraints import (
    LineageEngine, Observation, TimeRange, MutationWindow,
)
from thesis_research.src.lineage_constraints.goad import read_trace


def issued(record_id="i", **kwargs):
    base = Observation(record_id, "issuance", TimeRange(10, 10), issuer="ca-a",
                       request_id="7", serial="000A", thumbprint="aa11", skid="bb22",
                       template="template-a", principal="requester@example.test")
    return replace(base, **kwargs)


def authenticated(**kwargs):
    base = Observation("a", "authentication", TimeRange(20, 20), issuer="CA-A",
                       serial="0a", thumbprint="aa11", skid="bb22", principal="admin@example.test")
    return replace(base, **kwargs)


def decide(*records, windows=()):
    engine = LineageEngine()
    for r in (*records, *windows):
        engine.add(r)
    return engine, engine.decisions["a"]


class LineageConstraintTests(unittest.TestCase):
    def test_unique_complete_match_normalizes_serial(self):
        _, d = decide(issued(), authenticated())
        self.assertEqual((d.status, d.issuance_id, d.principal_divergence), ("resolved", "i", True))

    def test_serial_reuse_across_issuers_does_not_join(self):
        wrong = issued("other", issuer="ca-b", thumbprint="cc33")
        _, d = decide(wrong, issued(), authenticated(thumbprint="", skid=""))
        self.assertEqual(d.issuance_id, "i")

    def test_any_known_identity_conflict_rejects_pair(self):
        _, d = decide(issued(), authenticated(thumbprint="cc33"))
        self.assertNotEqual(d.status, "resolved")

    def test_skid_reuse_is_not_certificate_identity(self):
        _, d = decide(issued(serial="", thumbprint=""), authenticated(serial="", thumbprint=""))
        self.assertEqual(d.status, "insufficient_identity")

    def test_unidentified_issuance_blocks_manufactured_uniqueness(self):
        unknown = issued("unknown", request_id="8", serial="", thumbprint="", skid="")
        _, d = decide(issued(), unknown, authenticated())
        self.assertEqual(d.status, "ambiguous")

    def test_auth_before_issuance_cannot_be_resolved(self):
        _, d = decide(issued(), authenticated(time=TimeRange(1, 2)))
        self.assertEqual(d.status, "no_consistent_candidate")

    def test_overlapping_clock_bounds_require_abstention(self):
        _, d = decide(issued(time=TimeRange(9, 12)), authenticated(time=TimeRange(11, 14)))
        self.assertEqual(d.status, "uncertain_order")

    def test_failed_and_password_auth_do_not_become_successful_use(self):
        for auth in (authenticated(success=False), authenticated(success=None), authenticated(preauth_type=2)):
            _, d = decide(issued(), auth)
            self.assertNotEqual(d.status, "resolved")

    def test_missing_identifiers_preserve_possible_candidates(self):
        _, d = decide(issued(), authenticated(serial="", thumbprint="", skid=""))
        self.assertEqual(d.status, "missing_identifiers")
        self.assertEqual(d.candidate_ids, ("i",))

    def test_late_bridge_and_late_candidate_revise_decision(self):
        engine, d = decide(issued(serial="", thumbprint="", skid=""), authenticated())
        self.assertEqual(d.status, "insufficient_identity")
        bridge = Observation("b", "bridge", TimeRange(100, 100), issuer="ca-a", request_id="7",
                             serial="a", thumbprint="aa11", skid="bb22")
        engine.add(bridge)
        self.assertEqual(engine.decisions["a"].status, "resolved")
        updates = engine.add(issued("ambiguous-copy", request_id="8"))
        self.assertEqual(engine.decisions["a"].status, "ambiguous")
        self.assertTrue(any(u.retracts_resolved_link for u in updates))

    def test_bridge_conflicts_are_reported_not_overwritten(self):
        bridge = Observation("b", "bridge", TimeRange(100, 100), issuer="ca-a", request_id="7", serial="ff")
        _, d = decide(issued(), authenticated(), bridge)
        self.assertEqual(d.status, "conflicting_evidence")

    def test_checkpoint_duplicate_delivery_and_order_invariance(self):
        records = [issued(), authenticated(), Observation("b", "bridge", TimeRange(100, 100),
                   issuer="ca-a", request_id="7", serial="a")]
        expected = None
        for order in itertools.permutations(records):
            engine, decision = decide(*order)
            self.assertEqual(engine.add(order[0]), [])
            if expected is None:
                expected = decision
            self.assertEqual(decision, expected)
            restored = LineageEngine.restore(engine.checkpoint())
            self.assertEqual(restored.decisions, engine.decisions)
        engine = LineageEngine()
        engine.add(issued())
        with self.assertRaises(ValueError):
            engine.add(issued(serial="ff"))

    def test_exact_template_and_independent_time_endpoint_oracle(self):
        # Enumerate all integer times in the declared boxes, independently of
        # the engine's overlap formula. A definite overlap must hold everywhere.
        for lo, hi in [(0, 0), (0, 2), (2, 4), (4, 6), (6, 8)]:
            window = MutationWindow("w", "template-a", TimeRange(1, 2), TimeRange(5, 6), ("open", "close"))
            _, d = decide(issued(time=TimeRange(lo, hi)), authenticated(time=TimeRange(20, 20)), windows=(window,))
            outcomes = [start <= issue <= end
                        for start in range(1, 3) for end in range(5, 7) for issue in range(lo, hi + 1)]
            if d.exposure == "definite_overlap":
                self.assertTrue(all(outcomes))
            if d.exposure == "no_observed_overlap":
                self.assertFalse(any(outcomes))
        unrelated = MutationWindow("w", "template-other", TimeRange(1, 1), TimeRange(30, 30))
        _, d = decide(issued(), authenticated(), windows=(unrelated,))
        self.assertEqual(d.exposure, "no_observed_overlap")


class GoadProjectionTests(unittest.TestCase):
    directory = Path(__file__).resolve().parents[1] / "data/live_goad_traces"

    def test_complete_xml_roots_and_issuance_semantics(self):
        total = 0
        for path in self.directory.glob("trace_*.xml"):
            records, counts = read_trace(path, "CertGraph-Lab-CA")
            total += sum(counts.values())
            self.assertEqual(sum(r.kind == "issuance" for r in records), counts.get("4887", 0))
        self.assertEqual(total, 586)

    def test_failed_esc6_request_is_not_successful_certificate_use(self):
        records, _ = read_trace(self.directory / "trace_esc6_ca_flag_abuse.xml", "CertGraph-Lab-CA")
        auth = next(r for r in records if r.kind == "authentication")
        self.assertIs(auth.success, False)
        engine = LineageEngine()
        for record in records:
            engine.add(record)
        self.assertEqual(engine.decisions[auth.record_id].status, "failed_or_unknown_authentication")


if __name__ == "__main__":
    unittest.main()
