if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-CimInstance Win32_ComputerSystem).Domain -ne 'q1transfer.test'){throw 'Wrong clone forest'}
$adapter=Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}
Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex | Select AddressFamily,ServerAddresses | ConvertTo-Json -Compress
Set-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex -ServerAddresses @('127.0.0.1')
Set-DnsClient -InterfaceIndex $adapter.ifIndex -ConnectionSpecificSuffix 'q1transfer.test'
Clear-DnsClientCache
Restart-Service Netlogon
ipconfig.exe /registerdns | Out-Null
$domain=Get-ADDomain -Server localhost
if($domain.DNSRoot -ne 'q1transfer.test'){throw 'Local AD database belongs to another forest'}
@{domain=$domain.DNSRoot;domain_sid=$domain.DomainSID.Value;services=@(Get-Service ADWS,DNS,Netlogon | Select Name,Status);dns=@(Get-DnsClientServerAddress -InterfaceIndex $adapter.ifIndex | Select AddressFamily,ServerAddresses)}|ConvertTo-Json -Depth 5 -Compress
