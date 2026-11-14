# CertGraph offline review artifact — November 13, 2026

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
