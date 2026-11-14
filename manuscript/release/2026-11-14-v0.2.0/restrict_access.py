"""Restrict both artifact versions and verify anonymous file access is denied."""
from pathlib import Path
from datetime import datetime,timezone
from urllib.parse import urlsplit
import requests,json
OUT=Path(__file__).resolve().parent
s=requests.Session();s.headers['Authorization']='Bearer '+(Path.home()/'.config/certgraph/zenodo_token').read_text().strip()
def api(method,url,**kw):
 p=urlsplit(url);assert p.scheme=='https' and p.hostname=='zenodo.org' and not p.username
 r=s.request(method,url,timeout=40,allow_redirects=False,**kw)
 if not r.ok:raise RuntimeError('Zenodo '+method+' HTTP '+str(r.status_code)+' '+p.path+' '+r.text[:500])
 return r.json() if r.content else {}
results=[]
for rid in ['24221331','24212038']:
 url='https://zenodo.org/api/deposit/depositions/'+rid
 d=api('GET',url)
 if d['metadata'].get('access_right') not in ('closed','restricted'):
  if d.get('submitted'):d=api('POST',d['links']['edit'])
  metadata=d['metadata'];metadata['access_right']='closed'
  metadata.pop('embargo_date',None);metadata.pop('access_conditions',None)
  d=api('PUT',url,json={'metadata':metadata})
  assert d['metadata']['access_right'] in ('closed','restricted')
  d=api('POST',d['links']['publish'])
 if d['metadata'].get('access_right') in ('closed','restricted'):
  # The legacy response retains submitted=true while a published record is edited.
  public_check=requests.get('https://zenodo.org/api/records/'+rid,timeout=30)
  public_check.raise_for_status()
  if public_check.json()['metadata'].get('access_right') not in ('closed','restricted'):
   d=api('POST',d['links']['publish'])
 d=api('GET',url)
 assert d['metadata']['access_right'] in ('closed','restricted')
 public=requests.get('https://zenodo.org/api/records/'+rid,timeout=30);public.raise_for_status()
 record=public.json();access=record['metadata'].get('access_right')
 assert access in ('closed','restricted'),access
 filename='CertGraph_Artifact_v'+('0.2.0' if rid=='24221331' else '0.1.0')+'.zip'
 download=requests.get('https://zenodo.org/api/records/'+rid+'/files/'+filename+'/content',headers={'Range':'bytes=0-0'},stream=True,timeout=30)
 status=download.status_code;download.close()
 assert status in (401,403,404),status
 item={'record_id':rid,'access_right':access,'anonymous_file_http_status':status,'file_access_denied':True,'metadata_remains_public':True}
 results.append(item)
 # Append a current access marker without deleting the historical verification.
 directory=OUT if rid=='24221331' else OUT.parent/'2026-11-14'
 path=directory/'ZENODO_STATUS.json'
 state=json.loads(path.read_text());state.update(access_right=access,status='published_files_restricted',files_public=False,access_changed_utc=datetime.now(timezone.utc).isoformat())
 path.write_text(json.dumps(state,indent=2)+'\n')
 (OUT/'ACCESS_RESTRICTION.json').write_text(json.dumps({'verified_utc':datetime.now(timezone.utc).isoformat(),'versions':results},indent=2)+'\n')
 print(json.dumps(item),flush=True)
