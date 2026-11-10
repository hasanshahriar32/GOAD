import unittest

from thesis_research.src.lineage_constraints.published_rule_replay import replay


class PublishedProxyTests(unittest.TestCase):
    def test_proxy_exposes_san_and_principal_mapping_requirements(self):
        ca = {"record_id": "ca:1", "event_id": "4887", "fields": {"Attributes": "CertificateTemplate:T\nSAN:upn=admin@test"}}
        auth = {"record_id": "dc:1", "event_id": "4768", "fields": {"TargetUserName": "Admin", "CertThumbprint": "aa", "Status": "0x42"}}
        self.assertEqual(replay([ca, auth])["pairs"], [])
        adapted = replay([ca, auth], True)
        self.assertEqual(adapted["pairs"][0]["auth_status"], "0x42")
        # A candidate association must not be mislabeled successful PKINIT.
        concealed = {**ca, "fields": {"Attributes": "CertificateTemplate:T"}}
        self.assertEqual(replay([concealed, auth], True)["eligible_issuances"], 0)

    def test_multivalue_semantics_are_declared_unsupported(self):
        ca = {"record_id": "ca:2", "event_id": "4887", "fields": {"Attributes": "CertificateTemplate:T\nSAN:upn=a@test&upn=b@test"}}
        self.assertEqual(replay([ca])["unsupported_multivalue_or_missing_upn_records"], ["ca:2"])


if __name__ == "__main__":
    unittest.main()
