"""Upload the verified ZIP to the existing draft using a private local token.

The token is sent only as an Authorization header to zenodo.org. It is never
printed, saved in the workspace, added to a URL, or included in reports.
"""
import argparse
import hashlib,json,os,stat
from pathlib import Path
from urllib.parse import urlsplit
import requests

RELEASE=Path(__file__).resolve().parents[1]/'release/2026-11-14'
TOKEN_FILE=Path.home()/'.config/certgraph/zenodo_token'

def digest(p):return hashlib.sha256(p.read_bytes()).hexdigest()
def allowed_url(url):
 p=urlsplit(url)
 if p.scheme!='https' or p.hostname!='zenodo.org' or p.port not in (None,443) or p.username or p.password:raise ValueError('Refusing to send authorization to an unexpected host')
 return url
def api(session,method,url,**kwargs):
 response=session.request(method,allowed_url(url),timeout=90,allow_redirects=False,**kwargs)
 if not response.ok:raise RuntimeError('Zenodo '+method+' failed: HTTP '+str(response.status_code)+' at '+urlsplit(url).path)
 return response.json() if response.content else {}
def license_ok(metadata):
 rights=metadata.get('rights')
 if rights is None:rights=[metadata.get('license',{})]
 if len(rights)!=1:return False
 item=rights[0]
 if isinstance(item,str):
  identifier=item.lower()
  if identifier=='gpl-3.0-only':return True
  # The legacy Zenodo API normalizes our explicit gpl-3.0-only PUT to
  # gpl-3.0. Accept that alias only with the explicit only-version terms
  # and canonical SPDX URL retained in the public metadata.
  terms=metadata.get('description','')+' '+metadata.get('notes','')
  return identifier=='gpl-3.0' and 'GPL-3.0-only' in terms and 'https://spdx.org/licenses/GPL-3.0-only.html' in terms
 if str(item.get('id','')).lower()=='gpl-3.0-only':return True
 title=item.get('title','')
 if isinstance(title,dict):title=title.get('en','')
 link=item.get('link') or item.get('url')
 return title.strip().lower()=='gnu general public license v3.0 only' and link=='https://spdx.org/licenses/GPL-3.0-only.html'

def main(publish=False):
 state=json.loads((RELEASE/'ZENODO_STATUS.json').read_text())
 audit=json.loads((RELEASE/'PACKAGE_AUDIT.json').read_text())
 checks=json.loads((RELEASE/'REPRODUCTION_RESULTS.json').read_text())
 artifact=RELEASE/audit['artifact']
 if not checks['all_passed'] or digest(artifact)!=checks['artifact_sha256'] or digest(artifact)!=audit['sha256']:raise ValueError('Release differs from the tested ZIP')
 if TOKEN_FILE.is_symlink() or not TOKEN_FILE.is_file():raise RuntimeError('Save the token in the private local file ~/.config/certgraph/zenodo_token first')
 info=TOKEN_FILE.stat()
 if info.st_uid!=os.getuid() or stat.S_IMODE(info.st_mode)!=0o600:raise RuntimeError('Token file must be owned by the current user with permissions 600')
 token=TOKEN_FILE.read_text().strip()
 if not token or '\n' in token or '\r' in token:raise RuntimeError('Token file must contain one token only')
 session=requests.Session();session.headers.update({'Authorization':'Bearer '+token,'User-Agent':'CertGraphArtifactDeposit/0.1.0'})
 record_id=state['record_id']
 if not record_id.isdigit():raise ValueError('Invalid draft ID')
 legacy='https://zenodo.org/api/deposit/depositions/'+record_id
 deposit=api(session,'GET',legacy)
 if deposit.get('submitted'):
  print('Record is already submitted; run anonymous public verification.');return
 metadata=deposit.get('metadata',{})
 if 'CertGraph' not in metadata.get('title','') or metadata.get('version')!='0.1.0':raise ValueError('Unexpected deposit title/version')
 if len(metadata.get('creators',[]))!=3:raise ValueError('Unexpected artifact creators')
 expected_doi=state['reserved_doi']
 actual_doi=metadata.get('prereserve_doi',{}).get('doi') or deposit.get('doi')
 if actual_doi and actual_doi!=expected_doi:raise ValueError('Draft DOI differs')
 files=deposit.get('files',[])
 names={f.get('filename') or f.get('key') or f.get('name') for f in files}
 if names-{audit['artifact']}:raise ValueError('Unexpected additional files in draft; no files were removed')
 if audit['artifact'] not in names:
  bucket=allowed_url(deposit['links']['bucket'])
  with artifact.open('rb') as stream:api(session,'PUT',bucket.rstrip('/')+'/'+audit['artifact'],data=stream,headers={'Content-Type':'application/octet-stream'})
 deposit=api(session,'GET',legacy)
 matches=[f for f in deposit.get('files',[]) if (f.get('filename') or f.get('key') or f.get('name'))==audit['artifact']]
 if len(matches)!=1:raise ValueError('Uploaded file not uniquely present')
 file=matches[0];size=file.get('filesize',file.get('size'))
 if int(size)!=audit['size_bytes']:raise ValueError('Uploaded byte count differs')
 checksum=file.get('checksum','')
 if checksum not in (audit['md5'],'md5:'+audit['md5'],'sha256:'+audit['sha256']):raise ValueError('Uploaded checksum differs')
 # The modern draft exposes custom-license details that the legacy conversion
 # may omit. Read it without changing any unrelated metadata.
 metadata=deposit['metadata'];license_verified=license_ok(metadata)
 if not license_verified:
  modern=api(session,'GET','https://zenodo.org/api/records/'+record_id+'/draft')
  license_verified=license_ok(modern.get('metadata',{}))
 report={'record_id':record_id,'draft_url':'https://zenodo.org/uploads/'+record_id,
         'reserved_doi':expected_doi,'file':audit['artifact'],'size_bytes':audit['size_bytes'],
         'checksum':checksum,'local_sha256':audit['sha256'],'license_verified':license_verified,
         'published_by_this_call':False,'token_logged':False}
 (RELEASE/'UPLOAD_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
 state.update({'files_uploaded':True,'status':'uploaded_draft','license_verified':license_verified})
 (RELEASE/'ZENODO_STATUS.json').write_text(json.dumps(state,indent=2)+'\n')
 if publish:
  if not license_verified:raise ValueError('ZIP uploaded, but license requires correction before publication')
  api(session,'POST',deposit['links']['publish'],json={})
  report['published_by_this_call']=True
  (RELEASE/'UPLOAD_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
  print('Publication requested successfully. Run anonymous archive verification before changing manuscript availability.')
 else:print('ZIP uploaded and checksum verified. Draft retained.')

if __name__=='__main__':
 p=argparse.ArgumentParser();p.add_argument('--publish',action='store_true');main(p.parse_args().publish)
