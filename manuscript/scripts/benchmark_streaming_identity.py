"""Matched incremental replay of reference and SQLite identity projection.

All timestamps erased equally; no temporal solver speed comparison is implied.
"""
from dataclasses import asdict
from pathlib import Path
import hashlib,json,platform,random,statistics,sys,time
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from thesis_research.src.lineage_constraints.engine import LineageEngine,Observation,TimeRange
from thesis_research.src.lineage_constraints.sql_lineage import SQLiteLineage
BASE=ROOT/'manuscript/reviews/2026-11-14/extended_validation/streaming_identity'
def dump(p,v):p.write_text(json.dumps(v,indent=2,sort_keys=True)+'\n')
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def key(ds):return {k:(v.status,tuple(v.candidate_ids if hasattr(v,'candidate_ids') else v.candidates),v.issuance_id) for k,v in ds.items()}
def workload(n,seed):
 rng=random.Random(seed);records=[];exports=[]
 for i in range(n):
  missing=i%5==0;serial=f'{i+1:x}'
  records.append(Observation(f'c{i}','issuance',TimeRange(0,0),issuer='ca',request_id=str(i+1),serial='' if missing else serial))
  if missing:exports.append(Observation(f'b{i}','bridge',TimeRange(0,0),issuer='ca',request_id=str(i+1),serial=serial))
 rng.shuffle(records)
 steps=[('add',r) for r in records[:20]]
 steps += [('add',Observation(f'a{i}','authentication',TimeRange(0,0),issuer='ca',serial=f'{i+1:x}')) for i in range(10)]
 steps += [('add',r) for r in records[20:]]
 steps += [('add',r) for r in exports]
 # Duplicate delivery and a conflicting optional export, followed by correction.
 steps += [('add',records[0]),('add',exports[0])]
 bad=Observation('bad','bridge',TimeRange(0,0),issuer='ca',request_id='1',serial='ff')
 steps += [('add',bad),('remove',bad)]
 return steps

def run():
 BASE.mkdir(exist_ok=False)
 sources=[Path(__file__)]+[ROOT/'thesis_research/src/lineage_constraints'/n for n in ['engine.py','sql_lineage.py']]
 protocol=dict(issuances=[100,300,600],seeds=[94009,95003,96001],authentications=10,missing_serial_rate=.2,
 evidence='Complete issuer scope; all event times zero; delayed correct bridges, duplicates, conflicting bridge/remove, checkpoint recovery',
 scope='Matched identity projection on one host; no Windows, mutation, intent or production interference claim',
 source_sha256={str(p.relative_to(ROOT)):digest(p) for p in sources},python=platform.python_version(),platform=platform.platform())
 dump(BASE/'protocol.json',protocol);rows=[]
 with (BASE/'predictions.jsonl').open('w') as pf:
  for n in protocol['issuances']:
   for seed in protocol['seeds']:
    e=LineageEngine();sql=SQLiteLineage();times={'reference':[],'sql_guarded':[]};observed={};checks=0;retractions={'reference':0,'sql_guarded':0};old={}
    steps=workload(n,seed)
    dump(BASE/f'workload_{n}_{seed}.json',[dict(op=op,record=asdict(r)) for op,r in steps])
    for step,(op,r) in enumerate(steps):
     if op=='add':observed[r.record_id]=r
     else:observed.pop(r.record_id,None)
     methods=['reference','sql_guarded'] if (seed+step)%2 else ['sql_guarded','reference']
     outputs={}
     for method in methods:
      obj=e if method=='reference' else sql
      start=time.perf_counter_ns();getattr(obj,op)(r if op=='add' else r.record_id);times[method].append((time.perf_counter_ns()-start)/1e6)
      values=key(e.decisions if method=='reference' else sql.decisions());outputs[method]=values
      for aid,v in values.items():
       prior=old.get((method,aid));retractions[method]+=bool(prior and prior[0]=='resolved' and (v[0]!='resolved' or prior[2]!=v[2]));old[(method,aid)]=v
     assert outputs['reference']==outputs['sql_guarded'];checks+=len(outputs['reference'])
     for aid,(status,candidates,chosen) in outputs['reference'].items():
      if chosen is not None:assert chosen=='c'+aid[1:]
     pf.write(json.dumps(dict(n=n,seed=seed,step=step,reference=outputs['reference'],sql_guarded=outputs['sql_guarded']))+'\n')
     if step==len(steps)//2:
      start=time.perf_counter();e=LineageEngine.restore(e.checkpoint());reference_restart=time.perf_counter()-start
      start=time.perf_counter();sql.close();sql=SQLiteLineage()
      for item in observed.values():sql.add(item)
      sql_restart=time.perf_counter()-start
      assert key(e.decisions)==key(sql.decisions())
    assert e.decisions['a0'].status=='resolved'
    row=dict(issuances=n,seed=seed,updates=len(steps),decision_equivalence_checks=checks,retractions=retractions,
      checkpoint_bytes=len(e.checkpoint().encode()),restart_seconds=dict(reference=reference_restart,sql_reinsert=sql_restart))
    for method,a in times.items():
     a_sorted=sorted(a);row[method]=dict(total_update_ms=sum(a),median_update_ms=statistics.median(a),p95_update_ms=a_sorted[(95*len(a)+99)//100-1],max_update_ms=max(a),raw_ms=a)
    rows.append(row);sql.close()
 dump(BASE/'results.json',dict(status='passed',rows=rows,timing='Only add/remove calls timed; SQL decision query used again for verification outside timer. SQL add includes its internal query. No inference-only shortcut. SQL restart uses repeated insertion; unlike serialized reference restore.',checks=sum(r['decision_equivalence_checks'] for r in rows)))
 dump(BASE/'manifest.json',{str(p.relative_to(BASE)):digest(p) for p in BASE.iterdir() if p.is_file()})
 print(json.dumps([{k:r[k] for k in ['issuances','seed','updates','decision_equivalence_checks','retractions']} for r in rows],indent=2))
if __name__=='__main__':run()
