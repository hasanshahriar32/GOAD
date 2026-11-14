"""Independent saved-prefix, recovery-count and manifest verification."""
from pathlib import Path
import hashlib,json
ROOT=Path(__file__).resolve().parents[2]
OUT=ROOT/'manuscript/reviews/2026-11-14/extended_validation/streaming_identity'
def run():
 for name,h in json.loads((OUT/'manifest.json').read_text()).items():assert hashlib.sha256((OUT/name).read_bytes()).hexdigest()==h
 r=json.loads((OUT/'results.json').read_text());prefixes=0;checks=0;retractions={};previous={};last={}
 for line in (OUT/'predictions.jsonl').open():
  p=json.loads(line);assert p['reference']==p['sql_guarded'];prefixes+=1;checks+=len(p['reference']);key=(p['n'],p['seed'])
  for aid,(status,candidates,chosen) in p['reference'].items():
   if chosen is not None:assert chosen=='c'+aid[1:]
   old=previous.get((*key,aid));retractions[key]=retractions.get(key,0)+bool(old and old[0]=='resolved' and (status!='resolved' or chosen!=old[2]));previous[(*key,aid)]=(status,candidates,chosen)
  last[key]=p
 assert checks==r['checks']==35055
 for row in r['rows']:
  key=(row['issuances'],row['seed']);assert last[key]['step']==row['updates']-1
  assert retractions[key]==row['retractions']['reference']==row['retractions']['sql_guarded']==1
  assert all(v[0]=='resolved' for v in last[key]['reference'].values())
 output=dict(status='passed',prefixes=prefixes,decision_equivalence_checks=checks,runs=len(r['rows']),retractions_per_run=1,final_truth_checks=90,
 limit='Verifies saved outputs, expected IDs and aggregates; source execution performed separate restart assertions. Timing is not independently attested.')
 (OUT.parent/'streaming_verification.json').write_text(json.dumps(output,indent=2)+'\n');print(json.dumps(output,indent=2))
if __name__=='__main__':run()
