if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
$kb=Get-HotFix -Id KB5126651
if(-not (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending')){throw 'No pending servicing reboot'}
@{kb=$kb.HotFixID;utc=[DateTime]::UtcNow.ToString('o');basis='Signed package, recorded CBS S_OK and pending reboot; WUSA completion is reported separately if available'} | ConvertTo-Json -Compress
shutdown.exe /r /t 10 /d p:2:17
'CONTROLLED_PATCH_REBOOT_SCHEDULED'
