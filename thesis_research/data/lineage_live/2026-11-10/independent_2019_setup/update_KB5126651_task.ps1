$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$out='C:\Q1Evidence\updates\KB5126651_result.json'
try {
 if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
 $path=(Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 5} | ForEach-Object {Join-Path ($_.DeviceID+'\') 'OCT26.MSU'} | Where-Object {Test-Path $_} | Select-Object -First 1)
 if(-not $path){throw 'Read-only update package absent'}
 $hash=(Get-FileHash $path -Algorithm SHA256).Hash.ToLower()
 if($hash -ne 'a0a374cf1f0a738823ad09b1a60a4feae1ff20a3c1022177d9d3c9deb06d691b'){throw 'Package content digest differs'}
 $signature=Get-AuthenticodeSignature $path
 $before=[DateTime]::UtcNow.ToString('o')
 $p=Start-Process wusa.exe -ArgumentList ($path+' /quiet /norestart') -Wait -PassThru
 @{kb='KB5126651';package_sha256=$hash;authenticode_status=[string]$signature.Status;authenticode_subject=$signature.SignerCertificate.Subject;started_utc=$before;ended_utc=[DateTime]::UtcNow.ToString('o');exit_code=$p.ExitCode;completed=$true;installer='WUSA normal signature/applicability validation'} | ConvertTo-Json -Compress | Set-Content $out
} catch { @{kb='KB5126651';completed=$false;error=$_.Exception.ToString()} | ConvertTo-Json -Compress | Set-Content $out;exit 1 }
