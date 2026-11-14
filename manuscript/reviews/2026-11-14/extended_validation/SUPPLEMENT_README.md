# Extended CertGraph validation supplement

This supplement contains the independent factorial generator, matched incremental identity replay, stronger small-instance interdiction baselines, saved inputs/predictions, independent verifiers and source hashes. It is separate from the frozen Zenodo version.

Extract and run from the package root with Python 3.11 or newer; the five new scripts use the standard library. Recheck supplied evidence:

```
python manuscript/scripts/verify_evidence_value.py
python manuscript/scripts/verify_streaming_identity.py
```

To regenerate, preserve/rename the relevant existing output directory first. The factorial runner also refuses to replace `evidence_value_protocol.json`, which should be preserved/renamed with its results. The runners write protocol/source hashes before measurement:

```
python manuscript/scripts/evaluate_evidence_value.py
python manuscript/scripts/benchmark_streaming_identity.py
python manuscript/scripts/compare_interdiction_baselines.py
```

Timings vary by machine. The identity experiment erases time consistently and does not measure temporal reasoning or Windows collection. The optimization extension reuses 60 saved small instances; it does not claim a new algorithm. Source licensing follows the included repository license.

`MANIFEST.json` binds package payloads. Existing-study verification logs in the package document additional checks; the full original frozen research data for those checks is in the earlier research release. No human responses, new live trials, private keys or credentials are included.
