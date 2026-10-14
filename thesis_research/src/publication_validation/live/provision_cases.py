"""Create six controlled cases only after successful, snapshot-protected CA setup."""
import base64,gzip,hashlib,json,os,secrets,datetime
from pathlib import Path
import winrm
ROOT=Path(__file__).resolve().parents[4]
BASE=ROOT/'thesis_research/data/live_adcs_2026-10-14'
assert json.loads((BASE/'provisioning/manifest.json').read_text())['status_code']==0
out=BASE/'controlled_cases';out.mkdir(parents=True,exist_ok=True)
script=Path(__file__).with_name('provision_cases.ps1');source=script.read_text()
definition=json.loads((ROOT/'ansible/roles/adcs_templates/files/ESC13.json').read_text())
public="$TemplateDefinition='"+json.dumps(definition,separators=(',',':')).replace("'","''")+"' | ConvertFrom-Json;\n"+source
pw=os.environ['GOAD_COLLECTION_PASSWORD'];case_pw=secrets.token_urlsafe(24)+'aA1!'
credential_path=Path('/tmp/certgraph_lab_credentials.json')
# Private test-account credential is not part of the evidence repository.
if credential_path.exists():
    case_pw=json.loads(credential_path.read_text())['password']
else:
    fd=os.open(credential_path,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(fd,'w') as f:json.dump({'username':'cg.publication@essos.local','password':case_pw},f)
control=winrm.Session('http://192.168.121.4:5985/wsman',auth=('ESSOS\\vagrant',pw),transport='ntlm',operation_timeout_sec=30,read_timeout_sec=40)
for group in ['Domain Admins','Enterprise Admins']:
    result=control.run_ps("$ErrorActionPreference='Stop'; Add-ADGroupMember '"+group+"' vagrant")
    if result.status_code:raise RuntimeError('Setup membership failed')
s=winrm.Session('http://192.168.121.4:5985/wsman',auth=('ESSOS\\vagrant',pw),transport='ntlm',operation_timeout_sec=30,read_timeout_sec=40)
encoded=base64.b64encode(gzip.compress(public.encode())).decode()
remote=r'C:\Windows\Temp\CertGraphPublicationCases.b64'
# Stage only public source, in small commands; the account password stays in memory.
for i in range(0,len(encoded),1800):
    action='WriteAllText' if i==0 else 'AppendAllText'
    r=s.run_ps(f"[IO.File]::{action}('{remote}','{encoded[i:i+1800]}')")
    if r.status_code:raise RuntimeError('Public script staging failed')
prefix="$CasePassword=ConvertTo-SecureString '"+case_pw+"' -AsPlainText -Force;"
prefix+="$SetupCredential=New-Object Management.Automation.PSCredential('ESSOS\\vagrant',(ConvertTo-SecureString '"+pw.replace("'","''")+"' -AsPlainText -Force));"
loader=prefix+"try {$b=[Convert]::FromBase64String([IO.File]::ReadAllText('"+remote+"'));$m=New-Object IO.MemoryStream(,$b);$g=New-Object IO.Compression.GzipStream($m,[IO.Compression.CompressionMode]::Decompress);$r=New-Object IO.StreamReader($g);Invoke-Expression $r.ReadToEnd()} finally {Remove-Item '"+remote+"' -ErrorAction SilentlyContinue}"
expected={'CGPubPositive':'issued','CGPubApproval':'pending','CGPubSignature':'denied_unsigned','CGPubDenied':'denied_template_acl','CGPubUnpublished':'unsupported_template','CGPubNoPolicy':'issued_without_policy'}
(out/'expected_outcomes.json').write_text(json.dumps({'recorded_before_provisioning_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'cases':expected,'scope':'Enrollment outcomes only; not complete ESC13 exploitability labels.'},indent=2)+'\n')
try:
    r=s.run_ps(loader)
finally:
    clean=[]
    for group in ['Domain Admins','Enterprise Admins']:
        result=control.run_ps("$ErrorActionPreference='Stop'; Remove-ADGroupMember '"+group+"' vagrant -Confirm:$false")
        clean.append({'group':group,'removal_status':result.status_code})
    (out/'membership_cleanup.json').write_text(json.dumps(clean,indent=2))
for name,body in [('stdout',r.std_out),('stderr',r.std_err)]:
    (out/f'provision_{name}.txt').write_text(body.decode(errors='replace').replace(case_pw,'<redacted>').replace(pw,'<redacted>'))
meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'status_code':r.status_code,'script_sha256':hashlib.sha256(public.encode()).hexdigest(),'private_credentials_location':str(credential_path)}
(out/'provision_manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
if r.status_code:raise SystemExit(r.status_code)
