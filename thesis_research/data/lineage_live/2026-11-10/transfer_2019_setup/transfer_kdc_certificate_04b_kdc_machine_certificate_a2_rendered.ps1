if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
$ready=$false;for($i=0;$i -lt 30;$i++){certutil.exe -config 'Q1XFER19.q1transfer.test\Q1-Transfer-CA' -ping;if($LASTEXITCODE -eq 0){$ready=$true;break};Start-Sleep 2};if(-not $ready){throw 'Transfer CA RPC not ready'};
if((Get-ADDomain).DNSRoot -ne 'q1transfer.test'){throw 'Wrong independent forest'}
$existing=@(Get-ChildItem Cert:\LocalMachine\My -SSLServerAuthentication | Where-Object {$_.HasPrivateKey -and $_.Issuer -like '*CN=Q1-Transfer-CA*' -and $_.Subject -ne $_.Issuer})
if($existing.Count -eq 0){
  $p=Start-Process certreq.exe -ArgumentList '-enroll -machine -q DomainController' -Wait -PassThru -NoNewWindow
  if($p.ExitCode -ne 0){throw ('KDC_CERTIFICATE_ENROLLMENT_EXIT:'+ $p.ExitCode)}
}
Restart-Service Kdc -Force
$machine=@(Get-ChildItem Cert:\LocalMachine\My -SSLServerAuthentication | Where-Object {$_.HasPrivateKey -and $_.Issuer -like '*CN=Q1-Transfer-CA*' -and $_.Subject -ne $_.Issuer})
if($machine.Count -eq 0){throw 'A CA signing certificate is not a KDC machine certificate'}
$machine | Select Subject,Issuer,Thumbprint,HasPrivateKey,NotAfter,@{Name='eku';Expression={@($_.EnhancedKeyUsageList | ForEach-Object {[string]$_.ObjectId})}} | ConvertTo-Json -Compress -Depth 5
