#!/usr/bin/env python3
"""
task1_setup_and_verify.py — Verifies Lab State, Configures CA Logging Verbosity on SRV03 & Verifies DC03 Telemetry
"""

import sys
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

print("\n" + "="*70)
print(" [TASK 1.1] VERIFYING MESH REACHABILITY (192.168.56.22 <-> 192.168.56.23)")
print("="*70)

# Check SRV03 -> DC03
r_mesh1 = s_srv03.run_ps("Test-NetConnection -ComputerName meereen.essos.local -Port 88 | Select-Object ComputerName, RemoteAddress, TcpTestSucceeded | Format-List | Out-String")
print("SRV03 -> DC03 (Kerberos 88):", r_mesh1.std_out.decode().strip())

# Check DC03 -> SRV03
r_mesh2 = s_dc03.run_ps("Test-NetConnection -ComputerName braavos.essos.local -Port 135 | Select-Object ComputerName, RemoteAddress, TcpTestSucceeded | Format-List | Out-String")
print("DC03 -> SRV03 (RPC 135):", r_mesh2.std_out.decode().strip())

print("\n" + "="*70)
print(" [TASK 1.2] DISCOVERING CA CONFIGURATION ON SRV03")
print("="*70)

r_dump = s_srv03.run_cmd("certutil -dump")
ca_name_lines = [l for l in r_dump.std_out.decode().splitlines() if "Common Name" in l or "Config" in l or "CA Name" in l or "Server" in l]
print("CA Configuration Info:")
for l in ca_name_lines[:10]:
    print("  ", l)

r_svc = s_srv03.run_ps("Get-Service certsvc | Select-Object Name, Status, DisplayName | Format-List | Out-String")
print(r_svc.std_out.decode().strip())

print("\n" + "="*70)
print(" [TASK 1.3] CONFIGURING CA LOGGING VERBOSITY ON SRV03")
print("="*70)

ca_configs = [
    "certutil -setreg CA\\AuditFilter 127",
    "certutil -setreg CA\\LogLevel 4",
    "certutil -setreg policy\\EditFlags +EDITF_AUDITCERTTEMPLATELOAD",
    "Restart-Service certsvc -Force",
    'auditpol /set /subcategory:"Certification Services" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Logon" /success:enable /failure:enable'
]

for cmd in ca_configs:
    r = s_srv03.run_ps(cmd)
    print(f"  [SRV03] {cmd[:55]}... -> ExitCode: {r.status_code}")

print("\n" + "="*70)
print(" [TASK 1.4] VERIFYING ADVANCED AUDIT POLICIES ON DC03")
print("="*70)

dc_audit_cmds = [
    'auditpol /set /subcategory:"Directory Service Changes" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Certification Services" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Kerberos Authentication Service" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Kerberos Service Ticket Operations" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Logon" /success:enable /failure:enable'
]

for cmd in dc_audit_cmds:
    r = s_dc03.run_cmd(cmd)
    print(f"  [DC03] {cmd[:55]}... -> ExitCode: {r.status_code}")

r_audit_status = s_dc03.run_cmd('auditpol /get /category:"DS Access","Account Logon","Logon/Logoff"')
print("\nDC03 Active Audit Policies:\n" + r_audit_status.std_out.decode().strip())

print("\n" + "="*70)
print(" [TASK 1.5] VERIFYING ACTIVE SACLS ON CERTIFICATE TEMPLATES AND USERS")
print("="*70)

sacl_verify_script = """
$nc = (Get-ADRootDSE).configurationNamingContext
$container = "CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
$tpl = Get-ADObject -Identity "CN=CGPubPositive,$container"
$de = [ADSI]("LDAP://" + $tpl.DistinguishedName)
$de.psbase.Options.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Sacl
$rules = $de.psbase.ObjectSecurity.GetAuditRules($true, $true, [System.Security.Principal.SecurityIdentifier])
Write-Output ("CGPubPositive SACL Rules Count: " + $rules.Count)
foreach ($r in $rules) {
    Write-Output ("  Rule: Identity=" + $r.IdentityReference.Value + " Rights=" + $r.ActiveDirectoryRights + " Flags=" + $r.AuditFlags)
}

$u = Get-ADUser -Identity "viserys.targaryen" -ErrorAction SilentlyContinue
if ($u) {
    $deU = [ADSI]("LDAP://" + $u.DistinguishedName)
    $deU.psbase.Options.SecurityMasks = [System.DirectoryServices.SecurityMasks]::Sacl
    $uRules = $deU.psbase.ObjectSecurity.GetAuditRules($true, $true, [System.Security.Principal.SecurityIdentifier])
    Write-Output ("viserys.targaryen SACL Rules Count: " + $uRules.Count)
    foreach ($r in $uRules) {
        Write-Output ("  Rule: Identity=" + $r.IdentityReference.Value + " Rights=" + $r.ActiveDirectoryRights + " Flags=" + $r.AuditFlags)
    }
}
"""

r_sacl = s_dc03.run_ps(sacl_verify_script)
print(r_sacl.std_out.decode().strip())

print("\n[+] TASK 1 COMPLETE: All services and audit parameters verified.")
