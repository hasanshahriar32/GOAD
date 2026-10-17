#!/usr/bin/env python3
"""
configure_lab_mesh.py — Sets static mesh IPs and DNS/hosts mapping on DC03 & SRV03
"""

import sys
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm')
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm')

print("[*] Setting static IP on DC03 Ethernet 4...")
r1 = s_dc03.run_ps("""
New-NetIPAddress -InterfaceAlias 'Ethernet 4' -IPAddress '192.168.56.23' -PrefixLength 24 -ErrorAction SilentlyContinue
Add-Content -Path 'C:\\Windows\\System32\\drivers\\etc\\hosts' -Value '192.168.56.22 braavos.essos.local braavos'
Add-DnsServerResourceRecordA -Name 'braavos' -ZoneName 'essos.local' -IPv4Address '192.168.56.22' -ErrorAction SilentlyContinue
""")
print("DC03 Output:", r1.std_out.decode().strip())

print("[*] Setting static IP on SRV03 Ethernet 4...")
r2 = s_srv03.run_ps("""
New-NetIPAddress -InterfaceAlias 'Ethernet 4' -IPAddress '192.168.56.22' -PrefixLength 24 -ErrorAction SilentlyContinue
Set-DnsClientServerAddress -InterfaceAlias 'Ethernet 4' -ServerAddresses '192.168.56.23' -ErrorAction SilentlyContinue
Add-Content -Path 'C:\\Windows\\System32\\drivers\\etc\\hosts' -Value '192.168.56.23 meereen.essos.local meereen'
""")
print("SRV03 Output:", r2.std_out.decode().strip())

print("[*] Testing RPC from DC03 to SRV03...")
r3 = s_dc03.run_ps("Test-NetConnection -ComputerName braavos.essos.local -Port 135 | Format-List")
print(r3.std_out.decode())

print("[*] Testing certificate enrollment on DC03...")
r4 = s_dc03.run_ps("""
$c = Get-Certificate -Template 'User' -CertStoreLocation 'Cert:\\CurrentUser\\My' -ErrorAction SilentlyContinue
if ($c) {
    Write-Output ("SUCCESS_ISSUED: Subject=" + $c.Certificate.Subject + " Serial=" + $c.Certificate.SerialNumber)
} else {
    Write-Output ("Error: " + $Error[0])
}
""")
print(r4.std_out.decode())
