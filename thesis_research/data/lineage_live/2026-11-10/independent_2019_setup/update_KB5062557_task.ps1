$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$out='C:\Q1Evidence\updates\KB5062557_result.json'
try {
 if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
 $path=(Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 5} | ForEach-Object {Join-Path ($_.DeviceID+'\') 'JULY25.MSU'} | Where-Object {Test-Path $_} | Select-Object -First 1)
 if(-not $path){throw 'Read-only update package absent'}
 $hash=(Get-FileHash $path -Algorithm SHA256).Hash.ToLower()
 if($hash -ne '4d9db36760f2ea5876f5212f1a977b64917061b06b257f876c8f036f629691f2'){throw 'Package content digest differs'}
 $signature=Get-AuthenticodeSignature $path
 $before=[DateTime]::UtcNow.ToString('o')
 $p=Start-Process wusa.exe -ArgumentList ($path+' /quiet /norestart') -Wait -PassThru
 @{kb='KB5062557';package_sha256=$hash;authenticode_status=[string]$signature.Status;authenticode_subject=$signature.SignerCertificate.Subject;started_utc=$before;ended_utc=[DateTime]::UtcNow.ToString('o');exit_code=$p.ExitCode;completed=$true;installer='WUSA normal signature/applicability validation'} | ConvertTo-Json -Compress | Set-Content $out
} catch { @{kb='KB5062557';completed=$false;error=$_.Exception.ToString()} | ConvertTo-Json -Compress | Set-Content $out;exit 1 }
