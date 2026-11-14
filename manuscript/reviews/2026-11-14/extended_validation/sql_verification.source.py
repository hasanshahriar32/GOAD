"""Independent set-based oracle over saved inputs; imports neither correlator."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path


def ident(record):
    def hexval(value,serial=False):
        value=''.join((value or '').split()).replace(':','').lower().removeprefix('0x')
        return (value.lstrip('0') or '0') if value and serial else value
    return {'issuer':record['issuer'].strip().casefold(),'serial':hexval(record['serial'],True),
            'thumbprint':hexval(record['thumbprint']),'skid':hexval(record['skid'])}


def oracle(records,method):
    profiles=[]
    for issue in records.values():
        if issue['kind']!='issuance' or issue['success'] is not True:continue
        facts=[issue]+[b for b in records.values() if b['kind']=='bridge' and issue['issuer'].strip() and issue['request_id']
            and b['issuer'].strip().casefold()==issue['issuer'].strip().casefold() and b['request_id']==issue['request_id']]
        fields={k:{ident(f)[k] for f in facts if ident(f)[k]} for k in ident(issue)}
        conflict=any(len(values)>1 for values in fields.values()) or any(len({f[k].strip().casefold() for f in facts if f[k].strip()})>1 for k in ('template','principal'))
        profiles.append((issue['record_id'],fields,conflict))
    result={}
    for auth in records.values():
        if auth['kind']!='authentication':continue
        aid=auth['record_id'];a=ident(auth);candidates=[]
        if auth['success'] is True and auth['preauth_type'] in (15,16,17):
            for iid,fields,conflict in profiles:
                if a['issuer'] and fields['issuer'] and a['issuer'] not in fields['issuer']:continue
                mismatch=any(a[k] and fields[k] and a[k] not in fields[k] for k in a)
                shared={k for k in ('serial','thumbprint','skid') if a[k] and a[k] in fields[k]}
                strong='thumbprint' in shared or ('serial' in shared and a['issuer'] and fields['issuer'])
                if method=='sql_strong_join':accept=not conflict and not mismatch and strong
                else:accept=(conflict and (shared or not mismatch)) or (not conflict and not mismatch)
                if accept:candidates.append((iid,conflict,bool(strong)))
        candidates.sort();chosen=None
        if auth['success'] is not True:status='failed_or_unknown_authentication'
        elif auth['preauth_type'] not in (15,16,17):status='not_certificate_authentication'
        elif any(c[1] for c in candidates):status='conflicting_evidence'
        elif not candidates:status='no_consistent_candidate'
        elif not any(a[k] for k in ('serial','thumbprint','skid')):status='missing_identifiers'
        elif len(candidates)>1:status='ambiguous'
        elif not candidates[0][2]:status='insufficient_identity'
        else:status='resolved';chosen=candidates[0][0]
        result[aid]=(status,[c[0] for c in candidates],chosen)
    return result


def run(directory,output):
    if output.exists():raise FileExistsError(output)
    manifest=json.loads((directory/'manifest.json').read_text())
    for name,expected in manifest.items():
        if hashlib.sha256((directory/name).read_bytes()).hexdigest()!=expected:raise ValueError('Saved artifact changed')
    rows=[json.loads(line) for line in (directory/'predictions.jsonl').read_text().splitlines()]
    index={(r['case_id'],r['step'],r['method'],r['auth_id']):r for r in rows}
    if len(index)!=len(rows):raise AssertionError('Duplicate prediction key')
    checked=0;random_labels=0;family=defaultdict(Counter);finals=defaultdict(Counter)
    for line in (directory/'cases.jsonl').read_text().splitlines():
        case=json.loads(line);records={};previous={};latent=case['latent_truth']
        if latent:
            expected=latent['selected_issuance_id'] if latent['authentication_succeeded'] else None
            if case['truth_issuance_id']!=expected:raise AssertionError('Latent truth differs')
            random_labels+=1
        for step,item in enumerate(case['steps']):
            record=item['record']
            if item['operation']=='add':records[record['record_id']]=record
            else:records.pop(record['record_id'],None)
            for method in ('constraint_identity','sql_guarded','sql_strong_join'):
                decisions=oracle(records,method)
                for aid,(status,candidates,chosen) in decisions.items():
                    row=index[(case['case_id'],step,method,aid)]
                    if (row['status'],row['candidates'],row['issuance_id'])!=(status,candidates,chosen):raise AssertionError('Independent oracle differs')
                    old=previous.get((method,aid));retract=bool(old and old[0]=='resolved' and (status!='resolved' or old[2]!=chosen))
                    if row['retracts_resolved_link']!=retract:raise AssertionError('Retraction differs')
                    previous[(method,aid)]=(status,candidates,chosen);checked+=1
                    if step==len(case['steps'])-1:
                        wrong=int(chosen is not None and chosen!=case['truth_issuance_id'])
                        family[(case['family'],method)].update(cases=1,wrong_certain=wrong,correct_certain=int(chosen is not None and chosen==case['truth_issuance_id']))
                        group='outside_assumption' if case['assumption_violation'] else 'main'
                        finals[(group,method)].update(cases=1,resolved=int(status=='resolved'),correct_certain=int(chosen is not None and chosen==case['truth_issuance_id']),
                            wrong_certain=wrong,successful_truth=int(case['truth_issuance_id'] is not None),candidate_retained=int(case['truth_issuance_id'] is not None and case['truth_issuance_id'] in candidates))
    result=json.loads((directory/'results.json').read_text())
    for (group,method),counts in finals.items():
        if dict(counts)!=result['by_group_method'][group+'/'+method]:raise AssertionError('Aggregate differs')
    if checked!=len(rows):raise AssertionError('Unchecked rows')
    report={'status':'passed','prediction_rows_checked':checked,'random_latent_labels_checked':random_labels,
        'by_family_method':{f+'/'+m:dict(v) for (f,m),v in family.items()},
        'interpretation':'Identity-only projection erases chronology. The 60 preceding_auth controls produce wrong terminal linkage in every method; 60 outside_model_forgery controls also fool every method. These failures are retained, not treated as enterprise rates.',
        'input_manifest_sha256':hashlib.sha256((directory/'manifest.json').read_bytes()).hexdigest(),
        'verifier_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');output.with_suffix('.source.py').write_bytes(Path(__file__).read_bytes())
    print(json.dumps({k:v for k,v in report.items() if k!='by_family_method'},indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('output',type=Path);a=p.parse_args();run(a.directory,a.output)
