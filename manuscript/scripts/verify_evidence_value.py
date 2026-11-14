"""Independent artifact/latent-label verifier; imports no detector or generator."""
from collections import defaultdict
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
BASE=ROOT/'manuscript/reviews/2026-11-14/extended_validation'
def run():
 out=BASE/'evidence_value';manifest=json.loads((out/'manifest.json').read_text())
 for name,h in manifest.items():assert hashlib.sha256((out/name).read_bytes()).hexdigest()==h
 cases={c['id']:c for c in map(json.loads,(out/'cases.jsonl').read_text().splitlines())};assert len(cases)==432
 protocol=json.loads((BASE/'evidence_value_protocol.json').read_text())
 for name,h in protocol['source_sha256'].items():assert hashlib.sha256((ROOT/name).read_bytes()).hexdigest()==h
 for c in cases.values():
  phys=c['physical'];truth=phys[c['target']]
  assert len({(p['issuer'],p['serial']) for p in phys})==len(phys)==c['n']
  for stage in c['stages']:
   auth=next(r for r in stage if r['kind']=='authentication')
   assert all(auth[k]==truth[k] for k in ['issuer','serial','thumbprint'])
   assert auth['success'] is True
   for r in stage:
    if r['kind']=='issuance':
     latent=phys[int(r['record_id'][1:])]
     assert all(not r[k] or r[k]==latent[k] for k in ['issuer','serial','thumbprint','skid'])
 predictions=list(map(json.loads,(out/'predictions.jsonl').read_text().splitlines()));seen=set();by_stage=defaultdict(dict);summary=defaultdict(lambda:dict(cases=0,correct_resolved=0,wrong_resolved=0,truth_retained=0))
 for r in predictions:
  c=cases[r['case']];truth='c'+str(c['target']);identity=(r['case'],r['step'],r['method']);assert identity not in seen;seen.add(identity)
  assert r['truth']==truth and r['final']==(r['step']==len(c['stages'])-1)
  assert set(r['candidates'])<={p['id'] for p in c['physical']}
  if r['chosen'] is not None:assert r['chosen'] in r['candidates']
  by_stage[(r['case'],r['step'])][r['method']]=r
  if r['method'] in ['ignore_exports','repair_k1']:assert truth in r['candidates']
  if c['mode']!='one_fault' and r['chosen'] is not None:assert r['chosen']==truth
  if r['final']:
   d=summary[r['method']];d['cases']+=1;d['correct_resolved']+=r['chosen']==truth;d['wrong_resolved']+=r['chosen'] is not None and r['chosen']!=truth;d['truth_retained']+=truth in r['candidates']
   if c['mode'] in ['clean','delayed'] and r['method'] in ['reference','sql_guarded','sql_strong']:assert r['chosen']==truth
 for methods in by_stage.values():
  assert len(methods)==5
  assert all(methods['reference'][k]==methods['sql_guarded'][k] for k in ['chosen','candidates','status'])
 result=json.loads((out/'results.json').read_text())
 for method,metrics in summary.items():
  for k,v in metrics.items():assert result['groups']['all/'+method][k]==v
 checked=dict(status='passed',cases=len(cases),prediction_rows=len(predictions),stage_equivalence_checks=len(by_stage),latent_certificate_identity_checks=True,within_budget_retention_checks=True,summary=summary)
 (BASE/'evidence_value_verification.json').write_text(json.dumps(checked,indent=2)+'\n');print(json.dumps(checked,indent=2))
if __name__=='__main__':run()
