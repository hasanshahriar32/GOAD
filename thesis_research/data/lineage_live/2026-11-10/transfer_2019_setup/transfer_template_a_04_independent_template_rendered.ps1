if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
$definition='{"flags":131616,"revision":100,"msPKI-Certificate-Application-Policy":["1.3.6.1.5.5.7.3.2"],"msPKI-Certificate-Name-Flag":33554432,"msPKI-Enrollment-Flag":0,"msPKI-Minimal-Key-Size":2048,"msPKI-Private-Key-Flag":16842752,"msPKI-RA-Signature":0,"msPKI-Template-Minor-Revision":4,"msPKI-Template-Schema-Version":2,"pKICriticalExtensions":["2.5.29.15","2.5.29.7"],"pKIDefaultCSPs":["3,Microsoft Base DSS Cryptographic Provider","2,Microsoft Base Cryptographic Provider v1.0","1,Microsoft Enhanced Cryptographic Provider v1.0"],"pKIDefaultKeySpec":2,"pKIExpirationPeriod":[0,64,57,135,46,225,254,255],"pKIExtendedKeyUsage":["1.3.6.1.5.5.7.3.2"],"pKIKeyUsage":[128,0],"pKIMaxIssuingDepth":0,"pKIOverlapPeriod":[0,128,166,10,255,222,255,255]}' | ConvertFrom-Json
$domain=Get-ADDomain
if($domain.DNSRoot -ne 'q1transfer.test'){throw 'Wrong independent forest'}
$existing=Get-ADUser -Filter {SamAccountName -eq 'q1.reader'} -Properties UserPrincipalName
if($existing){
 if($existing.UserPrincipalName -ne 'q1.reader@q1transfer.test'){throw 'Unexpected existing test account'}
 Set-ADAccountPassword $existing -Reset -NewPassword (ConvertTo-SecureString '<private-value-1>' -AsPlainText -Force)
 Enable-ADAccount $existing
}else{
 New-ADUser -Name q1.reader -SamAccountName q1.reader -UserPrincipalName 'q1.reader@q1transfer.test' -EmailAddress 'q1.reader@q1transfer.test' -AccountPassword (ConvertTo-SecureString '<private-value-1>' -AsPlainText -Force) -Enabled $true -PasswordNeverExpires $true
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
$attrs['displayName']='Q1TransferA'
$attrs['msPKI-Cert-Template-OID']=$forestOid+'.20261110.2029'
$dn='CN=Q1TransferA,CN=Certificate Templates,'+$pki
New-ADObject -Name Q1TransferA -Type pKICertificateTemplate -Path ('CN=Certificate Templates,'+$pki) -OtherAttributes $attrs
$enroller=Get-ADUser q1.reader
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
Set-Acl -Path ('AD:'+$dn) -AclObject $acl
$ca=Get-ADObject -SearchBase ('CN=Enrollment Services,'+$pki) -LDAPFilter '(cn=Q1-Transfer-CA)'
Set-ADObject $ca -Add @{certificateTemplates=[string[]]@('Q1TransferA')}
Restart-Service CertSvc
New-Item -Path C:\Q1TransferA -ItemType Directory -Force | Out-Null
icacls.exe C:\Q1TransferA /grant 'Q1XFER\q1.reader:(OI)(CI)M' | Out-Null
@{domain=$domain.DNSRoot;domain_sid=$domain.DomainSID.Value;admin_sid=(Get-ADUser Administrator).SID.Value;enroller_sid=$enroller.SID.Value;template=$dn;oid=$attrs['msPKI-Cert-Template-OID'];ca='Q1-Transfer-CA';computer=$env:COMPUTERNAME} | ConvertTo-Json -Compress
