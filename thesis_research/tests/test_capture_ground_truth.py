"""Reject wrong-certificate exports and false successful-attack labels."""

import csv
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import tempfile
import unittest
import xml.etree.ElementTree as ET

from cryptography import x509
from cryptography.hazmat.primitives import hashes, serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from scripts.capture_trace7_split_actor_delayed_pkinit import adjudicate_capture, verify_pfx_certificate


class CaptureGroundTruthTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key = rsa.generate_private_key(public_exponent=65537, key_size=2048)
        name = x509.Name([x509.NameAttribute(NameOID.COMMON_NAME, "capture-test")])
        now = datetime.now(timezone.utc)
        def certificate(serial):
            return (x509.CertificateBuilder().subject_name(name).issuer_name(name)
                    .public_key(cls.key.public_key()).serial_number(serial)
                    .not_valid_before(now - timedelta(minutes=1)).not_valid_after(now + timedelta(days=1))
                    .sign(cls.key, hashes.SHA256()))
        cls.issued = certificate(7)
        cls.other = certificate(8)
        cls.pfx = pkcs12.serialize_key_and_certificates(b"test", cls.key, cls.issued, None,
                                                       serialization.BestAvailableEncryption(b"Password123!"))

    def test_pfx_must_match_exact_new_certificate(self):
        _, certificate, _ = verify_pfx_certificate(self.pfx, self.issued.public_bytes(serialization.Encoding.DER))
        self.assertEqual(certificate.serial_number, 7)
        with self.assertRaises(ValueError):
            verify_pfx_certificate(self.pfx, self.other.public_bytes(serialization.Encoding.DER))

    def make_fixture(self, directory, status="0x0", thumbprint="aa11", rollback=True, mutator="khal.drogo"):
        (directory / "certificate_identity.json").write_text(json.dumps({"serial": "a", "sha1_thumbprint": "aa11"}))
        (directory / "00_domain_context.json").write_text(json.dumps({"stdout": json.dumps({"domain_sid": "S-1-5-21-1-2-3", "dns_root": "essos.local"})}))
        (directory / "case_timeline.json").write_text(json.dumps({"original_template_name_flag": 33554432}))
        with (directory / "srv03_ca_db_bridge.csv").open("w", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=["Issued Request ID", "Serial Number", "Certificate Hash"])
            writer.writeheader()
            writer.writerow({"Issued Request ID": "7", "Serial Number": "000a", "Certificate Hash": "aa 11"})
        root = ET.Element("Events")
        def event(eid, fields):
            node = ET.SubElement(root, "Event")
            system = ET.SubElement(node, "System")
            ET.SubElement(system, "EventID").text = str(eid)
            ET.SubElement(system, "EventRecordID").text = str(len(root))
            ET.SubElement(system, "Computer").text = "lab-host"
            data = ET.SubElement(node, "EventData")
            for key, value in fields.items():
                ET.SubElement(data, "Data", Name=key).text = value
        event(4887, {"RequestId": "7", "Requester": "ESSOS\\viserys.targaryen"})
        for value in (["1", "33554432"] if rollback else ["1"]):
            event(5136, {"ObjectDN": "CN=CGPubPositive,CN=Certificate Templates,DC=test",
                         "AttributeLDAPDisplayName": "msPKI-Certificate-Name-Flag",
                         "AttributeValue": value, "OperationType": "%%14674", "SubjectUserName": mutator,
                         "SubjectUserSid": "S-1-5-21-1-2-3-1115", "SubjectDomainName": "ESSOS"})
        event(4768, {"CertSerialNumber": "0A", "CertThumbprint": thumbprint, "Status": status,
                     "PreAuthType": "16", "TargetUserName": "Administrator", "CertIssuerName": "CertGraph-Lab-CA",
                     "TargetSid": "S-1-5-21-1-2-3-500", "TargetDomainName": "ESSOS.LOCAL"})
        ET.ElementTree(root).write(directory / "trace_split_actor_delayed_pkinit.xml")

    def test_success_label_requires_the_whole_evidence_chain(self):
        with tempfile.TemporaryDirectory() as temporary:
            directory = Path(temporary)
            self.make_fixture(directory)
            self.assertTrue(adjudicate_capture(directory)["successful_controlled_case"])
            for kwargs in ({"status": "0x42"}, {"thumbprint": "bb22"}, {"rollback": False}, {"mutator": "other-user"}):
                self.make_fixture(directory, **kwargs)
                self.assertFalse(adjudicate_capture(directory)["successful_controlled_case"])


if __name__ == "__main__":
    unittest.main()
