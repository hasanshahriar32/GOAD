"""Install official updates only in the independently provisioned lab copy."""
import argparse
import base64
import hashlib
import json
from pathlib import Path

from .provision_2019 import credentials,session,execute

ROOT=Path(__file__).resolve().parents[4]
OUTPUT=ROOT/"thesis_research/data/lineage_live/2026-11-10/independent_2019_setup"
PACKAGES={"july":("KB5062557","JULY25.MSU"),"october":("KB5126651","OCT26.MSU")}


def start(which):
    kb,file=PACKAGES[which]
    manifest=json.loads((OUTPUT/"11_verified_update_media.json").read_text())
    expected=next(r["sha256"] for r in manifest["packages"] if r["kb"]==kb)
    script=r"""$ErrorActionPreference='Stop';$ProgressPreference='SilentlyContinue'
$out='C:\Q1Evidence\updates\KB_TOKEN_result.json'
try {
 if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
 $path=(Get-CimInstance Win32_LogicalDisk | Where-Object {$_.DriveType -eq 5} | ForEach-Object {Join-Path ($_.DeviceID+'\') 'FILE_TOKEN'} | Where-Object {Test-Path $_} | Select-Object -First 1)
 if(-not $path){throw 'Read-only update package absent'}
 $hash=(Get-FileHash $path -Algorithm SHA256).Hash.ToLower()
 if($hash -ne 'HASH_TOKEN'){throw 'Package content digest differs'}
 $signature=Get-AuthenticodeSignature $path
 $before=[DateTime]::UtcNow.ToString('o')
 $p=Start-Process wusa.exe -ArgumentList ($path+' /quiet /norestart') -Wait -PassThru
 @{kb='KB_TOKEN';package_sha256=$hash;authenticode_status=[string]$signature.Status;authenticode_subject=$signature.SignerCertificate.Subject;started_utc=$before;ended_utc=[DateTime]::UtcNow.ToString('o');exit_code=$p.ExitCode;completed=$true;installer='WUSA normal signature/applicability validation'} | ConvertTo-Json -Compress | Set-Content $out
} catch { @{kb='KB_TOKEN';completed=$false;error=$_.Exception.ToString()} | ConvertTo-Json -Compress | Set-Content $out;exit 1 }
""".replace("KB_TOKEN",kb).replace("FILE_TOKEN",file).replace("HASH_TOKEN",expected)
    script_path=OUTPUT/("update_"+kb+"_task.ps1")
    if script_path.exists():raise FileExistsError(script_path)
    script_path.write_text(script)
    (OUTPUT/("update_"+kb+"_source.py")).write_bytes(Path(__file__).read_bytes())
    encoded=base64.b64encode(script.encode()).decode()
    remote="C:\\Windows\\Temp\\Q1Install_"+kb+".ps1"
    management=r"""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Wrong independent forest'}
New-Item 'C:\Q1Evidence\updates' -ItemType Directory -Force | Out-Null
$task='GoadQ1-Update-KB_TOKEN'
if(Get-ScheduledTask -TaskName $task -ErrorAction SilentlyContinue){throw 'Owned update task already exists'}
[IO.File]::WriteAllBytes('REMOTE_TOKEN',[Convert]::FromBase64String('ENCODED_TOKEN'))
if((Get-FileHash 'REMOTE_TOKEN' -Algorithm SHA256).Hash.ToLower() -ne 'SCRIPT_HASH_TOKEN'){throw 'Task source differs'}
$action=New-ScheduledTaskAction -Execute powershell.exe -Argument '-NoProfile -File REMOTE_TOKEN'
$principal=New-ScheduledTaskPrincipal -UserId SYSTEM -LogonType ServiceAccount -RunLevel Highest
$settings=New-ScheduledTaskSettingsSet -ExecutionTimeLimit (New-TimeSpan -Hours 2)
Register-ScheduledTask -TaskName $task -Action $action -Principal $principal -Settings $settings | Out-Null
Start-ScheduledTask -TaskName $task
'OWNED_LOCAL_UPDATE_TASK_STARTED'
""".replace("KB_TOKEN",kb).replace("REMOTE_TOKEN",remote).replace("ENCODED_TOKEN",encoded).replace("SCRIPT_HASH_TOKEN",hashlib.sha256(script.encode()).hexdigest())
    secret=credentials();print(execute(session("domain",secret),"12_start_"+kb,management,OUTPUT,secret))


def status(which):
    kb,_=PACKAGES[which];secret=credentials();s=session("domain",secret)
    result=s.run_ps("$p='C:\\Q1Evidence\\updates\\"+kb+"_result.json';if(Test-Path $p){Get-Content $p -Raw}else{Get-ScheduledTask -TaskName 'GoadQ1-Update-"+kb+"' | Select TaskName,State | ConvertTo-Json -Compress}")
    value=result.std_out.decode("utf-8-sig",errors="replace")
    print(value)
    if '"completed"' in value:
        path=OUTPUT/("13_result_"+kb+".json")
        if not path.exists():path.write_text(value)


if __name__=="__main__":
    p=argparse.ArgumentParser();p.add_argument("action",choices=("start","status"));p.add_argument("package",choices=PACKAGES)
    args=p.parse_args();start(args.package) if args.action=="start" else status(args.package)
