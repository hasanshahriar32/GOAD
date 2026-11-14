"""Independently verify the public archive before marking it published locally."""
from pathlib import Path
import hashlib,json
from datetime import datetime,timezone
import requests

RELEASE=Path(__file__).resolve().parents[1]/'release/2026-11-14'

def main():
 status=json.loads((RELEASE/'ZENODO_STATUS.json').read_text())
 audit=json.loads((RELEASE/'PACKAGE_AUDIT.json').read_text())
 record_id=status['record_id']
 if not record_id.isdigit():raise ValueError('Invalid record identifier')
 session=requests.Session();session.headers['User-Agent']='CertGraphArtifactVerifier/0.1.0'
 response=session.get('https://zenodo.org/api/records/'+record_id,timeout=30)
 response.raise_for_status();record=response.json();metadata=record['metadata']
 if record.get('doi')!=status['reserved_doi']:raise ValueError('Public DOI differs from the reserved draft')
 if 'CertGraph' not in metadata.get('title','') or metadata.get('version')!='0.1.0':raise ValueError('Wrong artifact metadata')
 creators=metadata.get('creators',[])
 if len(creators)!=3:raise ValueError('Expected three artifact creators')
 license=metadata.get('license',{})
 license_id=license if isinstance(license,str) else license.get('id')
 if not license_id:
  rights=metadata.get('rights',[])
  license_id=rights[0].get('id') if len(rights)==1 else None
 title=None;license_url=None
 terms=metadata.get('description','')+' '+metadata.get('notes','')
 legacy_only=(license_id=='gpl-3.0' and 'GPL-3.0-only' in terms and 'https://spdx.org/licenses/GPL-3.0-only.html' in terms)
 if legacy_only:
  title='GNU General Public License v3.0 only';license_url='https://spdx.org/licenses/GPL-3.0-only.html'
 if not legacy_only and (not license_id or license_id.lower()!='gpl-3.0-only'):
  candidates=metadata.get('rights') or [metadata.get('license',{})]
  if len(candidates)!=1:raise ValueError('Public license is ambiguous')
  item=candidates[0];title=item.get('title','')
  if isinstance(title,dict):title=title.get('en','')
  license_url=item.get('link') or item.get('url')
  if title.strip().lower()!='gnu general public license v3.0 only' or license_url!='https://spdx.org/licenses/GPL-3.0-only.html':raise ValueError('Public license does not match the retained GPL-v3-only terms')
 files=record.get('files',[])
 if isinstance(files,dict):files=list(files.get('entries',{}).values())
 match=[f for f in files if f.get('key')==audit['artifact'] or f.get('filename')==audit['artifact']]
 if len(match)!=1:raise ValueError('Artifact file not uniquely present')
 f=match[0]
 if f.get('size')!=audit['size_bytes']:raise ValueError('Public artifact byte count differs')
 checksum=f.get('checksum','')
 if checksum and checksum not in ('md5:'+audit['md5'],'sha256:'+audit['sha256']):raise ValueError('Archive checksum differs')
 url='https://zenodo.org/records/'+record_id+'/files/'+audit['artifact']+'?download=1'
 download=session.get(url,timeout=90);download.raise_for_status()
 actual=hashlib.sha256(download.content).hexdigest()
 if actual!=audit['sha256'] or len(download.content)!=audit['size_bytes']:raise ValueError('Downloaded archive differs from tested release')
 report={'verified_utc':datetime.now(timezone.utc).isoformat(),'public_record_url':'https://zenodo.org/records/'+record_id,
         'doi':record['doi'],'file_url':url,'size_bytes':len(download.content),'sha256':actual,
         'archive_checksum':checksum,'license_id':license_id,'license_title':title,'license_url':license_url,'creator_count':len(creators),
         'version':metadata['version'],'anonymous_download_verified':True,'status':'passed'}
 (RELEASE/'PUBLIC_ARCHIVE_VERIFICATION.json').write_text(json.dumps(report,indent=2)+'\n')
 (RELEASE/'PUBLIC_ZENODO_METADATA.json').write_text(json.dumps(record,indent=2)+'\n')
 status.update({'published':True,'files_uploaded':True,'status':'published_verified',
                'public_record_url':report['public_record_url'],'file_url':url,'license':license_id,
                'published_verification':report})
 (RELEASE/'ZENODO_STATUS.json').write_text(json.dumps(status,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
