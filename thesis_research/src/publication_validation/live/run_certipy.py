"""Versioned read-only Certipy find run, with redacted command metadata."""
import argparse,datetime,hashlib,json,os,subprocess,time
from pathlib import Path

def main():
    p=argparse.ArgumentParser();p.add_argument('--binary',required=True);p.add_argument('--dc',required=True)
    p.add_argument('--user',required=True);p.add_argument('--output',type=Path,required=True);p.add_argument('--dc-only',action='store_true')
    a=p.parse_args();a.output.mkdir(parents=True,exist_ok=True)
    command=[a.binary,'find','-u',a.user,'-p',os.environ['GOAD_COLLECTION_PASSWORD'],'-dc-ip',a.dc,'-ns',a.dc,
             '-ldap-scheme','ldap','-json','-text','-oids','-output','certipy','-timeout','15']
    if a.dc_only:command.append('-dc-only')
    version=subprocess.run([a.binary,'-v'],capture_output=True,text=True)
    start=time.perf_counter();r=subprocess.run(command,capture_output=True,timeout=240,cwd=a.output.resolve())
    duration=time.perf_counter()-start
    (a.output/'certipy_stdout.txt').write_bytes(r.stdout);(a.output/'certipy_stderr.txt').write_bytes(r.stderr)
    redacted=command.copy();redacted[redacted.index('-p')+1]='<environment>'
    meta={'collected_utc':datetime.datetime.now(datetime.timezone.utc).isoformat(),'version':(version.stdout+version.stderr).strip(),
          'command':redacted,'returncode':r.returncode,'elapsed_seconds':duration,'scope':'Read-only actual Certipy enumeration; no exploitation or ground-truth claim.',
          'outputs':{f.name:hashlib.sha256(f.read_bytes()).hexdigest() for f in a.output.iterdir() if f.is_file()}}
    (a.output/'tool_manifest.json').write_text(json.dumps(meta,indent=2)+'\n')
    print(json.dumps({'returncode':r.returncode,'elapsed_seconds':duration,'files':list(meta['outputs'])}))
    if r.returncode:raise SystemExit(r.returncode)
if __name__=='__main__':main()
