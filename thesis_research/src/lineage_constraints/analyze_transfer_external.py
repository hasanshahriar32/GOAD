"""External configuration findings in distinct template/batch units."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

from .adjudicate_policy_matrix import events


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(matrix,adjudication,sigma_path,output):
    if output.exists():raise FileExistsError(output)
    for name,expected in read(sigma_path/'manifest.json').items():
        if sha(sigma_path/name)!=expected:raise ValueError('External output differs')
    protocol=read(matrix/'protocol.json');labels={r['trial']:r for r in read(adjudication)['trials']}
    sigma=read(sigma_path/'results.json');files={Path(f['path']).parent.name:f for f in sigma['files']}
    by_condition=defaultdict(Counter);rows=[]
    for block in protocol['blocks']:
        designs=[t for t in protocol['trials'] if t['block']==block['id']]
        for template in sorted({t['template'] for t in designs}):
            selected=[t for t in designs if t['template']==template];cases=[labels[t['id']] for t in selected]
            pre=[c['actual_certipy_template_result'] for c in cases];post=[c['actual_postrollback_certipy_template_result'] for c in cases]
            if pre[0]!=pre[1] or post[0]!=post[1]:raise AssertionError('Copied enumeration views disagree')
            relevant=set()
            for event in events(matrix/block['id']/'events.xml'):
                if event['fields'].get('TemplateInternalName')==template:
                    host,rid=event['id'].rsplit(':',1);relevant.add(host+':Security:'+rid)
            flags={rule:bool(set(ids)&relevant) for rule,ids in files[block['id']]['matches'].items()}
            row={'block':block['id'],'template':template,'condition':block['condition'],'certificate_cases':[t['id'] for t in selected],
                'certipy_pre_esc1':'ESC1' in pre[0].get('[!] Vulnerabilities',{}),
                'certipy_post_esc1':'ESC1' in post[0].get('[!] Vulnerabilities',{}),
                'sigma_subject_rule':flags.get('5ee3a654-372f-11ec-8d3d-0242ac130003',False),
                'sigma_eku_rule':flags.get('bfbd3291-de87-4b7c-88a2-d6a5deb28668',False),
                'verified_administrative_cases':sum(c['successful_administrator_use'] for c in cases)}
            rows.append(row);by_condition[block['condition']].update(template_batch_units=1,certificate_cases=len(cases),
                certipy_pre_esc1=int(row['certipy_pre_esc1']),certipy_post_esc1=int(row['certipy_post_esc1']),
                sigma_subject_rule=int(row['sigma_subject_rule']),sigma_eku_rule=int(row['sigma_eku_rule']),
                verified_administrative_cases=row['verified_administrative_cases'])
    result={'scope':'Twelve distinct template/batch/enroller units; two certificate cases share each actual pre/post enumeration. Configuration-risk findings are not attack-intent or certificate-use labels.',
        'units':rows,'by_condition':{k:dict(v) for k,v in by_condition.items()},'upstream_commit':sigma['upstream_commit'],'versions':sigma['versions'],
        'input_sha256':{str(p):sha(p) for p in (matrix/'protocol.json',adjudication,sigma_path/'manifest.json')},'source_sha256':sha(Path(__file__))}
    output.write_text(json.dumps(result,indent=2,sort_keys=True)+'\n');print(json.dumps(result['by_condition'],indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser()
    for name in ('matrix','adjudication','sigma_path','output'):p.add_argument(name,type=Path)
    a=p.parse_args();run(a.matrix,a.adjudication,a.sigma_path,a.output)
