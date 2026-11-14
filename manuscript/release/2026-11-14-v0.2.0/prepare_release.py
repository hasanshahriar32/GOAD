"""Package existing verified releases without rewriting their frozen manifests."""
from pathlib import Path
import hashlib,json,zipfile
ROOT=Path(__file__).resolve().parents[3]
OUT=Path(__file__).resolve().parent
inputs={
 'original/CertGraph_Artifact_v0.1.0.zip':ROOT/'manuscript/release/2026-11-14/CertGraph_Artifact_v0.1.0.zip',
 'supplements/CertGraph_Revision_Analyses.zip':ROOT/'manuscript/submission_files/CertGraph_Revision_Analyses.zip',
 'supplements/CertGraph_Extended_Validation.zip':ROOT/'manuscript/submission_files/CertGraph_Extended_Validation.zip',
 'manuscript/CertGraph_IEEE_Professor_Revision.zip':ROOT/'manuscript/submission_files/CertGraph_IEEE_Professor_Revision.zip',
 'manuscript/main.pdf':ROOT/'manuscript/main.pdf',
 'LICENSE':ROOT/'LICENSE',
}
readme='''# CertGraph research artifact, version 0.2.0

CertGraph: Revisable Certificate Lineage for Active Directory Certificate Services under Incomplete Evidence

This version collects the original v0.1.0 research evidence, subsequent revision analyses and extended validation, and the current anonymous manuscript PDF and LaTeX sources. Nested archives preserve each study's original paths, manifests and verification instructions; extract each into a separate directory. The public archive retains the existing record's authorship. The manuscript itself uses anonymous author placeholders for review.

## Changes since 0.1.0

- Ambiguity/illustrative loss analysis and retained-history benchmark.
- Independent generated evidence-value study: 432 histories and 4,320 saved predictions.
- Incremental identity replay: 35,055 reference/guarded-SQL comparisons.
- Stronger remediation baselines on 60 saved small instances.
- Revised manuscript framing, organization and figures, including explicit negative results.

No new Windows certificate cases or investigator participants are claimed. The existing public laboratory evidence still covers 72 cases. SQL equivalence and stronger competing heuristics constrain novelty claims. Generated workloads and shared-host timings do not establish enterprise effectiveness or journal acceptance.

## Verification

The original archive README supplies six verification commands and dependency versions. Each supplement includes its own README and hash manifest. From a fresh extraction of the extended-validation ZIP run:

    python manuscript/scripts/verify_evidence_value.py
    python manuscript/scripts/verify_streaming_identity.py

The manuscript ZIP contains editable LaTeX and vector figure assets; the PDF is supplied separately. No DOCX is included because the existing Word export does not match the current manuscript.

Historical reports and manifests retain their original version-specific wording and source hashes. Statements that Zenodo was unchanged refer to the time those analyses were created. This outer release is the subsequent collection of those artifacts. Unkeyed file hashes establish integrity, not source authenticity.

The software retains the existing GNU GPL v3 license, with the public record's explicit GPL-3.0-only terms. Dependencies are not bundled. Private keys, authentication tokens, guest disks and complete credential-bearing capture trees are excluded.
'''
payload={name:p.read_bytes() for name,p in inputs.items()}
for name,data in payload.items():
 if name.endswith('.zip'):
  with zipfile.ZipFile(inputs[name]) as z:
   assert z.testzip() is None
   assert not any(n.startswith('/') or '..' in Path(n).parts for n in z.namelist())
payload['README.md']=readme.encode()
hashes={n:hashlib.sha256(b).hexdigest() for n,b in payload.items()}
payload['SHA256SUMS.json']=(json.dumps(hashes,indent=2)+'\n').encode()
archive=OUT/'CertGraph_Artifact_v0.2.0.zip'
with zipfile.ZipFile(archive,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
 for n,b in sorted(payload.items()):z.writestr(n,b)
audit={'version':'0.2.0','artifact':archive.name,'sha256':hashlib.sha256(archive.read_bytes()).hexdigest(),'md5':hashlib.md5(archive.read_bytes()).hexdigest(),'size_bytes':archive.stat().st_size,'payload_sha256':hashes,'published':False}
(OUT/'PACKAGE_AUDIT.json').write_text(json.dumps(audit,indent=2)+'\n')
(OUT/'README.md').write_text(readme)
old=json.loads((ROOT/'manuscript/release/2026-11-14/PUBLIC_ZENODO_METADATA.json').read_text())['metadata']
metadata={k:old[k] for k in ['creators','access_right']}
metadata.update(title='CertGraph research artifact: Revisable Certificate Lineage for Active Directory Certificate Services under Incomplete Evidence',upload_type='software',version='0.2.0',license='gpl-3.0',description='<p>Version 0.2.0 collects the original 72-case public laboratory artifact, later generated evidence-value and incremental-replay studies, stronger remediation baselines, and the revised anonymous manuscript and editable LaTeX sources. No additional live cases or investigator participants are claimed. See the package README for reproduction and interpretation boundaries.</p><p>License: GNU General Public License v3.0 only (SPDX GPL-3.0-only), https://spdx.org/licenses/GPL-3.0-only.html . No CC-BY relicensing is granted. This research artifact is not an assertion of journal publication.</p>')
for c in metadata['creators']:
 if c.get('affiliation') is None:c.pop('affiliation',None)
(OUT/'ZENODO_METADATA.json').write_text(json.dumps({'metadata':metadata},indent=2)+'\n')
print(json.dumps({k:v for k,v in audit.items() if k!='payload_sha256'},indent=2))
if __name__=='__main__':pass
