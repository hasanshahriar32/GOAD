if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$nc=(Get-ADRootDSE).configurationNamingContext
$flag=(Get-ADObject ('CN=Q1Evidence,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Properties msPKI-Certificate-Name-Flag).'msPKI-Certificate-Name-Flag'
if($flag -ne 33554432){throw 'Baseline not restored'}
@{utc=[DateTime]::UtcNow.ToString('o');restored_name_flag=$flag} | ConvertTo-Json -Compress
shutdown.exe /s /t 10
'RESTORED_LAB_SHUTDOWN_SCHEDULED'
