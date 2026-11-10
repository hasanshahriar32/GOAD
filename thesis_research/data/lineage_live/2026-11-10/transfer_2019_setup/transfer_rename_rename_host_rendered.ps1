if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-CimInstance Win32_ComputerSystem).PartOfDomain){throw 'Expected standalone clone'}
Rename-Computer -NewName Q1XFER19 -Force
shutdown.exe /r /t 10
'NEW_HOSTNAME_REBOOT_SCHEDULED'