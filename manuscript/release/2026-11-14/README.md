# CertGraph research artifact, version 0.1.0

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
