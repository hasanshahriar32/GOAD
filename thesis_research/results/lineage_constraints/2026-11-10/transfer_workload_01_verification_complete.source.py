"""Verify prospective transfer inputs, provenance, key reuse and concurrency."""
import argparse
from collections import Counter,defaultdict
import hashlib
import json
from pathlib import Path

from cryptography import x509
from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding


def read(path):return json.loads(path.read_text())
def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()


def run(matrix,adjudication,output,ca_observation=None):
    if output.exists():raise FileExistsError(output)
    protocol=read(matrix/'protocol.json');run_manifest=read(matrix/'run_manifest.json')
    if run_manifest['attempted']!=len(protocol['trials']):raise AssertionError('Incomplete prospective workload')
    for name,expected in protocol['source_sha256'].items():
        if sha(matrix/'sources'/Path(name).name)!=expected:raise AssertionError('Frozen source differs')
    labels={t['trial']:t for t in read(adjudication)['trials']};groups=defaultdict(list);public_keys=defaultdict(set)
    outcomes=Counter();submissions=defaultdict(list);thumbprints=set();contexts=[]
    ca=None;ca_details={}
    if ca_observation:
        for name,expected in read(ca_observation/'manifest.json').items():
            if sha(ca_observation/name)!=expected:raise AssertionError('Public CA observation changed')
        raw=(ca_observation/'ca_certificate.cer').read_bytes()
        try:ca=x509.load_der_x509_certificate(raw)
        except ValueError:ca=x509.load_pem_x509_certificate(raw)
        ca.public_key().verify(ca.signature,ca.tbs_certificate_bytes,padding.PKCS1v15(),ca.signature_hash_algorithm)
        observed=json.loads(read(ca_observation/'observation.json')['stdout'])
        from cryptography.hazmat.primitives import hashes
        thumb=ca.fingerprint(hashes.SHA1()).hex()
        values=observed['ntauth_thumbprints'];values=[values] if isinstance(values,str) else values
        if thumb not in [v.replace(' ','').lower() for v in values]:raise AssertionError('CA absent from observed NTAuth membership')
        ca_details={'public_ca_sha256':sha(ca_observation/'ca_certificate.cer'),'self_signature_verified':True,
                    'observed_ntauth_membership':True,'scope':'Later public CA/trust observation; historical use remains grounded in raw KDC evidence'}
    for trial in protocol['trials']:
        path=matrix/trial['id']
        for name,expected in read(path/'manifest.json').items():
            if sha(path/name)!=expected:raise AssertionError('Raw trial changed')
        csr=x509.load_pem_x509_csr((path/'request.csr').read_bytes())
        csr.public_key().verify(csr.signature,csr.tbs_certrequest_bytes,padding.PKCS1v15(),csr.signature_hash_algorithm)
        if csr.signature_hash_algorithm.name!='sha256':raise AssertionError('Unexpected signature hash')
        raw=(path/'issued_certificate.cer').read_bytes()
        try:cert=x509.load_der_x509_certificate(raw)
        except ValueError:cert=x509.load_pem_x509_certificate(raw)
        if ca:
            if cert.issuer!=ca.subject:raise AssertionError('Leaf issuer differs from observed CA')
            ca.public_key().verify(cert.signature,cert.tbs_certificate_bytes,padding.PKCS1v15(),cert.signature_hash_algorithm)
        fmt=serialization.PublicFormat.SubjectPublicKeyInfo
        spki=csr.public_key().public_bytes(serialization.Encoding.DER,fmt)
        if spki!=cert.public_key().public_bytes(serialization.Encoding.DER,fmt):raise AssertionError('Certificate differs from request key')
        public_keys[trial['enroller']].add(hashlib.sha256(spki).hexdigest())
        groups[(trial['enroller'],trial['target'])].append(sha(path/'request.csr'))
        fingerprint=sha(path/'issued_certificate.cer')
        if fingerprint in thumbprints:raise AssertionError('A prior certificate was substituted')
        thumbprints.add(fingerprint)
        before=json.loads(read(path/'01_before_state.json')['stdout']);after=json.loads(read(path/'99_final_state.json')['stdout'])
        if before['name_flag']!=33554432 or after['name_flag']!=33554432:raise AssertionError('Unrestored template')
        context=json.loads(read(path/'00_domain_context.json')['stdout']);contexts.append(context)
        if context['dns_root']!='q1transfer.test' or context['computer']!='Q1XFER19':raise AssertionError('Not the transfer cohort')
        identity=read(path/'00_requester_identity.json')['stdout']
        if context['enroller_sid'] not in identity or context['domain_sid']+'-512' in identity:raise AssertionError('Unexpected request identity/privilege')
        linkage=read(path/'batch_evidence.json')
        if sha(matrix/trial['block']/'events.xml')!=linkage['security_sha256'] or sha(path/'events.xml')!=linkage['security_sha256']:raise AssertionError('Shared batch provenance differs')
        envelope=read(path/'09_submission.json')
        if envelope['host_after']<envelope['host_before']:raise AssertionError('Invalid command envelope')
        submissions[trial['block']].append((envelope['host_before'],envelope['host_after']))
        outcomes[labels[trial['id']]['observed_outcome']]+=1
    if any(len(set(values))!=1 for values in groups.values()):raise AssertionError('Repeated requests not byte-identical')
    if any(len(values)!=1 for values in public_keys.values()):raise AssertionError('Key reuse claim differs')
    if len(set.union(*public_keys.values()))!=len(public_keys):raise AssertionError('Different users unexpectedly share a private-key group')
    peaks={}
    for block,intervals in submissions.items():
        points=sorted([(start,1) for start,end in intervals]+[(end,-1) for start,end in intervals]);active=0;peak=0
        for stamp,delta in points:active+=delta;peak=max(peak,active)
        peaks[block]=peak
    report={'status':'passed','certificate_cases_checked':len(protocol['trials']),'unique_public_certificates':len(thumbprints),
        'observed_outcomes':dict(outcomes),'reused_key_groups':{k:len(v) for k,v in public_keys.items()},
        'fixed_signed_request_groups':len(groups),'peak_overlapping_submission_envelopes_by_batch':peaks,
        'domain_sid_values':sorted({c['domain_sid'] for c in contexts}),'issuer_names':sorted({c['ca_name'] for c in contexts}),
        'public_ca_verification':ca_details,'leaf_signatures_verified':len(thumbprints) if ca else 0,
        'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'adjudication_sha256':sha(adjudication),
        'scope':'Checks exact requests/keys, fresh forest context, ordinary enrollers, restoration and overlapping host command envelopes. Shared batch files are not independent event samples; not proof of simultaneous CA execution or OS-distribution transfer.'}
    output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n');output.with_suffix('.source.py').write_bytes(Path(__file__).read_bytes());print(json.dumps(report,indent=2))


if __name__=='__main__':
    p=argparse.ArgumentParser();p.add_argument('matrix',type=Path);p.add_argument('adjudication',type=Path);p.add_argument('output',type=Path);p.add_argument('--ca-observation',type=Path);a=p.parse_args();run(a.matrix,a.adjudication,a.output,a.ca_observation)
