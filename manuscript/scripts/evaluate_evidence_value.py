"""Independent factorial generator for equal-input identity/evidence value.

Frozen before execution; no imports from the earlier simulator. Labels are the
physical certificate selected before projection, not a correlator's answer.
"""
from collections import defaultdict
from dataclasses import asdict,replace
import hashlib,itertools,json,platform,random,statistics,sys,time
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT))
from thesis_research.src.lineage_constraints.engine import LineageEngine,Observation,TimeRange
from thesis_research.src.lineage_constraints.sql_lineage import SQLiteLineage
from thesis_research.src.lineage_constraints.repair import reason_with_bridge_budget
BASE=ROOT/'manuscript/reviews/2026-11-14/extended_validation'

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,x):p.write_text(json.dumps(x,indent=2,sort_keys=True)+'\n')
def protocol():
 p=BASE/'evidence_value_protocol.json'
 sources=[Path(__file__)]+[ROOT/'thesis_research/src/lineage_constraints'/n for n in ['engine.py','sql_lineage.py','repair.py']]
 x=dict(seeds=[91009,92003,93001],issuances=[4,16,64],missing_rates=[0,.25,.75],exports=['none','clean','one_fault','delayed'],replicates=4,
 primary=['wrong_resolved','correct_resolved','truth_retained','candidate_count','retractions'],
 projection='Identity only, all timestamps [0,0], no mutation/intent labels; same records per primary method',
 ablation='ignore_exports deliberately removes optional evidence; repair enumerates deletion of at most one bridge',
 scope='Independent synthetic generator, not independent operational deployment or enterprise prevalence',
 source_sha256={str(p.relative_to(ROOT)):sha(p) for p in sources},python=platform.python_version())
 if p.exists():raise FileExistsError(p)
 dump(p,x);return x

def generated(seed,n,missing,mode,index):
 rng=random.Random(f'ev:{seed}:{n}:{missing}:{mode}:{index}')
 prefix=f'{seed}-{n}-{missing}-{mode}-{index}'
 physical=[];records=[];bridges=[]
 target=rng.randrange(n)
 for i in range(n):
  issuer=f'ca-{i%2}';serial=f'{i//2+1:x}';thumb=hashlib.sha256(f'{prefix}:cert:{i}'.encode()).hexdigest()[:40]
  skid=hashlib.sha256(f'{prefix}:key:{i//3}'.encode()).hexdigest()[:40]
  cert=dict(id=f'c{i}',issuer=issuer,serial=serial,thumbprint=thumb,skid=skid)
  physical.append(cert);hidden=rng.random()<missing
  records.append(Observation(f'c{i}','issuance',TimeRange(0,0),issuer=issuer,request_id=str(i//2+1),serial='' if hidden else serial,thumbprint='' if hidden else thumb,skid='' if hidden else skid,template='template-'+str(i%3),principal='enroller-'+str(i%2)))
  bridges.append(Observation(f'b{i}','bridge',TimeRange(0,0),issuer=issuer,request_id=str(i//2+1),serial=serial,thumbprint=thumb,skid=skid))
 actual=physical[target]
 auth=Observation('a','authentication',TimeRange(0,0),issuer=actual['issuer'],serial=actual['serial'],thumbprint=actual['thumbprint'],principal='authorized-target-'+str(index%2))
 if mode=='one_fault':
  # One optional row lies about the queried certificate; raw anchors stay truthful.
  b=bridges[target];bridges[target]=replace(b,serial='ff'+b.serial,thumbprint='f'*40)
 if mode=='none':bridges=[]
 stages=[records+[auth]]
 if bridges:
  if mode=='delayed':stages.append(records+[auth]+bridges[:n//2])
  stages.append(records+[auth]+bridges)
 return prefix,physical,target,stages

def evaluate(records,method):
 if method=='repair_k1':
  d=reason_with_bridge_budget(records,[],'a',1)
  return d.certain_issuance_id,set(d.possible_issuance_ids),d.status
 if method.startswith('sql'):
  db=SQLiteLineage('guarded' if method=='sql_guarded' else 'strong_join')
  # Insert canonical records without timing every intermediate SQL query.
  try:
   for r in records:db.add(r)
   d=db.decisions()['a'];return d.issuance_id,set(d.candidates),d.status
  finally:db.close()
 e=LineageEngine();e.records={r.record_id:r for r in records if not(method=='ignore_exports' and r.kind=='bridge')};e.recompute();d=e.decisions['a']
 return d.issuance_id,set(d.candidate_ids),d.status

def run():
 x=protocol();out=BASE/'evidence_value';out.mkdir(exist_ok=False)
 totals=defaultdict(lambda:defaultdict(int));counts=defaultdict(list);retractions=defaultdict(int);timings=defaultdict(list)
 with (out/'cases.jsonl').open('w') as cf,(out/'predictions.jsonl').open('w') as pf:
  for seed,n,missing,mode,index in itertools.product(x['seeds'],x['issuances'],x['missing_rates'],x['exports'],range(x['replicates'])):
   cid,physical,target,stages=generated(seed,n,missing,mode,index);truth=f'c{target}'
   cf.write(json.dumps(dict(id=cid,seed=seed,n=n,missing_rate=missing,mode=mode,physical=physical,target=target,stages=[[asdict(r) for r in stage] for stage in stages]))+'\n')
   prev={}
   for step,records in enumerate(stages):
    outputs={}
    for method in ['reference','sql_guarded','sql_strong','ignore_exports','repair_k1']:
     start=time.perf_counter();chosen,candidates,status=evaluate(records,method);timings[method].append(time.perf_counter()-start)
     outputs[method]=(chosen,candidates,status)
     retract=prev.get(method) is not None and (chosen!=prev[method]);retractions[method]+=retract
     pf.write(json.dumps(dict(case=cid,step=step,method=method,chosen=chosen,candidates=sorted(candidates),status=status,retracted=retract,truth=truth,final=step==len(stages)-1))+'\n')
     prev[method]=chosen
     if step==len(stages)-1:
      for group in ['all','export:'+mode,'missing:'+str(missing)]:
       key=group+'/'+method;t=totals[key];t['cases']+=1;t['correct_resolved']+=chosen==truth;t['wrong_resolved']+=chosen is not None and chosen!=truth;t['truth_retained']+=truth in candidates
       counts[key].append(len(candidates))
    assert outputs['reference']==outputs['sql_guarded']
    if mode!='one_fault':
     assert all(c is None or c==truth for c,_,_ in outputs.values())
 for key,t in totals.items():
  a=sorted(counts[key]);t['mean_candidates']=statistics.mean(a);t['p95_candidates']=a[(95*len(a)+99)//100-1];t['max_candidates']=max(a)
 result=dict(status='passed',cases=len(counts['all/reference']),groups=dict(totals),prefix_retractions=dict(retractions),
 measured_runner_seconds={k:sum(v) for k,v in timings.items()},timing_scope='Includes fresh SQL loading and intermediate add queries, excludes generator; not a fair engine speed comparison',
 protocol_sha256=sha(BASE/'evidence_value_protocol.json'))
 dump(out/'results.json',result)
 dump(out/'manifest.json',{str(p.relative_to(out)):sha(p) for p in out.iterdir() if p.is_file()})
 print(json.dumps({k:v for k,v in result['groups'].items() if k.startswith('all/')},indent=2))
if __name__=='__main__':run()
