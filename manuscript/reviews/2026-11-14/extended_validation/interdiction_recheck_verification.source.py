"""Independent plain-adjacency cut feasibility and saved-value verification."""
import argparse
from decimal import Decimal
import hashlib
import json
from pathlib import Path


def run(directory,historical,output):
    if output.exists():raise FileExistsError(output)
    for name,expected in json.loads((directory/'manifest.json').read_text()).items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:raise AssertionError('Hash differs')
    graphs={g['id']:g for g in json.loads((directory/'graphs.json').read_text())};rows=json.loads((directory/'per_case.json').read_text())
    old=json.loads(historical.read_text());matched=0;greedy_matched=0;queries=0
    for row in rows:
        g=graphs[row['graph_id']];edges={(u,v):a for u,v,a in g['edges']};cut=[tuple(e) for e in row['corrected']['cut']]
        if len(set(cut))!=len(cut) or any(e not in edges or not edges[e].get('blockable',True) for e in cut):raise AssertionError('Invalid cut')
        cost=sum((Decimal(str(edges[e]['cost'])) for e in cut),Decimal(0))
        if cost>Decimal(row['budget'])+Decimal('0.000000001') or abs(float(cost)-row['corrected']['cost'])>1e-9:raise AssertionError('Budget/cost differs')
        adjacency={u:[] for u in g['nodes']}
        for u,v,a in g['edges']:
            if (u,v) not in set(cut):adjacency[u].append(v)
        severed=0
        for source,target in g['pairs']:
            seen={source};stack=[source]
            while stack:
                u=stack.pop()
                for v in adjacency[u]:
                    if v not in seen:seen.add(v);stack.append(v)
            severed+=target not in seen;queries+=1
        pct=100*severed/len(g['pairs'])
        if abs(pct-row['corrected']['pct'])>1e-9:raise AssertionError('Reachability objective differs')
        budget=str(row['budget']);index=row['graph_id']
        reported=old['empirical_metrics']['stackelberg_coadaptive_mincut'][budget]['paths_severed_per_topology'][index]
        greedy=old['empirical_metrics']['greedy_capacity_disruption'][budget]['paths_severed_per_topology'][index]
        matched+=abs(reported-row['legacy']['pct'])<1e-9;greedy_matched+=abs(greedy-row['static_greedy']['pct'])<1e-9
    result={'status':'passed','graph_budget_cases_checked':len(rows),'reachability_queries_checked':queries,
        'historical_legacy_percentages_reproduced':matched,'historical_static_greedy_percentages_reproduced':greedy_matched,
        'corrected_vs_legacy_same_percentages':sum(abs(r['legacy']['pct']-r['corrected']['pct'])<1e-9 for r in rows),
        'scope':'Independent cut/cost/objective checks and historical value comparison; no optimality/equilibrium claim',
        'input_manifest_sha256':hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest(),
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');output.with_suffix('.source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for n in ('directory','historical','output'):p.add_argument(n,type=Path)
    a=p.parse_args();run(a.directory,a.historical,a.output)
