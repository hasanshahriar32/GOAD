if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-ADDomain).DNSRoot -ne 'q1transfer.test'){throw 'Wrong independent forest'}
$u=Get-ADUser q1.reader
$path='WSMan:\localhost\Service\RootSDDL'
$before=(Get-Item $path).Value
$ace='(A;;GRGX;;;'+$u.SID.Value+')'
if($before -notlike ('*'+$u.SID.Value+'*')){
 $parts=$before -split 'S:',2
 if($parts.Count -ne 2){throw 'Unexpected WinRM root descriptor shape'}
 $after=$parts[0]+$ace+'S:'+$parts[1]
 Set-Item $path -Value $after -Force
}
@{principal_sid=$u.SID.Value;rights='Read and Execute on WinRM service only';before=$before;after=(Get-Item $path).Value;domain_admin_membership=@(Get-ADPrincipalGroupMembership $u | Where-Object {$_.SID.Value -eq ((Get-ADDomain).DomainSID.Value+'-512')}).Count} | ConvertTo-Json -Compress
