"""Version the existing public artifact; keep credentials out of logs and payloads."""
from pathlib import Path
from urllib.parse import urlsplit
from datetime import datetime,timezone
import argparse,hashlib,json,stat
import requests
OUT=Path(__file__).resolve().parent
STATE=OUT/'ZENODO_STATUS.json'
def save(d):STATE.write_text(json.dumps(d,indent=2)+'\n')
def safe(url):
 p=urlsplit(url)
 if p.scheme!='https' or p.hostname!='zenodo.org' or p.port not in (None,443) or p.username or p.password:raise ValueError('Unexpected API host')
 return url
def main(publish):
 audit=json.loads((OUT/'PACKAGE_AUDIT.json').read_text())
 assert json.loads((OUT/'VERIFICATION.json').read_text())['status']=='passed'
 artifact=OUT/audit['artifact'];assert hashlib.sha256(artifact.read_bytes()).hexdigest()==audit['sha256']
 token=Path.home()/'.config/certgraph/zenodo_token'
 assert not token.is_symlink() and stat.S_IMODE(token.stat().st_mode)==0o600
 s=requests.Session();s.headers.update(Authorization='Bearer '+token.read_text().strip())
 def api(method,url,**kw):
  r=s.request(method,safe(url),timeout=90,allow_redirects=False,**kw)
  if not r.ok:raise RuntimeError('Zenodo HTTP '+str(r.status_code)+' '+urlsplit(url).path)
  return r.json() if r.content else {}
 if STATE.exists():state=json.loads(STATE.read_text());url=state['deposit_url']
 else:
  base='https://zenodo.org/api/deposit/depositions/24212038'
  old=api('GET',base);assert old['submitted']
  result=api('POST',old['links']['newversion'])
  url=result['links']['latest_draft']
  state={'previous_record_id':'24212038','deposit_url':safe(url),'version':'0.2.0','published':False}
  save(state)
 d=api('GET',url)
 if d.get('submitted'):
  print('Already published; run public verification.');return
 assert str(d['id'])!='24212038'
 state.update(record_id=str(d['id']),draft_url='https://zenodo.org/uploads/'+str(d['id']));save(state)
 metadata=json.loads((OUT/'ZENODO_METADATA.json').read_text())
 d=api('PUT',url,json=metadata)
 for f in d.get('files',[]):
  name=f.get('filename') or f.get('key')
  if name==audit['artifact']:continue
  if name!='CertGraph_Artifact_v0.1.0.zip':raise ValueError('Unexpected draft attachment; stopping')
  api('DELETE',f['links']['self'])
 d=api('GET',url)
 if not any((f.get('filename') or f.get('key'))==audit['artifact'] for f in d.get('files',[])):
  with artifact.open('rb') as stream:api('PUT',d['links']['bucket'].rstrip('/')+'/'+audit['artifact'],data=stream,headers={'Content-Type':'application/octet-stream'})
 d=api('GET',url);assert len(d['files'])==1
 f=d['files'][0];assert (f.get('filename') or f.get('key'))==audit['artifact']
 assert f.get('filesize',f.get('size'))==audit['size_bytes']
 assert f['checksum'] in (audit['md5'],'md5:'+audit['md5'])
 m=d['metadata'];assert m['version']=='0.2.0' and m['title']==metadata['metadata']['title']
 assert len(m['creators'])==3 and 'GPL-3.0-only' in m['description']
 license=m.get('license');license=license.get('id') if isinstance(license,dict) else license
 assert license in ('gpl-3.0','gpl-3.0-only')
 state.update(files_uploaded=True,uploaded_checksum=f['checksum'],artifact_sha256=audit['sha256'],reserved_doi=m.get('prereserve_doi',{}).get('doi'),status='uploaded_verified');save(state)
 print('New-version draft uploaded; checksum and metadata verified:',state['draft_url'],flush=True)
 if publish:
  result=api('POST',d['links']['publish'])
  state.update(published=bool(result.get('submitted')),status='publication_requested',published_utc=datetime.now(timezone.utc).isoformat());save(state)
  print('Publication requested for record',state['record_id'],flush=True)
if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');main(p.parse_args().publish)
