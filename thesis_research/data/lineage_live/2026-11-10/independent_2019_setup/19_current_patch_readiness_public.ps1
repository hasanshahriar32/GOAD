if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$v=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$pending=Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
if($v.CurrentBuild -ne '17763' -or $v.UBR -ne 9376 -or $pending){throw 'Required installed build or servicing readiness not observed'}
$kb=Get-HotFix -Id KB5126651
$services=@(Get-Service CertSvc,Kdc)
if(@($services | Where-Object {$_.Status -ne 'Running'}).Count){throw 'Lab services not running'}
$d=Get-ADDomain;$u=Get-ADUser q1.enroller -Properties Enabled;$groups=@(Get-ADPrincipalGroupMembership $u | Select Name,@{n='SID';e={$_.SID.Value}})
if(-not $u.Enabled -or @($groups | Where-Object {$_.SID -eq ($d.DomainSID.Value+'-512')}).Count){throw 'Unexpected enroller privilege/state'}
$nc=(Get-ADRootDSE).configurationNamingContext
$t=Get-ADObject ('CN=Q1Evidence,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Properties msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,pKIExtendedKeyUsage
if($t.'msPKI-Certificate-Name-Flag' -ne 33554432){throw 'Baseline template not restored'}
$k=Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Kdc' -ErrorAction SilentlyContinue
$o=Get-CimInstance Win32_OperatingSystem
@{build=$v.CurrentBuild;ubr=$v.UBR;hotfix=$kb.HotFixID;reboot_pending=$pending;utc=[DateTime]::UtcNow.ToString('o');last_boot=$o.LastBootUpTime;os=$o.Caption;strong_binding_registry=$k.StrongCertificateBindingEnforcement;use_subject_alt_name=$k.UseSubjectAltName;kdc_file_version=(Get-Item ($env:windir+'\System32\kdcsvc.dll')).VersionInfo.FileVersion;domain=$d.DNSRoot;enroller_sid=$u.SID.Value;groups=$groups;name_flag=$t.'msPKI-Certificate-Name-Flag';enrollment_flag=$t.'msPKI-Enrollment-Flag';eku=$t.pKIExtendedKeyUsage;services=@($services | Select Name,Status);defender=(Get-MpComputerStatus | Select AntivirusEnabled,RealTimeProtectionEnabled)} | ConvertTo-Json -Depth 6 -Compress
auditpol.exe /get /subcategory:'Kerberos Authentication Service'
auditpol.exe /get /subcategory:'Certification Services'
auditpol.exe /get /subcategory:'Directory Service Changes'
