"""Verify the published version without credentials."""
from pathlib import Path
from datetime import datetime,timezone
import requests,json,hashlib
from concurrent.futures import ThreadPoolExecutor
OUT=Path(__file__).resolve().parent
state=json.loads((OUT/'ZENODO_STATUS.json').read_text())
audit=json.loads((OUT/'PACKAGE_AUDIT.json').read_text())
s=requests.Session()
url='https://zenodo.org/api/records/'+state['record_id']
r=s.get(url,timeout=60);r.raise_for_status();record=r.json()
m=record['metadata'];assert m['version']=='0.2.0'
assert 'GPL-3.0-only' in m['description'] and len(m['creators'])==3
f=record['files'];assert len(f)==1 and f[0]['key']==audit['artifact']
assert f[0]['checksum']=='md5:'+audit['md5'] and f[0]['size']==audit['size_bytes']
download='https://zenodo.org/records/'+state['record_id']+'/files/'+audit['artifact']+'?download=1'
# Anonymous ranged downloads can resume after a dropped connection.
parts=OUT/'.download_parts';parts.mkdir(exist_ok=True)
size=audit['size_bytes'];chunk=512*1024
content_url=url+'/files/'+audit['artifact']+'/content'
def fetch(start):
 end=min(size,start+chunk)-1;target=parts/str(start)
 if target.exists() and target.stat().st_size==end-start+1:return target.read_bytes()
 for attempt in range(3):
  try:
   response=requests.get(content_url,headers={'Range':f'bytes={start}-{end}'},timeout=45)
   response.raise_for_status()
   assert response.status_code==206 and response.headers['Content-Range']==f'bytes {start}-{end}/{size}'
   assert len(response.content)==end-start+1
   target.write_bytes(response.content)
   return response.content
  except (requests.RequestException,AssertionError):
   if attempt==2:raise
with ThreadPoolExecutor(max_workers=4) as pool:
 data=b''.join(pool.map(fetch,range(0,size,chunk)))
assert len(data)==size and hashlib.sha256(data).hexdigest()==audit['sha256']
report={'status':'passed','verified_utc':datetime.now(timezone.utc).isoformat(),'doi':record['doi'],'public_record_url':'https://zenodo.org/records/'+state['record_id'],'version':m['version'],'size_bytes':len(data),'sha256':audit['sha256'],'anonymous_download_verified':True}
(OUT/'PUBLIC_ARCHIVE_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
(OUT/'PUBLIC_ZENODO_METADATA.json').write_text(json.dumps(record,indent=2)+'\n')
state.update(published=True,status='published_verified',doi=record['doi'],public_record_url=report['public_record_url'],public_verification=report)
(OUT/'ZENODO_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
(OUT/'RELEASE_COMPLETION.md').write_text('# CertGraph 0.2.0 release\n\nPublished: '+report['public_record_url']+'\n\nDOI: https://doi.org/'+record['doi']+'\n\nPublic download matches the verified local package by SHA-256: `'+audit['sha256']+'`. The v0.1.0 record is preserved. The manuscript remains anonymous; its withheld archive link was not restored. Public archive authorship continues the existing record.\n')
print(json.dumps(report,indent=2))
