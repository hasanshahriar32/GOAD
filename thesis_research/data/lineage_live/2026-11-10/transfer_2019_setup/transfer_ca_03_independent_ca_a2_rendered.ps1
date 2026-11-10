if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-ADDomain).DNSRoot -ne 'q1transfer.test'){throw 'Wrong independent forest'}
$feature=Install-WindowsFeature ADCS-Cert-Authority -IncludeManagementTools
if(-not $feature.Success){throw 'CA feature installation failed'}
$active=(Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration' -Name Active -ErrorAction SilentlyContinue).Active
if($active){throw 'Refusing replacement of existing CA'}
Install-AdcsCertificationAuthority -CAType EnterpriseRootCA -CACommonName 'Q1-Transfer-CA' -CryptoProviderName 'RSA#Microsoft Software Key Storage Provider' -KeyLength 2048 -HashAlgorithmName SHA256 -ValidityPeriod Years -ValidityPeriodUnits 1 -Force
certutil -setreg CA\AuditFilter 127
certutil -setreg policy\EditFlags +EDITF_AUDITCERTTEMPLATELOAD
auditpol /set /subcategory:'Certification Services' /success:enable /failure:enable
auditpol /set /subcategory:'Kerberos Authentication Service' /success:enable /failure:enable
auditpol /set /subcategory:'Directory Service Changes' /success:enable /failure:enable
Restart-Service CertSvc
Get-Service CertSvc | Select Name,Status | ConvertTo-Json -Compress
