if((Get-ADDomain).DNSRoot -ne 'q1transfer.test'){throw 'Wrong transfer forest'}
$config='HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration'
$active=(Get-ItemProperty $config).Active
if($active -ne 'Q1-Transfer-CA'){throw 'Unexpected active CA'}
$hash=@((Get-ItemProperty ($config+'\'+$active)).CACertHash)[-1]
$cert=Get-ChildItem Cert:\LocalMachine\My | Where-Object {$_.Thumbprint -eq $hash}
if(@($cert).Count -ne 1){throw 'CA certificate not uniquely found'}
$remote='C:\Q1TransferA\public_transfer_ca.cer'
Export-Certificate -Cert $cert -FilePath $remote -Type CERT | Out-Null
$root=Get-ADRootDSE
$ntauth=Get-ADObject ('CN=NTAuthCertificates,CN=Public Key Services,CN=Services,'+$root.configurationNamingContext) -Properties cACertificate
$thumbs=@($ntauth.cACertificate | ForEach-Object {(New-Object Security.Cryptography.X509Certificates.X509Certificate2 -ArgumentList @(,$_)).Thumbprint})
@{ca=$active;subject=$cert.Subject;issuer=$cert.Issuer;thumbprint=$cert.Thumbprint;ntauth_thumbprints=$thumbs;domain_sid=(Get-ADDomain).DomainSID.Value;utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Depth 4 -Compress
