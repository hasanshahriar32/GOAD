"""Prospective new-forest concurrent, multi-template and reused-key workload.

No outcome labels enter inference. All private keys remain in memory or temporary
0600 PFX files. Four requests per batch share an exported evidence interval;
certificate outcomes, rather than copied event files, are the sampling units.
"""
import argparse
import base64
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime,timezone
import hashlib
import json
import os
from pathlib import Path
import random
import re
import shutil
import subprocess
import tempfile
import time
import xml.etree.ElementTree as ET

from asn1crypto.core import UTF8String
from cryptography import x509
from cryptography.hazmat.primitives import hashes,serialization
from cryptography.hazmat.primitives.asymmetric import rsa
from cryptography.hazmat.primitives.serialization import pkcs12,NoEncryption
from cryptography.x509.oid import NameOID,ObjectIdentifier

from .independent_policy_2019 import IndependentRunner,system_export_script
from .lab.transfer_2019 import connection,credentials,DOMAIN,NETBIOS,CA
from scripts.capture_trace7_split_actor_delayed_pkinit import get_current_event_record_id,export_events_since,pull_file_winrm

ROOT=Path(__file__).resolve().parents[3]
EVENT_IDS=(4624,4634,4647,4648,4672,4688,4689,4768,4769,4771,4616,4886,4887,4888,4898,4899,5136)
USERS={"Q1TransferA":"q1.reader","Q1TransferB":"q1.operator"}
ORIGINAL=33554432


def sha(path):return hashlib.sha256(path.read_bytes()).hexdigest()
def dump(path,data):path.write_text(json.dumps(data,indent=2,sort_keys=True)+"\n")
def manifest(path):dump(path/"manifest.json",{str(p.relative_to(path)):sha(p) for p in path.rglob('*') if p.is_file() and p.name!='manifest.json'})


def freeze(path):
    if path.exists():raise FileExistsError(path)
    blocks=[];trials=[]
    for repeat in range(2):
        conditions=['baseline','enabled','rollback_first'];random.Random(83003+repeat).shuffle(conditions)
        for condition in conditions:
            bid=f"b{len(blocks)+1:02d}";ids=[]
            for template,user in USERS.items():
                for target in ('self','admin'):
                    tid=f"r{len(blocks)+1:02d}_{template}_{target}"
                    trials.append({'id':tid,'block':bid,'template':template,'enroller':user,'target':target,
                        'condition':'transfer_'+condition+'_'+target,'expected_admin_certificate':condition=='enabled' and target=='admin'})
                    ids.append(tid)
            blocks.append({'id':bid,'condition':condition,'trials':ids})
    sources=[Path(__file__),Path(__file__).with_name('independent_policy_2019.py'),Path(__file__).parent/'lab/transfer_2019.py',
        Path(__file__).parent/'lab/provision_2019.py',Path(__file__).with_name('adjudicate_policy_matrix.py'),
        Path(__file__).with_name('evaluate_live_identity.py'),Path(__file__).with_name('engine.py'),Path(__file__).with_name('goad.py'),
        ROOT/'scripts/capture_trace7_split_actor_delayed_pkinit.py']
    dump(path,{'schema':1,'declared_utc':datetime.now(timezone.utc).isoformat(),'domain':DOMAIN,'ca':CA,
        'required_build':'17763.9376','blocks':blocks,'trials':trials,
        'scope':'Prospective transfer to a new forest/CA/accounts/templates, derived from the same Windows image family; not an independent OS distribution or enterprise prevalence sample',
        'design':'Six batches; four concurrent enrollments/authentications per batch; two templates and ordinary enrollers; each user reuses one RSA key across reissuances; fixed signed request per user/target',
        'key_reuse':'Repeated issuance with the same public key; not a Windows renewal-protocol experiment',
        'timing':'Identity-only inference; no claim to calibrate cross-host audit-clock bounds',
        'source_sha256':{str(p.relative_to(ROOT)):sha(p) for p in sources}})


class Runner(IndependentRunner):
    def __init__(self,output,certipy,user=None,context=None):
        self.output=output;self.certipy=certipy;self.secret=credentials();self.admin=connection()
        self.user=user;self.enroller=connection(user=user) if user else None;self.context=context

    def state(self,name,template):
        body="$nc=(Get-ADRootDSE).configurationNamingContext;$dn='CN="+template+",CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc;$t=Get-ADObject $dn -Properties *;"
        body+="@{dn=$dn;name_flag=[int]$t.'msPKI-Certificate-Name-Flag';enrollment_flag=$t.'msPKI-Enrollment-Flag';ra_signatures=$t.'msPKI-RA-Signature';eku=$t.pKIExtendedKeyUsage;sddl=$t.nTSecurityDescriptor.GetSecurityDescriptorSddlForm('All');template_oid=$t.'msPKI-Cert-Template-OID'}|ConvertTo-Json -Depth 5 -Compress"
        return self.ps(self.admin,name,body)

    def flag(self,name,value):
        body="if((Get-ADDomain).DNSRoot -ne '"+DOMAIN+"'){throw 'Wrong transfer forest'};$nc=(Get-ADRootDSE).configurationNamingContext;"
        for template in USERS:
            body+="Set-ADObject ('CN="+template+",CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Replace @{'msPKI-Certificate-Name-Flag'="+str(value)+"};"
        return self.ps(self.admin,name,body+"'TRANSFER_WRITE_COMPLETE'")

    def refresh(self,name):
        self.ps(self.admin,name,"Restart-Service CertSvc -Force;(Get-Service CertSvc).WaitForStatus('Running',[TimeSpan]::FromSeconds(30));'CA_RUNNING'")
        config=self.context['computer']+'.'+DOMAIN+'\\'+CA
        self.ps(self.admin,name+'_rpc',"$ok=$false;for($i=0;$i -lt 15;$i++){certutil.exe -config '"+config+"' -ping;if($LASTEXITCODE -eq 0){$ok=$true;break};Start-Sleep 2};if(-not $ok){throw 'RPC_NOT_READY'};exit 0")

    def find_user(self,name,user):
        path=self.output/name;path.mkdir()
        command=[self.certipy,'find','-u',user+'@'+DOMAIN,'-p',self.secret['enroller_password'],'-dc-ip','127.0.0.4','-target-ip','127.0.0.4',
            '-dc-host',self.context['computer']+'.'+DOMAIN,'-ldap-scheme','ldap','-ldap-port','389','-dc-only','-json','-text','-output','certipy','-timeout','10']
        started=time.monotonic();r=subprocess.run(command,cwd=path,capture_output=True,text=True,timeout=120)
        command[command.index('-p')+1]='<private environment>'
        stdout,stderr=r.stdout,r.stderr
        for value in self.secret.values():stdout=stdout.replace(value,'<redacted>');stderr=stderr.replace(value,'<redacted>')
        dump(path/'execution.json',{'command':command,'returncode':r.returncode,'stdout':stdout,'stderr':stderr,'elapsed_seconds':time.monotonic()-started})
        if r.returncode:raise RuntimeError('Certipy enumeration failed')
        return path


def request_trial(trial,path,context,certipy,key,csr):
    r=Runner(path,certipy,trial['enroller'],context)
    r.ps(r.enroller,'00_requester_identity','whoami /user;whoami /groups')
    (path/'request.csr').write_bytes(csr)
    dump(path/'request_binding.json',{'block':trial['block'],'requested_upn':('administrator' if trial['target']=='admin' else trial['enroller'])+'@'+DOMAIN,
        'request_sha256':hashlib.sha256(csr).hexdigest(),'signature_hash':'sha256','key_reuse_group':trial['enroller']})
    remote='C:\\'+trial['template']+'\\'+trial['id']
    r.ps(r.admin,'08_stage_public_csr',"[IO.File]::WriteAllBytes('"+remote+".req',[Convert]::FromBase64String('"+base64.b64encode(csr).decode()+"'))")
    if pull_file_winrm(r.admin,remote+'.req')!=csr:raise ValueError('CSR transfer differs')
    config=context['computer']+'.'+DOMAIN+'\\'+CA
    script="$p=Start-Process certreq.exe -ArgumentList '-submit -q -f -config \""+config+"\" -attrib \"CertificateTemplate:"+trial['template']+"\" "+remote+".req "+remote+".cer' -Wait -PassThru -NoNewWindow;'SUBMIT_EXIT:'+$p.ExitCode"
    row=r.ps(r.enroller,'09_submission',script)
    code=int(re.search(r'SUBMIT_EXIT:(-?\d+)',row['stdout'])[1])
    if code:raise RuntimeError('Native enrollment failed: '+str(code))
    raw=pull_file_winrm(r.admin,remote+'.cer');(path/'issued_certificate.cer').write_bytes(raw)
    try:cert=x509.load_der_x509_certificate(raw)
    except ValueError:cert=x509.load_pem_x509_certificate(raw)
    fmt=serialization.PublicFormat.SubjectPublicKeyInfo
    if cert.public_key().public_bytes(serialization.Encoding.DER,fmt)!=key.public_key().public_bytes(serialization.Encoding.DER,fmt):raise ValueError('Certificate key differs')
    upns=[UTF8String.load(n.value).native for n in cert.extensions.get_extension_for_class(x509.SubjectAlternativeName).value
          if isinstance(n,x509.OtherName) and n.type_id.dotted_string=='1.3.6.1.4.1.311.20.2.3']
    identity={'serial':format(cert.serial_number,'x'),'sha1':cert.fingerprint(hashes.SHA1()).hex(),'sha256':cert.fingerprint(hashes.SHA256()).hex(),'upns':upns}
    dump(path/'certificate_identity.json',identity)
    return cert,identity


def authenticate(cert,key,certipy,username,path):
    with tempfile.TemporaryDirectory(prefix='goad-q1-transfer-private-') as temporary:
        pfx=Path(temporary)/'issued.pfx';fd=os.open(pfx,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(fd,'wb') as stream:stream.write(pkcs12.serialize_key_and_certificates(b'auth',key,cert,None,NoEncryption()))
        before=time.time();mono=time.monotonic_ns()
        r=subprocess.run([certipy,'auth','-pfx',str(pfx),'-dc-ip','127.0.0.4','-username',username,'-domain',DOMAIN,'-no-hash','-no-save'],cwd=temporary,capture_output=True,text=True,timeout=90)
        dump(path,{'returncode':r.returncode,'stdout':r.stdout,'stderr':r.stderr,'host_before':before,'host_after':time.time(),
            'elapsed_ns':time.monotonic_ns()-mono,'scope':'Diagnostic output only; exact matching KDC outcome is adjudicated separately'})


def run(protocol_path,output,certipy):
    protocol=json.loads(protocol_path.read_text())
    for name,expected in protocol['source_sha256'].items():
        if sha(ROOT/name)!=expected:raise ValueError('Frozen source changed: '+name)
    output.mkdir(parents=True,exist_ok=False);dump(output/'protocol.json',protocol)
    source=output/'sources';source.mkdir()
    for name in protocol['source_sha256']:(source/Path(name).name).write_bytes((ROOT/name).read_bytes())
    runner=Runner(output,certipy)
    context_script="""$d=Get-ADDomain;$a=Get-ADUser Administrator;$v=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
if($d.DNSRoot -ne 'q1transfer.test' -or $v.UBR -ne 9376){throw 'Wrong transfer forest/build'}
if(Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'){throw 'Pending servicing reboot'}
$users=@(Get-ADUser q1.reader;Get-ADUser q1.operator)
@{dns_root=$d.DNSRoot;domain_netbios=$d.NetBIOSName;domain_sid=$d.DomainSID.Value;admin_sid=$a.SID.Value;mutator_name=$a.SamAccountName;mutator_sid=$a.SID.Value;computer=$env:COMPUTERNAME;ca_name='Q1-Transfer-CA';build=$v.CurrentBuild;ubr=$v.UBR;utc=[DateTime]::UtcNow.ToString('o');users=@($users|Select SamAccountName,@{n='sid';e={$_.SID.Value}})}|ConvertTo-Json -Depth 5 -Compress"""
    inventory=runner.ps(runner.admin,'00_inventory',context_script);context=json.loads(inventory['stdout'])
    observed=datetime.fromisoformat(context['utc'].replace('Z','+00:00')).timestamp()
    if not inventory['host_before']-5<=observed<=inventory['host_after']+5:raise RuntimeError('Transfer clock preflight failed')
    runner.context=context
    users={u['SamAccountName']:u['sid'] for u in context['users']}
    # Enable telemetry only after credential-bearing forest setup has finished.
    runner.ps(runner.admin,'01_capture_audits',"""auditpol.exe /set /subcategory:'Process Creation' /success:enable /failure:enable
auditpol.exe /set /subcategory:'Process Termination' /success:enable /failure:enable
auditpol.exe /set /subcategory:'Kerberos Service Ticket Operations' /success:enable /failure:enable
auditpol.exe /set /subcategory:'Logon' /success:enable /failure:enable
auditpol.exe /set /subcategory:'Logoff' /success:enable /failure:enable
'AUDIT_CONFIGURATION_COMPLETE'""")
    keys={user:rsa.generate_private_key(public_exponent=65537,key_size=2048) for user in users};requests={}
    for user in users:
        for target in ('self','admin'):
            name='administrator' if target=='admin' else user;sid=context['admin_sid'] if target=='admin' else users[user]
            names=[x509.OtherName(ObjectIdentifier('1.3.6.1.4.1.311.20.2.3'),UTF8String(name+'@'+DOMAIN).dump()),x509.UniformResourceIdentifier('tag:microsoft.com,2022-09-14:sid:'+sid)]
            requests[(user,target)]=x509.CertificateSigningRequestBuilder().subject_name(x509.Name([x509.NameAttribute(NameOID.COMMON_NAME,user)])).add_extension(x509.SubjectAlternativeName(names),False).sign(keys[user],hashes.SHA256()).public_bytes(serialization.Encoding.PEM)
    trials={t['id']:t for t in protocol['trials']};completed=[]
    for block in protocol['blocks']:
        batch=output/block['id'];batch.mkdir();runner.output=batch
        security=get_current_event_record_id(runner.admin);system=get_current_event_record_id(runner.admin,'System')
        dump(batch/'event_boundary.json',{'Security':security,'System':system})
        initial={t:runner.state('before_'+t,t) for t in USERS}
        if any(json.loads(p['stdout'])['name_flag']!=ORIGINAL for p in initial.values()):raise RuntimeError('Transfer baseline not restored')
        try:
            if block['condition']!='baseline':runner.flag('enable',ORIGINAL|1)
            if block['condition']=='rollback_first':runner.flag('rollback_first',ORIGINAL)
            assigned={t:runner.state('assigned_'+t,t) for t in USERS};runner.refresh('pre_refresh')
            pre={u:runner.find_user('pre_'+u,u) for u in users}
            for tid in block['trials']:
                trial=trials[tid];path=output/tid;path.mkdir()
                c={k:v for k,v in context.items() if k!='users'}
                c.update(enroller_name=trial['enroller'],enroller_sid=users[trial['enroller']],template_name=trial['template'])
                dump(path/'00_domain_context.json',{'stdout':json.dumps(c),'source':'00_inventory.json; directory-observed account selected by the frozen trial'})
                dump(path/'01_before_state.json',initial[trial['template']]);dump(path/'04_assigned_state.json',assigned[trial['template']]);dump(path/'04_assigned_state_effective_policy.json',assigned[trial['template']])
                dump(path/'event_boundary.json',{'source':'Security','start_record_id':security})
                shutil.copytree(pre[trial['enroller']],path/'06_certipy_find')
            with ThreadPoolExecutor(max_workers=4) as pool:
                pending={tid:pool.submit(request_trial,trials[tid],output/tid,
                    json.loads(json.loads((output/tid/'00_domain_context.json').read_text())['stdout']),certipy,keys[trials[tid]['enroller']],requests[(trials[tid]['enroller'],trials[tid]['target'])]) for tid in block['trials']}
                issued={tid:f.result() for tid,f in pending.items()}
            runner.flag('restore_before_auth',ORIGINAL);runner.refresh('post_refresh')
            post={u:runner.find_user('post_'+u,u) for u in users}
            with ThreadPoolExecutor(max_workers=4) as pool:
                pending=[]
                for tid,(cert,identity) in issued.items():
                    trial=trials[tid];username='administrator' if 'administrator@'+DOMAIN in [u.casefold() for u in identity['upns']] else trial['enroller']
                    pending.append(pool.submit(authenticate,cert,keys[trial['enroller']],certipy,username,output/tid/'13_certipy_auth.json'))
                for future in pending:future.result()
        finally:
            runner.flag('99_restore',ORIGINAL)
            final={t:runner.state('99_final_'+t,t) for t in USERS}
            if any(json.loads(p['stdout'])['name_flag']!=ORIGINAL for p in final.values()):raise RuntimeError('Transfer restoration failed')
        time.sleep(2)
        raw=export_events_since(runner.admin,security,EVENT_IDS)
        ET.ElementTree(ET.fromstring('<Events>'+raw+'</Events>')).write(batch/'events.xml',encoding='utf-8',xml_declaration=True)
        system_row=runner.ps(runner.admin,'kdc_system_export',system_export_script(system))
        ET.ElementTree(ET.fromstring('<Events>'+system_row['stdout']+'</Events>')).write(batch/'kdc_system_events.xml',encoding='utf-8',xml_declaration=True)
        ca=runner.ps(runner.admin,'ca_export',"certutil.exe -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv;if($LASTEXITCODE -ne 0){throw 'CA export failed'};exit 0")
        for tid in block['trials']:
            trial=trials[tid];path=output/tid
            shutil.copyfile(batch/'events.xml',path/'events.xml');shutil.copyfile(batch/'kdc_system_events.xml',path/'kdc_system_events.xml')
            shutil.copytree(post[trial['enroller']],path/'12_postrollback_certipy_find')
            dump(path/'99_ca_bridge.json',ca);dump(path/'99_final_state.json',final[trial['template']])
            dump(path/'outcome.json',{'id':tid,'condition':trial['condition'],'status':'issued_auth_attempted','native_submission_exit':0,'restored':True,
                'scope':'Certificate outcome in a shared concurrent batch; not an independently randomized event file'})
            dump(path/'batch_evidence.json',{'batch':block['id'],'security_sha256':sha(batch/'events.xml'),'shared_trial_ids':block['trials']})
            manifest(path);completed.append(tid)
        manifest(batch);dump(output/'progress.json',completed);print(json.dumps({'block':block['id'],'completed_certificates':len(completed)}),flush=True)
    dump(output/'run_manifest.json',{'planned':len(trials),'attempted':len(completed),'batches':len(protocol['blocks']),'scope':protocol['scope']})


if __name__=='__main__':
    parser=argparse.ArgumentParser();sub=parser.add_subparsers(dest='action',required=True)
    f=sub.add_parser('freeze');f.add_argument('protocol',type=Path)
    r=sub.add_parser('run');r.add_argument('protocol',type=Path);r.add_argument('output',type=Path);r.add_argument('--certipy',required=True)
    args=parser.parse_args()
    if args.action=='freeze':freeze(args.protocol)
    else:run(args.protocol,args.output,args.certipy)
