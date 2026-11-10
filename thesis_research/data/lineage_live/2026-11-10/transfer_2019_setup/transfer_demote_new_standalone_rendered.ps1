if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Unexpected seed forest'}
Uninstall-ADDSDomainController -LastDomainControllerInDomain -RemoveApplicationPartitions -DemoteOperationMasterRole -IgnoreLastDNSServerForZone -LocalAdministratorPassword (ConvertTo-SecureString '<private-value-0>' -AsPlainText -Force) -NoRebootOnCompletion -Force
shutdown.exe /r /t 10
'CHILD_FOREST_REMOVED_REBOOT_SCHEDULED'