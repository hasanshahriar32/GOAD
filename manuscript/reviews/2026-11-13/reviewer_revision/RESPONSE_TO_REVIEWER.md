> WITHDRAWN at the author’s request. This report does not describe the active manuscript. See [the context-checked decisions](../careful_revision/REVIEW_DECISIONS.md).

# Revision in response to the CertGraph reviewer report

Date: November 13, 2026. Scope: `manuscript/`, associated offline evidence checks, and a local reproducibility package. No laboratory captures or saved study outputs were overwritten. A pre-revision snapshot is in `before/`.

The supplied report combines scientific concerns that remain relevant with citation numbers and passages from an older manuscript. Changes below were checked against the actual starting source rather than applying the old reference numbers to different current entries.

## Scientific concerns

| Reviewer concern | Revision and evidence |
|---|---|
| Gating title and “cure” exceed the results | Retitled the paper **CertGraph: Issuer-Scoped Certificate Provenance for Active Directory Certificate Services Investigation and Remediation**. Removed shortcut-elimination framing. Both the abstract and conclusion retain the identical-classification and long-path failure results. |
| Three loosely connected contributions | Made certificate-specific investigation the central question. Recast the contributions as the evidence contract, controlled certificate-use evaluation, and complementary remediation analysis. Optional learning is in Appendices A and B and cannot gate provenance collection. |
| 0/63 versus 41/63 | The starting introduction no longer claimed 0/63. The appendix identifies 41/63 as an original-label diagnostic, explains the ten reachable positive cases and repeated inputs, and reports the matched studies separately. No specificity estimate is inferred from those 63 cases. |
| Weak GNN training evidence | Moved the formulation and evaluations to appendices. Retained 22 unique training inputs, 21 repeated in validation, symbolic labels, and family-disjoint follow-up. No real-data GNN performance is invented. |
| Theorem excludes its own attention | Replaced the theorem/long proof with a diagnostic showing the target-dependent attention derivative explicitly. The residual inequality is stated in the common hidden space and includes all other derivative paths. It is not a guarantee for raw features or shortcut elimination. |
| Stackelberg misnomer | Replaced the strategic-equilibrium formulation with budgeted pair disconnection over blockable edges. Removed the unused follower response and regularized utility that were not the evaluated objective. Named the implementation an adaptive sequential heuristic. |
| Correctness fix does not improve optimality | Retained 43/60 optimum matches and maximum gap of two pairs. The single corrections appendix records the uncorrected control's 46/60 result. No performance improvement is attributed to restoring metadata. |
| Nonsignificant budget-24 result | Retained exact raw p = 0.0625 and both Holm-adjusted p = 0.25 values. Removed the illustrative equilibrium figure and plotted measured fixed-budget values with population SD. |
| Live scale and unexecuted products | Kept the primary denominator at 72 cases: 66 successful uses including 13 administrative uses, and six rejections. The separate split-actor pilot is not added to that denominator. Preserved the shared image-family boundary and distinctions between actual Certipy/Sigma runs, a query proxy, and unexecuted HADES/Splunk deployments. |
| Related work too late | Moved Related Work immediately after Introduction and separated it from Discussion and Conclusion. |

## Technical consistency

| Concern | Resolution |
|---|---|
| Wrong SAN OID | The starting source already used `szOID_SUBJECT_ALT_NAME2` / 2.5.29.17; retained it. The template-name OID is not described as a SAN carrier. |
| Poisson arithmetic | Source inspection found a stronger correction: 2,000 arrivals are sampled uniformly over simulated duration T, with probability 0.055 of choosing one of fifteen maintenance templates. Replaced the unconditional per-hour Poisson interpretation with the matching-template sampling probability and the observed finite-workload counts. Corrected generated maintenance durations to [10,35] seconds. A fresh replay reproduces dataset counts, ablation results and the horizon/polling matrix exactly. Fresh timing is not substituted for saved timing. |
| Figure 1 schema mismatch | Replaced the image with a vocabulary diagram matching the six node types and ten relation types of the definition. Removed the sixteen-relation caption. |
| Unsupported throughput/scale claims in pipeline figure | Replaced the pipeline with a source-to-contract diagram containing no unmeasured sweep, latency or graph-size claims. Collection proceeds independently of neural screening. |
| Illustrative equilibrium curves | Removed the image. The replacement plot reads the corrected saved measurements and labels the x-axis as assigned disruption budget. |
| CA/KDC projections and listing disagree | Removed the field-name-disjointness proposition. The CA projection now lists fields actually shown in the selected 4887 payload; KDC projection includes `CertIssuerName`. SKID is explicitly CA-database enrichment, not a demonstrated field in that listing. |
| Missing self-use column | Added self-use counts to the paired-policy table, derived from verified per-trial outcomes with assertions. All eight rows sum self + admin = trials. |
| Mixed SD conventions | Standardized displayed dispersions to population SD for each finite evaluated set. Converted the three-seed bilinear SD from sample to population: IID 2.19 to 1.79 percentage points; larger background 1.00 to 0.82. Means, classifications, labels and raw saved results are unchanged. Paired tests still use per-graph observations. |
| Underscores disappear | Changed the escaped underscore to an encoded glyph. PDF extraction is checked for `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` and `szOID_SUBJECT_ALT_NAME2`, including across line breaks. |
| Incomplete update algorithm | Aligned the pseudocode with the revisable contract: all relevant observations enter retained state, including late exports, removals and failed outcomes. It no longer requires an active mutation merely to retain an issuance. Identity and temporal decisions remain separate. |

## Bibliography and literature positioning

- Corrected Certipy to the executed **5.0.4** release (published November 22, 2025), with a versioned release URL.
- Added separate software entries for **pySigma 2.1.0** and **SQLite backend 2.1.1**, and pinned Sigma rules to the recorded commit. No nonexistent software DOI was invented.
- Replaced the TIME conference reference with its verified **Theoretical Computer Science** journal extension. The underlying possible/certain-answer attribution is retained.
- Added classical **Wood (1993)** and **Israeli and Wood (2002)** journal interdiction papers; distinguished their objectives from security games and cut hardness.
- Added GATv2 as an accurately labeled conference paper. Discussed R-GCN and gated GNN families through the cited journal reviews rather than claiming those models were executed.
- Expanded provenance positioning with a contemporary journal evaluation synthesis covering HOLMES, KAIROS and FLASH, and a journal paper on causality-preserving evaluation. These literature comparisons do not become experimental baselines.
- Confirmed HADES **23(1):936–953**, CPD **23(4):8967–8984**, and their DOI/title metadata. The unusual CPD page range is supported by the registry and the authors' institution. No HADES USENIX 2025 version was confirmed, so no unverified duplicate citation was added.
- Confirmed the timestamp preprint on arXiv and the Microsoft October 2026 update on its primary page. Neither is relabeled as a peer-reviewed evaluation.
- Added missing verified DOIs and explicit DOI display notes because the installed IEEEtran bibliography style does not print its `doi` field. Standardized access dates and protected proper nouns in titles.
- The report's NodeMerge/RapSheet, limited-query preference-elicitation and DEF CON-title references are absent from the starting bibliography. No unrelated paper was substituted to satisfy their old reference numbers. Removed the remaining implication that the hardening citation validates preference elicitation.

Final reference counts and cited-key checks are in `REFERENCE_AUDIT.json` and `FINAL_CHECKS.json`.

## Presentation and author information

- Retained IEEEtran journal formatting, with single-column tables/figures where legible and a full-width evidence pipeline and remediation table.
- Abstract is approximately 190 words and states the evidence contract, controlled results and remediation role directly.
- Consolidated implementation corrections and excluded attempts in one appendix; removed draft-history framing from the main claims.
- Preserved the existing affiliation, corresponding author and author contributions. Added an ethics/dual-use statement tied to the isolated testbeds.
- Added **“This research received no specific grant from any funding agency”** after the author's confirmation.
- Removed the obsolete writing-process declaration as requested. No replacement authorship claim is made.

## Reproducibility and remaining submission action

The local review artifact includes frozen synthetic inputs, labels, predictions, checkpoints, relevant source snapshots, verification reports, evidence tables and reproduction instructions. Credential-bearing live capture trees, private keys, tokens and VM images are excluded. Consequently, the package permits offline checks of the synthetic studies and derived live summaries; it does not independently reproduce every live certificate outcome without the retained original captures.

**Still open:** publish the reviewed/sanitized artifact in a persistent archive and insert its assigned DOI. A local ZIP is not a public deposit. No DOI, publication status or journal acceptance is fabricated. The paper's data-availability statement remains explicit about the absent persistent deposit. Journal-specific submission declarations and any artifact-release license decisions remain the authors' responsibility.

## Validation performed

- Confirmation: 5,400 cases, 27,000 predictions, 2,000 independently checked randomized labels.
- Component study: 2,700 identity histories, 1,800 temporal histories, 16,200 predictions, 3,600 temporal-oracle queries.
- Relational study: 16,269 prediction rows and 450 latent labels.
- Interdiction: 120 graph/budget cases and 11,100 reachability queries.
- Literal learning study: 5,100 independent labels and 10,800 checkpoint predictions.
- Seeded streaming replay: exact agreement on saved dataset, ablation and sensitivity counts.
- Final PDF/build, reference, manifest and package checks: `FINAL_CHECKS.json`.

These are checks of existing evidence and source-faithful revisions, not new enterprise deployments or additional live attack cases.
