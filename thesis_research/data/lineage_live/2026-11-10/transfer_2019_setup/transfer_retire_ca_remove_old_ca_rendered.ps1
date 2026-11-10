if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '52-54-00-21-29-02'}).Count){throw 'Not the isolated transfer clone'}
if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Unexpected seed forest'}
Uninstall-AdcsCertificationAuthority -Force
$r=Uninstall-WindowsFeature ADCS-Cert-Authority
if(-not $r.Success){throw 'CA role removal failed'}
foreach($store in @('Cert:\LocalMachine\My','Cert:\LocalMachine\Root','Cert:\LocalMachine\CA')){
 Get-ChildItem $store | Where-Object {$_.Issuer -like '*CN=Q1-Evidence-CA*' -or $_.Subject -like '*CN=Q1-Evidence-CA*'} | Remove-Item -Force
}
'OLD_CA_REMOVED_FROM_CHILD_ONLY'