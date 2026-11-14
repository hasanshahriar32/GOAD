# Extended research validation results

## Completed experiments

1. **Independent-generator evidence-value experiment:** 432 new designed histories, 864 observation stages and 4,320 method/stage predictions. Methods: current reference, actual guarded SQL, strong SQL join, ignore-export ablation and one-record repair. Factors: three seeds, 4/16/64 issuances, 0/25/75% missing identifiers, absent/clean/corrupt/delayed exports, four replicates. Primary methods receive identical evidence. An independent verifier imports neither generator nor detector and checks physical labels, truthful raw projection, within-budget retention, guarded equivalence, hashes and aggregate counts.

2. **Matched incremental identity replay:** nine generated streams at 100/300/600 issuances, ten authentications and three seeds. Includes delayed enrichment, duplicate delivery, checkpoint/SQL recovery, a conflicting optional row and its removal. 35,055 saved decision comparisons match, all 90 final answers identify the expected physical certificate, and every run withdraws one link then recovers. A separate verifier checks saved prefixes, counts, IDs, retractions and manifests.

3. **Stronger remediation baselines:** independent plain-adjacency exhaustive enumeration reproduces optimal counts on all 60 saved small instances. Dynamic single-edge greedy matches 45 optima, two-edge lookahead 56, current adaptive 43 and static greedy 21. All budget/immutability constraints pass. This is an exploratory comparison on saved instances, not independent enterprise evidence or a new algorithm claim.

4. **Full existing test suite:** 78 tests passed. Additional frozen-study component, SQL and bilinear reproduction checks are recorded beside their outputs. The public-certificate verification covers the existing 72 cases; these new offline studies add no Windows certificate case.

## Findings

The new evidence-value grid gives 260 correct resolved links and 404 true retained candidates for both reference and guarded SQL. Strong SQL gives 292 correct resolutions and 292 true retained candidates. Ignoring exports gives 176 correct resolutions and retains all 432 true candidates; one-record repair gives 131 correct resolutions and retains all 432. There are zero wrong resolved claims in this grid. Reference loss of 28 true candidates comes from corrupt optional evidence. Mean candidate counts are 1.98 for reference/guarded SQL, 0.68 for strong SQL and 5.30 for ignore/repair; p95 counts are 8, 1 and 25 respectively.

This is a designed mixture, not a prevalence estimate. Useful exports reduce ambiguity, but conservative repair has no demonstrated certainty advantage over ignoring exports. Guarded equivalence persists. No method dominates all endpoints.

Median cumulative reference add/remove times across seeds are 125.95/1,079.43/4,382.80 ms for 134/374/734 updates; guarded SQL takes 258.43/1,884.22/7,298.14 ms. Both execute real incremental updates on equal identity inputs. Timings exclude workload construction, verification, restart and Windows collection. Raw timing series and source/platform information are retained. These serial shared-host figures are not maximum sustainable throughput.

The stronger two-edge baseline reduces the case for highlighting the adaptive heuristic as a novel remediation advance. The manuscript reports the result explicitly.

## Manuscript integration

The evidence-value table, matched replay results and stronger optimization comparison are integrated into the evaluation. The conclusion and supplementary-data description are updated. Existing evidence and negative results remain. IEEE formatting and four figures are retained; figure input hashes are refreshed.

## Execution blocks

The external device currently reports 0 bytes and the historical backing-disk mount is absent. Local Windows overlays exist, but the seed's backing image is under `/source/goad_vms/` on that unavailable disk. No GOAD VM is running. The read-only qemu metadata check confirmed the dependency. Live replication, longer Windows collection and response validation cannot be executed against that absent base.

Actual investigator usefulness requires independent participants or independently adjudicated operational cases. It cannot be replaced by invented responses or self-evaluation. `NEXT_LIVE_PROTOCOL.md` prepares the remaining design. These gaps remain open; this work does not certify Q1 readiness.

## Reproduction

From the GOAD root, standard library Python is sufficient for the new scripts:

```
python manuscript/scripts/verify_evidence_value.py
python manuscript/scripts/verify_streaming_identity.py
```

The runners refuse to overwrite their frozen protocol/output directories. Preserve/rename existing run directories and protocol before repeating:

```
python manuscript/scripts/evaluate_evidence_value.py
python manuscript/scripts/benchmark_streaming_identity.py
python manuscript/scripts/compare_interdiction_baselines.py
```

All scripts and necessary frozen inputs accompany the supplementary ZIP. New generated histories are distinct from the prior confirmation generator, but remain synthetic. Public Zenodo version is unchanged.
