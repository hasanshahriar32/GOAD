if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
certutil.exe -config ($env:COMPUTERNAME+'.q1lab.test\Q1-Evidence-CA') -view -restrict 'Disposition=20' -out 'RequestID,RequesterName,SerialNumber,CertificateHash,CertificateTemplate' csv
if($LASTEXITCODE -ne 0){throw 'CA export failed'}
exit 0