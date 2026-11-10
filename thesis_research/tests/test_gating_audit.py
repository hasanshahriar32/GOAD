import unittest
from thesis_research.src.lineage_constraints.gating_audit import family,esc1_reference


class GatingLabelTests(unittest.TestCase):
    def test_reachable_deep_membership_is_positive(self):
        positive,negative=family(12011,8,0)
        self.assertEqual(esc1_reference(positive),0)
        self.assertEqual(esc1_reference(negative),6)

    def test_explicit_deny_overrides_reachable_allow(self):
        positive,negative=family(13001,4,1)
        self.assertEqual(esc1_reference(positive,"closure"),0)
        self.assertEqual(esc1_reference(negative,"closure"),6)
        self.assertEqual(positive["X"].tolist(),negative["X"].tolist())

