"""Verify the released public CSR/certificate/CA/KDC observations offline.

No original capture trees, detector code, passwords or private keys are read.
This verifies certificate-use observations, not event-source authenticity or
unobserved historical policy state.
"""
import argparse
from collections import Counter,defaultdict
import hashlib,json
from pathlib import Path
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import padding
from cryptography.x509.oid import NameOID

def hexkey(v):return ''.join((v or '').split()).replace(':','').lower().removeprefix('0x').lstrip('0') or '0'
def read(p):return json.loads(p.read_text())

def verify(root):
 for name,expected in read(root/'MANIFEST.json').items():
  if hashlib.sha256((root/name).read_bytes()).hexdigest()!=expected:raise ValueError('Release evidence changed: '+name)
 ca=x509.load_der_x509_certificate((root/'transfer_ca.der').read_bytes())
 counts=Counter();cohorts=defaultdict(Counter);fingerprints=set();later=0;signatures=0
 for case in read(root/'cases.json'):
  p=root/case;e=read(p/'evidence.json');ctx=e['context']
  cert=x509.load_der_x509_certificate((p/'certificate.der').read_bytes())
  csr=x509.load_der_x509_csr((p/'request.der').read_bytes())
  csr.public_key().verify(csr.signature,csr.tbs_certrequest_bytes,padding.PKCS1v15(),csr.signature_hash_algorithm)
  fmt=serialization.PublicFormat.SubjectPublicKeyInfo
  if cert.public_key().public_bytes(serialization.Encoding.DER,fmt)!=csr.public_key().public_bytes(serialization.Encoding.DER,fmt):raise ValueError('CSR key differs')
  serial=format(cert.serial_number,'x');thumb=cert.fingerprint(hashes.SHA1()).hex();fingerprint=cert.fingerprint(hashes.SHA256()).hex()
  if fingerprint in fingerprints:raise ValueError('Repeated public certificate')
  fingerprints.add(fingerprint)
  cn=cert.issuer.get_attributes_for_oid(NameOID.COMMON_NAME)[0].value
  if cn.casefold()!=ctx['ca_name'].casefold():raise ValueError('Issuer differs')
  rows=[r for r in e['ca_rows'] if hexkey(r['Serial Number'])==hexkey(serial) and hexkey(r['Certificate Hash'])==hexkey(thumb)]
  if len(rows)!=1:raise ValueError('Missing/nonunique CA row')
  requestid=rows[0]['Issued Request ID'];requester=ctx['domain_netbios']+'\\'+ctx['enroller_name']
  issued=[r for r in e['events'] if r['event_id']==4887 and r['fields'].get('RequestId')==requestid and r['fields'].get('Requester','').casefold()==requester.casefold()]
  if not issued:raise ValueError('No matching issuance event')
  successes=[];failures=[]
  for r in e['events']:
   f=r['fields']
   if r['event_id']!=4768 or hexkey(f.get('CertSerialNumber'))!=hexkey(serial) or hexkey(f.get('CertThumbprint'))!=hexkey(thumb):continue
   if f.get('CertIssuerName','').casefold()!=cn.casefold():continue
   if f.get('Status') in ('0','0x0','0x00000000') and f.get('PreAuthType') in ('15','16','17'):
    if f.get('TargetDomainName','').casefold()!=ctx['dns_root'].casefold():raise ValueError('Wrong target domain')
    pairs=[(ctx['admin_sid'],'administrator'),(ctx['enroller_sid'],ctx['enroller_name'].casefold())]
    if not any(f.get('TargetSid')==sid and f.get('TargetUserName','').casefold()==name for sid,name in pairs):raise ValueError('Unexpected target identity')
    successes.append(f)
   elif f.get('Status') not in ('',None,'0','0x0','0x00000000'):failures.append(f)
  system=[r for r in e['kdc_system_events'] if r['event_id'] in (39,40,41) and hexkey(r['fields'].get('SerialNumber'))==hexkey(serial) and hexkey(r['fields'].get('Thumbprint'))==hexkey(thumb)]
  admin=any(f.get('TargetSid')==ctx['admin_sid'] for f in successes)
  self_use=any(f.get('TargetSid')==ctx['enroller_sid'] for f in successes)
  outcome='privileged_certificate_use' if admin else 'self_certificate_use' if self_use else 'certificate_authentication_rejected' if failures or system else 'unverified'
  if outcome!=e['reported_outcome'] or outcome=='unverified':raise ValueError('Outcome differs: '+case)
  if e['policies']['before']['name_flag']!=e['policies']['restored']['name_flag']:raise ValueError('Template not restored')
  if e['cohort']=='transfer_workload_01':
   if cert.issuer!=ca.subject:raise ValueError('CA subject mismatch')
   ca.public_key().verify(cert.signature,cert.tbs_certificate_bytes,padding.PKCS1v15(),cert.signature_hash_algorithm);signatures+=1
  later+=e['ca_export_timing']=='later_read_only_supplement'
  counts[outcome]+=1;cohorts[e['cohort']][outcome]+=1
 if counts!=Counter(privileged_certificate_use=13,self_certificate_use=53,certificate_authentication_rejected=6):raise ValueError('Primary denominator differs')
 return {'status':'passed','certificate_cases':len(fingerprints),'successful_uses':66,'administrative_uses':13,
         'self_uses':53,'certificate_bound_rejections':6,'signed_requests_verified':len(fingerprints),
         'transfer_leaf_signatures_verified':signatures,'later_supplemented_ca_exports':later,
         'by_cohort':dict(cohorts),'scope':'Public certificate/CSR/CA/KDC selected-field verification; no private keys or raw capture tree required. Source integrity and missing historical policy are not established by these unkeyed hashes.'}

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('directory',type=Path);p.add_argument('--output',type=Path);a=p.parse_args();report=verify(a.directory)
 if a.output:a.output.write_text(json.dumps(report,indent=2,sort_keys=True)+'\n')
 print(json.dumps(report,indent=2,sort_keys=True))
