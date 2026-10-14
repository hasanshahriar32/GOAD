"""Provision only the snapshot-protected ESSOS lab CA; no silent replacement."""
import base64,gzip,hashlib,json,subprocess,datetime,os
from pathlib import Path
import winrm
ROOT=Path(__file__).resolve().parents[4]
SNAPSHOT='publication-pre-adcs-20261014'
for vm in ['provider_GOAD-DC03','provider_GOAD-SRV03']:
    r=subprocess.run(['virsh','-c','qemu:///system','snapshot-info',vm,SNAPSHOT],capture_output=True,text=True)
    if r.returncode:raise RuntimeError(f'Required baseline snapshot missing for {vm}')
pw=os.environ['GOAD_COLLECTION_PASSWORD']
script=Path(__file__).with_name('provision_ca.ps1');source=script.read_text()
# Do not write the credential-bearing wrapper or include it in logs.
prefix="$PublicationCredential=New-Object Management.Automation.PSCredential('ESSOS\\vagrant',(ConvertTo-SecureString '"+pw.replace("'","''")+"' -AsPlainText -Force));"
encoded=base64.b64encode(gzip.compress((prefix+source).encode())).decode()
loader="$b=[Convert]::FromBase64String('"+encoded+"');$m=New-Object IO.MemoryStream(,$b);$g=New-Object IO.Compression.GzipStream($m,[IO.Compression.CompressionMode]::Decompress);$r=New-Object IO.StreamReader($g);Invoke-Expression $r.ReadToEnd()"
session=winrm.Session('http://192.168.121.209:5985/wsman',auth=('vagrant',pw),transport='ntlm',operation_timeout_sec=30,read_timeout_sec=40)
out=ROOT/'thesis_research/data/live_adcs_2026-10-14/provisioning';out.mkdir(parents=True,exist_ok=True)
r=session.run_ps(loader)
# PowerShell errors can echo source lines: redact the credential defensively.
for name,body in [('stdout',r.std_out),('stderr',r.std_err)]:
    (out/f'ca_install_{name}.txt').write_text(body.decode(errors='replace').replace(pw,'<redacted>'))
meta={'utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'host':'BRAAVOS','status_code':r.status_code,'baseline_snapshot':SNAPSHOT,'script_sha256':hashlib.sha256(source.encode()).hexdigest(),'ca_name':'CertGraph-Lab-CA'}
(out/'manifest.json').write_text(json.dumps(meta,indent=2)+'\n');print(json.dumps(meta))
if r.status_code:raise SystemExit(r.status_code)
