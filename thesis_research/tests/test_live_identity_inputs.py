import json
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from thesis_research.src.lineage_constraints.evaluate_live_identity import identity_prediction

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"thesis_research/data/lineage_live/2026-11-10/paired_policy_matrix_02"


class LiveIdentityInputTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"trial"
        shutil.copytree(DATA/"r01_enabled_admin_san",self.path)

    def test_inference_does_not_require_certificate_csr_or_outcome_labels(self):
        for name in ["issued_certificate.cer","request.csr","outcome.json","certificate_identity.json"]:
            (self.path/name).unlink()
        rows,_=identity_prediction(self.path)
        self.assertEqual(sum(r["status"]=="unique_identity_link" for r in rows),1)
        self.assertEqual(sum(r["privileged_identity_divergence"] is True for r in rows),1)

    def test_missing_sid_aliases_require_principal_abstention(self):
        path=self.path/"events.xml";tree=ET.parse(path)
        for event in list(tree.getroot()):
            if any(c.text=="4624" for c in event.iter() if c.tag.rsplit("}",1)[-1]=="EventID"):
                tree.getroot().remove(event)
        tree.write(path,encoding="utf-8",xml_declaration=True)
        rows,_=identity_prediction(self.path)
        self.assertTrue(rows)
        self.assertTrue(all(r["privileged_identity_divergence"] is None for r in rows))

    def test_conflicting_logon_sid_aliases_require_abstention(self):
        path=self.path/"events.xml";tree=ET.parse(path)
        for event in list(tree.getroot()):
            code=next((c.text for c in event.iter() if c.tag.rsplit("}",1)[-1]=="EventID"),None)
            fields={c.attrib.get("Name"):c for c in event.iter() if c.tag.rsplit("}",1)[-1]=="Data"}
            if code=="4624" and fields.get("TargetUserName") is not None and fields["TargetUserName"].text=="viserys.targaryen":
                copy=ET.fromstring(ET.tostring(event))
                for child in copy.iter():
                    if child.attrib.get("Name")=="TargetUserSid":child.text="S-1-5-21-999-888-777-1234"
                    if child.tag.rsplit("}",1)[-1]=="EventRecordID":child.text="9999999"
                tree.getroot().append(copy);break
        tree.write(path,encoding="utf-8",xml_declaration=True)
        rows,_=identity_prediction(self.path)
        self.assertTrue(all(r["privileged_identity_divergence"] is None for r in rows))

    def test_missing_optional_bridge_does_not_manufacture_strong_identity(self):
        path=self.path/"99_ca_bridge.json";row=json.loads(path.read_text())
        row["stdout"]='"Issued Request ID","Requester Name","Serial Number","Certificate Hash","Certificate Template"\n'
        path.write_text(json.dumps(row))
        rows,_=identity_prediction(self.path)
        self.assertTrue(rows)
        self.assertTrue(all(r["status"]=="identity_unresolved" for r in rows))


class DirectoryTemplateMappingTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory();self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"trial"
        source=ROOT/"thesis_research/data/lineage_live/2026-11-10/independent_2019_matrix_02/r01_enabled_admin_san"
        shutil.copytree(source,self.path)

    def test_observed_directory_oid_mapping_resolves_name_difference(self):
        rows,_=identity_prediction(self.path)
        self.assertEqual(sum(r["privileged_identity_divergence"] is True for r in rows),1)

    def test_missing_directory_mapping_leaves_template_conflict_unresolved(self):
        (self.path/"04_assigned_state.json").unlink()
        rows,_=identity_prediction(self.path)
        self.assertTrue(rows)
        self.assertTrue(all(r["status"]=="identity_unresolved" for r in rows))

    def test_different_object_dn_does_not_authorize_oid_equivalence(self):
        path=self.path/"04_assigned_state.json";raw=json.loads(path.read_text());policy=json.loads(raw["stdout"])
        policy["dn"]="CN=DifferentTemplate,DC=q1lab,DC=test";raw["stdout"]=json.dumps(policy);path.write_text(json.dumps(raw))
        rows,_=identity_prediction(self.path)
        self.assertTrue(all(r["status"]=="identity_unresolved" for r in rows))
