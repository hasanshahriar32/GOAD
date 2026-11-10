"""A new forest in a child overlay of the preserved October-security-build VM.

The seed and original disk mounts are read-only. Changes affect only the child
overlay. Setup records executed scripts/sources, redacting generated secrets.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import secrets
import subprocess
from types import SimpleNamespace

import winrm
from . import provision_2019 as base

ROOT=Path(__file__).resolve().parents[4]
STATE=Path.home()/".cache/goad-q1-transfer-2019"
SEED=Path.home()/".cache/goad-q1-lab-2019"
ENDPOINT="http://127.0.0.1:57986/wsman"
DOMAIN="q1transfer.test"
NETBIOS="Q1XFER"
CA="Q1-Transfer-CA"
MAC="52-54-00-21-29-02"
NAME="goad-lineage-transfer2019"
OUTPUT=ROOT/"thesis_research/data/lineage_live/2026-11-10/transfer_2019_setup"
GUARD="if(-not @(Get-NetAdapter | Where-Object {$_.MacAddress -eq '"+MAC+"'}).Count){throw 'Not the isolated transfer clone'}\n"


def credentials():
    STATE.mkdir(parents=True,exist_ok=True)
    path=STATE/"credentials.json"
    if not path.exists():
        data={key:secrets.token_urlsafe(24)+"aA1!" for key in
              ("administrator_password","enroller_password","dsrm_password")}
        descriptor=os.open(path,os.O_CREAT|os.O_EXCL|os.O_WRONLY,0o600)
        with os.fdopen(descriptor,"w") as stream:json.dump(data,stream)
    return json.loads(path.read_text())


def connection(mode="domain", user=None):
    if mode=="old":
        secret=json.loads((SEED/"credentials.json").read_text())
        principal="Administrator"
    else:
        secret=credentials()
        principal="Administrator"
    password=secret["administrator_password"]
    if user:
        principal=user+"@"+DOMAIN;password=credentials()["enroller_password"]
    return winrm.Session(ENDPOINT,auth=(principal,password),transport="ntlm",read_timeout_sec=360,operation_timeout_sec=300)


def start():
    credentials()
    source=Path("/run/media/m4x1d/255fb331-4ad9-49d7-92b8-080d9effb0ef")
    if not (SEED/"windows2019.qcow2").exists() or not source.is_dir():raise FileNotFoundError("Preserved lab/source mount absent")
    if subprocess.run(["docker","container","inspect",NAME],capture_output=True).returncode==0:raise RuntimeError("Transfer container already exists")
    overlay=STATE/"transfer2019.qcow2"
    mounts=["-v",str(source)+":/source:ro","-v",str(SEED)+":/seed:ro","-v",str(STATE)+":/lab"]
    if not overlay.exists():
        subprocess.run(["docker","run","--rm","--network","none","--entrypoint","qemu-img",*mounts,
                        "goad-lineage-qemu:local","create","-f","qcow2","-F","qcow2","-b","/seed/windows2019.qcow2","/lab/transfer2019.qcow2"],check=True)
    command=["docker","run","-d","--name",NAME,"--network","goad-lineage-isolated","--device","/dev/kvm",
        "--memory","4096m","--cpus","2",*mounts,"-p","127.0.0.1:57986:15985","-p","127.0.0.4:88:18888",
        "-p","127.0.0.4:389:1389","-p","127.0.0.4:636:1636","goad-lineage-qemu:local",
        "-enable-kvm","-m","3072","-smp","2","-cpu","host","-drive","file=/lab/transfer2019.qcow2,format=qcow2,if=ide",
        "-netdev","user,id=mgmt,net=10.21.0.0/24,dhcpstart=10.21.0.15,restrict=on,hostfwd=tcp::15985-10.21.0.15:5985,hostfwd=tcp::18888-10.21.0.15:88,hostfwd=tcp::1389-10.21.0.15:389,hostfwd=tcp::1636-10.21.0.15:636",
        "-device","e1000,netdev=mgmt,mac=52:54:00:21:29:02","-display","none"]
    subprocess.run(command,check=True)
    OUTPUT.mkdir(parents=True,exist_ok=True)
    (OUTPUT/"launcher_source.py").write_bytes(Path(__file__).read_bytes())
    inspect=json.loads(subprocess.check_output(["docker","inspect",NAME],text=True))[0]
    mounts=inspect["Mounts"]
    assert all(not m["RW"] for m in mounts if m["Destination"] in ("/source","/seed"))
    (OUTPUT/"launch.json").write_text(json.dumps({"utc":datetime.now(timezone.utc).isoformat(),"command":command,"mounts":mounts},indent=2)+"\n")


def setup(action):
    OUTPUT.mkdir(parents=True,exist_ok=True)
    secret=credentials()
    old=json.loads((SEED/"credentials.json").read_text())
    redact={**secret,**{"old_"+k:v for k,v in old.items()}}
    original_execute=base.execute

    def execute(conn,phase,script,output,ignored):
        # Render the previously checked setup for a new namespace and objects.
        replacements={"q1lab.test":DOMAIN,"Q1LAB":NETBIOS,"Q1-Evidence-CA":CA,
                      "Q1Evidence":"Q1TransferA","q1.enroller":"q1.reader",
                      ".20261110.2019":".20261110.2029"}
        if action in ("template_b","remoting_b"):
            replacements.update({"Q1Evidence":"Q1TransferB","q1.enroller":"q1.operator",
                                 ".20261110.2019":".20261110.2030"})
        if action not in ("retire_ca","demote","rename","probe_old","probe_local","probe_domain","clock","shutdown"):
            for before,after in replacements.items():script=script.replace(before,after)
        script=GUARD+script
        name="transfer_"+action+"_"+phase
        # Capture exact executed wrapper and redacted public script even for short scripts.
        public=script
        for i,value in enumerate(redact.values()):public=public.replace(value,"<private-value-"+str(i)+">")
        (OUTPUT/(name+"_rendered.ps1")).write_text(public)
        (OUTPUT/(name+"_executed_setup.py")).write_bytes(Path(__file__).read_bytes())
        return original_execute(conn,name,script,OUTPUT,redact)

    base.execute=execute
    base.credentials=lambda:secret
    base.session=lambda mode,ignored:connection("local" if mode=="local" else "domain")
    if action.startswith("probe_"):
        mode=action.removeprefix("probe_")
        execute(connection(mode),"inventory","""$v=Get-ItemProperty 'HKLM:\SOFTWARE\Microsoft\Windows NT\CurrentVersion';$c=Get-CimInstance Win32_ComputerSystem
@{domain=$c.Domain;domain_member=$c.PartOfDomain;computer=$env:COMPUTERNAME;build=$v.CurrentBuild;ubr=$v.UBR;utc=[DateTime]::UtcNow.ToString('o')} | ConvertTo-Json -Compress""",OUTPUT,redact)
    elif action=="retire_ca":
        execute(connection("old"),"remove_old_ca","""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Unexpected seed forest'}
Uninstall-AdcsCertificationAuthority -Force
$r=Uninstall-WindowsFeature ADCS-Cert-Authority
if(-not $r.Success){throw 'CA role removal failed'}
foreach($store in @('Cert:\LocalMachine\My','Cert:\LocalMachine\Root','Cert:\LocalMachine\CA')){
 Get-ChildItem $store | Where-Object {$_.Issuer -like '*CN=Q1-Evidence-CA*' -or $_.Subject -like '*CN=Q1-Evidence-CA*'} | Remove-Item -Force
}
'OLD_CA_REMOVED_FROM_CHILD_ONLY'""",OUTPUT,redact)
    elif action=="demote":
        script="""if((Get-ADDomain).DNSRoot -ne 'q1lab.test'){throw 'Unexpected seed forest'}
Uninstall-ADDSDomainController -LastDomainControllerInDomain -RemoveApplicationPartitions -DemoteOperationMasterRole -IgnoreLastDNSServerForZone -LocalAdministratorPassword (ConvertTo-SecureString 'LOCAL_SECRET' -AsPlainText -Force) -NoRebootOnCompletion -Force
shutdown.exe /r /t 10
'CHILD_FOREST_REMOVED_REBOOT_SCHEDULED'""".replace("LOCAL_SECRET",secret["administrator_password"])
        execute(connection("old"),"new_standalone",script,OUTPUT,redact)
    elif action=="rename":
        execute(connection("local"),"rename_host","""if((Get-CimInstance Win32_ComputerSystem).PartOfDomain){throw 'Expected standalone clone'}
Rename-Computer -NewName Q1XFER19 -Force
shutdown.exe /r /t 10
'NEW_HOSTNAME_REBOOT_SCHEDULED'""",OUTPUT,redact)
    elif action=="clock":
        execute(connection(),"clock","if((Get-ADDomain).DNSRoot -ne '"+DOMAIN+"'){throw 'Wrong forest'};Set-Date -Date ([DateTime]::Parse('"+datetime.now(timezone.utc).isoformat()+"').ToLocalTime()) | Out-Null;[DateTime]::UtcNow.ToString('o')",OUTPUT,redact)
    elif action=="shutdown":
        execute(connection(),"shutdown","if((Get-ADDomain).DNSRoot -ne '"+DOMAIN+"'){throw 'Wrong forest'};shutdown.exe /s /t 10;'TRANSFER_SHUTDOWN_SCHEDULED'",OUTPUT,redact)
    else:
        mapped={"new_forest":"forest","template_a":"template","template_b":"template",
                "remoting_a":"enroller_remoting","remoting_b":"enroller_remoting"}.get(action,action)
        base.run(SimpleNamespace(action=mapped,output=OUTPUT))


if __name__=="__main__":
    parser=argparse.ArgumentParser();parser.add_argument("action",choices=["start","probe_old","retire_ca","demote","probe_local","rename","new_forest","probe_domain","ca","template_a","template_b","kdc_certificate","remoting_a","remoting_b","clock","shutdown"])
    args=parser.parse_args()
    if args.action=="start":start()
    else:setup(args.action)
