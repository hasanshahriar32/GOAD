"""Build the current CertGraph research artifact from an explicit allowlist.

Does not upload, publish, create a token, or read a browser profile.
"""
from pathlib import Path
import hashlib,importlib.metadata,json,re,zipfile

ROOT=Path(__file__).resolve().parents[2]
MAN=ROOT/'manuscript'
RELEASE=MAN/'release/2026-11-14'
BASE=ROOT/'thesis_research/results/lineage_constraints/2026-11-10'
TITLE='CertGraph research artifact: Cryptographic Invariant Provenance and Multiplicative Bilinear Gating for Active Directory Certificate Services Escalation Interdiction'
README='''# CertGraph research artifact, version 0.1.0

This package accompanies the CertGraph manuscript. It includes frozen synthetic
inputs, labels, predictions, checkpoints, executed-source snapshots, verification
modules, derived manuscript tables and selected public laboratory evidence.
It retains the repository's GNU GPL v3 license; third-party Python libraries are
not bundled. The Zenodo record description must preserve that software license,
rather than silently replacing it with the upload form's CC-BY default.

## Evidence inventory

* Confirmation: 5,400 histories, 27,000 saved method predictions.
* Component study: 2,700 identity and 1,800 temporal histories.
* Identity-only SQL: 5,423 prefixes, 16,269 saved predictions.
* Literal graph learning: 5,100 labeled inputs, 10,800 held-out predictions.
* Interdiction: 120 graph/budget cases, 60 exhaustive small cases.
* Equal-query path projection, feature-channel diagnostic and falsification controls.
* `public_live/`: 72 public certificates, signed requests, selected CA rows,
  CA/KDC/directory event fields and recorded template-policy projections.

The public live verifier reconstructs 66 successful uses (53 self, 13 admin)
and six certificate-bound rejections. It verifies all 72 signed requests and
certificate/request key matches, and 24 transfer-cohort leaf signatures under
the separately captured public CA certificate. Eighteen CA exports explicitly
come from a later read-only supplement. Public certificate bytes retain the
fictional/isolated lab identities necessary to check issuer and principal links.

Private keys, passwords, PFX files, ticket caches, complete live-capture trees,
process command lines, guest-management code and VM disks are excluded. The
public evidence is a selected-field export, not an unmodified Windows log file.
Source hashes track derivation; unkeyed hashes do not authenticate a compromised
collector. Missing historical policy and failed clock assumptions remain outside
the certificate-use verification guarantee. No additional live cases are claimed.

## Reproduce the verification

Run from this extracted root with Python 3.11. Exact versions used for release
verification are in `environment_versions.json`; install the versioned Python
dependencies in `requirements-verification.txt` for the checkpoint/live checks.
The confirmation, component, SQL and interdiction checks use the standard library.
Use fresh output names where a verifier writes a file.

```sh
python thesis_research/src/lineage_constraints/verify_results.py thesis_research/results/lineage_constraints/2026-11-10/confirmation
python thesis_research/src/lineage_constraints/verify_robustness.py thesis_research/results/lineage_constraints/2026-11-10/robustness
python thesis_research/src/lineage_constraints/verify_sql_comparison.py thesis_research/results/lineage_constraints/2026-11-10/sql_comparison sql_recheck.json
python thesis_research/src/lineage_constraints/verify_interdiction_recheck.py thesis_research/results/lineage_constraints/2026-11-10/interdiction_recheck thesis_research/results/phase2/defense_results.json interdiction_recheck.json
python -m thesis_research.src.lineage_constraints.verify_bilinear_study thesis_research/results/lineage_constraints/2026-11-10/bilinear_study bilinear_recheck.json
python manuscript/scripts/verify_public_certificate_evidence.py public_live --output live_recheck.json
```

The first five commands audit frozen synthetic/graph studies. The last needs
only the public live export, not detector code or the original capture folders.
These checks preserve negative controls and assumptions; they do not establish
enterprise effectiveness, complete taxonomy coverage or an optimal policy.

## Manuscript conventions

The manuscript retains its original section order and model formulations.
The literal-learning table reports sample SD across three seeds. Remediation
reports population SD across the finite set of graphs. No saved results were
converted to a different SD convention. Code labels retained for provenance may
include development names; they do not change these interpretation boundaries.

## Integrity and provenance

`ARTIFACT_SHA256.json` binds every payload file. Original frozen-study manifests
remain intact. `public_live/MANIFEST.json` independently binds the selected live
export. `CITATION.cff` supplies artifact authorship; the artifact is not a journal
publication. DOI status is recorded separately in the release-status file and
is not inferred from having a local ZIP. The public GOAD fork is background lab
infrastructure; the advertised CertGraph-CIPG URL was not publicly accessible at
the release check and is not claimed as a verified distribution of this revision.
'''

def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()

def main():
 files=set()
 for directory in ['confirmation','robustness','sql_comparison','bilinear_study','gating_audit',
                   'interdiction_recheck','interdiction_audit','projection_contract_cached',
                   'projection_repeated','falsification_controls']:
  files.update(p for p in (BASE/directory).rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts)
 modules=['__init__.py','engine.py','simulator.py','baselines.py','temporal.py','repair.py','source_faults.py',
          'sql_lineage.py','sql_comparison.py','literal_bilinear.py','bilinear_study.py','verify_bilinear_study.py',
          'verify_results.py','verify_robustness.py','verify_sql_comparison.py','verify_interdiction_recheck.py',
          'verify_interdiction_audit.py','verify_projection.py','METHOD.md','SQL_IDENTITY_EQUIVALENCE.md']
 files.update(ROOT/'thesis_research/src/lineage_constraints'/n for n in modules)
 files.update((MAN/'generated').glob('*'))
 files.update(p for p in (MAN/'scripts').glob('generate_*') if p.suffix=='.py')
 files.update([MAN/'scripts/evidence_table_layout.py',MAN/'scripts/verify_public_certificate_evidence.py',
               MAN/'scripts/export_public_certificate_evidence.py',Path(__file__)])
 files.update([ROOT/'LICENSE',ROOT/'thesis_research/results/phase2/defense_results.json',
               ROOT/'thesis_research/results/phase3/cipg_stress_test_results.json'])
 # These derived files contain template-risk outcomes and public identities,
 # not management transcripts. Their hashes are used by table generators.
 for name in ['paired_policy_external_comparison.json','independent_2019_external_comparison.json',
              'interdiction_recheck_statistics/results.json','interdiction_recheck_verification.json',
              'bilinear_study_verification.json','gating_audit_verification.json']:
  files.add(BASE/name)
 payload={str(p.relative_to(ROOT)):p.read_bytes() for p in sorted(files) if p.is_file()}
 for p in sorted((RELEASE/'public_live').rglob('*')):
  if p.is_file():payload['public_live/'+str(p.relative_to(RELEASE/'public_live'))]=p.read_bytes()
 payload['verification/LIVE_EVIDENCE_VERIFICATION.json']=(RELEASE/'LIVE_EVIDENCE_VERIFICATION.json').read_bytes()
 payload['README.md']=README.encode()
 versions={name:importlib.metadata.version(name) for name in ['cryptography','numpy','networkx','torch','scikit-learn','scipy','matplotlib']}
 payload['environment_versions.json']=(json.dumps(versions,indent=2)+'\n').encode()
 payload['requirements-verification.txt']=('\n'.join(name+'=='+value for name,value in versions.items())+'\n').encode()
 payload['CITATION.cff']=('cff-version: 1.2.0\nmessage: "Please cite this research artifact when using it."\ntype: software\ntitle: "'+TITLE+'"\nversion: 0.1.0\ndate-released: 2026-11-14\nauthors:\n  - family-names: Shahriar\n    given-names: "Md. Hasan"\n  - family-names: Biswas\n    given-names: Taufiq\n  - family-names: Hossain\n    given-names: "Md. Ramim"\nlicense: GPL-3.0-only\n').encode()
 forbidden_suffixes=('.pfx','.pem','.key','.ccache','.kirbi','.qcow2','.pyc')
 violations=[]
 for name,raw in payload.items():
  if name.endswith(forbidden_suffixes) or '/data/lineage_live/' in name:violations.append(name)
  # Match actual PEM boundary lines, not the quoted detection expressions in
  # this release-builder's own source code.
  if re.search(rb'(?m)^-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----\r?$',raw):violations.append(name)
  if re.search(rb'(?:gh[pousr]_[A-Za-z0-9]{30,}|github_pat_[A-Za-z0-9_]{40,})',raw):violations.append(name)
 if violations:raise ValueError('Unexpected sensitive material in release allowlist: '+', '.join(violations))
 hashes={name:hashlib.sha256(raw).hexdigest() for name,raw in sorted(payload.items())}
 payload['ARTIFACT_SHA256.json']=(json.dumps(hashes,indent=2)+'\n').encode()
 target=RELEASE/'CertGraph_Artifact_v0.1.0.zip'
 with zipfile.ZipFile(target,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
  for name,raw in sorted(payload.items()):z.writestr(name,raw)
 with zipfile.ZipFile(target) as z:assert z.testzip() is None
 report={'artifact':target.name,'sha256':sha(target),'md5':hashlib.md5(target.read_bytes()).hexdigest(),
         'size_bytes':target.stat().st_size,'manifest_bound_payload_files':len(hashes),
         'public_live_cases':72,'forbidden_file_types':0,'private_key_markers':0,'access_token_markers':0,
         'scope':'Allowlisted payload plus selected public evidence; no complete raw live trees or command transcripts.',
         'license':'Existing project GPL v3 retained; CC-BY default must not replace it.'}
 (RELEASE/'PACKAGE_AUDIT.json').write_text(json.dumps(report,indent=2)+'\n')
 (RELEASE/'README.md').write_text(README)
 (RELEASE/'ARTIFACT_SHA256.json').write_text(json.dumps(hashes,indent=2)+'\n')
 print(json.dumps(report,indent=2))

if __name__=='__main__':main()
