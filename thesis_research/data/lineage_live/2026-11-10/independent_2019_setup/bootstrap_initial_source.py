"""Provision only the fresh, independent Q1 research VM behind localhost:57985.

The stock source is mounted read-only by independent_2019.sh. Credentials are
random and stored mode 0600 outside the repository; scripts redact their values
from saved output. No license state, clock, or update policy is modified.
"""

import argparse
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
    result=connection.run_ps("$ErrorActionPreference='Stop'; $ProgressPreference='SilentlyContinue'\n"+script)
    stdout,stderr=result.std_out.decode("utf-8-sig",errors="replace"),result.std_err.decode("utf-8-sig",errors="replace")
    for value in secret.values():stdout=stdout.replace(value,"<redacted>");stderr=stderr.replace(value,"<redacted>")
    data={"status_code":result.status_code,"host_before":before,"host_after":time.time(),"stdout":stdout,"stderr":stderr,
          "scope":"Fresh independent research VM only","source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    path.write_text(json.dumps(data,indent=2)+"\n")
    if result.status_code:raise RuntimeError(name+" failed; see saved raw outcome")
    return stdout


def run(args):
    args.output.mkdir(parents=True,exist_ok=True)
    secret=credentials()
    connection=session("local" if args.action in ("inventory","roles","forest") else "domain",secret)
    inventory="""$o=Get-CimInstance Win32_OperatingSystem; $c=Get-CimInstance Win32_ComputerSystem
@{os=$o.Caption;build=$o.BuildNumber;computer=$env:COMPUTERNAME;domain=$c.Domain;part_of_domain=$c.PartOfDomain;utc=[DateTime]::UtcNow.ToString('o');features=@(Get-WindowsFeature AD-Domain-Services,ADCS-Cert-Authority | Select Name,InstallState)} | ConvertTo-Json -Compress -Depth 5"""
    if args.action=="inventory":
        execute(connection,"00_stock_inventory",inventory,args.output,secret)
    elif args.action=="roles":
        script="""$c=Get-CimInstance Win32_ComputerSystem
if($c.PartOfDomain){throw 'Refusing feature setup on an existing domain member'}
$o=Get-CimInstance Win32_OperatingSystem
if($o.Caption -notlike '*2019*'){throw 'Unexpected OS'}
$feature=Install-WindowsFeature AD-Domain-Services,ADCS-Cert-Authority -IncludeManagementTools
$feature | Select Success,RestartNeeded,ExitCode | ConvertTo-Json -Compress
if(-not $feature.Success){throw 'Feature installation failed'}
"""
        execute(connection,"01_feature_install",script,args.output,secret)
    elif args.action=="forest":
        script="""if((Get-CimInstance Win32_ComputerSystem).PartOfDomain){throw 'Refusing to replace an existing domain'}
Set-LocalUser Administrator -Password (ConvertTo-SecureString 'ADMIN_SECRET' -AsPlainText -Force)
Enable-LocalUser Administrator
Import-Module ADDSDeployment
Install-ADDSForest -DomainName 'q1lab.test' -DomainNetbiosName Q1LAB -InstallDns -SafeModeAdministratorPassword (ConvertTo-SecureString 'DSRM_SECRET' -AsPlainText -Force) -NoRebootOnCompletion -Force
shutdown.exe /r /t 8
'NEW_FOREST_INSTALLED_REBOOT_SCHEDULED'
""".replace("ADMIN_SECRET",secret["administrator_password"]).replace("DSRM_SECRET",secret["dsrm_password"])
        execute(connection,"02_new_forest",script,args.output,secret)
    elif args.action=="ca":
        script="""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
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
    elif args.action=="template":
        definition=json.loads((ROOT/"ansible/roles/adcs_templates/files/ESC13.json").read_text())
        # Keep the validated schema/crypto attributes, without the old policy OID.
        for name in ["name","displayName","objectClass","msPKI-Cert-Template-OID","msPKI-Certificate-Policy"]:definition.pop(name,None)
        script="$definition='"+json.dumps(definition,separators=(",",":"))+"' | ConvertFrom-Json\n"
        script+="""$domain=Get-ADDomain
if($domain.DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
New-ADUser -Name q1.enroller -SamAccountName q1.enroller -UserPrincipalName 'q1.enroller@q1lab.test' -EmailAddress 'q1.enroller@q1lab.test' -AccountPassword (ConvertTo-SecureString 'ENROLLER_SECRET' -AsPlainText -Force) -Enabled $true -PasswordNeverExpires $true
$root=Get-ADRootDSE
$pki='CN=Public Key Services,CN=Services,'+$root.configurationNamingContext
$forestOid=(Get-ADObject ('CN=OID,'+$pki) -Properties msPKI-Cert-Template-OID).'msPKI-Cert-Template-OID'
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
$admins=Get-ADGroup 'Domain Admins'
$acl=New-Object DirectoryServices.ActiveDirectorySecurity
$acl.SetAccessRuleProtection($true,$false)
$acl.SetOwner($admins.SID)
$acl.AddAccessRule((New-Object DirectoryServices.ActiveDirectoryAccessRule($admins.SID,'GenericAll','Allow')))
$auth=New-Object Security.Principal.SecurityIdentifier('S-1-5-11')
$acl.AddAccessRule((New-Object DirectoryServices.ActiveDirectoryAccessRule($auth,'GenericRead','Allow')))
$enroll=[Guid]'0e10c968-78fb-11d2-90d4-00c04f79dc55'
$acl.AddAccessRule((New-Object DirectoryServices.ActiveDirectoryAccessRule($enroller.SID,'ExtendedRight','Allow',$enroll)))
Set-Acl -Path ('AD:\'+$dn) -AclObject $acl
$ca=Get-ADObject -SearchBase ('CN=Enrollment Services,'+$pki) -LDAPFilter '(cn=Q1-Evidence-CA)'
Set-ADObject $ca -Add @{certificateTemplates=[string[]]@('Q1Evidence')}
Restart-Service CertSvc
New-Item -Path C:\Q1Evidence -ItemType Directory -Force | Out-Null
@{domain=$domain.DNSRoot;domain_sid=$domain.DomainSID.Value;admin_sid=(Get-ADUser Administrator).SID.Value;enroller_sid=$enroller.SID.Value;template=$dn;oid=$attrs['msPKI-Cert-Template-OID'];ca='Q1-Evidence-CA';computer=$env:COMPUTERNAME} | ConvertTo-Json -Compress
""".replace("ENROLLER_SECRET",secret["enroller_password"])
        execute(connection,"04_independent_template",script,args.output,secret)
    elif args.action=="final_inventory":
        execute(connection,"05_final_inventory",inventory+"\nGet-HotFix | Select HotFixID,InstalledOn | ConvertTo-Json -Compress\n$k=Get-ItemProperty HKLM:\\SYSTEM\\CurrentControlSet\\Services\\Kdc; @{strong_binding_value=$k.StrongCertificateBindingEnforcement;value_present=($k.PSObject.Properties.Name -contains 'StrongCertificateBindingEnforcement')} | ConvertTo-Json -Compress",args.output,secret)
    print(json.dumps({"phase":args.action,"status":"saved","output":str(args.output)}))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["inventory","roles","forest","ca","template","final_inventory"])
    parser.add_argument("--output",type=Path,required=True)
    run(parser.parse_args())
