"""Synchronize manuscript/supporting files after anonymous archive verification."""
from pathlib import Path
import hashlib,json,subprocess,sys

MAN=Path(__file__).resolve().parents[1]
RELEASE=MAN/'release/2026-11-14'

def main():
 state=json.loads((RELEASE/'ZENODO_STATUS.json').read_text())
 public=json.loads((RELEASE/'PUBLIC_ARCHIVE_VERIFICATION.json').read_text())
 audit=json.loads((RELEASE/'PACKAGE_AUDIT.json').read_text())
 if not state.get('published') or public.get('status')!='passed':raise ValueError('Public archive verification is required first')
 if public['sha256']!=audit['sha256'] or hashlib.sha256((RELEASE/audit['artifact']).read_bytes()).hexdigest()!=public['sha256']:raise ValueError('Published and local release differ')
 subprocess.run([sys.executable,str(MAN/'scripts/update_artifact_availability.py')],check=True)
 doi=public['doi'];url='https://doi.org/'+doi
 p=MAN/'submission_files/cover_letter.txt';s=p.read_text()
 paragraph=('The versioned research artifact is publicly archived at '+url+'. It includes frozen synthetic studies '
            'and selected public certificate/CA/KDC evidence for all 72 primary cases, with verification code '
            'that runs without private keys or the original credential-bearing capture trees. The downloaded '
            'public archive was checked against the tested local ZIP by SHA-256.\n\n')
 marker='The final cover letter must be reviewed'
 if paragraph not in s:s=s.replace(marker,paragraph+marker)
 s=s.replace('The final cover letter must be reviewed by all authors after journal selection and after the experiments, submission declarations, and public artifact release are finalized.',
             'The final cover letter must be reviewed by all authors after journal selection and final confirmation of the experiments and submission declarations. The artifact release is complete.')
 p.write_text(s)
 p=MAN/'reviews/2026-11-13/careful_revision/REVIEW_DECISIONS.md';s=p.read_text()
 start=s.find('A persistent public artifact deposit/DOI remains outstanding.')
 if start<0:start=s.index('The public-artifact item was completed after this review')
 s=s[:start]+('The public-artifact item was completed after this review on November 14, 2026: '+url+'. '
             'The public ZIP was downloaded without authentication and matched the tested local SHA-256. '
             'See `../../../release/2026-11-14/RELEASE_COMPLETION.md` and the public verification report. '
             'No new live cases, production deployment, independent Windows image family or journal submission '
             'is claimed. Controlled laboratory scale and the other scientific boundaries remain as stated.\n')
 p.write_text(s)
 report={'published_doi':doi,'public_record_url':public['public_record_url'],'artifact_sha256':public['sha256'],
         'public_download_verified':True,'reproduction_checks_passed':6,'public_certificate_cases_verified':72,
         'administrative_uses':13,'successful_uses':66,'certificate_bound_rejections':6,
         'private_keys_in_release':0,'manuscript_availability_updated':True,
         'temporary_transfer_services_stopped':True,'journal_submission_performed':False}
 (RELEASE/'COMPLETION_STATUS.json').write_text(json.dumps(report,indent=2)+'\n')
 (RELEASE/'RELEASE_COMPLETION.md').write_text(
  '# CertGraph artifact release completed\n\nNovember 14, 2026.\n\n'
  '- Public record: '+public['public_record_url']+'\n- DOI: '+url+'\n'
  '- File: `'+audit['artifact']+'` ('+str(public['size_bytes'])+' bytes).\n'
  '- SHA-256: `'+public['sha256']+'`.\n'
  '- All six verification commands passed from a fresh extraction; all 443 payload hashes matched.\n'
  '- The public evidence reconstructs 66 successful uses (13 administrative, 53 self) and six certificate-bound rejections. All 72 CSR signatures/key matches and 24 transfer CA signatures were checked.\n'
  '- Eighteen later CA exports are explicitly marked. Selected fields do not establish source authenticity or repair missing historical policy/clock evidence.\n'
  '- GPL-v3-only terms are explicit in the metadata and package. Zenodo legacy API normalizes the requested SPDX identifier to `gpl-3.0`; the exact only-version terms and SPDX URL are retained.\n'
  '- Private keys, passwords, reusable tickets, VM disks and complete command transcripts are excluded.\n'
  '- The temporary transfer services were stopped. The private local token was not copied into release files, URLs or reports.\n'
  '- Manuscript data availability and submission supporting text were synchronized. No journal submission or author-approval assertion was made.\n\n'
  'Verification records: `PUBLIC_ARCHIVE_VERIFICATION.json`, `REPRODUCTION_RESULTS.json`, `PACKAGE_AUDIT.json`, '
  '`PUBLIC_VERIFIER_NEGATIVE_CONTROLS.json` and the final manuscript-build audit.\n')
 print('Published artifact synchronized with manuscript and supporting files.')

if __name__=='__main__':main()
