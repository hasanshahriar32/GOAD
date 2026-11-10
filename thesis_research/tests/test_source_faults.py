import unittest
from thesis_research.src.lineage_constraints.falsification_controls import correlated_case,order_case
from thesis_research.src.lineage_constraints.source_faults import reason_with_source_budget


class SourceFaultTests(unittest.TestCase):
    def test_correlated_export_cannot_create_certain_link_within_source_budget(self):
        records,mapping=correlated_case();result=reason_with_source_budget(records,(),"auth",mapping,1)
        self.assertIn("true-issue",result["possible_issuance_ids"])
        self.assertIsNone(result["certain_issuance_id"])
        self.assertEqual(result["hypotheses_checked"],2)

    def test_unknown_bridge_failure_domain_is_rejected(self):
        records,mapping=correlated_case();mapping.pop(next(iter(mapping)))
        with self.assertRaises(ValueError):reason_with_source_budget(records,(),"auth",mapping)

    def test_order_consistency_is_not_source_authentication(self):
        result=order_case()
        self.assertFalse(result["truth_overlap"])
        self.assertTrue(result["network_consistent"])
        self.assertEqual(result["false_but_consistent_order"],"definite_overlap")
