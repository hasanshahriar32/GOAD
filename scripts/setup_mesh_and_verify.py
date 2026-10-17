#!/usr/bin/env python3
"""
setup_mesh_and_verify.py — Sets static mesh IPs and verifies bidirectional socket connectivity
"""

import sys
import base64
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm', read_timeout_sec=60, operation_timeout_sec=50)

hosts_content = "127.0.0.1 localhost\r\n192.168.56.23 meereen.essos.local meereen\r\n192.168.56.22 braavos.essos.local braavos\r\n"
b64 = base64.b64encode(hosts_content.encode('utf-8')).decode('ascii')

print("[*] Configuring DC03...")
dc_cmd = f"""
New-NetIPAddress -InterfaceAlias 'Ethernet 4' -IPAddress '192.168.56.23' -PrefixLength 24 -ErrorAction SilentlyContinue
[IO.File]::WriteAllBytes('C:\\Windows\\System32\\drivers\\etc\\hosts', [Convert]::FromBase64String('{b64}'))
"""
r1 = s_dc03.run_ps(dc_cmd)
print("DC03 setup done, code:", r1.status_code)

print("[*] Configuring SRV03...")
srv_cmd = f"""
New-NetIPAddress -InterfaceAlias 'Ethernet 4' -IPAddress '192.168.56.22' -PrefixLength 24 -ErrorAction SilentlyContinue
[IO.File]::WriteAllBytes('C:\\Windows\\System32\\drivers\\etc\\hosts', [Convert]::FromBase64String('{b64}'))
"""
r2 = s_srv03.run_ps(srv_cmd)
print("SRV03 setup done, code:", r2.status_code)

print("[*] Testing DC03 -> SRV03 TCP Port 135...")
test_script1 = """
$client = New-Object System.Net.Sockets.TcpClient
try {
    $client.Connect('192.168.56.22', 135)
    Write-Output "DC03 -> SRV03 Port 135: CONNECTED_SUCCESS"
    $client.Close()
} catch {
    Write-Output ("DC03 -> SRV03 Port 135 FAILED: " + $_.Exception.Message)
}
"""
r3 = s_dc03.run_ps(test_script1)
print(r3.std_out.decode().strip())

print("[*] Testing SRV03 -> DC03 TCP Port 88 (Kerberos)...")
test_script2 = """
$client = New-Object System.Net.Sockets.TcpClient
try {
    $client.Connect('192.168.56.23', 88)
    Write-Output "SRV03 -> DC03 Port 88: CONNECTED_SUCCESS"
    $client.Close()
} catch {
    Write-Output ("SRV03 -> DC03 Port 88 FAILED: " + $_.Exception.Message)
}
"""
r4 = s_srv03.run_ps(test_script2)
print(r4.std_out.decode().strip())
