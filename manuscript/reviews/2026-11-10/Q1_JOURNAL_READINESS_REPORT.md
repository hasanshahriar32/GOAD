# Q1 submission readiness: current evidence assessment

The manuscript now has a matched relational baseline, a prospective new-forest workload, an independently checked collection-cost pilot and a corrected full-size remediation rerun. These substantially strengthen its focused evidence-assurance contribution. This is a scientific assessment rather than a journal acceptance forecast. JCR and SJR quartiles must be checked for a selected journal, category and year; neither system grades a manuscript.

The newest completed-cycle report is [RESEARCH_GAP_CLOSURE_RESULTS.md](../../../research_notes/2026-11-10/RESEARCH_GAP_CLOSURE_RESULTS.md). The earlier detailed record is [LIVE_RESEARCH_AND_NOVELTY_UPDATE.md](../../../research_notes/2026-11-10/LIVE_RESEARCH_AND_NOVELTY_UPDATE.md). The earlier [component-study report](../../../research_notes/2026-11-10/Q1_GAP_CLOSURE_CONTINUATION.md) and [initial constraint confirmation](../../../research_notes/2026-11-10/RESEARCH_DEVELOPMENT_REPORT.md) remain relevant for their frozen studies. Their earlier lists of unperformed live work are superseded by the completed work below.

| Scientific question | Evidence now available | Assessment |
|---|---|---|
| Can a captured certificate be linked to an actual privileged use? | Four final 12-trial matrices plus a prospective 24-certificate cohort: 66 successful cases, 13 administrative uses and six certificate-bound rejections; CA/public-certificate/KDC/SID checks. All 24 transfer leaf signatures also verify. | Substantially strengthened in controlled laboratories. Eighteen missing CA exports use a transparent later-snapshot supplement. |
| Does the tested enabling bit matter under matched inputs? | Nine supported matched blocks across the two older environments and current-patch SID-URL form; identical signed administrative CSR/key within each block/form, policy equality and restored state. | Conditional privileged-use contrast supported; current-patch UPN-only blocks do not produce that privileged outcome. |
| Are comparisons actual third-party executions? | Actual Certipy 5.0.4 enumeration and three upstream Sigma rules through pySigma/SQLite in all 48 final trials; 24 additional postrollback scans. | Completed for configuration-risk tasks. Full SIEM/provenance-system comparisons remain distinct. |
| Are current patch semantics covered? | Signed update installation, post-reboot build 17763.9376, two 12-trial request-form matrices. UPN-only: six self uses and six rejections. SID-URL: nine self uses and three administrative uses. | Executed and independently adjudicated. All 24 postrollback scans cease flagging tested-template ESC1, including before the three administrative uses. This covers a measured build and configuration, not every modern deployment. |
| Is gating a demonstrated general shortcut cure? | New matched augmentation audit, 6,000 verified checkpoint predictions, corrected deep-path labels. | No. The current gate misses deep positives and does not outperform the augmentation-matched additive arm in pooled accuracy. |
| Does the static experiment validate the literal bilinear formulation? | Explicit implementation audit distinguishes feature-channel sigmoid from general bilinear edge scoring. | Implemented and independently checked: 5,100 labels and 10,800 held-out predictions on typed family-disjoint inputs. It establishes no classification gain over matched additive attention. |
| Is interdiction optimal or an equilibrium solver? | Exhaustive 60-case comparison/6,113 feasible subsets, plus a metadata-preserving rerun of all 120 original graph/budget instances and 11,100 independent reachability checks. | No. The evaluated policy is heuristic; metadata is preserved in the corrected reference, which remains suboptimal in some cases. |
| Does the cone speed ratio preserve the same task? | The historical cone drops queried pairs; a new path-preserving projection retains every pair and its possible paths. | Historical 1,246x ratio cannot support an equal-task acceleration claim. Repeated equal-task measurements retain all pairs and include projection cost: median ratio 7.54 at 5,000 actual nodes; 45 timing pairs and solver outcomes verified. |
| Is the novelty new CA/KDC correlation or a new graph-complexity result? | Closest provenance, uncertain-query, temporal-constraint, entity-resolution and vendor detection work checked. | Those constituent ideas predate this work. The candidate contribution is certificate-specific evidence contracts and controlled evaluation. |
| Are reported costs operationally meaningful? | Collection command envelopes/offline inference plus a three-pair periodic-collection pilot with 48 verified authentications, CPU, RSS and retained checkpoints. | Actual pilot cost measured: paired median client-envelope increases of 48.6–100.3 ms. Lifetime/high-load/production bounds remain outside the evidence. |

The best submission direction centers the certificate-evidence problem and its falsifiable contracts. Broad GNN superiority, universal attack detection, causal attribution from time alone, and optimal autonomous remediation would overstate the artifact. Current revisions retain the article's styling, title, section structure, figures and layer count while making the scientific claims match the evidence.

Current-patch validation, literal bilinear implementation, stronger whole-family splits, and explicit false-order/correlated-source controls now have executed evidence. The matched identity-contract, prospective-transfer and collection-cost questions now have completed evidence. The findings below distinguish those completed studies from broader unmeasured deployment claims and journal-fit decisions.

## What the new current-patch experiment establishes

The measured system is Windows Server 2019 build **17763.9376**, with KB5126651 installed, no pending servicing reboot, running KDC/CA services, enabled Defender, and an ordinary enroller. No compatibility override was introduced. Microsoft documents both [strong-binding enforcement](https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers) and the [SID-URL mapping format](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-pkca/e8fd2c1d-50d3-493a-9b58-5e453850c567); neither is a new technique claimed by this paper.

| Current-patch form | Successful self uses | Successful Admin uses | Exact-certificate KDC rejections | Postrollback tested-template ESC1 findings |
|---|---:|---:|---:|---:|
| UPN only, 12 trials | 6 | 0 | 6 | 0/12 |
| UPN and matching SID URL, 12 trials | 9 | 3 | 0 | 0/12 |

All successful outcomes match certificate bytes, CA row, issuance event and successful KDC principal/SID evidence. All six rejections match public certificate serial and thumbprint to KDC System event 39. The enabled UPN-only legitimate-self controls also fail; reporting them prevents treating every authentication failure as evidence of prevented malicious behavior.

The postrollback observation is useful because it measures two different states: the current template is no longer flagged as ESC1, while a previously issued SID-URL certificate can still authenticate as Administrator. It supports investigating issuance and use together. It does **not** imply Certipy is wrong about its configuration task, or that an existing provenance system cannot produce the same investigation result.

The identity reference was frozen before these collections and remains unchanged. It links all 18 successful current-patch authentications, including the three privileged SID divergences. Outcome labels and certificate/CSR bytes are excluded from its inference inputs. The six rejected authentications are outside its successful-use linkage denominator. This is prospective evidence for that narrowly defined detector, with postcollection evidence completion explicitly recorded.

The collector's no-event System query skipped subsequent CA exports in 18 trials. Original trial files and manifests are retained. A separately hashed, later read-only CA snapshot supplies the missing exports only in temporary verification views, with provenance recorded per trial. It cannot establish past policy state or audit-clock calibration. Three regression tests check evidence preservation, tampering and forest mismatch; an actual empty-query control verifies the collector correction. The lab was shut down after baseline-flag readback and its writable disk preserved.

The old and updated workflows differ in postrollback CA refresh and enumeration. Signed request bytes and keys are matched within each block and form, but not between forms. Therefore this is controlled within-form evidence and observed cross-form behavior, rather than a pure patch-only or same-key cross-form causal experiment.

## Novelty assessment against the closest research questions

| Proposed contribution | What predates this work | Defensible added value | Remaining reviewer concern |
|---|---|---|---|
| Certificate-specific provenance | CA/KDC correlation, AD provenance and certificate abuse are established. | Explicit issuer namespaces, conjunctive identifiers, incomplete candidates, revision, and byte/CA/KDC-grounded controls. | Must show why these contracts change investigative decisions beyond a competent evidence join. |
| Uncertain and conflicting evidence | Possible/certain answers, temporal constraints and entity resolution are established. | Reproducible ADCS-specific failure cases, fault units, candidate coverage and false-definite trade-offs. | The synthetic distribution is designed, and trusted raw sources remain assumptions. |
| Current-patch rollback experiment | Strong binding and SID-URL behavior are documented. | Matched inputs, legitimate-use controls, actual external outputs and postrollback certificate-use evidence. | Three blocks per form, one updated forest; not a new bypass or prevalence estimate. |
| Literal bilinear architecture | Attention, gates and residual paths are established. | Faithful trainable realization and matched controls expose a negative result rather than an implementation gap. | No observed classification benefit; it cannot carry a broad architecture-superiority claim. |
| Budgeted remediation | Directed multiway cut and network interdiction are established. | Same-query path-preserving projection and exact small-instance heuristic audit. | Assigned disruption costs and heuristic gaps prevent business-impact or equilibrium claims. |

The strongest publication argument is a security measurement and evidence-assurance contribution. The architecture and optimization parts currently provide supporting analysis and falsification. Presenting all three as independently superior new methods would be difficult to defend. Keeping the existing title and styling is compatible with making this contribution hierarchy explicit.

## Completed gap-closure cycle and contribution hierarchy

The new [detailed results](../../../research_notes/2026-11-10/RESEARCH_GAP_CLOSURE_RESULTS.md) close several concrete local research gaps:

1. **Competent relational identity baseline:** 1,470 histories and 5,423 evaluated prefixes, with 16,269 independently checked predictions. Guarded SQLite and the reference agree throughout; both retract 225 provisional links. Sixty chronology-negative controls and 60 consistently forged histories expose information/trust boundaries. No unique reasoning-primitive or full HADES execution claim follows.
2. **Prospective identity/workload transfer:** a new domain SID, hostname and CA, two templates and two ordinary enrollers. Twenty-four distinct certificates yield 20 self uses and four administrative uses; the unchanged detector links all 24. Four submission envelopes overlap in every batch. The OS image family is shared, so this demonstrates namespace/workload transfer rather than broad OS diversity.
3. **Actual collection-cost pilot:** three paired arm orders, eight legitimate authentications per arm, all 48 matched to exact certificate/KDC records. Periodic export/reference updates increase median client process envelopes by 48.6, 80.0 and 100.3 ms. Python RSS is 56.5–59.5 MiB, excluding children and VM. A separate postmeasurement barrier fixes the initial outcome-export undercount without changing the timing denominator.
4. **Cryptographic outcome checks:** all 24 transfer leaf signatures and the new root self-signature verify under a separately captured public CA certificate. Later observed NTAuth membership and historical KDC acceptance are reported separately.
5. **Corrected primary remediation evidence:** all historical adaptive/greedy percentages reproduce, but preserving metadata changes nine objectives and 24 cut counts. The primary table now uses the corrected implementation. At budget 24, disconnection remains 98.5%, with 5.7 rather than 6.0 mean revoked edges; the corresponding edge-count reduction is 47.7%. Corrected exact-rank/Holm results support budget 6 under both procedures and budget 18 under exact signed rank only.

The defensible contribution is the certificate-specific evidence contract, controlled security measurement, prospective transfer and auditable failure boundaries. Literal bilinear superiority, globally optimal remediation, enterprise business-impact reduction and a new strong-binding bypass remain unsupported. Those unsupported claims should not be used to market the submission.

The full external-system boundary remains explicit. HADES describes authentication/logon correlation and Windows Security/Sysmon provenance in its [published implementation section](https://publikationen.bibliothek.kit.edu/1000185068/174692774). The older 48 trial exports contain 4,780 filtered Security events; the new six batch exports add 4,544 events including process creation and service tickets. They still lack complete Sysmon/file/socket provenance. A claim of full-PIDS superiority would require executing the relevant system with compatible telemetry. The completed relational comparison answers the narrower identity-contract question.

Broader organization/OS transfer, sustained high-load collection, lifetime retention and analyst productivity are further studies if those deployment/utility claims are pursued. They are not results implied by the current laboratory evidence. Final author review, factual submission declarations, data-sharing permissions and an immutable release remain necessary publication work. No public release or submission has been made.

## JCR and SJR interpretation

JCR's JIF quartile compares a journal within a Web of Science category; Q1 is its highest quartile. A journal can occupy different category positions. See [Clarivate's JCR guidance](https://clarivate.libguides.com/jcr). SCImago separately groups journals by SJR within subject categories using Scopus-sourced data; see [SCImago's FAQ](https://www.scimagolab.com/faqs-2/). A Q1 label in one system or category does not establish Q1 in the other. Record journal title, ISSN, metric system, category, data year and retrieval date when selecting a target.

Neither ranking defines a minimum number of experiments, a manuscript novelty score, or an acceptance probability. My assessment is that the empirical foundation is materially stronger and a focused submission is plausible, while claiming all research gaps are closed would exceed the available comparisons. Journal fit and external review remain decisive.

## Verification and evidence pointers

- [Current-patch detailed findings](../../../research_notes/2026-11-10/CURRENT_PATCH_FINDINGS.md) records the outcome interpretation and reproduction paths.
- [Validation summary](../../../research_notes/2026-11-10/VALIDATION_SUMMARY.json) records the final test/build and integrity results.
- The existing single-column style, title, seven-section hierarchy, original figures and original static implementation remain preserved.


Final local validation for this cycle: **78 passing tests, 38 compiled pages, no unresolved citation/reference markers**, and successful study/source/privacy/style integrity checks. New tables are visually checked on pages 28 and 30. Research VMs and temporary sleep inhibitors are stopped; private lab disks remain preserved. See the linked validation summary for exact hashes and retained compiler warnings.
