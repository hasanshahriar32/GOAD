# Read-only ADCS evidence collection. No template, ACL, account, or CA changes.
$ErrorActionPreference = 'Stop'
Import-Module ActiveDirectory
$root = Get-ADRootDSE
$config = $root.configurationNamingContext
$base = "CN=Public Key Services,CN=Services,$config"
function AclRecord($obj) {
    if ($null -eq $obj.nTSecurityDescriptor) { return $null }
    return @{
        sddl = $obj.nTSecurityDescriptor.GetSecurityDescriptorSddlForm([System.Security.AccessControl.AccessControlSections]::All)
        access = @($obj.nTSecurityDescriptor.Access | ForEach-Object {
            @{identity=$_.IdentityReference.Value; rights=$_.ActiveDirectoryRights.ToString();
              control=$_.AccessControlType.ToString(); object_type=$_.ObjectType.ToString();
              inherited_object_type=$_.InheritedObjectType.ToString(); inherited=$_.IsInherited;
              inheritance=$_.InheritanceType.ToString()}
        })
    }
}
$templates = @(Get-ADObject -SearchBase "CN=Certificate Templates,$base" -LDAPFilter '(objectClass=pKICertificateTemplate)' -Properties * | ForEach-Object {
    @{dn=$_.DistinguishedName; name=$_.Name; display_name=$_.displayName; guid=$_.ObjectGUID.ToString();
      eku=@($_.pKIExtendedKeyUsage); application_policy=@($_.'msPKI-Certificate-Application-Policy');
      certificate_policy=@($_.'msPKI-Certificate-Policy');
      name_flags=$_.'msPKI-Certificate-Name-Flag'; enrollment_flags=$_.'msPKI-Enrollment-Flag';
      signatures=$_.'msPKI-RA-Signature'; schema_version=$_.'msPKI-Template-Schema-Version';
      when_changed=$_.whenChanged.ToUniversalTime().ToString('o'); acl=(AclRecord $_)}
})
$policies = @(Get-ADObject -SearchBase "CN=OID,$base" -LDAPFilter '(objectClass=msPKI-Enterprise-Oid)' -Properties displayName,msPKI-Cert-Template-OID,msDS-OIDToGroupLink | ForEach-Object {
    @{dn=$_.DistinguishedName; name=$_.Name; display_name=$_.displayName;
      oid=$_.'msPKI-Cert-Template-OID'; group_link=$_.'msDS-OIDToGroupLink'}
})
$cas = @(Get-ADObject -SearchBase "CN=Enrollment Services,$base" -LDAPFilter '(objectClass=pKIEnrollmentService)' -Properties * | ForEach-Object {
    @{dn=$_.DistinguishedName; name=$_.Name; host=$_.dNSHostName; templates=@($_.certificateTemplates); flags=$_.flags; acl=(AclRecord $_)}
})
$groups = @(Get-ADGroup -Filter * -Properties member,memberOf | ForEach-Object {
    @{dn=$_.DistinguishedName; name=$_.SamAccountName; sid=$_.SID.Value;
      scope=$_.GroupScope.ToString(); category=$_.GroupCategory.ToString();
      members=@($_.member); member_of=@($_.memberOf)}
})
$users = @(Get-ADUser -Filter * -Properties memberOf,primaryGroupID | ForEach-Object {
    @{dn=$_.DistinguishedName; name=$_.SamAccountName; sid=$_.SID.Value;
      enabled=$_.Enabled; member_of=@($_.memberOf); primary_group_id=$_.primaryGroupID}
})
$os = Get-CimInstance Win32_OperatingSystem
@{schema_version=1; collected_utc=[DateTime]::UtcNow.ToString('o'); computer=$env:COMPUTERNAME;
  domain=$root.defaultNamingContext; configuration=$config;
  os=@{caption=$os.Caption; version=$os.Version; build=$os.BuildNumber};
  templates=$templates; policies=$policies; certificate_authorities=$cas; groups=$groups; users=$users;
  scope='Read-only LDAP/AD cmdlet snapshot. Does not establish effective access, CA runtime settings, trust, or authentication success.'
} | ConvertTo-Json -Depth 12 -Compress
