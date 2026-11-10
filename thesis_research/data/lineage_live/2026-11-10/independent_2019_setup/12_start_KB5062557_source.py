"""Provision only the fresh, independent Q1 research VM behind localhost:57985.

The stock source is mounted read-only by independent_2019.sh. Credentials are
random and stored mode 0600 outside the repository; scripts redact their values
from saved output. No license state, clock, or update policy is modified.
"""

import argparse
import base64
import hashlib
import json
import os
from pathlib import Path
import secrets
import time

import winrm

ROOT=Path(__file__).resolve().parents[4]
PRIVATE=Path("/tmp/goad-q1-independent-2019/credentials.json")
ENDPOINT="http://127.0.0.1:57985/wsman"
EXECUTED_SOURCE=Path(__file__).read_bytes()


def credentials():
    if PRIVATE.exists():return json.loads(PRIVATE.read_text())
    data={"administrator_password":secrets.token_urlsafe(24)+"aA1!", "enroller_password":secrets.token_urlsafe(24)+"bB2!",
          "dsrm_password":secrets.token_urlsafe(24)+"cC3!"}
    descriptor=os.open(PRIVATE,os.O_WRONLY|os.O_CREAT|os.O_EXCL,0o600)
    with os.fdopen(descriptor,"w") as target:json.dump(data,target)
    return data


def session(mode,secret):
    if mode=="local":user,password="vagrant","vagrant"
    else:user,password="Q1LAB\\Administrator",secret["administrator_password"]
    return winrm.Session(ENDPOINT,auth=(user,password),transport="ntlm",read_timeout_sec=360,operation_timeout_sec=300)


def execute(connection,name,script,output,secret):
    path=output/(name+".json")
    if path.exists():raise FileExistsError(path)
    before=time.time()
    full_script="$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'\ntry {\n"+script+"\n'__Q1_PHASE_COMPLETE__'\n} catch { '__Q1_PHASE_FAILURE__'; $_.Exception.ToString(); exit 1 }"
    staged_script_sha256=None
    if len(full_script.encode("utf-16le"))*4//3>6500:
        public=full_script
        prefix=[]
        for index,value in enumerate(secret.values()):
            variable="$Q1Private_"+str(index)
            if value in public:
                public=public.replace("'"+value+"'",variable)
                prefix.append(variable+"='"+value+"';")
        if any(value in public for value in secret.values()):raise ValueError("Private value remains in a staged public script")
        staged_script_sha256=hashlib.sha256(public.encode()).hexdigest()
        (output/(name+"_public.ps1")).write_text(public)
        encoded=base64.b64encode(public.encode()).decode()
        remote="C:\\Windows\\Temp\\Q1_"+name+".b64"
        for index in range(0,len(encoded),1800):
            method="WriteAllText" if index==0 else "AppendAllText"
            piece=connection.run_ps("[IO.File]::"+method+"('"+remote+"','"+encoded[index:index+1800]+"')")
            if piece.status_code:raise RuntimeError("Public source staging failed")
        public_path=remote+".ps1"
        decoded=connection.run_ps("[IO.File]::WriteAllBytes('"+public_path+"',[Convert]::FromBase64String([IO.File]::ReadAllText('"+remote+"')));(Get-FileHash '"+public_path+"' -Algorithm SHA256).Hash")
        if decoded.status_code or decoded.std_out.decode().strip().casefold()!=staged_script_sha256:
            raise RuntimeError("Staged public script hash mismatch")
        loader="$ErrorActionPreference='Stop';"+"".join(prefix)+"try{& '"+public_path+"'}catch{'__Q1_LOADER_FAILURE__';$_.Exception.ToString();exit 1}finally{Remove-Item '"+remote+"','"+public_path+"' -ErrorAction SilentlyContinue}"
        result=connection.run_ps(loader)
    else:
        result=connection.run_ps(full_script)
    stdout,stderr=result.std_out.decode("utf-8-sig",errors="replace"),result.std_err.decode("utf-8-sig",errors="replace")
    for value in secret.values():stdout=stdout.replace(value,"<redacted>");stderr=stderr.replace(value,"<redacted>")
    data={"status_code":result.status_code,"host_before":before,"host_after":time.time(),"stdout":stdout,"stderr":stderr,
          "scope":"Fresh independent research VM only","source_sha256":hashlib.sha256(EXECUTED_SOURCE).hexdigest(),
          "staged_public_script_sha256":staged_script_sha256,"completion_marker_seen":"__Q1_PHASE_COMPLETE__" in stdout}
    (output/(name+"_source.py")).write_bytes(EXECUTED_SOURCE)
    path.write_text(json.dumps(data,indent=2)+"\n")
    if result.status_code or "__Q1_PHASE_COMPLETE__" not in stdout:raise RuntimeError(name+" failed or lacks completion marker; see saved raw outcome")
    return stdout


def run(args):
    args.output.mkdir(parents=True,exist_ok=True)
    secret=credentials()
    connection=session("local" if args.action in ("inventory","roles","forest","forest_retry","remove_unconfigured_ca_feature") else "domain",secret)
    inventory="""$o=Get-CimInstance Win32_OperatingSystem; $c=Get-CimInstance Win32_ComputerSystem
@{os=$o.Caption;build=$o.BuildNumber;computer=$env:COMPUTERNAME;domain=$c.Domain;part_of_domain=$c.PartOfDomain;utc=[DateTime]::UtcNow.ToString('o');features=@(Get-WindowsFeature AD-Domain-Services,ADCS-Cert-Authority | Select Name,InstallState)} | ConvertTo-Json -Compress -Depth 5"""
    if args.action=="inventory":
        execute(connection,"00_stock_inventory",inventory,args.output,secret)
    elif args.action=="roles":
        script="""$c=Get-CimInstance Win32_ComputerSystem
if($c.PartOfDomain){throw 'Refusing feature setup on an existing domain member'}
$o=Get-CimInstance Win32_OperatingSystem
if($o.Caption -notlike '*2019*'){throw 'Unexpected OS'}
$feature=Install-WindowsFeature AD-Domain-Services -IncludeManagementTools
$feature | Select Success,RestartNeeded,ExitCode | ConvertTo-Json -Compress
if(-not $feature.Success){throw 'Feature installation failed'}
"""
        execute(connection,"01_feature_install",script,args.output,secret)
    elif args.action=="remove_unconfigured_ca_feature":
        script="""if((Get-CimInstance Win32_ComputerSystem).PartOfDomain){throw 'Unexpected domain membership'}
$active=(Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration' -Name Active -ErrorAction SilentlyContinue).Active
if($active){throw 'Refusing removal of a configured CA'}
$f=Uninstall-WindowsFeature ADCS-Cert-Authority
$f | Select Success,RestartNeeded,ExitCode | ConvertTo-Json -Compress
if(-not $f.Success){throw 'Unconfigured role removal failed'}
"""
        execute(connection,"02a_remove_unconfigured_ca_feature",script,args.output,secret)
    elif args.action in ("forest","forest_retry"):
        script="""if((Get-CimInstance Win32_ComputerSystem).PartOfDomain){throw 'Refusing to replace an existing domain'}
Set-LocalUser Administrator -Password (ConvertTo-SecureString 'ADMIN_SECRET' -AsPlainText -Force)
Enable-LocalUser Administrator
Import-Module ADDSDeployment
Install-ADDSForest -DomainName 'q1lab.test' -DomainNetbiosName Q1LAB -InstallDns -SafeModeAdministratorPassword (ConvertTo-SecureString 'DSRM_SECRET' -AsPlainText -Force) -NoRebootOnCompletion -Force
shutdown.exe /r /t 8
'NEW_FOREST_INSTALLED_REBOOT_SCHEDULED'
""".replace("ADMIN_SECRET",secret["administrator_password"]).replace("DSRM_SECRET",secret["dsrm_password"])
        execute(connection,"02b_new_forest" if args.action=="forest_retry" else "02_new_forest",script,args.output,secret)
    elif args.action=="ca":
        script="""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$feature=Install-WindowsFeature ADCS-Cert-Authority -IncludeManagementTools
if(-not $feature.Success){throw 'CA feature installation failed'}
$active=(Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration' -Name Active -ErrorAction SilentlyContinue).Active
if($active){throw 'Refusing replacement of existing CA'}
Install-AdcsCertificationAuthority -CAType EnterpriseRootCA -CACommonName 'Q1-Evidence-CA' -CryptoProviderName 'RSA#Microsoft Software Key Storage Provider' -KeyLength 2048 -HashAlgorithmName SHA256 -ValidityPeriod Years -ValidityPeriodUnits 1 -Force
certutil -setreg CA\AuditFilter 127
certutil -setreg policy\EditFlags +EDITF_AUDITCERTTEMPLATELOAD
auditpol /set /subcategory:'Certification Services' /success:enable /failure:enable
auditpol /set /subcategory:'Kerberos Authentication Service' /success:enable /failure:enable
auditpol /set /subcategory:'Directory Service Changes' /success:enable /failure:enable
Restart-Service CertSvc
Get-Service CertSvc | Select Name,Status | ConvertTo-Json -Compress
"""
        execute(connection,"03_independent_ca",script,args.output,secret)
    elif args.action in ("template","template_retry","template_resume","template_file_resume"):
        definition=json.loads((ROOT/"ansible/roles/adcs_templates/files/ESC13.json").read_text())
        # Keep the validated schema/crypto attributes, without the old policy OID.
        for name in ["name","displayName","objectClass","msPKI-Cert-Template-OID","msPKI-Certificate-Policy"]:definition.pop(name,None)
        script="$definition='"+json.dumps(definition,separators=(",",":"))+"' | ConvertFrom-Json\n"
        script+="""$domain=Get-ADDomain
if($domain.DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$existing=Get-ADUser -Filter {SamAccountName -eq 'q1.enroller'} -Properties UserPrincipalName
if($existing){
 if($existing.UserPrincipalName -ne 'q1.enroller@q1lab.test'){throw 'Unexpected existing test account'}
 Set-ADAccountPassword $existing -Reset -NewPassword (ConvertTo-SecureString 'ENROLLER_SECRET' -AsPlainText -Force)
 Enable-ADAccount $existing
}else{
 New-ADUser -Name q1.enroller -SamAccountName q1.enroller -UserPrincipalName 'q1.enroller@q1lab.test' -EmailAddress 'q1.enroller@q1lab.test' -AccountPassword (ConvertTo-SecureString 'ENROLLER_SECRET' -AsPlainText -Force) -Enabled $true -PasswordNeverExpires $true
}
$root=Get-ADRootDSE
$pki='CN=Public Key Services,CN=Services,'+$root.configurationNamingContext
$forestOid=(Get-ADObject ('CN=OID,'+$pki) -Properties msPKI-Cert-Template-OID).'msPKI-Cert-Template-OID'
if(-not $forestOid){throw 'Forest template OID root is absent'}
$attrs=@{}
foreach($p in $definition.PSObject.Properties){
 $v=$p.Value
 if($p.Name -in @('pKIExpirationPeriod','pKIOverlapPeriod','pKIKeyUsage')){$v=[byte[]]$v}
 elseif($v -is [array]){$v=[string[]]$v}
 elseif($v -is [long]){$v=[int]$v}
 $attrs[$p.Name]=$v
}
$attrs['displayName']='Q1Evidence'
$attrs['msPKI-Cert-Template-OID']=$forestOid+'.20261110.2019'
$dn='CN=Q1Evidence,CN=Certificate Templates,'+$pki
New-ADObject -Name Q1Evidence -Type pKICertificateTemplate -Path ('CN=Certificate Templates,'+$pki) -OtherAttributes $attrs
$enroller=Get-ADUser q1.enroller
Add-ADGroupMember -Identity 'S-1-5-32-580' -Members $enroller
if(@(Get-ADPrincipalGroupMembership $enroller | Where-Object {$_.SID.Value -eq ($domain.DomainSID.Value+'-512')}).Count -ne 0){throw 'Test enroller must not be a domain administrator'}
$admins=Get-ADGroup 'Domain Admins'
$acl=New-Object DirectoryServices.ActiveDirectorySecurity
$acl.SetAccessRuleProtection($true,$false)
$acl.SetOwner($admins.SID)
$acl.AddAccessRule((New-Object DirectoryServices.ActiveDirectoryAccessRule($admins.SID,'GenericAll','Allow')))
$auth=New-Object Security.Principal.SecurityIdentifier('S-1-5-11')
$acl.AddAccessRule((New-Object DirectoryServices.ActiveDirectoryAccessRule($auth,'GenericRead','Allow')))
$enroll=[Guid]'0e10c968-78fb-11d2-90d4-00c04f79dc55'
$acl.AddAccessRule((New-Object DirectoryServices.ActiveDirectoryAccessRule($enroller.SID,'ExtendedRight','Allow',$enroll)))
$everyone=New-Object Security.Principal.SecurityIdentifier('S-1-1-0')
$acl.AddAuditRule((New-Object DirectoryServices.ActiveDirectoryAuditRule($everyone,'WriteProperty','Success')))
Set-Acl -Path ('AD:\'+$dn) -AclObject $acl
$ca=Get-ADObject -SearchBase ('CN=Enrollment Services,'+$pki) -LDAPFilter '(cn=Q1-Evidence-CA)'
Set-ADObject $ca -Add @{certificateTemplates=[string[]]@('Q1Evidence')}
Restart-Service CertSvc
New-Item -Path C:\Q1Evidence -ItemType Directory -Force | Out-Null
icacls.exe C:\Q1Evidence /grant 'Q1LAB\q1.enroller:(OI)(CI)M' | Out-Null
@{domain=$domain.DNSRoot;domain_sid=$domain.DomainSID.Value;admin_sid=(Get-ADUser Administrator).SID.Value;enroller_sid=$enroller.SID.Value;template=$dn;oid=$attrs['msPKI-Cert-Template-OID'];ca='Q1-Evidence-CA';computer=$env:COMPUTERNAME} | ConvertTo-Json -Compress
""".replace("ENROLLER_SECRET",secret["enroller_password"])
        phase="04f_independent_template_file_resume" if args.action=="template_file_resume" else "04d_independent_template_resume" if args.action=="template_resume" else "04c_independent_template_retry" if args.action=="template_retry" else "04_independent_template"
        execute(connection,phase,script,args.output,secret)
    elif args.action in ("kdc_certificate","kdc_certificate_retry"):
        script="""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$existing=@(Get-ChildItem Cert:\LocalMachine\My -SSLServerAuthentication | Where-Object {$_.HasPrivateKey -and $_.Issuer -like '*CN=Q1-Evidence-CA*' -and $_.Subject -ne $_.Issuer})
if($existing.Count -eq 0){
  $p=Start-Process certreq.exe -ArgumentList '-enroll -machine -q DomainController' -Wait -PassThru -NoNewWindow
  if($p.ExitCode -ne 0){throw ('KDC_CERTIFICATE_ENROLLMENT_EXIT:'+ $p.ExitCode)}
}
Restart-Service Kdc -Force
$machine=@(Get-ChildItem Cert:\LocalMachine\My -SSLServerAuthentication | Where-Object {$_.HasPrivateKey -and $_.Issuer -like '*CN=Q1-Evidence-CA*' -and $_.Subject -ne $_.Issuer})
if($machine.Count -eq 0){throw 'A CA signing certificate is not a KDC machine certificate'}
$machine | Select Subject,Issuer,Thumbprint,HasPrivateKey,NotAfter,@{Name='eku';Expression={@($_.EnhancedKeyUsageList | ForEach-Object {[string]$_.ObjectId})}} | ConvertTo-Json -Compress -Depth 5
"""
        execute(connection,"04g_kdc_machine_certificate_retry" if args.action=="kdc_certificate_retry" else "04b_kdc_machine_certificate",script,args.output,secret)
    elif args.action=="enroller_remoting":
        script="""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$u=Get-ADUser q1.enroller
$path='WSMan:\localhost\Service\RootSDDL'
$before=(Get-Item $path).Value
$ace='(A;;GRGX;;;'+$u.SID.Value+')'
if($before -notlike ('*'+$u.SID.Value+'*')){
 $parts=$before -split 'S:',2
 if($parts.Count -ne 2){throw 'Unexpected WinRM root descriptor shape'}
 $after=$parts[0]+$ace+'S:'+$parts[1]
 Set-Item $path -Value $after -Force
}
@{principal_sid=$u.SID.Value;rights='Read and Execute on WinRM service only';before=$before;after=(Get-Item $path).Value;domain_admin_membership=@(Get-ADPrincipalGroupMembership $u | Where-Object {$_.SID.Value -eq ((Get-ADDomain).DomainSID.Value+'-512')}).Count} | ConvertTo-Json -Compress
"""
        execute(connection,"04h_enroller_remoting_access",script,args.output,secret)
    elif args.action=="final_inventory":
        execute(connection,"05_final_inventory",inventory+"\nGet-HotFix | Select HotFixID,InstalledOn | ConvertTo-Json -Compress\n$k=Get-ItemProperty HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Kdc; @{strong_binding_value=$k.StrongCertificateBindingEnforcement;value_present=($k.PSObject.Properties.Name -contains 'StrongCertificateBindingEnforcement')} | ConvertTo-Json -Compress",args.output,secret)
    print(json.dumps({"phase":args.action,"status":"saved","output":str(args.output)}))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["inventory","roles","forest","forest_retry","remove_unconfigured_ca_feature","ca","template","template_retry","template_resume","template_file_resume","kdc_certificate","kdc_certificate_retry","enroller_remoting","final_inventory"])
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
