from fractions import Fraction
import unittest
from thesis_research.src.lineage_constraints.summarize_interdiction_recheck import exact_rank


class RecheckRankTests(unittest.TestCase):
    def test_five_equal_positive_pairs_have_two_extreme_sign_assignments(self):
        result=exact_rank([Fraction(1,3)]*5)
        self.assertEqual(result['tail_assignments'],2)
        self.assertEqual(result['p_value'],.0625)

    def test_balanced_equal_rank_pair_has_unit_p_value(self):
        self.assertEqual(exact_rank([Fraction(1,7),Fraction(-1,7)])['p_value'],1)

    def test_zeros_do_not_create_sign_assignments(self):
        self.assertEqual(exact_rank([Fraction(0)]*30),{'p_value':1.,'nonzero_pairs':0,'sign_assignments':1})
