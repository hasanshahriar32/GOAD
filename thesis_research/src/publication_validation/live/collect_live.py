"""Read-only WinRM collector for a user-owned GOAD domain controller.
Password comes from an environment variable, never a command-line argument.
"""
import argparse,datetime,hashlib,json,os,base64,gzip
from pathlib import Path
import winrm

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--host',required=True);ap.add_argument('--user',required=True)
    ap.add_argument('--output',type=Path,required=True);ap.add_argument('--https',action='store_true')
    args=ap.parse_args();password=os.environ['GOAD_COLLECTION_PASSWORD']
    scheme,port=('https',5986) if args.https else ('http',5985)
    script=Path(__file__).with_name('collect_adcs.ps1');source=script.read_text()
    session=winrm.Session(f'{scheme}://{args.host}:{port}/wsman',auth=(args.user,password),transport='ntlm',server_cert_validation='ignore',operation_timeout_sec=30,read_timeout_sec=40)
    # WinRM's encoded command has a Windows command-line length limit.
    compressed=base64.b64encode(gzip.compress(source.encode('utf-8'))).decode('ascii')
    loader="$b=[Convert]::FromBase64String('"+compressed+"');$m=New-Object IO.MemoryStream(,$b);$g=New-Object IO.Compression.GzipStream($m,[IO.Compression.CompressionMode]::Decompress);$r=New-Object IO.StreamReader($g);Invoke-Expression $r.ReadToEnd()"
    start=datetime.datetime.now(datetime.timezone.utc).isoformat();r=session.run_ps(loader)
    args.output.mkdir(parents=True,exist_ok=True)
    (args.output/'collection_stderr.txt').write_bytes(r.std_err)
    if r.status_code:raise RuntimeError(f'Collection failed with status {r.status_code}; see collection_stderr.txt')
    data=json.loads(r.std_out.decode('utf-8-sig'));payload=r.std_out
    (args.output/'adcs_snapshot.json').write_bytes(payload)
    metadata={'host':args.host,'principal':args.user,'started_utc':start,'snapshot_sha256':hashlib.sha256(payload).hexdigest(),
        'script_sha256':hashlib.sha256(source.encode()).hexdigest(),'status':'collected','read_only':True}
    (args.output/'collection_manifest.json').write_text(json.dumps(metadata,indent=2)+'\n')
    print(json.dumps({k:len(data[k]) for k in ['templates','policies','certificate_authorities','groups','users']}))
if __name__=='__main__':main()
