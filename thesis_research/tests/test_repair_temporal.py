"""Independent finite-world checks and counterexamples for the new components."""

from dataclasses import replace
from fractions import Fraction
from itertools import product
import random
import unittest

from thesis_research.src.lineage_constraints.engine import Observation, TimeRange
from thesis_research.src.lineage_constraints.repair import reason_with_bridge_budget
from thesis_research.src.lineage_constraints.temporal import Constraint, TemporalNetwork


class RepairTests(unittest.TestCase):
    def setUp(self):
        self.issue = Observation("i", "issuance", TimeRange(1, 1), "ca", "7", "01", "", "aa")
        self.auth = Observation("a", "authentication", TimeRange(3, 3), "ca", serial="1", thumbprint="bb", skid="aa")
        self.bad = Observation("b", "bridge", TimeRange(0, 0), "ca", "7", "1", "cc", "aa")

    def test_bad_enrichment_does_not_erase_possible_truth_within_budget(self):
        records = (self.issue, self.auth, self.bad)
        self.assertNotIn("i", reason_with_bridge_budget(records, (), "a", 0).possible_issuance_ids)
        d = reason_with_bridge_budget(records, (), "a", 1)
        self.assertEqual(d.possible_issuance_ids, ("i",))
        self.assertIsNone(d.certain_issuance_id)  # The retained bad-export world still abstains.
        self.assertEqual(d.candidate_witnesses["i"], ("b",))

    def test_abstaining_world_cannot_be_filtered_to_manufacture_certainty(self):
        issue = replace(self.issue, serial="", skid="")
        good = replace(self.bad, thumbprint="bb")
        zero = reason_with_bridge_budget((issue, self.auth, good), (), "a", 0)
        one = reason_with_bridge_budget((issue, self.auth, good), (), "a", 1)
        self.assertEqual(zero.certain_issuance_id, "i")
        self.assertIsNone(one.certain_issuance_id)

    def test_budget_monotonicity_and_arrival_order(self):
        records = (self.issue, self.auth, self.bad, replace(self.bad, record_id="b2", thumbprint="dd"))
        old = set()
        for budget in (0, 1, 2):
            d = reason_with_bridge_budget(records, (), "a", budget)
            self.assertTrue(old <= set(d.possible_issuance_ids))
            self.assertEqual(d, reason_with_bridge_budget(tuple(reversed(records)), (), "a", budget))
            old = set(d.possible_issuance_ids)
        self.assertIn("i", old)

    def test_fault_budget_is_not_guarantee_under_extra_faults(self):
        records = (self.issue, self.auth, self.bad, replace(self.bad, record_id="b2"))
        self.assertNotIn("i", reason_with_bridge_budget(records, (), "a", 1).possible_issuance_ids)
        self.assertIn("i", reason_with_bridge_budget(records, (), "a", 2).possible_issuance_ids)

    def test_limits_and_record_namespace(self):
        with self.assertRaises(ValueError):
            reason_with_bridge_budget((self.issue, self.auth, self.bad), (), "a", 1, max_hypotheses=1)
        with self.assertRaises(ValueError):
            reason_with_bridge_budget((self.issue, self.issue, self.auth), (), "a")
        for budget in (-1, 0.5, True):
            with self.assertRaises(ValueError):
                reason_with_bridge_budget((self.issue, self.auth), (), "a", budget)


class TemporalTests(unittest.TestCase):
    def test_order_can_resolve_overlap_without_narrow_clock_bounds(self):
        bounds = {x: (0, 100) for x in ("o", "i", "r")}
        self.assertEqual(TemporalNetwork(bounds).overlap("o", "i", "r"), "possible_overlap")
        constraints = [Constraint("o", "i", 0, "verified-open-response-before-enroll"),
                       Constraint("i", "r", 0, "verified-issued-response-before-rollback")]
        self.assertEqual(TemporalNetwork(bounds, constraints).overlap("o", "i", "r"), "definite_overlap")

    def test_inconsistent_model_does_not_yield_vacuous_definite_answer(self):
        edges = [Constraint("o", "i", 0, "first"), Constraint("i", "o", 0, "second", strict=True)]
        network = TemporalNetwork({"o": None, "i": None, "r": None}, edges)
        self.assertFalse(network.consistent)
        self.assertEqual(network.overlap("o", "i", "r"), "inconsistent_evidence")
        self.assertEqual(set(network.inconsistent_core()), {"first", "second"})

    def test_strict_fractional_boundary_and_unbounded_variables(self):
        network = TemporalNetwork({"o": (0, 0), "i": None, "r": (1, 1)},
                                  [Constraint("o", "i", 0, "positive", True),
                                   Constraint("i", "r", 0, "less-than-one", True)])
        self.assertTrue(network.consistent)
        self.assertEqual(network.overlap("o", "i", "r"), "definite_overlap")
        tiny = TemporalNetwork({"o": (0, 0), "i": (Fraction(1, 10**30), Fraction(1, 10**30)), "r": (1, 1)})
        self.assertEqual(tiny.overlap("o", "i", "r"), "definite_overlap")

    def test_exact_solver_against_independent_rational_grid_enumeration(self):
        # For three variables and integer bounds, quarter ticks witness strict
        # feasible order cells; integer-only enumeration would miss open cells.
        rng = random.Random(481)
        names = ("o", "i", "r")
        for case in range(240):
            bounds = {x: tuple(sorted((rng.randrange(3), rng.randrange(3)))) for x in names}
            edges = [Constraint(rng.choice(names), rng.choice(names), rng.randrange(-1, 2), f"e{j}", bool(rng.randrange(2)))
                     for j in range(rng.randrange(6))]
            worlds = []
            for values in product(*(range(bounds[x][0]*4, bounds[x][1]*4+1) for x in names)):
                assignment = dict(zip(names, values))
                if all((assignment[c.left]-assignment[c.right] < c.upper*4 if c.strict else
                        assignment[c.left]-assignment[c.right] <= c.upper*4) for c in edges):
                    worlds.append(assignment)
            truths = [w["o"] <= w["i"] <= w["r"] for w in worlds]
            expected = ("inconsistent_evidence" if not worlds else "definite_overlap" if all(truths)
                        else "possible_overlap" if any(truths) else "impossible_overlap")
            self.assertEqual(TemporalNetwork(bounds, edges).overlap(*names), expected, f"case {case}")


if __name__ == "__main__":
    unittest.main()
