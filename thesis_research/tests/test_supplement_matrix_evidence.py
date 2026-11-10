import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from thesis_research.src.lineage_constraints.supplement_matrix_evidence import evidence_view


class SupplementEvidenceTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(); self.addCleanup(self.temp.cleanup)
        self.matrix = Path(self.temp.name)/"matrix"; self.matrix.mkdir()
        self.supplement = Path(self.temp.name)/"supplement"; self.supplement.mkdir()
        self.context = {"dns_root":"q1lab.test", "domain_sid":"S-1-5-21-1-2-3",
                        "computer":"LAB", "ca_name":"CA"}
        for name in ("r01", "r02"):
            p=self.matrix/name; p.mkdir()
            self.write(p/"00_domain_context.json", {"stdout":json.dumps(self.context)})
        self.write(self.matrix/"r02/99_ca_bridge.json", {"returncode":0,"stdout":"original export"})
        for p in self.matrix.iterdir(): self.manifest(p)
        self.write(self.supplement/"context.json", {"stdout":json.dumps({
            "domain":"q1lab.test", "domain_sid":"S-1-5-21-1-2-3", "computer":"LAB", "ca":"CA"})})
        self.write(self.supplement/"ca_export.json", {"returncode":0,"stdout":"later export"})
        self.manifest(self.supplement)

    def write(self, path, value): path.write_text(json.dumps(value))

    def manifest(self, directory):
        self.write(directory/"manifest.json", {p.name:hashlib.sha256(p.read_bytes()).hexdigest()
            for p in directory.iterdir() if p.name!="manifest.json"})

    def test_missing_export_filled_only_in_view_and_original_export_preserved(self):
        before={str(p):p.read_bytes() for p in self.matrix.rglob("*") if p.is_file()}
        with evidence_view(self.matrix,self.supplement) as (view,supplied):
            self.assertEqual(supplied,["r01"])
            self.assertEqual(json.loads((view/"r01/99_ca_bridge.json").read_text())["stdout"],"later export")
            self.assertEqual(json.loads((view/"r02/99_ca_bridge.json").read_text())["stdout"],"original export")
        self.assertEqual(before,{str(p):p.read_bytes() for p in self.matrix.rglob("*") if p.is_file()})

    def test_changed_supplement_fails_hash_check(self):
        (self.supplement/"ca_export.json").write_text("{}")
        with self.assertRaisesRegex(ValueError,"Supplement hash mismatch"):
            with evidence_view(self.matrix,self.supplement): pass

    def test_another_forest_is_rejected_even_with_valid_manifest(self):
        path=self.supplement/"context.json"; data=json.loads(path.read_text())
        context=json.loads(data["stdout"]); context["domain_sid"]="S-1-5-21-9-8-7"
        data["stdout"]=json.dumps(context); self.write(path,data); self.manifest(self.supplement)
        with self.assertRaisesRegex(ValueError,"different CA/forest"):
            with evidence_view(self.matrix,self.supplement): pass
