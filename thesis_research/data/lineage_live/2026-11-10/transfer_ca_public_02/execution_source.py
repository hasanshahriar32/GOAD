"""Read-only public CA certificate and directory trust observation after pilot."""
import argparse
import json
from pathlib import Path

from ..transfer_workload import Runner,manifest
from scripts.capture_trace7_split_actor_delayed_pkinit import pull_file_winrm


def run(output):
    output.mkdir(parents=True,exist_ok=False);runner=Runner(output,'unused')
    script=r"""if((Get-ADDomain).DNSRoot -ne 'q1transfer.test'){throw 'Wrong transfer forest'}
$config='HKLM:\SYSTEM\CurrentControlSet\Services\CertSvc\Configuration'
$active=(Get-ItemProperty $config).Active
if($active -ne 'Q1-Transfer-CA'){throw 'Unexpected active CA'}
$hash=(@((Get-ItemProperty ($config+'\'+$active)).CACertHash)[-1] -replace '\s','').ToUpperInvariant()
$cert=@(foreach($store in @('Cert:\LocalMachine\My','Cert:\LocalMachine\Root','Cert:\LocalMachine\CA')){Get-ChildItem $store | Where-Object {$_.Thumbprint -eq $hash}}) | Sort-Object Thumbprint -Unique
if(@($cert).Count -ne 1 -or -not $cert){throw ('CA certificate not uniquely found for public hash '+$hash)}
$remote='C:\Q1TransferA\public_transfer_ca.cer'
Export-Certificate -Cert $cert -FilePath $remote -Type CERT | Out-Null
$root=Get-ADRootDSE
$ntauth=Get-ADObject ('CN=NTAuthCertificates,CN=Public Key Services,CN=Services,'+$root.configurationNamingContext) -Properties cACertificate
$thumbs=@($ntauth.cACertificate | ForEach-Object {([Security.Cryptography.X509Certificates.X509Certificate2]::new([byte[]]$_)).Thumbprint})
@{ca=$active;subject=$cert.Subject;issuer=$cert.Issuer;thumbprint=$cert.Thumbprint;ntauth_thumbprints=$thumbs;domain_sid=(Get-ADDomain).DomainSID.Value;utc=[DateTime]::UtcNow.ToString('o')}|ConvertTo-Json -Depth 4 -Compress
"""
    (output/'public_observation.ps1').write_text(script)
    runner.ps(runner.admin,'observation',script)
    (output/'ca_certificate.cer').write_bytes(pull_file_winrm(runner.admin,'C:\\Q1TransferA\\public_transfer_ca.cer'))
    (output/'execution_source.py').write_bytes(Path(__file__).read_bytes());manifest(output)
    print(json.dumps({'status':'captured','scope':'Public certificate and observed NTAuth membership only; no private-key export'}))


if __name__=='__main__':
    parser=argparse.ArgumentParser();parser.add_argument('output',type=Path);args=parser.parse_args();run(args.output)
