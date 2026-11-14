# CertGraph revision analyses supplement

This package supports two analyses added after the frozen Zenodo artifact:

1. Ambiguity and illustrative decision-cost sensitivity, reusing frozen confirmation labels/predictions.
2. A generated retained-history benchmark of the current reference.

Run from the extracted package root with Python 3.11 or newer. The scripts use only the standard library. Output paths mirror the project layout.

```
python manuscript/scripts/analyze_attribution_utility.py
```

Compare results with `manuscript/reviews/2026-11-14/research_revision/utility_analysis.json`. To repeat the benchmark, first rename the supplied `history_benchmark` result directory to preserve it. Then run:

```
python manuscript/scripts/benchmark_retained_history.py
```

The benchmark writes a new protocol before executing. Check expected-candidate assertions and checkpoint equality; timing values will vary across machines. Snapshot initialization is outside the timer. These are not Windows collection, SQL performance or production-throughput measurements. The failed initial setup is documented separately and contributes no reported result.

`MANIFEST.json` binds the included files with SHA-256. The original frozen study verification remains in the main research artifact. These analyses do not add new live certificate cases. Source-code licensing follows the repository license included in this supplement; external dependencies are not bundled.
