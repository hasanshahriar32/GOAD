from dataclasses import replace
import unittest

from thesis_research.src.lineage_constraints.engine import Observation,TimeRange,LineageEngine
from thesis_research.src.lineage_constraints.sql_lineage import SQLiteLineage


class SQLLineageTests(unittest.TestCase):
    def setUp(self):
        self.issue=Observation('i','issuance',TimeRange(0,0),'ca','1','01','aa',template='Template',principal='user')
        self.auth=Observation('a','authentication',TimeRange(0,0),'ca',serial='1',thumbprint='aa')

    def compare(self,records):
        engine=LineageEngine();sql=SQLiteLineage();self.addCleanup(sql.close)
        for record in records:
            engine.add(record); actual=sql.add(record)
            self.assertEqual({k:(v.status,v.candidate_ids,v.issuance_id) for k,v in engine.decisions.items()},
                             {k:(v.status,v.candidates,v.issuance_id) for k,v in actual.items()})
        return engine,sql

    def test_late_incomplete_competitor_retracts_guarded_uniqueness(self):
        competitor=replace(self.issue,record_id='j',request_id='2',serial='',thumbprint='')
        engine,sql=self.compare([self.auth,self.issue,competitor])
        self.assertEqual(sql.decisions()['a'].status,'ambiguous')
        sql.remove('j');engine.remove('j')
        self.assertEqual(sql.decisions()['a'].issuance_id,engine.decisions['a'].issuance_id)

    def test_issuer_scope_and_conflicting_bridge(self):
        bridge=replace(self.issue,record_id='b',kind='bridge',serial='2')
        foreign=replace(bridge,record_id='other',issuer='other-ca')
        self.compare([self.auth,self.issue,foreign,bridge])

    def test_failed_and_noncertificate_authentication_are_not_links(self):
        self.compare([self.issue,replace(self.auth,success=False),replace(self.auth,record_id='pw',preauth_type=2)])

    def test_skid_reuse_does_not_identify_one_certificate(self):
        i=replace(self.issue,skid='bb');a=replace(self.auth,serial='',thumbprint='',skid='bb')
        self.compare([i,replace(i,record_id='j',request_id='2',serial='2',thumbprint='cc'),a])

    def test_observed_template_oid_alias_prevents_false_profile_conflict(self):
        aliases={'1.2.3':'Template'}
        engine=LineageEngine(aliases);sql=SQLiteLineage(template_aliases=aliases);self.addCleanup(sql.close)
        bridge=replace(self.issue,record_id='b',kind='bridge',template='1.2.3')
        for record in [self.issue,bridge,self.auth]:engine.add(record);sql.add(record)
        self.assertEqual(sql.decisions()['a'].status,'resolved')
        self.assertEqual(sql.decisions()['a'].issuance_id,engine.decisions['a'].issuance_id)
