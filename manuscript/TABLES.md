# Table layout

All fifteen manuscript tables use `tabularx` with the float's current `\linewidth`. Text columns wrap; quantitative columns use consistent alignment and, where appropriate, share the remaining width. The shared `\evidencetable` style uses 8.5 pt type with 10.2 pt leading. Whole tables are not scaled down to fit.

Eleven tables occupy one column. Four dense comparisons span both columns: the legacy streaming benchmark, the matched policy-intervention matrix, the current-patch certificate-outcome matrix, and the remediation comparison. These are float choices within the existing IEEE layout; the document class and page geometry are unchanged.

`scripts/evidence_table_layout.py` defines the width and wrapping rules. Its `style_evidence_tables` function is shared by all seven evidence generators, so regeneration preserves the layouts. `Y` and `C` in `manuscript.sty` provide flexible left-aligned and centered columns. The three tables written directly in `sections/06_empirical_evaluation.tex` use the same layout rules. The sensitivity table includes space between its two-line precision/recall groups.

Regenerate evidence from the repository root with its existing `manuscript/scripts/generate_*_evidence.py` scripts, then run `bash compile.sh` from this directory. Regeneration reads the frozen saved results; no new VM experiment is required for a presentation change.

The table revision is documented under `reviews/2026-11-14/table_layout/`, including a rollback snapshot, before/after page proofs, build log and numerical-preservation checks. Values are unchanged. That table-only build had 22 pages; the subsequent full-layout review is documented under `reviews/2026-11-14/overall_layout/` and supersedes its pagination.
