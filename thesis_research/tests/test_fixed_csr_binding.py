from datetime import datetime,timedelta,timezone
import unittest

from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12
from cryptography.x509.oid import NameOID

from thesis_research.src.lineage_constraints.paired_policy_matrix import exact_reissued_pfx


class FixedCSRBindingTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.key=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        name=x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,"controlled-only")])
        now=datetime.now(timezone.utc)
        def issue(serial):
            return x509.CertificateBuilder().subject_name(name).issuer_name(name).public_key(cls.key.public_key()).serial_number(serial).not_valid_before(now).not_valid_after(now+timedelta(days=1)).sign(cls.key,hashes.SHA256())
        cls.first,cls.second=issue(1),issue(2)

    def test_reissuance_contains_exact_new_certificate_not_previous_certificate(self):
        encoded=self.second.public_bytes(serialization.Encoding.DER)
        raw=exact_reissued_pfx(self.key,encoded)
        key,certificate,chain=pkcs12.load_key_and_certificates(raw,b"Password123!")
        self.assertEqual(certificate.fingerprint(hashes.SHA256()),self.second.fingerprint(hashes.SHA256()))
        self.assertNotEqual(certificate.fingerprint(hashes.SHA256()),self.first.fingerprint(hashes.SHA256()))

    def test_unrelated_private_key_is_rejected(self):
        other=rsa.generate_private_key(public_exponent=65537,key_size=2048)
        with self.assertRaises(ValueError):
            exact_reissued_pfx(other,self.second.public_bytes(serialization.Encoding.DER))
