import unittest
from thesis_research.src.lineage_constraints.audit_legacy_statistics import exact_signed_rank


class ExactPairedStatisticsTests(unittest.TestCase):
    def test_five_nonzero_positive_pairs_do_not_reject_at_five_percent(self):
        result=exact_signed_rank([0]*25+[1,2,3,4,5])
        self.assertEqual(result["nonzero_pairs"],5)
        self.assertEqual(result["sign_assignments"],32)
        self.assertEqual(result["p_value"],.0625)

    def test_identical_policies_have_no_signed_rank_difference(self):
        self.assertEqual(exact_signed_rank([0]*30)["p_value"],1.)
