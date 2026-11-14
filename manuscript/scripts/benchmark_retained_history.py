"""Frozen synthetic snapshot benchmark of the current lineage reference.

Measures recomputation after one new authentication, not Windows collection or
SQL equivalence. Independent expected candidates follow from generated serials.
"""
import hashlib,json,platform,statistics,sys,time,tracemalloc
from dataclasses import asdict
from pathlib import Path
ROOT=Path(__file__).resolve().parents[2]
sys.path.insert(0,str(ROOT))
from thesis_research.src.lineage_constraints.engine import LineageEngine,Observation,TimeRange
OUT=ROOT/'manuscript/reviews/2026-11-14/research_revision/history_benchmark'

def run():
    OUT.mkdir(parents=True,exist_ok=False)
    engine_path=ROOT/'thesis_research/src/lineage_constraints/engine.py'
    protocol=dict(issuances=[100,1000,5000],authentications=20,repetitions=5,
       incomplete_rates=[0,0.1],timing='One authentication add, recomputing all 20 retained authentication decisions',
       time_bounds='All issuance [0,0], authentication [1,1]',
       scope='Generated retained snapshots; excludes ingestion history, Windows collection, SQL and deployment',
       source_sha256=hashlib.sha256(engine_path.read_bytes()).hexdigest(),
       script_sha256=hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),python=sys.version,platform=platform.platform())
    (OUT/'protocol.json').write_text(json.dumps(protocol,indent=2)+'\n')
    rows=[]
    for n in protocol['issuances']:
      for rate in protocol['incomplete_rates']:
        durations=[]
        for repeat in range(protocol['repetitions']):
          engine=LineageEngine()
          weak=set()
          for i in range(n):
            missing=rate>0 and i%10==0
            r=Observation(f'c{i}','issuance',TimeRange(0,0),issuer='ca',serial='' if missing else f'{i+1:x}')
            engine.records[r.record_id]=r
            if missing:weak.add(r.record_id)
          for j in range(19):
            r=Observation(f'a{j}','authentication',TimeRange(1,1),issuer='ca',serial=f'{(j*10+1)%n+1:x}')
            engine.records[r.record_id]=r
          engine.recompute() # unmeasured warm-up
          auth=Observation('a19','authentication',TimeRange(1,1),issuer='ca',serial=f'{191%n+1:x}')
          started=time.perf_counter_ns(); engine.add(auth);durations.append((time.perf_counter_ns()-started)/1e6)
          for j in range(20):
            expected=weak|{f'c{(j*10+1)%n}'}
            decision=engine.decisions[f'a{j}']
            assert set(decision.candidate_ids)==expected
            assert decision.status==('ambiguous' if weak else 'resolved')
          checkpoint=engine.checkpoint()
          assert LineageEngine.restore(checkpoint).decisions==engine.decisions
        tracemalloc.start();engine.recompute();_,peak=tracemalloc.get_traced_memory();tracemalloc.stop()
        rows.append(dict(issuances=n,incomplete_rate=rate,repetitions=5,update_ms=durations,
            median_update_ms=statistics.median(durations),max_update_ms=max(durations),
            candidates_per_auth=1+len(weak),checkpoint_bytes=len(checkpoint.encode()),
            traced_recompute_peak_bytes=peak,verified_decisions=100))
    result=dict(protocol=protocol,rows=rows,status='passed',claims='Timing is descriptive on one shared host; snapshot records seeded outside timer; traced memory excludes resident state.')
    (OUT/'results.json').write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps(rows,indent=2))
if __name__=='__main__':run()
