"""Export allowlisted public certificate evidence; never copy live capture trees.

Only public certificates/CSRs, selected CA rows, selected event fields and
recorded policy projections leave the original capture. Private keys, command
transcripts, tickets, process-creation events and account secrets are excluded.
"""
import argparse
import csv
import hashlib
import io
import json
from pathlib import Path
import xml.etree.ElementTree as ET
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization

ROOT=Path(__file__).resolve().parents[2]
LIVE=ROOT/'thesis_research/data/lineage_live/2026-11-10'
RESULTS=ROOT/'thesis_research/results/lineage_constraints/2026-11-10'
COHORTS={
 'paired_policy_matrix_02':'paired_policy_matrix_02_adjudication_final.json',
 'independent_2019_matrix_02':'independent_2019_matrix_02_adjudication_final.json',
 'current_patch_upn_01':'current_patch_upn_01_review/adjudication.json',
 'current_patch_sid_01':'current_patch_sid_01_review/adjudication.json',
 'transfer_workload_01':'transfer_workload_01_adjudication_final.json',
}
EVENT_FIELDS={
 4887:{'RequestId','Requester','Subject','Attributes'},
 4768:{'TargetUserName','TargetDomainName','TargetSid','Status','PreAuthType',
       'CertIssuerName','CertSerialNumber','CertThumbprint'},
 5136:{'SubjectUserName','SubjectUserSid','ObjectDN','ObjectGUID',
       'AttributeLDAPDisplayName','AttributeValue','OperationType'},
}
SYSTEM_FIELDS={'AccountName','Subject','Issuer','SerialNumber','Thumbprint','IssuancePolicies'}
CONTEXT_FIELDS={'domain_sid','viserys_sid','dns_root','build','ubr','os','admin_sid','computer',
                'enroller_name','enroller_sid','mutator_name','mutator_sid','domain_netbios',
                'ca_name','template_name'}
POLICY_FIELDS={'dn','template_oid','ra_signatures','name_flag','eku','sddl','enrollment_flag'}
CA_FIELDS={'Issued Request ID','Requester Name','Serial Number','Certificate Hash','Certificate Template'}

def read(p):return json.loads(p.read_text())
def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def dump(p,obj):p.write_text(json.dumps(obj,indent=2,sort_keys=True)+'\n')
def hexkey(v):return ''.join((v or '').split()).replace(':','').lower().removeprefix('0x').lstrip('0') or '0'

def selected_events(path,system_log=False):
 if not path.exists():return []
 rows=[]
 for ev in ET.parse(path).getroot():
  sy=next(c for c in ev if c.tag.rsplit('}',1)[-1]=='System')
  meta={c.tag.rsplit('}',1)[-1]:c.text or '' for c in sy}
  eid=int(meta['EventID'])
  if system_log and eid not in (39,40,41):continue
  if not system_log and eid not in EVENT_FIELDS:continue
  fields=SYSTEM_FIELDS if system_log else EVENT_FIELDS[eid]
  values={c.attrib['Name']:c.text or '' for c in ev.iter()
          if c.tag.rsplit('}',1)[-1]=='Data' and c.attrib.get('Name') in fields}
  stamp=next((c.attrib.get('SystemTime') for c in sy if c.tag.rsplit('}',1)[-1]=='TimeCreated'),None)
  rows.append({'event_id':eid,'record_id':meta['EventRecordID'],'computer':meta.get('Computer'),
               'recorded_time':stamp,'fields':values})
 return rows

def export(output):
 output.mkdir(parents=True,exist_ok=False)
 supplement=LIVE/'current_patch_ca_supplement_01'
 supplement_rows=list(csv.DictReader(io.StringIO(read(supplement/'ca_export.json')['stdout'])))
 cases=[]
 for cohort,judgement in COHORTS.items():
  matrix=LIVE/cohort;labels={r['trial']:r for r in read(RESULTS/judgement)['trials']}
  protocol=read(matrix/'protocol.json')
  for trial in protocol['trials']:
   src=matrix/trial['id'];label=labels[trial['id']];dest=output/cohort/trial['id'];dest.mkdir(parents=True)
   manifest=read(src/'manifest.json')
   public_inputs=['issued_certificate.cer','request.csr','events.xml','00_domain_context.json',
                  '01_before_state.json','04_assigned_state.json','99_final_state.json']
   for optional in ['99_ca_bridge.json','kdc_system_events.xml','04_assigned_state_effective_policy.json']:
    if (src/optional).exists():public_inputs.append(optional)
   for name in public_inputs:
    if name in manifest and digest(src/name)!=manifest[name]:raise ValueError('Capture hash differs: '+cohort+'/'+trial['id']+'/'+name)
   raw=(src/'issued_certificate.cer').read_bytes()
   try:cert=x509.load_der_x509_certificate(raw)
   except ValueError:cert=x509.load_pem_x509_certificate(raw)
   csr_raw=(src/'request.csr').read_bytes();csr=x509.load_pem_x509_csr(csr_raw)
   # Re-encode parsed public structures, excluding any appended PEM blocks.
   (dest/'certificate.der').write_bytes(cert.public_bytes(serialization.Encoding.DER))
   (dest/'request.der').write_bytes(csr.public_bytes(serialization.Encoding.DER))
   serial=format(cert.serial_number,'x');thumb=cert.fingerprint(hashes.SHA1()).hex()
   if cert.fingerprint(hashes.SHA256()).hex()!=label['sha256']:raise ValueError('Adjudication certificate differs')
   bridge=src/'99_ca_bridge.json';later=not bridge.exists()
   if later:
    if cohort not in ('current_patch_upn_01','current_patch_sid_01'):raise ValueError('Unexpected missing CA export')
    ca_rows=supplement_rows
   else:ca_rows=list(csv.DictReader(io.StringIO(read(bridge)['stdout'])))
   matching=[{k:v for k,v in row.items() if k in CA_FIELDS} for row in ca_rows
             if hexkey(row.get('Serial Number'))==hexkey(serial) and hexkey(row.get('Certificate Hash'))==hexkey(thumb)]
   if len(matching)!=1:raise ValueError('CA identity not unique')
   context=json.loads(read(src/'00_domain_context.json')['stdout'])
   context={k:v for k,v in context.items() if k in CONTEXT_FIELDS}
   if cohort=='paired_policy_matrix_02':
    context.setdefault('enroller_name','viserys.targaryen');context.setdefault('enroller_sid',context['viserys_sid'])
    context.setdefault('domain_netbios','ESSOS');context.setdefault('ca_name','CertGraph-Lab-CA')
   policies={}
   for name,label_name in [('01_before_state.json','before'),('04_assigned_state.json','assigned'),
                           ('99_final_state.json','restored'),('04_assigned_state_effective_policy.json','effective')]:
    if (src/name).exists():policies[label_name]={k:v for k,v in json.loads(read(src/name)['stdout']).items() if k in POLICY_FIELDS}
   data={'schema_version':1,'cohort':cohort,'trial':trial['id'],'condition':trial['condition'],
         'context':context,'policies':policies,'ca_rows':matching,
         'ca_export_timing':'later_read_only_supplement' if later else 'trial_capture',
         'events':selected_events(src/'events.xml'),
         'kdc_system_events':selected_events(src/'kdc_system_events.xml',True),
         'reported_outcome':label['observed_outcome'],
         'mutation_history_validation':label.get('mutation_history_validation'),
         'source_provenance':{'trial_manifest_sha256':digest(src/'manifest.json'),
                              'adjudication_sha256':digest(RESULTS/judgement),
                              'selected_source_sha256':{name:digest(src/name) for name in public_inputs}}}
   if later:data['source_provenance']['later_ca_export_sha256']=digest(supplement/'ca_export.json')
   dump(dest/'evidence.json',data);cases.append(str(dest.relative_to(output)))
 # Only the prospective transfer cohort has this separately observed CA proof.
 raw=(LIVE/'transfer_ca_public_02/ca_certificate.cer').read_bytes()
 try:ca=x509.load_der_x509_certificate(raw)
 except ValueError:ca=x509.load_pem_x509_certificate(raw)
 (output/'transfer_ca.der').write_bytes(ca.public_bytes(serialization.Encoding.DER))
 dump(output/'cases.json',cases)
 dump(output/'MANIFEST.json',{str(p.relative_to(output)):digest(p) for p in sorted(output.rglob('*')) if p.is_file()})
 print(json.dumps({'public_cases':len(cases),'output':str(output),'private_keys_copied':0}))

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('output',type=Path);export(p.parse_args().output)
