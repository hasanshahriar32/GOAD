"""Update only manuscript artifact availability from verified release status."""
from pathlib import Path
import json,re

MAN=Path(__file__).resolve().parents[1]
RELEASE=MAN/'release/2026-11-14'

def main():
 status=json.loads((RELEASE/'ZENODO_STATUS.json').read_text())
 doi=status['reserved_doi']
 if not re.fullmatch(r'10\.5281/zenodo\.\d+',doi):raise ValueError('Unexpected archive DOI')
 subject=('The versioned CertGraph research artifact contains frozen synthetic protocols, labels, predictions, '
          'source snapshots, checkpoints, and offline verification code, together with selected public '
          'certificate, CA and KDC evidence for the 72 primary laboratory cases. ')
 if status.get('published'):
  location='It is archived at \\url{https://doi.org/'+doi+'}. '
 else:
  location='A Zenodo draft has reserved DOI \\texttt{'+doi+'}; public archive publication is pending. '
 scope=('The public-evidence verifier checks 66 successful uses, including 13 administrative uses, '
        'and six certificate-bound rejections without private keys or access to the original capture trees. '
        'Eighteen CA exports are explicitly identified as later read-only supplements. '
        'Private keys, passwords, reusable tickets, VM disks and complete command transcripts are excluded. '
        'The release README and hash manifests define the included fields and reproduction boundaries.')
 paragraph='\\noindent '+subject+location+scope+'\n'
 p=MAN/'sections/07_related_work_and_conclusion.tex';text=p.read_text()
 pattern=r'(\\section\*\{Data Availability\}\n).*?(?=\n\\section\*\{Funding\})'
 text,count=re.subn(pattern,lambda m:m[1]+paragraph,text,flags=re.S)
 if count!=1:raise ValueError('Data availability section not unique')
 p.write_text(text)
 # Keep the accompanying declaration consistent; no authorship approval is inferred.
 p=MAN/'submission_files/declarations.txt';text=p.read_text()
 a=text.index('Data availability:');b=text.index('Originality, exclusive submission and author approval:')
 wording=('Published archive: https://doi.org/'+doi if status.get('published') else 'Reserved DOI (unpublished draft): '+doi)
 data=('Data availability:\n'+wording+'\nThe release contains the frozen synthetic studies and selected public '
       'certificate/CA/KDC evidence for 72 cases. Independent public-evidence verification checks 66 successful '
       'uses including 13 administrative uses and six rejections. Eighteen CA exports are later read-only '
       'supplements. Private keys, passwords, ticket caches, VM images and complete command transcripts '
       'are excluded. See the artifact README, selected-field export and manifests for reproduction limits.\n\n'
       'Funding:\nThis research received no specific grant from any funding agency.\n\n')
 p.write_text(text[:a]+data+text[b:])
 print('Artifact availability synchronized:', 'published' if status.get('published') else 'reserved draft')

if __name__=='__main__':main()
