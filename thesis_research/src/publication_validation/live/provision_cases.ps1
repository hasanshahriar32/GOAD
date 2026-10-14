# Controlled enrollment prerequisite cases, deliberately confined to the GOAD lab.
# No existing template is edited. Snapshot rollback restores the pre-CA baseline.
$ErrorActionPreference='Stop'
$ProgressPreference='SilentlyContinue'
Import-Module ActiveDirectory
$PSDefaultParameterValues['*-AD*:Credential']=$SetupCredential
New-PSDrive -Name CGAD -PSProvider ActiveDirectory -Root '' -Server localhost -Credential $SetupCredential | Out-Null
$root=Get-ADRootDSE
if ($root.defaultNamingContext -ne 'DC=essos,DC=local') {throw 'Wrong domain'}
$base=$root.defaultNamingContext
$ou="OU=CertGraphPublication,$base"
if (!(Get-ADOrganizationalUnit -LDAPFilter '(ou=CertGraphPublication)' -SearchBase $base)) {
    New-ADOrganizationalUnit -Name CertGraphPublication -Path $base -ProtectedFromAccidentalDeletion $false
}
$existing=Get-ADUser -LDAPFilter '(sAMAccountName=cg.publication)'
if (!$existing) {
    New-ADUser -Name cg.publication -SamAccountName cg.publication -UserPrincipalName 'cg.publication@essos.local' -Path $ou -AccountPassword $CasePassword -Enabled $true
} elseif ($existing.DistinguishedName -ne "CN=cg.publication,$ou") {throw 'Unexpected existing account location'}
if (!(Get-ADGroup -LDAPFilter '(sAMAccountName=CGPublicationEnroll)')) {New-ADGroup -Name CGPublicationEnroll -GroupScope Global -GroupCategory Security -Path $ou}
if (!(Get-ADGroup -LDAPFilter '(sAMAccountName=CGPublicationPolicy)')) {New-ADGroup -Name CGPublicationPolicy -GroupScope Universal -GroupCategory Security -Path $ou}
Add-ADGroupMember CGPublicationEnroll cg.publication
$user=Get-ADUser cg.publication
$enroll=Get-ADGroup CGPublicationEnroll
$policyGroup=Get-ADGroup CGPublicationPolicy
$pki="CN=Public Key Services,CN=Services,$($root.configurationNamingContext)"
$forestOid=(Get-ADObject "CN=OID,$pki" -Properties msPKI-Cert-Template-OID).'msPKI-Cert-Template-OID'
$policyOid="$forestOid.20261014.1"
New-ADObject -Name CGPublicationPolicy -Type msPKI-Enterprise-Oid -Path "CN=OID,$pki" -OtherAttributes @{'displayName'='CGPublicationPolicy';'flags'=[int]2;'msPKI-Cert-Template-OID'=$policyOid}
Set-ADObject "CN=CGPublicationPolicy,CN=OID,$pki" -Replace @{'msDS-OIDToGroupLink'=$policyGroup.DistinguishedName}
$admin=Get-ADGroup 'Domain Admins'
$ea=Get-ADGroup 'Enterprise Admins'
$vagrant=Get-ADUser vagrant
$names=@('CGPubPositive','CGPubApproval','CGPubSignature','CGPubDenied','CGPubUnpublished','CGPubNoPolicy')
$results=@()
foreach ($i in 0..($names.Count-1)) {
    $name=$names[$i]
    $attrs=@{}
    foreach ($property in $TemplateDefinition.PSObject.Properties) {
        if ($property.Name -notin @('name','displayName','objectClass','msPKI-Cert-Template-OID','msPKI-Certificate-Policy')) {
            $v=$property.Value
            if ($property.Name -in @('pKIExpirationPeriod','pKIOverlapPeriod','pKIKeyUsage')) {$v=[byte[]]$v}
            elseif ($v -is [array]) {$v=[string[]]$v}
            elseif ($v -is [long]) {$v=[int]$v}
            $attrs[$property.Name]=$v
        }
    }
    $attrs['displayName']=$name
    $attrs['msPKI-Cert-Template-OID']="$forestOid.20261014.$(100+$i)"
    if ($name -ne 'CGPubNoPolicy') {$attrs['msPKI-Certificate-Policy']=[string[]]@($policyOid)}
    if ($name -eq 'CGPubApproval') {$attrs['msPKI-Enrollment-Flag']=[int]2}
    if ($name -eq 'CGPubSignature') {$attrs['msPKI-RA-Signature']=[int]1}
    New-ADObject -Name $name -Type pKICertificateTemplate -Path "CN=Certificate Templates,$pki" -OtherAttributes $attrs
    $dn="CN=$name,CN=Certificate Templates,$pki"
    $acl=New-Object System.DirectoryServices.ActiveDirectorySecurity
    $acl.SetAccessRuleProtection($true,$false)
    $acl.SetOwner($admin.SID)
    foreach ($sid in @($admin.SID,$ea.SID,$vagrant.SID)) {
        $acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule($sid,'GenericAll','Allow')))
    }
    $authenticated=New-Object Security.Principal.SecurityIdentifier('S-1-5-11')
    $acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule($authenticated,'GenericRead','Allow')))
    $enrollGuid=[Guid]'0e10c968-78fb-11d2-90d4-00c04f79dc55'
    $acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule($enroll.SID,'ExtendedRight','Allow',$enrollGuid)))
    if ($name -eq 'CGPubDenied') {
        $acl.AddAccessRule((New-Object System.DirectoryServices.ActiveDirectoryAccessRule($user.SID,'ExtendedRight','Deny',$enrollGuid)))
    }
    Set-Acl -Path "CGAD:\$dn" -AclObject $acl
    $results+=@{template=$name;dn=$dn;published=($name -ne 'CGPubUnpublished')}
}
$ca=Get-ADObject -SearchBase "CN=Enrollment Services,$pki" -LDAPFilter '(cn=CertGraph-Lab-CA)'
if (!$ca) {throw 'Expected lab CA not found'}
# Preserve all default publications; add only the controlled templates.
Set-ADObject $ca -Add @{certificateTemplates=[string[]]@($names | Where-Object {$_ -ne 'CGPubUnpublished'})}
@{user=$user.SamAccountName;user_sid=$user.SID.Value;policy_group=$policyGroup.DistinguishedName;policy_oid=$policyOid;cases=$results;scope='Enrollment and policy prerequisites in a controlled lab. No authentication/escalation outcome asserted.'} | ConvertTo-Json -Depth 5
