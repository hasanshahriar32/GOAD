# Publication validation revision

This suite replaces unsupported manuscript interpretations with reproducible synthetic evidence. It does **not** establish production ADCS exploit detection or Q1 acceptance. Read the [current paper](../../../../thesis_paper/journal_manuscript/manuscript.pdf) and [original audit](../../../../thesis_paper/reviews/2026-10-14/journal_readiness_review.md).

## Completed experiments

- Six legacy runs: seeds 11, 29, 47, each with and without hard negatives in training. Each run has independently namespaced 700/210/350 train/validation/test graphs. The two conditions have different test samples; their difference is not a matched causal estimate.
- Three paired ESC13 prerequisite runs: 300 training families, 100 validation families, and 150 IID, 150 long-path, 150 larger-background, and 100 remote-membership test families per seed. Each family contains opposite-label variants, confined to one split.
- GNN and MLP checkpoints selected by validation loss; RF settings fixed; no test-selected model. Exact input hashes checked across splits. Hash checks do not detect graph isomorphism or establish independent motif diversity.
- All paired cases checked with both queue-based and Boolean-closure references. They share a specification and are not independent Windows ground truth.
- Saved per-case predictions, probabilities, family IDs, model checkpoints, source hashes, package versions, and training histories.
- Cascade thresholds set to the minimum positive validation score. No test tuning and no guaranteed out-of-sample recall.

Results: [JSON artifacts](../../../results/publication_validation/), [generated summary](../../../../thesis_paper/journal_manuscript/generated/summary.json). Current synthetic results favor simple structural rules/counts over a claim of GNN superiority. The symbolic reference defines paired labels, so its perfect score is a consistency baseline.

## Reproduce from the repository root

Use the existing Python 3.11 `.venv`. Recorded package versions are in each results JSON; changing versions can change numerical outcomes. Commands run sequentially to avoid CPU contention. Training writes to the selected output directory: use a new `--output` path when preserving a prior run.

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 .venv/bin/python -m unittest discover -s thesis_research/tests -v
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 .venv/bin/python thesis_research/src/publication_validation/run_legacy.py
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 .venv/bin/python thesis_research/src/publication_validation/run_counterfactual.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python thesis_research/src/publication_validation/verify_results.py
OPENBLAS_NUM_THREADS=1 .venv/bin/python thesis_research/src/publication_validation/build_artifacts.py
```

Build the PDF with `tectonic manuscript.tex` from `thesis_paper/journal_manuscript`. Build Word with `python3 thesis_paper/journal_manuscript/build_manuscript_docx.py`; system Python has python-docx installed. The builder requires Pandoc. Desktop copying is optional via `--copy-to-desktop`.

`verify_results.py` recomputes aggregate metrics and cascade decisions from saved predictions, checks split/family overlap, validates selected epochs against recorded validation losses, and recomputes paired labels. This verifies reporting consistency, not the correctness of real-world labels. `build_artifacts.py` refuses incomplete default seed coverage and records input hashes for generated tables.

## Scope of the paired cases

`esc13_cases.py` documents the schema. Forward edges are resolved effective-allow relations. The predicate assumes eligible policy groups and resolved CA trust; ignores DACL deny/inheritance resolution, patch-specific KDC behavior, cross-forest semantics, relay, and collection errors; and treats approval/signature requirements as unmet. High-value membership is an input objective. Negative means this predicate is false, not absence of other attacks.

Remote membership swaps preserve degree counts and the two-layer target computation neighborhood while reversing the label. Local attributes cannot solve these pairs. Adding more layers, closure features, or global processing would change this test's assumptions. Larger-background graphs shift a count feature and are not enterprise-scale topology validation.

## Historical work

Original `results/phase1` and `results/phase2`, notebooks, full thesis, and slides remain historical. Local rule engines are not measured Certipy or BloodHound executions. The old journal files are preserved in `thesis_paper/reviews/2026-10-14/manuscript_before_repair.*`. Do not combine old unsupported latency, theorem, autonomous-remediation, or real-data claims with this revision.
