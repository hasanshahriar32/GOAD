"""Stronger dynamic baselines on the saved exact-optimum small instances."""
from collections import deque
from itertools import combinations
from pathlib import Path
import hashlib,json,time
ROOT=Path(__file__).resolve().parents[2]
SOURCE=ROOT/'thesis_research/results/lineage_constraints/2026-11-10/interdiction_audit/results.json'
OUT=ROOT/'manuscript/reviews/2026-11-14/extended_validation/interdiction_baselines'
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def count(edges,pairs,cut):
 adj={}
 for u,v,_ in edges:
  if (u,v) not in cut:adj.setdefault(u,[]).append(v)
 total=0
 for s,t in pairs:
  seen={s};queue=deque([s])
  while queue:
   for v in adj.get(queue.popleft(),[]):
    if v not in seen:seen.add(v);queue.append(v)
  total+=t not in seen
 return total

def greedy(edges,pairs,budget,width):
 cuts=set();cost=0;checks=0
 eligible={(u,v):a['cost'] for u,v,a in edges if a.get('blockable',True)}
 while True:
  before=count(edges,pairs,cuts);best=None
  candidates=sorted(set(eligible)-cuts)
  for size in range(1,width+1):
   for proposal in combinations(candidates,size):
    added=sum(eligible[e] for e in proposal)
    if cost+added>budget:continue
    after=count(edges,pairs,cuts|set(proposal));checks+=1;gain=after-before
    # Single-edge greedy continues zero-gain steps; pair lookahead also uses
    # the declared deterministic smaller-set/cost/lexicographic tie break.
    value=(gain/added,gain,-added,-size)
    if best is None or value>best[0]:best=(value,proposal,added)
  if best is None:break
  cuts.update(best[1]);cost+=best[2]
 return dict(cut=sorted(cuts),cost=cost,severed_pairs=count(edges,pairs,cuts),candidate_subsets_checked=checks)

def run():
 OUT.mkdir(exist_ok=False)
 (OUT/'protocol.json').write_text(json.dumps(dict(input_sha256=sha(SOURCE),source_sha256=sha(Path(__file__)),
 objective='Severed-pair count under assigned budget, lambda=0; dynamic width 1/2 marginal gain per added cost',
 scope='Exploratory stronger baselines on 60 saved seven-node exact instances; not a new algorithm or enterprise disruption'),indent=2)+'\n')
 data=json.loads(SOURCE.read_text());rows=[]
 for case in data:
  row={k:case[k] for k in ['seed','case','budget']};edges=case['edges'];pairs=case['pairs']
  # Independently enumerate feasible subsets using a plain adjacency oracle.
  feasible=[(u,v) for u,v,a in edges if a.get('blockable',True)];costs={(u,v):a['cost'] for u,v,a in edges};opt=-1
  for size in range(len(feasible)+1):
   for cut in combinations(feasible,size):
    if sum(costs[e] for e in cut)<=case['budget']:opt=max(opt,count(edges,pairs,set(cut)))
  assert opt==case['exact']['severed_pairs']
  for width in [1,2]:
   start=time.perf_counter();r=greedy(edges,pairs,case['budget'],width);r['seconds']=time.perf_counter()-start
   assert r['cost']<=case['budget'] and r['severed_pairs']<=opt
   assert all(e in feasible for e in map(tuple,r['cut']))
   row['dynamic_'+str(width)]=r
  row['optimum']=opt;row['adaptive']=case['metadata_preserving_adaptive']['severed_pairs'];row['static']=case['static_greedy_severed'];rows.append(row)
 summary={m:dict(optimum_matches=sum((r[m]['severed_pairs'] if m.startswith('dynamic') else r[m])==r['optimum'] for r in rows),
 max_gap=max(r['optimum']-(r[m]['severed_pairs'] if m.startswith('dynamic') else r[m]) for r in rows)) for m in ['adaptive','static','dynamic_1','dynamic_2']}
 (OUT/'results.json').write_text(json.dumps(dict(cases=len(rows),summary=summary,rows=rows,exact_oracle='Independent exhaustive plain-adjacency reachability'),indent=2)+'\n')
 print(json.dumps(summary,indent=2))
if __name__=='__main__':run()
