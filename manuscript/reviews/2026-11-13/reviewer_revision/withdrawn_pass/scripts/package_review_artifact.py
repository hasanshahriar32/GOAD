"""Build a local, allowlisted offline-review artifact; never publish it.

Raw live-capture trees and account/session material are deliberately excluded.
The package documents that live outcome summaries cannot replace raw evidence.
"""
from pathlib import Path
import hashlib
import importlib.metadata
import json
import re
import zipfile

ROOT=Path(__file__).resolve().parents[2]
MAN=ROOT/'manuscript'
REVIEW=MAN/'reviews/2026-11-13/reviewer_revision'
BASE=ROOT/'thesis_research/results/lineage_constraints/2026-11-10'
OUT=MAN/'submission_files'

README='''# CertGraph offline review artifact — November 13, 2026

This is a local review package, not a public archive or an assigned DOI.

Included: frozen confirmation/component/SQL/learning/interdiction/projection
studies, synthetic inputs and labels, checkpoints, source snapshots, current
offline verification modules, derived evidence tables and verification outputs.
Original result manifests are retained. ARTIFACT_SHA256.json additionally binds
each included file. Original repository licensing is included as LICENSE.

Excluded: complete live-capture trees, credentials, private keys, PFX/PEM/key
files, Kerberos caches/tickets, session state, VM disks and setup/control code.
Live-outcome aggregate verification JSONs are included for traceability, but
they are not raw-evidence reproductions. The 72-case live results cannot be
independently re-adjudicated from this reduced package alone. Preparing sanitized
public certificate/event evidence remains necessary for a fully public artifact.

## Recheck saved results

Use Python 3.11, with the package versions in environment_versions.json for the
learning verifier. The first four commands below use only the standard library.
Run commands from the extracted artifact root. Use a fresh output path for each
verifier that writes a report. These commands do not contact a Windows host.

```sh
python thesis_research/src/lineage_constraints/verify_results.py thesis_research/results/lineage_constraints/2026-11-10/confirmation
python thesis_research/src/lineage_constraints/verify_robustness.py thesis_research/results/lineage_constraints/2026-11-10/robustness
python thesis_research/src/lineage_constraints/verify_sql_comparison.py thesis_research/results/lineage_constraints/2026-11-10/sql_comparison sql_recheck.json
python thesis_research/src/lineage_constraints/verify_interdiction_recheck.py thesis_research/results/lineage_constraints/2026-11-10/interdiction_recheck thesis_research/results/phase2/defense_results.json interdiction_recheck.json
python -m thesis_research.src.lineage_constraints.verify_bilinear_study thesis_research/results/lineage_constraints/2026-11-10/bilinear_study bilinear_recheck.json
```

The manuscript uses population SD for finite-set descriptions. The stored
bilinear verifier reports sample SD; the evidence generator converts it using
sqrt((n-1)/n) for the three fixed seeds. Raw source results are not overwritten.

The source ZIP accompanying this artifact compiles separately with IEEEtran
and Tectonic or pdfLaTeX/BibTeX. A persistent public deposit and archive DOI are
still outstanding. No release license for new material or external publication
is silently inferred from this packaging operation.
'''


def main():
    OUT.mkdir(exist_ok=True)
    files=set()
    for name in ['confirmation','robustness','sql_comparison','bilinear_study',
                 'interdiction_recheck','interdiction_audit','projection_contract_cached','projection_repeated']:
        files.update(p for p in (BASE/name).rglob('*') if p.is_file() and not p.is_symlink() and '__pycache__' not in p.parts)
    offline=['__init__.py','engine.py','simulator.py','baselines.py','temporal.py',
             'repair.py','source_faults.py','sql_lineage.py','sql_comparison.py',
             'literal_bilinear.py','bilinear_study.py','verify_bilinear_study.py',
             'verify_results.py','verify_robustness.py','verify_sql_comparison.py',
             'verify_interdiction_recheck.py','verify_interdiction_audit.py',
             'verify_projection.py','METHOD.md','SQL_IDENTITY_EQUIVALENCE.md']
    files.update(ROOT/'thesis_research/src/lineage_constraints'/n for n in offline)
    files.add(ROOT/'thesis_research/results/phase2/defense_results.json')
    files.add(ROOT/'thesis_research/results/phase3/cipg_stress_test_results.json')
    files.update((MAN/'generated').glob('*'))
    files.update(p for p in (MAN/'scripts').glob('*.py') if 'export_docx' not in p.name)
    files.add(ROOT/'LICENSE')
    for n in ['bilinear_study_verification_final.json','transfer_workload_01_verification_final.json',
              'paired_policy_external_comparison.json','independent_2019_external_comparison.json',
              'current_patch_upn_01_adjudication_supplemented.json','current_patch_sid_01_adjudication_supplemented.json',
              'collection_pilot_02_verification.json','interdiction_recheck_statistics/results.json']:
        p=BASE/n
        if p.exists():files.add(p)
    for p in REVIEW.glob('*verification.json'):files.add(p)
    names={p.relative_to(ROOT).as_posix():p for p in sorted(files) if p.is_file()}
    assert not any('/data/lineage_live/' in n or n.endswith(('.pfx','.pem','.key','.ccache','.qcow2','.pyc')) for n in names)
    # A conservative literal-secret scan is in addition to the path allowlist.
    for name,p in names.items():
        if p.suffix in ('.py','.json','.jsonl','.sh'):
            s=p.read_text()
            if re.search(r'-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----',s):
                raise ValueError('Private key marker in allowlisted file: '+name)
    hashes={n:hashlib.sha256(p.read_bytes()).hexdigest() for n,p in names.items()}
    versions={}
    for name in ['numpy','networkx','torch','scikit-learn','scipy','matplotlib']:
        try:versions[name]=importlib.metadata.version(name)
        except importlib.metadata.PackageNotFoundError:pass
    zip_path=OUT/'CertGraph_Review_Artifact.zip'
    with zipfile.ZipFile(zip_path,'w',zipfile.ZIP_DEFLATED,compresslevel=7) as z:
        for name,p in names.items():z.write(p,name)
        z.writestr('README.md',README)
        z.writestr('environment_versions.json',json.dumps(versions,indent=2)+'\n')
        z.writestr('ARTIFACT_SHA256.json',json.dumps(hashes,indent=2)+'\n')
    with zipfile.ZipFile(zip_path) as z:assert z.testzip() is None
    report={'file':str(zip_path.relative_to(ROOT)),'sha256':hashlib.sha256(zip_path.read_bytes()).hexdigest(),
            'bytes':zip_path.stat().st_size,'bound_files':len(hashes),'contains_raw_live_capture_trees':False,
            'public_deposit_performed':False,'archive_doi':None,'zip_integrity':'passed'}
    (REVIEW/'ARTIFACT_PACKAGE.json').write_text(json.dumps(report,indent=2)+'\n')
    (REVIEW/'ARTIFACT_README.md').write_text(README)
    print(json.dumps(report,indent=2))


if __name__=='__main__':main()
