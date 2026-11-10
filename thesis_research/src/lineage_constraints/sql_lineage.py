"""Executed SQLite correlators for the same certificate identity subtask.

The ordinary strong join requires a unique strong consistent match. The guarded
query also retains incomplete candidates and flags conflicting evidence. Neither
is presented as HADES/Splunk or as a new database reasoning technique. Event
times and mutation exposure are intentionally outside this identity-only task.
"""
from dataclasses import dataclass
import sqlite3


FACTS = """
WITH facts AS (
 SELECT i.id iid, i.issuer, i.serial, i.thumb, i.skid, i.template, i.principal
 FROM observations i WHERE i.kind='issuance' AND i.success=1
 UNION ALL
 SELECT i.id, b.issuer, b.serial, b.thumb, b.skid, b.template, b.principal
 FROM observations i JOIN observations b
 ON b.kind='bridge' AND i.kind='issuance' AND i.success=1
 AND i.issuer<>'' AND i.request<>'' AND b.issuer=i.issuer AND b.request=i.request
), profiles AS (
 SELECT iid,
 (count(DISTINCT nullif(issuer,''))>1 OR count(DISTINCT nullif(serial,''))>1
  OR count(DISTINCT nullif(thumb,''))>1 OR count(DISTINCT nullif(skid,''))>1
  OR count(DISTINCT nullif(template,''))>1 OR count(DISTINCT nullif(principal,''))>1) conflict
 FROM facts GROUP BY iid
), matches AS (
 SELECT a.id aid, p.iid, p.conflict,
 max(f.issuer<>'') ki, max(a.issuer<>'' AND a.issuer=f.issuer) mi,
 max(f.serial<>'') ks, max(a.serial<>'' AND a.serial=f.serial) ms,
 max(f.thumb<>'') kt, max(a.thumb<>'' AND a.thumb=f.thumb) mt,
 max(f.skid<>'') kk, max(a.skid<>'' AND a.skid=f.skid) mk,
 a.issuer ai, a.serial aser, a.thumb ath, a.skid ask
 FROM observations a CROSS JOIN profiles p JOIN facts f ON f.iid=p.iid
 WHERE a.kind='authentication' AND a.success=1 AND a.preauth IN (15,16,17)
 GROUP BY a.id, p.iid
), compared AS (
 SELECT *, ((ai<>'' AND ki AND NOT mi) OR (aser<>'' AND ks AND NOT ms)
            OR (ath<>'' AND kt AND NOT mt) OR (ask<>'' AND kk AND NOT mk)) mismatch,
 (ms OR mt OR mk) shared, (mt OR (ms AND ai<>'' AND ki)) strong
 FROM matches
)
"""

GUARDED = FACTS + """
SELECT aid,iid,conflict,strong FROM compared
WHERE NOT(ai<>'' AND ki AND NOT mi)
AND ((conflict AND (shared OR NOT mismatch)) OR (NOT conflict AND NOT mismatch))
ORDER BY aid,iid
"""
STRONG_JOIN = FACTS + """
SELECT aid,iid,conflict,strong FROM compared
WHERE NOT conflict AND NOT mismatch AND strong ORDER BY aid,iid
"""


@dataclass(frozen=True)
class IdentityDecision:
    auth_id: str
    status: str
    candidates: tuple
    issuance_id: str | None = None


class SQLiteLineage:
    def __init__(self, method="guarded", template_aliases=None):
        if method not in ("guarded","strong_join"):raise ValueError(method)
        self.method=method
        self.aliases={k.strip().casefold():v.strip().casefold() for k,v in (template_aliases or {}).items()}
        self.db=sqlite3.connect(":memory:")
        self.db.execute("CREATE TABLE observations(id TEXT PRIMARY KEY,kind TEXT,issuer TEXT,request TEXT,serial TEXT,thumb TEXT,skid TEXT,template TEXT,principal TEXT,success INTEGER,preauth INTEGER)")
        self.db.execute("CREATE INDEX bridge_scope ON observations(kind,issuer,request)")
        self.records={}

    def close(self):self.db.close()

    def add(self, record):
        previous=self.records.get(record.record_id)
        if previous is not None:
            if previous!=record:raise ValueError("Conflicting immutable record ID")
            return self.decisions()
        identity=record.identity()
        template=record.template.strip().casefold()
        self.db.execute("INSERT INTO observations VALUES (?,?,?,?,?,?,?,?,?,?,?)",(
            record.record_id,record.kind,identity["issuer"],record.request_id,
            identity["serial"],identity["thumbprint"],identity["skid"],self.aliases.get(template,template),
            record.principal.strip().casefold(),record.success,record.preauth_type))
        self.records[record.record_id]=record
        return self.decisions()

    def remove(self, record_id):
        self.db.execute("DELETE FROM observations WHERE id=?",(record_id,))
        self.records.pop(record_id,None)
        return self.decisions()

    def decisions(self):
        candidates={}
        for aid,iid,conflict,strong in self.db.execute(GUARDED if self.method=="guarded" else STRONG_JOIN):
            candidates.setdefault(aid,[]).append((iid,bool(conflict),bool(strong)))
        decisions={}
        for record in self.records.values():
            if record.kind!="authentication":continue
            aid=record.record_id; rows=candidates.get(aid,[]);ids=tuple(r[0] for r in rows)
            missing=not any(record.identity()[k] for k in ("serial","thumbprint","skid"))
            chosen=None
            if record.success is not True:status="failed_or_unknown_authentication"
            elif record.preauth_type not in (15,16,17):status="not_certificate_authentication"
            elif any(r[1] for r in rows):status="conflicting_evidence"
            elif not rows:status="no_consistent_candidate"
            elif missing:status="missing_identifiers"
            elif len(rows)>1:status="ambiguous"
            elif not rows[0][2]:status="insufficient_identity"
            else:status="resolved";chosen=rows[0][0]
            decisions[aid]=IdentityDecision(aid,status,ids,chosen)
        return decisions
