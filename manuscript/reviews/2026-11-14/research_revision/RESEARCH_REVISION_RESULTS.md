# Research revision results

This revision implements the research-readiness review while preserving the IEEE document style and all four figures. The central title/contribution now concerns revisable certificate lineage under incomplete evidence. Learning and preventive interdiction remain supporting studies, with their negative results retained.

## Completed

- Replaced the legacy five-invariant method narrative with the contract actually evaluated: observation fields, namespace normalization, scoped enrichment, compatible incomplete candidates, strong identity, conflicts, success/order conditions, separate mutation overlap and explicit retraction. New pseudocode matches retained-set recomputation.
- Distinguished authorized identity delegation, observed overlap, necessary policy and malicious intent.
- Clarified that enrollment-edge cuts prevent future issuance but do not establish invalidation of existing credentials.
- Corrected Euler's DOI/article metadata; used the relevant journal version of order-incomplete query work. There are now 18 journal articles and two conference papers among 32 citations.
- Removed unsupported enterprise-wide polling/SOC-window assertions from the method discussion and narrowed the required-enrichment claim to selected evidence fields.
- Added reproducible ambiguity and illustrative loss analysis of frozen randomized predictions.
- Ran a new protocol-frozen benchmark of the current reference at 100/1,000/5,000 issuances, with complete and 10%-incomplete serial profiles, 20 authentications and five repetitions. The source and protocol hashes, raw timings and checkpoint sizes are retained.
- Added a current-reference benchmark table using the existing width-aware table style; the manuscript now has 16 tables.

## New findings

The 2,000 randomized histories yield 2,157 conservative candidate edges: 1,787 true and 370 incorrect alternatives. Mean candidate count is 1.0785; nearest-rank p95 is 2 and maximum is 9. Point-time matching retains only 1,345 candidates, all true in this cohort. These are additional descriptive analyses, not new independent histories.

For overlap loss `unclaimed_true + r * false_definite`, the conservative reference wins against point-time matching only at r > 203/51 (~3.98). The model excludes review cost, delay and value of possible answers. No administrator preferences were measured.

At 5,000 retained issuances, median reference updates are about 166 ms on this host, with 20 authentication decisions recomputed. Ten-percent missing serials expands each query to 501 candidates. The complete snapshot serializes to 1,149,218 bytes. This generated snapshot benchmark does not measure sequential ingestion, enterprise arrivals, CA/DC cost or SQL performance.

All 600 measured decisions match independently constructed expected IDs, and all 30 checkpoint restorations agree. An initial setup attempt requested issuance indices beyond the 100-record snapshot; it failed the oracle check and is retained as `history_benchmark_failed_setup`. The corrected modulo-index schedule was frozen before the reported run. The failed run is not included in results.

## Verification

- 29 existing contract, temporal/repair and SQL tests passed.
- Frozen confirmation verification passed: 27,000 prediction rows and 2,000 independently checked randomized labels.
- The prior review's public-evidence recheck passed all 72 cases; no new live case is claimed.
- PDF build and focused visual inspection cover the revised title, contract algorithm and new table.
- All four active figures and previous scientific result tables are retained. The figure manifest is refreshed against revised text.

## Still required for stronger submission evidence

The paper is more coherent and precise, but Q1 readiness is not certified. Independent live policy diversity, realistic benign/authorized-delegation workloads, investigator usefulness, operational cost elicitation, longer-running collection/retention, and task-aligned remediation validation remain open. Current synthetic timings do not close those gaps. The unchanged SQL equivalence, negative gating result and unfavorable bridge-ablation comparison remain visible.

Recommended next study: freeze the current evidence contract and evaluate the same projected observations with guarded SQL, strong join, bounded-time correlation and ignore-export ablation. Predeclare false-definite claims, true-link coverage, candidate p95, time-to-resolution and revisions as separate endpoints; distinguish added sensor information from reasoning changes. Use an independent administrator/environment and outcome adjudication for the live extension. Select size using error tolerance and clustering; repeated certificates in one policy block are not independent environments.

Public Zenodo version is unchanged. The accompanying revision supplement and updated local source ZIP contain the new work. Existing DOCX is stale and is not a verified export of this revision.
