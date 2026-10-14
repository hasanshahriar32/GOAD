"""Complete controlled case setup via fresh NTLM LDAP bindings.
Preserves prior failures and removes temporary setup memberships in finally.
"""
import datetime,json,os,hashlib
from pathlib import Path
import ldap3,winrm
from impacket.ldap import ldaptypes
from impacket.uuid import string_to_bin
ROOT=Path(__file__).resolve().parents[4];BASE=ROOT/'thesis_research/data/live_adcs_2026-10-14'
assert json.loads((BASE/'provisioning/manifest.json').read_text())['status_code']==0
out=BASE/'controlled_cases';pw=os.environ['GOAD_COLLECTION_PASSWORD']
control=winrm.Session('http://192.168.121.4:5985/wsman',auth=('ESSOS\\vagrant',pw),transport='ntlm')
records=[];cleanup=[]
def checked(c,action,dn,*args,**kwargs):
    ok=getattr(c,action)(dn,*args,**kwargs);records.append({'action':action,'dn':dn,'result':c.result.copy()})
    if not ok:raise RuntimeError(str(c.result))
def sid(value):
    s=ldaptypes.LDAP_SID();s.fromCanonical(value);return s
def ace(principal,mask,object_right=False,deny=False):
    cls=(ldaptypes.ACCESS_DENIED_OBJECT_ACE if deny else ldaptypes.ACCESS_ALLOWED_OBJECT_ACE) if object_right else ldaptypes.ACCESS_ALLOWED_ACE
    a=ldaptypes.ACE();a['AceType']=cls.ACE_TYPE;a['AceFlags']=0;a['Ace']=cls()
    a['Ace']['Mask']=ldaptypes.ACCESS_MASK();a['Ace']['Mask']['Mask']=mask;a['Ace']['Sid']=sid(principal)
    if object_right:
        a['Ace']['Flags']=1;a['Ace']['ObjectType']=string_to_bin('0e10c968-78fb-11d2-90d4-00c04f79dc55');a['Ace']['InheritedObjectType']=b''
    return a
def security(domain_sid,enroll_sid,user_sid,denied):
    sd=ldaptypes.SR_SECURITY_DESCRIPTOR();sd['Revision']=b'\x01';sd['Sbz1']=b'\x00';sd['Control']=0x9004
    sd['OwnerSid']=sid(domain_sid+'-512');sd['GroupSid']=sid(domain_sid+'-512');sd['Sacl']=b''
    acl=ldaptypes.ACL();acl['AclRevision']=4;acl['Sbz1']=0;acl['Sbz2']=0;acl.aces=[]
    if denied:acl.aces.append(ace(user_sid,256,True,True))
    acl.aces += [ace(domain_sid+'-'+rid,0x10000000) for rid in ['512','519','1000']]
    acl.aces += [ace('S-1-5-11',0x80000000),ace(enroll_sid,256,True)]
    sd['Dacl']=acl;return sd.getData()
try:
    for group in ['Domain Admins','Enterprise Admins']:
        r=control.run_ps("$ErrorActionPreference='Stop'; Add-ADGroupMember '"+group+"' vagrant")
        if r.status_code:raise RuntimeError('Setup membership failed')
    c=ldap3.Connection(ldap3.Server('192.168.121.4',get_info=ldap3.ALL),user='ESSOS\\vagrant',password=pw,authentication=ldap3.NTLM,auto_bind=True)
    domain='DC=essos,DC=local';pki='CN=Public Key Services,CN=Services,CN=Configuration,'+domain
    def entry(dn,attributes):
        if not c.search(dn,'(objectClass=*)',ldap3.BASE,attributes=attributes) or not c.entries:raise RuntimeError('Missing '+dn)
        return c.entries[0].entry_attributes_as_dict
    forest=entry('CN=OID,'+pki,['msPKI-Cert-Template-OID'])['msPKI-Cert-Template-OID'][0]
    ou='OU=CertGraphPublication,'+domain
    user_sid=entry('CN=cg.publication,'+ou,['objectSid'])['objectSid'][0]
    enroll_sid=entry('CN=CGPublicationEnroll,'+ou,['objectSid'])['objectSid'][0]
    domain_sid=user_sid.rsplit('-',1)[0];policy=forest+'.20261014.1'
    checked(c,'modify','CN=CGPublicationPolicy,CN=OID,'+pki,{'msDS-OIDToGroupLink':[(ldap3.MODIFY_REPLACE,['CN=CGPublicationPolicy,'+ou])]})
    definition=json.loads((ROOT/'ansible/roles/adcs_templates/files/ESC13.json').read_text())
    names=['CGPubPositive','CGPubApproval','CGPubSignature','CGPubDenied','CGPubUnpublished','CGPubNoPolicy']
    for i,name in enumerate(names):
        attrs={k:v for k,v in definition.items() if k not in ['name','displayName','objectClass','msPKI-Cert-Template-OID','msPKI-Certificate-Policy']}
        for k in ['pKIExpirationPeriod','pKIOverlapPeriod','pKIKeyUsage']:attrs[k]=bytes(attrs[k])
        attrs.update(displayName=name,**{'msPKI-Cert-Template-OID':forest+f'.20261014.{100+i}'})
        if name!='CGPubNoPolicy':attrs['msPKI-Certificate-Policy']=[policy]
        if name=='CGPubApproval':attrs['msPKI-Enrollment-Flag']=2
        if name=='CGPubSignature':attrs['msPKI-RA-Signature']=1
        attrs['nTSecurityDescriptor']=security(domain_sid,enroll_sid,user_sid,name=='CGPubDenied')
        checked(c,'add',f'CN={name},CN=Certificate Templates,'+pki,['top','pKICertificateTemplate'],attrs)
    checked(c,'modify','CN=CertGraph-Lab-CA,CN=Enrollment Services,'+pki,{'certificateTemplates':[(ldap3.MODIFY_ADD,[n for n in names if n!='CGPubUnpublished'])]})
    (out/'case_objects.json').write_text(json.dumps({'user_sid':user_sid,'enrollment_group_sid':enroll_sid,'policy_oid':policy,'templates':names,'scope':'Controlled enrollment tests; no exploitability label.'},indent=2))
finally:
    for group in ['Domain Admins','Enterprise Admins']:
        r=control.run_ps("$ErrorActionPreference='Stop'; Remove-ADGroupMember '"+group+"' vagrant -Confirm:$false")
        cleanup.append({'group':group,'removal_status':r.status_code})
    (out/'ldap_setup_operations.json').write_text(json.dumps({'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'operations':records,'cleanup':cleanup,'source_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest()},indent=2))
print('Created and published controlled templates; setup memberships removed:',all(r['removal_status']==0 for r in cleanup))
