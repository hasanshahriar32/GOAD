"""Check the clock-assumption guard against independently enumerated histories."""

import unittest

from thesis_research.src.lineage_constraints.clock_audit import audit_operation_bracket


class ClockAuditTests(unittest.TestCase):
    def test_clock_bound_cannot_explain_a_log_before_the_command(self):
        result = audit_operation_bracket(59.44, 73.1, 77.7, 0.08, 0.39)
        self.assertFalse(result["compatible"])
        self.assertTrue(result["log_must_precede_command_under_declared_clock_bound"])

    def test_unknown_nonnegative_audit_lag_does_not_imply_clock_failure(self):
        self.assertTrue(audit_operation_bracket(20, 4, 6, 0, 0)["compatible"])
        self.assertFalse(audit_operation_bracket(20, 4, 6, 0, 0, max_audit_delay=1)["compatible"])

    def test_finite_delay_matches_enumerated_physical_histories(self):
        for delay in (0, 1, 3):
            for observed in range(13):
                feasible = any(observed == operation + latency + offset
                               for operation in range(4, 7)
                               for latency in range(delay + 1)
                               for offset in range(-2, 3))
                actual = audit_operation_bracket(observed, 4, 6, -2, 2, max_audit_delay=delay)["compatible"]
                self.assertEqual(actual, feasible)


if __name__ == "__main__":
    unittest.main()
