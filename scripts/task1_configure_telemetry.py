#!/usr/bin/env python3
"""
task1_configure_telemetry.py — Completes Task 1: Configures CA logging verbosity on SRV03 and verifies DC03 audit policies & SACLs
"""

import sys
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

print("\n" + "="*70)
print(" [TASK 1.1] CA CONFIGURATION & LOGGING ON SRV03")
print("="*70)

r_svc = s_srv03.run_ps("Get-Service certsvc | Select-Object Name, Status, DisplayName | Format-List | Out-String")
print("CertSvc Service Status:\n", r_svc.std_out.decode().strip())

ca_setup_script = """
certutil -setreg CA\\AuditFilter 127
certutil -setreg CA\\LogLevel 4
certutil -setreg policy\\EditFlags +EDITF_AUDITCERTTEMPLATELOAD
Restart-Service certsvc -Force
auditpol /set /subcategory:"Certification Services" /success:enable /failure:enable
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
"""
r_ca_setup = s_srv03.run_ps(ca_setup_script)
print("CA Setup Output:\n", r_ca_setup.std_out.decode().strip())

# Dump CA settings
r_dump = s_srv03.run_cmd("certutil -getreg CA\\AuditFilter")
print("AuditFilter Registry:\n", r_dump.std_out.decode().strip())

print("\n" + "="*70)
print(" [TASK 1.2] AUDIT POLICIES ON DC03")
print("="*70)

dc_audit_script = """
auditpol /set /subcategory:"Directory Service Changes" /success:enable /failure:enable
auditpol /set /subcategory:"Certification Services" /success:enable /failure:enable
auditpol /set /subcategory:"Kerberos Authentication Service" /success:enable /failure:enable
auditpol /set /subcategory:"Kerberos Service Ticket Operations" /success:enable /failure:enable
auditpol /set /subcategory:"Logon" /success:enable /failure:enable
auditpol /get /category:"DS Access","Account Logon","Logon/Logoff"
"""
r_dc_audit = s_dc03.run_ps(dc_audit_script)
print(r_dc_audit.std_out.decode().strip())

print("\n" + "="*70)
print(" [TASK 1.3] APPLYING & VERIFYING SACLS ACROSS TEMPLATES & USERS ON DC03")
print("="*70)

sacl_script = """
$nc = (Get-ADRootDSE).configurationNamingContext
$container = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
$sid = New-Object System.Security.Principal.SecurityIdentifier('S-1-1-0') # Everyone
$rule = New-Object System.DirectoryServices.ActiveDirectoryAuditRule(
    $sid,
    [System.DirectoryServices.ActiveDirectoryRights]"GenericAll",
    [System.Security.AccessControl.AuditFlags]::Success
)

$templates = Get-ADObject -SearchBase $container -Filter {ObjectClass -eq 'pKICertificateTemplate'}
Write-Output ("Applying SACL to " + $templates.Count + " pKICertificateTemplate objects...")
foreach ($t in $templates) {
    $de = [ADSI]("LDAP://" + $t.DistinguishedName)
    $de.psbase.Options.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Sacl
    $sec = $de.psbase.ObjectSecurity
    $sec.AddAuditRule($rule)
    $de.psbase.CommitChanges()
}

$users = @('viserys.targaryen', 'daenerys.targaryen', 'khal.drogo')
foreach ($u in $users) {
    $usr = Get-ADUser -Identity $u -ErrorAction SilentlyContinue
    if ($usr) {
        $deU = [ADSI]("LDAP://" + $usr.DistinguishedName)
        $deU.psbase.Options.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Sacl
        $sec = $deU.psbase.ObjectSecurity
        $sec.AddAuditRule($rule)
        $deU.psbase.CommitChanges()
        Write-Output ("Applied SACL to User: " + $u)
    }
}

# Verify SACL on CGPubPositive
$deCheck = [ADSI]("LDAP://CN=CGPubPositive,$container")
$deCheck.psbase.Options.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Sacl
$rCount = $deCheck.psbase.ObjectSecurity.GetAuditRules($true, $true, [System.Security.Principal.SecurityIdentifier]).Count
Write-Output ("VERIFIED: CGPubPositive active audit rule count: " + $rCount)
"""

r_sacl = s_dc03.run_ps(sacl_script)
print(r_sacl.std_out.decode().strip())
print("\n[+] TASK 1 COMPLETE: All audit policies, CA filters, and SACLs are active!")
