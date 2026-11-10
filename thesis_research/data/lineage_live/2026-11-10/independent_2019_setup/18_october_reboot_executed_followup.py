"""Explicit, source-retained readiness/reboot steps for the independent lab."""
import argparse
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path

from .provision_2019 import credentials,session,execute,ROOT

SOURCE=Path(__file__).read_bytes()
OUTPUT=ROOT/"thesis_research/data/lineage_live/2026-11-10/independent_2019_setup"
GUARD="if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}\n"


def run(action):
    if action=="reboot":
        phase="18_october_reboot"
        body=r"""$kb=Get-HotFix -Id KB5126651
if(-not (Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending')){throw 'No pending servicing reboot'}
@{kb=$kb.HotFixID;utc=[DateTime]::UtcNow.ToString('o');basis='Signed package, recorded CBS S_OK and pending reboot; WUSA completion is reported separately if available'} | ConvertTo-Json -Compress
shutdown.exe /r /t 10 /d p:2:17
'CONTROLLED_PATCH_REBOOT_SCHEDULED'
"""
    elif action=="readiness":
        phase="19_current_patch_readiness"
        body=r"""$v=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion'
$pending=Test-Path 'HKLM:\SOFTWARE\Microsoft\Windows\CurrentVersion\Component Based Servicing\RebootPending'
if($v.CurrentBuild -ne '17763' -or $v.UBR -ne 9376 -or $pending){throw 'Required installed build or servicing readiness not observed'}
$kb=Get-HotFix -Id KB5126651
$services=@(Get-Service CertSvc,Kdc)
if(@($services | Where-Object {$_.Status -ne 'Running'}).Count){throw 'Lab services not running'}
$d=Get-ADDomain;$u=Get-ADUser q1.enroller -Properties Enabled;$groups=@(Get-ADPrincipalGroupMembership $u | Select Name,@{n='SID';e={$_.SID.Value}})
if(-not $u.Enabled -or @($groups | Where-Object {$_.SID -eq ($d.DomainSID.Value+'-512')}).Count){throw 'Unexpected enroller privilege/state'}
$nc=(Get-ADRootDSE).configurationNamingContext
$t=Get-ADObject ('CN=Q1Evidence,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Properties msPKI-Certificate-Name-Flag,msPKI-Enrollment-Flag,pKIExtendedKeyUsage
if($t.'msPKI-Certificate-Name-Flag' -ne 33554432){throw 'Baseline template not restored'}
$k=Get-ItemProperty 'HKLM:\SYSTEM\CurrentControlSet\Services\Kdc' -ErrorAction SilentlyContinue
$o=Get-CimInstance Win32_OperatingSystem
@{build=$v.CurrentBuild;ubr=$v.UBR;hotfix=$kb.HotFixID;reboot_pending=$pending;utc=[DateTime]::UtcNow.ToString('o');last_boot=$o.LastBootUpTime;os=$o.Caption;strong_binding_registry=$k.StrongCertificateBindingEnforcement;use_subject_alt_name=$k.UseSubjectAltName;kdc_file_version=(Get-Item ($env:windir+'\System32\kdcsvc.dll')).VersionInfo.FileVersion;domain=$d.DNSRoot;enroller_sid=$u.SID.Value;groups=$groups;name_flag=$t.'msPKI-Certificate-Name-Flag';enrollment_flag=$t.'msPKI-Enrollment-Flag';eku=$t.pKIExtendedKeyUsage;services=@($services | Select Name,Status);defender=(Get-MpComputerStatus | Select AntivirusEnabled,RealTimeProtectionEnabled)} | ConvertTo-Json -Depth 6 -Compress
auditpol.exe /get /subcategory:'Kerberos Authentication Service'
auditpol.exe /get /subcategory:'Certification Services'
auditpol.exe /get /subcategory:'Directory Service Changes'
"""
    elif action=="clock":
        phase="20_correct_collection_clock"
        now=datetime.now(timezone.utc).isoformat()
        body="$before=[DateTime]::UtcNow;Set-Date -Date ([DateTime]::Parse('"+now+"').ToLocalTime()) | Out-Null;@{before_utc=$before.ToString('o');after_utc=[DateTime]::UtcNow.ToString('o');reason='Align independent lab copy with actual host UTC before new PKINIT trials; not a historical audit-clock calibration claim'} | ConvertTo-Json -Compress"
    else:
        phase="22_final_shutdown"
        body=r"""$nc=(Get-ADRootDSE).configurationNamingContext
$flag=(Get-ADObject ('CN=Q1Evidence,CN=Certificate Templates,CN=Public Key Services,CN=Services,'+$nc) -Properties msPKI-Certificate-Name-Flag).'msPKI-Certificate-Name-Flag'
if($flag -ne 33554432){throw 'Baseline not restored'}
@{utc=[DateTime]::UtcNow.ToString('o');restored_name_flag=$flag} | ConvertTo-Json -Compress
shutdown.exe /s /t 10
'RESTORED_LAB_SHUTDOWN_SCHEDULED'
"""
    script=GUARD+body
    script_path=OUTPUT/(phase+"_public.ps1")
    if script_path.exists():raise FileExistsError(script_path)
    script_path.write_text(script);(OUTPUT/(phase+"_executed_followup.py")).write_bytes(SOURCE)
    (OUTPUT/(phase+"_request_manifest.json")).write_text(json.dumps({"source_sha256":hashlib.sha256(SOURCE).hexdigest(),
        "public_script_sha256":hashlib.sha256(script.encode()).hexdigest(),"action":action,"scope":"Independent writable q1lab.test copy only"},indent=2)+"\n")
    secret=credentials();print(execute(session("domain",secret),phase,script,OUTPUT,secret))


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("action",choices=("reboot","readiness","clock","shutdown"));args=p.parse_args();run(args.action)
