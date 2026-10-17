#!/usr/bin/env python3
"""
run_remote_setup.py — Configures Auditing and SACLs on DC03 & SRV03 via WinRM
"""

import sys
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

common_cmds = [
    'auditpol /set /subcategory:"Directory Service Changes" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Certification Services" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Kerberos Authentication Service" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Kerberos Service Ticket Operations" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Logon" /success:enable /failure:enable',
    'auditpol /set /subcategory:"Special Logon" /success:enable /failure:enable',
    'wevtutil cl Security'  # Clear Security log to establish clean t0 baseline
]

# 1. Setup DC03
print("\n" + "="*60)
print("[*] Instrumenting DC03 (meereen.essos.local)...")
print("="*60)
s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

for c in common_cmds:
    r = s_dc03.run_cmd(c)
    print(f"  [cmd] {c[:50]}... -> Code: {r.status_code}")

print("[*] Setting SACL on Certificate Templates container on DC03...")
sacl_cmd = (
    "$nc = (Get-ADRootDSE).configurationNamingContext; "
    "$p = \"AD:\\CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc\"; "
    "$ev = New-Object System.Security.Principal.SecurityIdentifier('S-1-1-0'); "
    "$r = New-Object System.DirectoryServices.ActiveDirectoryAuditRule($ev, [System.DirectoryServices.ActiveDirectoryRights]::WriteProperty -bor [System.DirectoryServices.ActiveDirectoryRights]::WriteDacl, [System.Security.AccessControl.AuditFlags]::Success, [System.DirectoryServices.ActiveDirectorySecurityInheritance]::All); "
    "$a = Get-Acl $p -Audit; $a.AddAuditRule($r); Set-Acl -Path $p -AclObject $a; "
    "Write-Output 'SACL_APPLIED_SUCCESS'"
)
r_sacl = s_dc03.run_ps(sacl_cmd)
print("  [ps] SACL Status:", r_sacl.status_code, r_sacl.std_out.decode().strip())

# 2. Setup SRV03
print("\n" + "="*60)
print("[*] Instrumenting SRV03 (braavos.essos.local: ESSOS-CA)...")
print("="*60)
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

for c in common_cmds:
    r = s_srv03.run_cmd(c)
    print(f"  [cmd] {c[:50]}... -> Code: {r.status_code}")

ca_cmds = [
    'certutil -setreg CA\\AuditFilter 127',
    'certutil -setreg policy\\EditFlags +EDITF_AUDITCERTTEMPLATELOAD',
    'certutil -setreg CA\\LogLevel 4',
    'net stop certsvc',
    'net start certsvc'
]

for c in ca_cmds:
    r = s_srv03.run_cmd(c)
    print(f"  [cmd] {c[:50]}... -> Code: {r.status_code}")

print("\n" + "="*60)
print("[+] SUCCESS: Live GOAD VMs instrumented with full CIPG audit telemetry!")
print("="*60)
