if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-CimInstance Win32_ComputerSystem).PartOfDomain){throw 'Refusing to replace an existing domain'}
Set-LocalUser Administrator -Password (ConvertTo-SecureString '<private-value-0>' -AsPlainText -Force)
Enable-LocalUser Administrator
Import-Module ADDSDeployment
Install-ADDSForest -DomainName 'q1transfer.test' -DomainNetbiosName Q1XFER -InstallDns -SafeModeAdministratorPassword (ConvertTo-SecureString '<private-value-2>' -AsPlainText -Force) -NoRebootOnCompletion -Force
shutdown.exe /r /t 8
'NEW_FOREST_INSTALLED_REBOOT_SCHEDULED'
