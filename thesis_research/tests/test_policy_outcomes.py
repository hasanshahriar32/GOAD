import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
import xml.etree.ElementTree as ET

from thesis_research.src.lineage_constraints.adjudicate_policy_matrix import adjudicate,system_rejections

ROOT=Path(__file__).resolve().parents[2]
DATA=ROOT/"thesis_research/data/lineage_live/2026-11-10/policy_matrix_01"


class PolicyOutcomeTests(unittest.TestCase):
    def setUp(self):
        self.temp=tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path=Path(self.temp.name)/"trial"
        shutil.copytree(DATA/"r01_enabled_admin_san",self.path)
        self.trial=next(t for t in json.loads((DATA/"protocol.json").read_text())["trials"] if t["id"]=="r01_enabled_admin_san")

    def edit(self,event_id,field,value):
        path=self.path/"events.xml"
        tree=ET.parse(path)
        for event in tree.getroot():
            system=next(c for c in event if c.tag.rsplit("}",1)[-1]=="System")
            code=next(c.text for c in system if c.tag.rsplit("}",1)[-1]=="EventID")
            if code==str(event_id):
                for child in event.iter():
                    if child.attrib.get("Name")==field:child.text=value
        tree.write(path,encoding="utf-8",xml_declaration=True)
        manifest=json.loads((self.path/"manifest.json").read_text())
        manifest["events.xml"]=hashlib.sha256(path.read_bytes()).hexdigest()
        (self.path/"manifest.json").write_text(json.dumps(manifest))

    def test_actual_byte_anchored_trial_is_privileged_success(self):
        self.assertTrue(adjudicate(self.path,self.trial)["successful_administrator_use"])

    def test_failed_kdc_record_is_not_success(self):
        self.edit(4768,"Status","0x42")
        result=adjudicate(self.path,self.trial)
        self.assertFalse(result["successful_exact_certificate_use"])
        self.assertEqual(result["observed_outcome"],"certificate_authentication_rejected")
        self.assertEqual(result["rejected_kdc_statuses"],["0x42"])

    def test_inconsistent_target_sid_and_name_is_not_success(self):
        context=json.loads(json.loads((self.path/"00_domain_context.json").read_text())["stdout"])
        self.edit(4768,"TargetSid",context["viserys_sid"])
        self.assertFalse(adjudicate(self.path,self.trial)["successful_exact_certificate_use"])

    def test_different_ca_requester_is_not_the_controlled_chain(self):
        self.edit(4887,"Requester","ESSOS\\other-user")
        self.assertFalse(adjudicate(self.path,self.trial)["successful_administrator_use"])

    def test_missing_mutation_actor_does_not_erase_verified_authentication(self):
        self.edit(5136,"SubjectUserName","unrelated-principal")
        result=adjudicate(self.path,self.trial)
        self.assertTrue(result["successful_administrator_use"])
        self.assertFalse(result["controlled_mutation_chain_complete"])

    def test_changed_artifact_hash_fails_before_labeling(self):
        with (self.path/"events.xml").open("a") as target:target.write(" ")
        with self.assertRaises(ValueError):adjudicate(self.path,self.trial)

    def test_unknown_condition_does_not_claim_a_validated_mutation_chain(self):
        trial={**self.trial,"condition":"transfer_enabled_admin"}
        result=adjudicate(self.path,trial)
        self.assertTrue(result["successful_administrator_use"])
        self.assertIsNone(result["controlled_mutation_chain_complete"])
        self.assertIsNone(result["mutation_actor_checked"])
        self.assertEqual(result["mutation_history_validation"],"not_evaluated_for_this_condition")


class KdcSystemOutcomeTests(unittest.TestCase):
    def check(self,provider="Microsoft-Windows-Kerberos-Key-Distribution-Center",thumb="AA BB",serial="00 12"):
        with tempfile.TemporaryDirectory() as temp:
            p=Path(temp)/"events.xml"
            p.write_text(f'<Events><Event><System><Provider Name="{provider}"/><EventID>39</EventID><Computer>lab.test</Computer><EventRecordID>7</EventRecordID></System><EventData><Data Name="Serial">{serial}</Data><Data Name="Thumbprint">{thumb}</Data></EventData></Event></Events>')
            return system_rejections(p,"12","aabb")

    def test_exact_certificate_kdc_diagnostic_is_recorded(self):
        self.assertEqual(self.check(),[{"id":"lab.test:System:7","event_id":39}])

    def test_foreign_system_provider_is_not_certificate_rejection(self):
        self.assertEqual(self.check(provider="Microsoft-Windows-Kernel-Power"),[])

    def test_reused_serial_with_other_thumbprint_is_not_this_certificate(self):
        self.assertEqual(self.check(thumb="CC DD"),[])
