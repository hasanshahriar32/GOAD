"""Complete CA configuration with temporary setup memberships, restoring them.
The existing lab vagrant account is not left as a domain/enterprise admin.
"""
import datetime,json,os,hashlib,subprocess
from pathlib import Path
import winrm
ROOT=Path(__file__).resolve().parents[4]
out=ROOT/'thesis_research/data/live_adcs_2026-10-14/provisioning'
pw=os.environ['GOAD_COLLECTION_PASSWORD']
for vm in ['provider_GOAD-DC03','provider_GOAD-SRV03']:
    subprocess.run(['virsh','-c','qemu:///system','snapshot-info',vm,'publication-pre-adcs-20261014'],check=True,capture_output=True)
for f in ['manifest.json','ca_install_stdout.txt','ca_install_stderr.txt']:
    p=out/f
    if p.exists() and not (out/('attempt1_'+f)).exists():p.rename(out/('attempt1_'+f))
dc=winrm.Session('http://192.168.121.4:5985/wsman',auth=('ESSOS\\vagrant',pw),transport='ntlm',operation_timeout_sec=30,read_timeout_sec=40)
pre=dc.run_ps("$ErrorActionPreference='Stop'; Import-Module ActiveDirectory; @(Get-ADUser vagrant -Properties memberOf).memberOf | ConvertTo-Json -Compress")
if pre.status_code:raise RuntimeError('Could not record original setup-account memberships')
before=json.loads(pre.std_out);before=[before] if isinstance(before,str) else before
needed=[g for g in ['Domain Admins','Enterprise Admins'] if not any(dn.startswith('CN='+g+',') for dn in before)]
(out/'setup_memberships_before.json').write_text(json.dumps({'before':before,'temporary_groups':needed},indent=2))
status=1;cleanup=[]
try:
    for g in needed:
        r=dc.run_ps("$ErrorActionPreference='Stop'; Add-ADGroupMember -Identity '"+g+"' -Members vagrant")
        if r.status_code:raise RuntimeError('Temporary setup membership failed: '+r.std_err.decode(errors='replace').replace(pw,'<redacted>'))
    srv=winrm.Session('http://192.168.121.209:5985/wsman',auth=('ESSOS\\vagrant',pw),transport='ntlm',operation_timeout_sec=30,read_timeout_sec=40)
    public="""$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue';
if ($env:COMPUTERNAME -ne 'BRAAVOS') {throw 'Wrong host'}
if (Test-Path 'HKLM:\\SYSTEM\\CurrentControlSet\\Services\\CertSvc\\Configuration\\CertGraph-Lab-CA') {throw 'CA already configured'}
Install-AdcsCertificationAuthority -Credential $PublicationCredential -CAType EnterpriseRootCA -CACommonName 'CertGraph-Lab-CA' -CryptoProviderName 'RSA#Microsoft Software Key Storage Provider' -KeyLength 2048 -HashAlgorithmName SHA256 -ValidityPeriod Years -ValidityPeriodUnits 1 -Force | ConvertTo-Json -Depth 4
Get-Service CertSvc | Select-Object Name,Status | ConvertTo-Json -Compress
"""
    prefix="$PublicationCredential=New-Object Management.Automation.PSCredential('ESSOS\\vagrant',(ConvertTo-SecureString '"+pw.replace("'","''")+"' -AsPlainText -Force));"
    r=srv.run_ps(prefix+public);status=r.status_code
    (out/'ca_install_stdout.txt').write_text(r.std_out.decode(errors='replace').replace(pw,'<redacted>'))
    (out/'ca_install_stderr.txt').write_text(r.std_err.decode(errors='replace').replace(pw,'<redacted>'))
finally:
    for g in needed:
        r=dc.run_ps("$ErrorActionPreference='Stop'; Remove-ADGroupMember -Identity '"+g+"' -Members vagrant -Confirm:$false")
        cleanup.append({'group':g,'removal_status':r.status_code})
    (out/'setup_membership_cleanup.json').write_text(json.dumps(cleanup,indent=2))
meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':'BRAAVOS','status_code':status,'baseline_snapshot':'publication-pre-adcs-20261014','script_sha256':hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),'ca_name':'CertGraph-Lab-CA','temporary_memberships_restored':all(c['removal_status']==0 for c in cleanup)}
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
if status or not meta['temporary_memberships_restored']:raise SystemExit(1)
