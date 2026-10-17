#!/usr/bin/env python3
"""
setup_lowpriv_attacker.py — Configure realistic low-privilege attacker credentials and ACLs
"""
import sys
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

print("[1] De-contaminating DC03: Removing vagrant from Domain Admins...")
ps_dc1 = """
Remove-ADGroupMember -Identity 'Domain Admins' -Members 'vagrant' -Confirm:$false -ErrorAction SilentlyContinue
Add-ADGroupMember -Identity 'Administrators' -Members 'vagrant' -ErrorAction SilentlyContinue
Add-ADGroupMember -Identity 'Remote Management Users' -Members 'khal.drogo', 'viserys.targaryen' -ErrorAction SilentlyContinue
Get-ADGroupMember -Identity 'Domain Admins' | Select-Object -ExpandProperty SamAccountName
"""
r = s_dc.run_ps(ps_dc1)
print("Domain Admins Members:", r.std_out.decode('utf-8', errors='ignore').strip().split())

print("\n[2] Granting low-privilege ACLs on DC03...")
ps_dc2 = """
$nc = (Get-ADRootDSE).configurationNamingContext
$templatePath = "AD:CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
$acl = Get-Acl -Path $templatePath
$khal = New-Object System.Security.Principal.NTAccount('ESSOS', 'khal.drogo')

# GenericWrite on CGPubPositive
$ace1 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
    $khal,
    [System.DirectoryServices.ActiveDirectoryRights]::GenericWrite,
    [System.Security.AccessControl.AccessControlType]::Allow
)
$acl.AddAccessRule($ace1)

# ExtendedRight: Certificate-Enrollment (0e10c968-78fb-11d2-90d4-00c04f79dc55)
$enrollGuid = [Guid]'0e10c968-78fb-11d2-90d4-00c04f79dc55'
$ace2 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
    $khal,
    [System.DirectoryServices.ActiveDirectoryRights]::ExtendedRight,
    [System.Security.AccessControl.AccessControlType]::Allow,
    $enrollGuid
)
$acl.AddAccessRule($ace2)

# Also grant viserys.targaryen Enroll
$vis = New-Object System.Security.Principal.NTAccount('ESSOS', 'viserys.targaryen')
$ace_vis = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
    $vis,
    [System.DirectoryServices.ActiveDirectoryRights]::ExtendedRight,
    [System.Security.AccessControl.AccessControlType]::Allow,
    $enrollGuid
)
$acl.AddAccessRule($ace_vis)

Set-Acl -Path $templatePath -AclObject $acl
Write-Output "CGPubPositive ACL updated successfully"

# GenericWrite on CN=viserys.targaryen
$uPath = "AD:CN=viserys.targaryen,CN=Users,DC=essos,DC=local"
$uAcl = Get-Acl -Path $uPath
$ace3 = New-Object System.DirectoryServices.ActiveDirectoryAccessRule(
    $khal,
    [System.DirectoryServices.ActiveDirectoryRights]::GenericWrite,
    [System.Security.AccessControl.AccessControlType]::Allow
)
$uAcl.AddAccessRule($ace3)
Set-Acl -Path $uPath -AclObject $uAcl
Write-Output "viserys.targaryen ACL updated successfully"

# Template User Enroll rights
$uTmplPath = "AD:CN=User,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
$uTmplAcl = Get-Acl -Path $uTmplPath
$uTmplAcl.AddAccessRule($ace2)
$uTmplAcl.AddAccessRule($ace_vis)
Set-Acl -Path $uTmplPath -AclObject $uTmplAcl
Write-Output "User template ACL updated successfully"
"""
r = s_dc.run_ps(ps_dc2)
print(r.std_out.decode('utf-8', errors='ignore'))
if r.std_err:
    print("DC03 ACL ERR:", r.std_err.decode('utf-8', errors='ignore'))

print("\n[3] Configuring SRV03 groups...")
ps_srv = """
Remove-LocalGroupMember -Group 'Administrators' -Member 'ESSOS\\khal.drogo' -ErrorAction SilentlyContinue
Add-LocalGroupMember -Group 'Remote Management Users' -Member 'ESSOS\\khal.drogo' -ErrorAction SilentlyContinue
Add-LocalGroupMember -Group 'Remote Management Users' -Member 'ESSOS\\viserys.targaryen' -ErrorAction SilentlyContinue
Write-Output "SRV03 local groups updated successfully"
"""
r = s_srv.run_ps(ps_srv)
print(r.std_out.decode('utf-8', errors='ignore'))

print("\n[4] Testing WinRM authentication as low-privilege ESSOS\\khal.drogo...")
try:
    s_khal_dc = winrm.Session('http://127.0.0.1:55985/wsman', auth=('ESSOS\\khal.drogo', 'horse'), transport='ntlm')
    r_khal = s_khal_dc.run_cmd('whoami /user & whoami /groups')
    print("khal.drogo on DC03 output:")
    print(r_khal.std_out.decode('utf-8', errors='ignore'))
    if r_khal.std_err:
        print("khal.drogo DC03 ERR:", r_khal.std_err.decode('utf-8', errors='ignore'))
except Exception as e:
    print("Error connecting as khal.drogo to DC03:", e)

try:
    s_khal_srv = winrm.Session('http://127.0.0.1:56985/wsman', auth=('ESSOS\\khal.drogo', 'horse'), transport='ntlm')
    r_khal_srv = s_khal_srv.run_cmd('whoami /user & whoami /groups')
    print("khal.drogo on SRV03 output:")
    print(r_khal_srv.std_out.decode('utf-8', errors='ignore'))
    if r_khal_srv.std_err:
        print("khal.drogo SRV03 ERR:", r_khal_srv.std_err.decode('utf-8', errors='ignore'))
except Exception as e:
    print("Error connecting as khal.drogo to SRV03:", e)
