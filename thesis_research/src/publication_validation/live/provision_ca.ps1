# Controlled user-owned GOAD lab only. Creates a new CA if none exists.
# Before use: matching powered-off DC03/SRV03 snapshots must exist.
$ErrorActionPreference = 'Stop'
$ProgressPreference = 'SilentlyContinue'
if ($env:COMPUTERNAME -ne 'BRAAVOS') { throw 'Wrong host: expected BRAAVOS' }
if ((Get-CimInstance Win32_ComputerSystem).Domain -ne 'essos.local') { throw 'Wrong domain' }
if (Get-Service CertSvc -ErrorAction SilentlyContinue) { throw 'A CA already exists; refusing replacement' }
$feature = Install-WindowsFeature ADCS-Cert-Authority -IncludeManagementTools
$feature | Select-Object Success,RestartNeeded,ExitCode | ConvertTo-Json -Compress
if (!$feature.Success) { throw 'Feature installation failed' }
# Domain administrative credential is supplied in-memory by the runner.
$setup = Install-AdcsCertificationAuthority -Credential $PublicationCredential -CAType EnterpriseRootCA -CACommonName 'CertGraph-Lab-CA' -CryptoProviderName 'RSA#Microsoft Software Key Storage Provider' -KeyLength 2048 -HashAlgorithmName SHA256 -ValidityPeriod Years -ValidityPeriodUnits 1 -Force
$setup | ConvertTo-Json -Depth 4 -Compress
Get-Service CertSvc | Select-Object Name,Status | ConvertTo-Json -Compress
