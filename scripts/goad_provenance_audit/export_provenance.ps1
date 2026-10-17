<#
.SYNOPSIS
    export_provenance.ps1 — Lossless XML Export of Security Provenance Events
    Run on DC03 (192.168.56.12) & SRV03 (192.168.56.23)
.DESCRIPTION
    Dumps all relevant Security and CA events to XML files for CIPG parser ingestion.
#>

$TargetEventIDs = @(4624, 4625, 4662, 4672, 4768, 4769, 4886, 4887, 4898, 4899, 4900, 5136)
$StartTime = (Get-Date).AddHours(-3)
$Hostname = $env:COMPUTERNAME
$OutFile = "C:\Users\Public\${Hostname}_provenance_events.xml"

Write-Host "[*] Querying Security Event Log for Host: $Hostname..." -ForegroundColor Yellow

$Events = Get-WinEvent -FilterHashtable @{
    LogName   = 'Security'
    ID        = $TargetEventIDs
    StartTime = $StartTime
} -ErrorAction SilentlyContinue

if ($Events) {
    Write-Host "[+] Found $($Events.Count) matching provenance events. Exporting to XML..." -ForegroundColor Green
    $Events | ForEach-Object { $_.ToXml() } | Out-File -FilePath $OutFile -Encoding UTF8
    Write-Host "[+] Successfully saved: $OutFile" -ForegroundColor Green
} else {
    Write-Warning "No matching events found in the last 3 hours."
}

# If IIS is running on SRV03, also copy W3SVC1 HTTP logs
if (Test-Path "C:\inetpub\logs\LogFiles\W3SVC1") {
    Write-Host "[*] Copying IIS Web Enrollment HTTP logs..." -ForegroundColor Yellow
    Copy-Item "C:\inetpub\logs\LogFiles\W3SVC1\*.log" "C:\Users\Public\" -ErrorAction SilentlyContinue
    Write-Host "[+] Copied IIS logs to C:\Users\Public\" -ForegroundColor Green
}
