"""Recheck all historical graph/budget instances with metadata restoration.

Imports the original generator/policy without running its main/figure writer.
The corrected executable policy differs only in edge-attribute restoration and
returning its selected cut for independent feasibility/reachability checks.
"""
import argparse
from datetime import datetime,timezone
import difflib
import hashlib
import inspect
import json
from pathlib import Path
import random
import time

import networkx as nx
from thesis_research.src.phase2_certgraph import run_real_stackelberg_eval as legacy

ROOT=Path(__file__).resolve().parents[3]
HISTORICAL=ROOT/'thesis_research/results/phase2/defense_results.json'


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+'\n')


def corrected_source():
    source=inspect.getsource(legacy.stackelberg_backward_causal_mincut)
    original=source
    assert source.count('            G_curr.remove_edge(u, v)')==1
    assert source.count('G_curr.add_edge(u, v, cost=c)')==1
    source=source.replace('def stackelberg_backward_causal_mincut','def metadata_preserving_adaptive',1)
    source=source.replace('            G_curr.remove_edge(u, v)','            edge_attributes = dict(G_curr[u][v])\n            G_curr.remove_edge(u, v)',1)
    source=source.replace('G_curr.add_edge(u, v, cost=c)','G_curr.add_edge(u, v, **edge_attributes)',1)
    source=source.replace('return pct, len(E_cut), compliance',"return {'pct': pct, 'cut': E_cut, 'cost': C_total, 'compliance': compliance}",1)
    return original,source


def freeze(path):
    if path.exists():raise FileExistsError(path)
    original,source=corrected_source()
    dump(path,{'schema':1,'declared_utc':datetime.now(timezone.utc).isoformat(),'base_seed':42,'topologies':30,'budgets':[6,12,18,24],
        'classes':['ESC1','ESC2','ESC3','ESC4','ESC9','ESC13'],'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in [Path(__file__),Path(legacy.__file__)]},
        'historical_input_sha256':sha(HISTORICAL),'corrected_function_sha256':hashlib.sha256(source.encode()).hexdigest(),
        'scope':'Same original 30 generated graphs and all four budgets; metadata correction and historical reproducibility, not enterprise or optimality evidence'})


def run(protocol_path,output):
    protocol=json.loads(protocol_path.read_text())
    for name,expected in protocol['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Frozen source changed')
    if sha(HISTORICAL)!=protocol['historical_input_sha256']:raise ValueError('Historical input changed')
    output.mkdir(parents=True,exist_ok=False);dump(output/'protocol.json',protocol)
    original,source=corrected_source()
    if hashlib.sha256(source.encode()).hexdigest()!=protocol['corrected_function_sha256']:raise ValueError('Derived function differs')
    (output/'executed_corrected_policy.py').write_text(source)
    (output/'correction.diff').write_text(''.join(difflib.unified_diff(original.splitlines(True),source.splitlines(True),fromfile='original_function',tofile='metadata_preserving_function')))
    namespace={'nx':nx,'evaluate_severed':legacy.evaluate_severed};exec(compile(source,'executed_corrected_policy.py','exec'),namespace)
    fixed=namespace['metadata_preserving_adaptive'];rows=[];graphs=[]
    for esc in protocol['classes']:
        for repeat in range(5):
            index=len(graphs);seed=42+index*17
            g,pairs,target=legacy.generate_topology_nx(esc,num_users=random.Random(seed).randint(45,65),num_groups=random.Random(seed).randint(14,20),num_computers=random.Random(seed).randint(5,10),seed=seed)
            graph={'id':index,'class':esc,'seed':seed,'nodes':list(g.nodes),'edges':[[u,v,dict(a)] for u,v,a in g.edges(data=True)],'pairs':pairs}
            graphs.append(graph)
            for budget in protocol['budgets']:
                started=time.perf_counter();old=legacy.stackelberg_backward_causal_mincut(g,pairs,budget);old_seconds=time.perf_counter()-started
                started=time.perf_counter();new=fixed(g,pairs,budget);new_seconds=time.perf_counter()-started
                greedy=legacy.greedy_capacity_disruption(g,pairs,budget)
                for u,v in new['cut']:
                    if not g[u][v].get('blockable',True):raise AssertionError('Immutable edge selected')
                if sum(g[u][v]['cost'] for u,v in new['cut'])>budget+1e-9:raise AssertionError('Budget violated')
                rows.append({'graph_id':index,'budget':budget,'legacy':{'pct':old[0],'edges':old[1],'compliance':old[2]},
                    'corrected':new,'static_greedy':{'pct':greedy[0],'edges':greedy[1],'compliance':greedy[2]},
                    'legacy_seconds':old_seconds,'corrected_seconds':new_seconds})
            print(json.dumps({'graph':index,'cases':len(rows)}),flush=True)
    dump(output/'graphs.json',graphs);dump(output/'per_case.json',rows)
    result={'cases':len(rows),'graphs':len(graphs),'equal_legacy_corrected_pct':sum(abs(r['legacy']['pct']-r['corrected']['pct'])<1e-12 for r in rows),
        'equal_legacy_corrected_edge_count':sum(r['legacy']['edges']==len(r['corrected']['cut']) for r in rows),'scope':protocol['scope']}
    dump(output/'results.json',result)
    sources=output/'sources';sources.mkdir()
    for name in protocol['source_sha256']:(sources/Path(name).name).write_bytes((ROOT/name).read_bytes())
    dump(output/'manifest.json',{str(p.relative_to(output)):sha(p) for p in output.rglob('*') if p.is_file()})
    print(json.dumps(result,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();s=p.add_subparsers(dest='action',required=True)
    f=s.add_parser('freeze');f.add_argument('protocol',type=Path)
    r=s.add_parser('run');r.add_argument('protocol',type=Path);r.add_argument('output',type=Path)
    a=p.parse_args()
    if a.action=='freeze':freeze(a.protocol)
    else:run(a.protocol,a.output)
