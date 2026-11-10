"""Sequential child-clone setup with explicit reboot readiness barriers."""
from datetime import datetime,timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import time

from .transfer_2019 import connection,OUTPUT,DOMAIN


def ready(mode,expected,hostname=None):
    deadline=time.monotonic()+900
    while time.monotonic()<deadline:
        try:
            r=connection(mode).run_ps("$c=Get-CimInstance Win32_ComputerSystem;@{domain=$c.Domain;name=$env:COMPUTERNAME}|ConvertTo-Json -Compress")
            d=json.loads(r.std_out.decode('utf-8-sig'))
            if not r.status_code and d['domain'].casefold()==expected.casefold() and (not hostname or d['name']==hostname):return
        except Exception:pass
        time.sleep(10)
    raise TimeoutError("Reboot/forest readiness not reached")


def action(name):
    print(datetime.now(timezone.utc).isoformat(),name,flush=True)
    log=OUTPUT/("orchestrator_"+name+".log")
    with log.open('x') as stream:
        subprocess.run([sys.executable,'-m','thesis_research.src.lineage_constraints.lab.transfer_2019',name],stdout=stream,stderr=subprocess.STDOUT,check=True)


if __name__=='__main__':
    ready('local','WORKGROUP')
    action('rename');ready('local','WORKGROUP','Q1XFER19')
    action('new_forest');ready('domain',DOMAIN,'Q1XFER19')
    for name in ('ca','template_a','template_b','kdc_certificate','remoting_a','remoting_b','clock','probe_domain'):action(name)
    (OUTPUT/'setup_orchestrator_source.py').write_bytes(Path(__file__).read_bytes())
    (OUTPUT/'manifest.json').write_text(json.dumps({p.name:hashlib.sha256(p.read_bytes()).hexdigest() for p in OUTPUT.iterdir() if p.is_file() and p.name!='manifest.json'},indent=2)+'\n')
    print('TRANSFER_SETUP_COMPLETE',flush=True)
