# Research continuation: live interventions, static-model audit, and exact interdiction checks

This update supersedes the open-gap status in the earlier continuation report where the new results below supply evidence. Work remains in `/home/m4x1d/Desktop/GOAD`. The manuscript keeps its article class, single-column styling, title, seven main sections, and existing figures. No original static-model implementation or layer count has been changed.

## Assessment

The strongest defensible direction is certificate-specific evidence assurance: distinguish exact issuance-to-use linkage, successful privileged use, configuration risk, temporal overlap, and conditional necessity. The new live results strengthen this direction substantially. They do not establish a new cryptographic primitive, a universal GNN shortcut cure, an optimal Stackelberg solver, or a guarantee of Q1 acceptance.

Q1 is a journal/category/year ranking in JCR or SJR, not a manuscript score. No current journal-specific quartile or acceptance probability is asserted. The manuscript needs a coherent contribution and credible evidence before selecting a target; deleting truthful scope conditions would weaken that evidence.

## Completed paired live studies

Two final matrices each contain three randomized blocks and four conditions. Each block reuses identical signed administrative CSR bytes and the same key for baseline, enabled, and rollback-before-enrollment trials. The subject-supplied-name bit changes from 33554432 to 33554433. Recorded template DACL, EKU, approval/signature requirements, and template OID remain equal across the matched conditions. CA cache refresh and low-privilege RPC readiness are applied consistently.

| Environment | Condition | Trials | Verified self uses | Verified Administrator uses |
|---|---|---:|---:|---:|
| Windows 2016, ESSOS | Baseline, administrative SAN requested | 3 | 3 | 0 |
| Windows 2016, ESSOS | Subject bit enabled | 3 | 0 | 3 |
| Windows 2016, ESSOS | Rollback before enrollment | 3 | 3 | 0 |
| Windows 2016, ESSOS | Legitimate self enrollment | 3 | 3 | 0 |
| Independent Windows 2019, Q1LAB | Baseline, administrative SAN requested | 3 | 3 | 0 |
| Independent Windows 2019, Q1LAB | Subject bit enabled | 3 | 0 | 3 |
| Independent Windows 2019, Q1LAB | Rollback before enrollment | 3 | 3 | 0 |
| Independent Windows 2019, Q1LAB | Legitimate self enrollment | 3 | 3 | 0 |

All 24 use outcomes are checked using public certificate bytes, exact serial/thumbprint, one CA database row, matching 4887 requester/request evidence, successful certificate-bearing 4768, and consistent target SID/name/domain. Public certificate keys also match the signed CSR. Private keys and tickets are excluded from the retained trial datasets.

The 2016 requests use their actual Windows-generated SHA-1 CSR signature; explicit signature verification succeeds. The independent 2019 requests are host-generated with RSA-2048/SHA-256. Neither is silently relabeled as the other. The independent forest has separate domain SID, CA, template, account, and request mechanism. Its enroller belongs to Domain Users and Remote Management Users, with read/enroll permissions rather than domain-administrator membership. An administrator performs the independent template intervention; this differs from the original split-actor pilot.

All final readbacks restore the baseline. In the independent 2019 matrix, four trials lack the restoration value-addition 5136 in their captured event export. Eight have the complete mutation/restoration audit chain. Successful authentication remains a separately verified fact in all twelve. The missing events are not synthesized, inferred into the raw log, or used to erase an otherwise verified certificate use.

The CSR/policy verifier supports three matched conditional contrasts per environment. These establish the tested bit's role under the recorded configuration and execution controls. They do not prove necessity across unseen policies, concurrent mutations, patch levels, or all ADCS techniques. The original audit-clock contradiction remains unresolved; controlled synchronous operation order is a different evidence source.

Key artifacts under `thesis_research/results/lineage_constraints/2026-11-10/`:

- `paired_policy_matrix_02_adjudication_final.json` and `paired_policy_matrix_02_contrasts_final.json`.
- `independent_2019_matrix_02_adjudication_final.json` and `independent_2019_matrix_02_contrasts_final.json`.
- Raw data: corresponding directories in `thesis_research/data/lineage_live/2026-11-10/`.

## Actual external executions and an informative integration failure

Certipy-ad 5.0.4 performs actual DC-only LDAP enumeration in every final trial. Three unmodified SigmaHQ rules from frozen commit `d7c9da10c170a6988d68ebdf2c9f7bd8782b7c55` are compiled with pySigma 2.1.0 / SQLite backend 2.1.1 and executed on raw-event projections. Rule files, license, SQL, versions, mapping controls, results, and hashes are retained.

In each environment, the exact tested template is flagged by Certipy ESC1 and both template-risk Sigma predicates in all three enabled administrative and all three legitimate-self trials. Baseline and rollback-before-enrollment have no such tested-template matches. Other-template matches are reported separately. Legitimate self enrollment on a risky template is not an attack false positive for a configuration-risk rule.

This is an executed Certipy/Sigma comparison, not a full SIEM, Splunk, Cortex, Defender, or HADES deployment. The earlier Splunk SQLite exercise remains a semantic proxy. No local algorithm is renamed as an actual third-party product.

The independent 2019 CA export represents its template by OID, while 4887 supplies its name. Without a directory mapping, the identity reference abstains in all twelve trials. Adding the collected object's explicit OID/name mapping gives twelve exact identity links, three privileged SID divergences and nine nonprivileged outcomes. Inference uses logs, CA export, directory OID mapping, and observed SID evidence; public CER/CSR and outcome labels are excluded.

Both the initial abstention output and mapping-aware output are retained. The adjustment is development after observing a schema difference, so the improved result is not represented as an untouched held-out test. New tests require abstention if that mapping is missing or refers to another object DN.

## Development failures retained

The first ESSOS policy matrix has two RPC failures among twelve attempts. The first paired-CSR collector stops after a pending-request-store binding error in its second attempt. Both are retained separately from the final 12/12 matrix. The corrected collector verifies the held key against the exact newly issued certificate and never falls back to an older PFX.

The independent 2019 setup also retains failed feature-install ordering, a blocked script-transport attempt, and the initial clock-skew collection. Defender remains enabled; the setup uses normal public script-file transport after the blocked attempt. A four-hour host/guest difference causes PKINIT skew diagnostics, so that run is interrupted and excluded from the final policy results. Time is corrected only in the independent writable copy, and the corrected run has a host/guest preflight check.

Original disk images remain mounted read-only. Writable overlay states are preserved outside the repository. The original 2016 test copies have been shut down. No unrelated user services are modified.

## Static gating: a matched audit changes the claim

`gating_audit.py` freezes the existing source and executes three new seeds, with additive and feature-channel-gated implementations each receiving augmentation probability 0 or 0.3. Propagation depth and source implementations remain unchanged. Each seed tests 250 opposite-label families, at membership depths 0, 1, 2, 4 and 8, with randomized node indices and matched configuration features.

The label contract is a resolved-permission ESC1 abstraction: supplied subject, client authentication, no approval, reachable enrollment allow, and no reachable explicit deny. CA trust is assumed. BFS and Boolean closure independently agree on the labels. Reachable deep membership remains positive, correcting the historical generator's false-safe interpretation.

| Implementation | Augmentation | Correct / 1,500 cases | False positives | False negatives |
|---|---:|---:|---:|---:|
| Additive | 0 | 750 (50.00%) | 750 | 0 |
| Additive | 0.3 | 1,075 (71.67%) | 425 | 0 |
| Feature-channel gate | 0 | 1,050 (70.00%) | 0 | 450 |
| Feature-channel gate | 0.3 | 1,050 (70.00%) | 0 | 450 |

The gate misses all positive cases at depths 2, 4 and 8. Its zero false positives do not establish superior overall performance over the augmentation-matched additive comparator. A second tier processing only neural positives cannot recover those misses.

The audit also finds only 22 unique training inputs per seed, with 21 shared with validation. It is a diagnostic of the existing implementations, not independent motif-level generalization. No binomial interval over repeated canonical archetypes is claimed. The first-step transforms are fixed and the semantic projections are hand-initialized. The implemented feature-channel sigmoid is not a literal bilinear edge scorer. These facts are now disclosed in the manuscript rather than conflated with the general formulation.

`verify_gating_audit.py` reproduces all 6,000 predictions from saved checkpoints, verifies labels with Boolean closure, validates selected epochs and aggregate counts, and checks artifact hashes. Separately, the existing publication-validation suite passes its saved-result integrity check across nine runs, eighteen prediction sets, and 5,400 case rows. Its models and abstraction differ from the new NumPy gating diagnostic; their metrics are not merged.

The historical 41/63 result remains in its original artifact. Ten of those nominal hard negatives are reachable positives under transitive membership. The actual stored 22 disagreements are eight administrator-only-write, four deny-write, seven benign-OID, and three deep-OID cases; the earlier paper's 15 OID / 7 CA explanation was unsupported. Calibration, seven-node-tree, perturbation, and ablation numbers were checked against saved artifacts; unsupported numbers are removed, and the skip-ablation statistic is recomputed from fold values.

## Interdiction: implementation correction and an exact comparator

The historical function reinserts a temporarily removed edge with cost only, losing relation metadata during candidate scoring. `interdiction_audit.py` adds a reference that restores every attribute. It preserves the original implementation and historical results as a comparator.

A frozen 30-graph grid, each with seven vertices and twelve edges, evaluates budgets 3 and 6. There are sixty graph/budget cases. Exhaustive enumeration maximizes severed-pair count, with cost as a tie break; lambda is zero in this audit.

| Method | Matches optimal pair count |
|---|---:|
| Static greedy | 21 / 60 |
| Historical adaptive | 46 / 60 |
| Metadata-preserving adaptive | 43 / 60 |

The correction is semantically necessary but does not improve this grid's optimality frequency. Its largest gap is two pairs. `verify_interdiction_audit.py` independently checks all sixty optimum values using bitset transitive closure over 6,113 budget-feasible subsets, and checks the corrected cuts' costs and immutability.

The paper now calls the implemented solver a sequential heuristic. It is not branch-and-cut and supplies no equilibrium certificate. Its hardness statement is restricted to positive binary-encoded rational inputs, with a polynomial connector construction from known Directed Multiway Cut. This is a specialization of established complexity, not a new graph-complexity contribution. Historical 98.5% interdiction and cone timings are not relabeled as results of the corrected reference.

## Measured collection and inference cost

`operational_cost.py` verifies trial hashes, avoids double-counting duplicated policy command files, and measures ten offline inference repetitions per captured trial. It also reports Python-traced allocations separately from RSS.

| Quantity, median across twelve trials | ESSOS 2016 | Independent 2019 |
|---|---:|---:|
| First-to-last recorded command envelope | 50.91 s | 32.14 s |
| Offline identity inference | 10.99 ms | 9.18 ms |
| Python-traced peak allocation | 1.74 MB | 1.50 MB |

These are observed experiment costs on this host. They are not continuous polling delays, production throughput, bounded-history-memory guarantees, or measured authentication interference. The measurements prevent the legacy 13k-events/s replay from being interpreted as the entire collection pipeline's operational cost.

## Current primary-source research and novelty boundary

[Microsoft's October 30, 2026 investigation](https://www.microsoft.com/en-us/security/blog/2026/10/30/help-desk-impersonation-ad-cs-abuse-investigating-esc1-esc8-intrusion-paths/) reports certificate-backed intrusion paths and response differences. This establishes practical relevance; it does not establish priority for certificate abuse detection. [Unit 42's technical study](https://unit42.paloaltonetworks.com/active-directory-certificate-services-exploitation/) already describes combining directory modification, issuance and Kerberos telemetry. Generic multi-event correlation is therefore not a defensible novelty claim.

[Microsoft KB5014754](https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers) documents SID-binding enforcement changes. The independent base's 17763.4974 build is not current. An updated configuration is being prepared using the official July 2025 prerequisite and October 2026 security cumulative update, with a cold baseline preserved and read-only update media. A downloaded package or running installer is not an installed, tested patch result; the follow-up needs post-reboot build evidence and fresh trials before it enters the paper.

The earlier verified HADES, possible/certain query, temporal constraint, and entity-resolution literature remains relevant. The defensible research question is whether explicit certificate-specific evidence contracts yield useful revisable explanations and controlled false-claim behavior at an acceptable coverage/collection cost. The new studies make that question testable. They do not demonstrate superiority for every component: fault-budget reasoning loses certain-link coverage to an ignore-export comparator, the gate has horizon failures, and corrected interdiction remains heuristic.

## Remaining substantive work

1. Complete and verify the current-patch Windows configuration, rerun the frozen intervention matrix, and adjudicate both successful and certificate-bound failed KDC outcomes.
2. The literal bilinear implementation and varied family-level split study are now executed and independently checked (see the completed extensions below). They show no classification gain over matched additive attention; a positive operational justification for this module remains unestablished.
3. Demonstrate the new evidence contract's operational benefit against matched tasks and sources. Actual Sigma/Certipy execution is complete; a full external provenance system has not been executed.
4. Self-consistent false-order and correlated-export controls are now executed (see below). They establish failure boundaries under violated trust/fault assumptions, rather than source authentication.
5. Test continuous collection latency, long-history state growth, and retention contracts if deployment claims remain central.
6. Keep submission materials, generated tables, bibliography, final PDF and validation manifest synchronized. Author contribution, conflict, submission approval, and remote artifact availability statements require factual author review; no submission has been made.

The project now has stronger controlled evidence and substantially more honest component comparisons. The current evidence does not justify calling every scientific gate closed. Continued work should target the measured failures rather than restoring unsupported headline numbers.

## Completed extensions after the initial continuation assessment

The literal two-layer/four-head attention realization in `literal_bilinear.py` now has a frozen three-seed, four-arm study. All 5,100 labels are independently checked with NetworkX, and all 10,800 held-out predictions are reproduced from saved checkpoints. Typed whole-graph WL hashes and family IDs are disjoint across splits within each seed. Initial parameters are identical across arms, augmentation is matched, and validation loss alone selects checkpoints. Classifications are identical in all four arms: mean IID accuracy 86.00% (sample SD 2.19%), larger-background accuracy 87.00% (SD 1.00%), and long-path accuracy 50%. Every arm misses all 450 long-path positives. This closes an implementation and split-quality gap; it does not establish bilinear superiority. `bilinear_study_verification_final.json` also checks per-case classification equality across arms, rather than inferring equality from aggregate metrics.

The path-preserving projection now has 45 alternating-order timing pairs over nine graph tasks. All 1,188 queried pairs are reconstructed, solver outputs reproduce, and the median per-run speed ratio at 5,000 actual nodes/325 pairs is 7.54 (observed range 6.62–8.99), including projection. Full and projection-inclusive median times are 3,448.15 ms and 439.29 ms; their ratio need not equal the median of ratios. The original 1,246 ratio dropped some queries and cannot support an equal-task acceleration claim. `projection_repeated_verification.json` records the checks.

`falsification_controls/` contains two deterministic counterexamples, not a new accuracy corpus. False but self-consistent order can imply a wrong definite overlap. Six correlated wrong bridge rows from one exporter exceed a two-record budget and produce a wrong certain link. A sufficient six-record model retains the true candidate in 64 hypotheses, while an explicitly grouped one-source model retains it in two and abstains from certainty. The units and assumptions differ; this is not an equal-assumption superiority claim. The new grouped-source reference is in `source_faults.py`.

`legacy_statistics_audit/` reproduces the saved fold and topology statistics, then adds exact signed-rank sign-flip checks and an eight-test Holm family. At budget 24, five of thirty paired gains are nonzero, all positive; the mean gain is 0.94 percentage points. The exact two-sided p value is 0.0625 over 32 sign assignments, versus historical asymptotic Wilcoxon 0.0431 and paired t 0.0635. Both Holm-adjusted budget-24 p values are 0.3281. Only budget 6 remains below 0.05 in that family. The paper reports this sensitivity, rather than selecting the favorable unadjusted procedure. The retained remediation image's left objective curves are illustrative, not measured learning or equilibrium evidence; its caption now makes that distinction and clarifies weighted budget units.

The latest completed suite has 66 passing tests. `ARTIFACT_AUDIT_PREPATCH.json` checks eight study manifests, five existing matrix/source sets, generated table inputs, privacy in the new raw dataset, and preservation of the document class, single-column styling, title, seven main section titles, original static implementation files and existing figure bytes. The manuscript date is updated to November 2026. The newest PDF must be rebuilt again after the ongoing current-patch results are integrated.

The official July prerequisite has passed post-reboot verification at build 17763.7558. The October package has a valid Microsoft signature, recorded CBS S_OK, a KB5126651 hotfix entry and a pending reboot. A normal controlled reboot was scheduled; build 17763.9376 is not claimed until the post-reboot readiness guard passes. Two current-patch protocols, with UPN-only and UPN-plus-SID-URL requests, are frozen as `independent_2019_current_patch_*_protocol_v4.json`. The v4 follow-up also restores/read-backs the template and refreshes the CA before authentication, and repeats actual Certipy enumeration after rollback. Earlier unused local protocol versions remain as planning history.
