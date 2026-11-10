if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-ADDomain).DNSRoot -ne 'q1transfer.test'){throw 'Wrong forest'}
$nc=(Get-ADRootDSE).configurationNamingContext
$flags=@(foreach($name in @('Q1TransferA','Q1TransferB')){
 $t=Get-ADObject ('CN='+$name+',CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Properties msPKI-Certificate-Name-Flag
 if($t.'msPKI-Certificate-Name-Flag' -ne 33554432){throw 'Transfer template not restored'}
 @{template=$name;name_flag=$t.'msPKI-Certificate-Name-Flag'}
})
@{utc=[DateTime]::UtcNow.ToString('o');restored_templates=$flags}|ConvertTo-Json -Depth 4 -Compress
shutdown.exe /s /t 10
'TRANSFER_SHUTDOWN_SCHEDULED'