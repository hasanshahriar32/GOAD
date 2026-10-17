#!/usr/bin/env python3
import sys
import base64
sys.path.insert(0, '/home/m4x1d/Desktop/GOAD/.venv/lib/python3.11/site-packages')
import winrm

s_dc03 = winrm.Session('http://127.0.0.1:55985/wsman', auth=('vagrant', 'vagrant'), transport='ntlm')
s_srv03 = winrm.Session('http://127.0.0.1:56985/wsman', auth=('ESSOS\\vagrant', 'vagrant'), transport='ntlm')

# Read C:\srv_cert.cer from SRV03
r_cer = s_srv03.run_ps('[System.IO.File]::ReadAllText("C:\\srv_cert.cer")')
cer_text = r_cer.std_out.decode('utf-8', errors='ignore')

# Push to DC03 and accept
encoded = base64.b64encode(cer_text.encode('utf-8')).decode('ascii')
accept_ps = f'''
$bytes = [System.Convert]::FromBase64String("{encoded}")
[System.IO.File]::WriteAllBytes("C:\\issued_cert.cer", $bytes)
$p = Start-Process -FilePath "certreq.exe" -ArgumentList "-accept -q -f C:\\issued_cert.cer" -Wait -PassThru -NoNewWindow
Write-Output ("CertReq Accept ExitCode: " + $p.ExitCode)
Get-ChildItem Cert:\\CurrentUser\\My | Select-Object Subject, Thumbprint, NotAfter
'''
r_acc = s_dc03.run_ps(accept_ps)
print("DC03 Accept Output:\n", r_acc.std_out.decode('utf-8', errors='ignore'))
