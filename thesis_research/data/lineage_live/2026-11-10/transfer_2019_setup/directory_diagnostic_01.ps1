$ErrorActionPreference='Continue'
whoami /user
Get-CimInstance Win32_OperatingSystem | Select LastBootUpTime | ConvertTo-Json -Compress
Get-Service ADWS,Netlogon,DNS,DFSR | Select Name,Status | ConvertTo-Json -Compress
Get-SmbShare | Select Name | ConvertTo-Json -Compress
Get-ADDomain -Server localhost | Select DNSRoot,DomainSID | ConvertTo-Json -Compress
nltest.exe /dsgetdc:q1transfer.test /force
Resolve-DnsName -Name '_ldap._tcp.dc._msdcs.q1transfer.test' -Type SRV -Server 127.0.0.1 | Select Name,NameTarget,Port | ConvertTo-Json -Compress
Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Netlogon\Parameters' | Select SysvolReady | ConvertTo-Json -Compress
Get-WinEvent -LogName 'DFS Replication' -MaxEvents 6 | Select Id,TimeCreated,Message | ConvertTo-Json -Depth 4 -Compress
exit 0