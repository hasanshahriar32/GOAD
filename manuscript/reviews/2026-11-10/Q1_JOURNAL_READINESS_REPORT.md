# Q1 submission readiness: current evidence assessment

The manuscript has materially stronger evidence, but it is not yet defensible to declare every Q1 submission gap closed. This is a scientific assessment rather than a journal acceptance forecast. JCR and SJR quartiles must be checked for a selected journal, category and year; neither system grades a manuscript.

The detailed record is [LIVE_RESEARCH_AND_NOVELTY_UPDATE.md](../../../research_notes/2026-11-10/LIVE_RESEARCH_AND_NOVELTY_UPDATE.md). The earlier [component-study report](../../../research_notes/2026-11-10/Q1_GAP_CLOSURE_CONTINUATION.md) and [initial constraint confirmation](../../../research_notes/2026-11-10/RESEARCH_DEVELOPMENT_REPORT.md) remain relevant for their frozen studies. Their earlier lists of unperformed live work are superseded by the completed work below.

| Scientific question | Evidence now available | Assessment |
|---|---|---|
| Can a captured certificate be linked to an actual privileged use? | Four final 12-trial matrices, 42 successful exact-certificate authentications, nine administrative uses, six certificate-bound rejections; CA/public-certificate/KDC/SID checks. | Substantially strengthened in controlled laboratories. Eighteen missing CA exports use a transparent later-snapshot supplement. |
| Does the tested enabling bit matter under matched inputs? | Nine supported matched blocks across the two older environments and current-patch SID-URL form; identical signed administrative CSR/key within each block/form, policy equality and restored state. | Conditional privileged-use contrast supported; current-patch UPN-only blocks do not produce that privileged outcome. |
| Are comparisons actual third-party executions? | Actual Certipy 5.0.4 enumeration and three upstream Sigma rules through pySigma/SQLite in all 48 final trials; 24 additional postrollback scans. | Completed for configuration-risk tasks. Full SIEM/provenance-system comparisons remain distinct. |
| Are current patch semantics covered? | Signed update installation, post-reboot build 17763.9376, two 12-trial request-form matrices. UPN-only: six self uses and six rejections. SID-URL: nine self uses and three administrative uses. | Executed and independently adjudicated. All 24 postrollback scans cease flagging tested-template ESC1, including before the three administrative uses. This covers a measured build and configuration, not every modern deployment. |
| Is gating a demonstrated general shortcut cure? | New matched augmentation audit, 6,000 verified checkpoint predictions, corrected deep-path labels. | No. The current gate misses deep positives and does not outperform the augmentation-matched additive arm in pooled accuracy. |
| Does the static experiment validate the literal bilinear formulation? | Explicit implementation audit distinguishes feature-channel sigmoid from general bilinear edge scoring. | Implemented and independently checked: 5,100 labels and 10,800 held-out predictions on typed family-disjoint inputs. It establishes no classification gain over matched additive attention. |
| Is interdiction optimal or an equilibrium solver? | Exhaustive 60-case small-graph comparison and independent check of 6,113 feasible subsets. | No. The evaluated policy is heuristic; metadata is preserved in the corrected reference, which remains suboptimal in some cases. |
| Does the cone speed ratio preserve the same task? | The historical cone drops queried pairs; a new path-preserving projection retains every pair and its possible paths. | Historical 1,246x ratio cannot support an equal-task acceleration claim. Repeated equal-task measurements retain all pairs and include projection cost: median ratio 7.54 at 5,000 actual nodes; 45 timing pairs and solver outcomes verified. |
| Is the novelty new CA/KDC correlation or a new graph-complexity result? | Closest provenance, uncertain-query, temporal-constraint, entity-resolution and vendor detection work checked. | Those constituent ideas predate this work. The candidate contribution is certificate-specific evidence contracts and controlled evaluation. |
| Are reported costs operationally meaningful? | Collection command envelopes and offline identity inference measured separately. | Better grounded; continuous polling, retention and production interference are not established. |

The best submission direction centers the certificate-evidence problem and its falsifiable contracts. Broad GNN superiority, universal attack detection, causal attribution from time alone, and optimal autonomous remediation would overstate the artifact. Current revisions retain the article's styling, title, section structure, figures and layer count while making the scientific claims match the evidence.

Current-patch validation, literal bilinear implementation, stronger whole-family splits, and explicit false-order/correlated-source controls now have executed evidence. The remaining scientific priority is demonstrating additional investigative value against matched provenance tasks under a justified deployment contract. The findings below explain what the new work closes and what still determines journal fit.

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

## Remaining research priorities, ordered by scientific value

1. **Matched provenance comparison.** Define the same input fields and exact issuance-to-use output for this reference and the closest reproducible external system. Record telemetry requirements, abstentions, conflicting cases and revisions. Actual Certipy/Sigma execution closes the configuration-baseline gap, but cannot substitute for this task. HADES/Splunk platform superiority is currently unmeasured.
2. **Independent transfer workload.** Freeze the detector and evidence mapping, then collect a second updated forest or independently held workload with multiple issuers/templates, concurrent requests, renewal/reused keys and delivery loss. Evaluate complete investigative episodes, not individual correlated event rows. Repeating one forest cannot replace this transfer check.
3. **Continuous collection cost.** Measure end-to-end export delay, retained history, wall-clock throughput, process RSS and authentication interference during a sustained benign workload. Existing command envelopes and offline milliseconds answer narrower cost questions.
4. **Analyst or policy utility.** Measure whether explicit uncertainty reduces incorrect investigative conclusions or remediation errors on a matched task. More graph-classification accuracy is not evidence for this claim.
5. **Author and artifact review.** Review factual declarations and data-sharing permissions, select a journal/category/year, and prepare an immutable release with dependencies and licenses. No public release, author approval or submission is implied by the local files.

These are concrete experiments or decisions, not requests to redesign the manuscript. Negative findings already measured should stay in the paper; removing them would not close these gaps.

The external-comparison input boundary has now been checked. HADES describes authentication/logon correlation and process/system provenance using Windows Security and Sysmon telemetry; see its [published paper, implementation section](https://publikationen.bibliothek.kit.edu/1000185068/174692774). Our [saved input audit](../../../research_notes/2026-11-10/PROVENANCE_INPUT_COVERAGE.json) covers 48 trial files and 4,780 recorded Security events. Those filtered exports contain 4624, 4768, 4886, 4887, 4898 and 5136, but no collected 4769, process-creation 4688 or Sysmon channel. This is a dataset boundary, not evidence those activities did not occur. A fair full-system comparison therefore requires additional telemetry or a deliberately restricted common subtask. Emulating a few published predicates would need to be labeled a proxy, rather than an executed HADES baseline.

## JCR and SJR interpretation

JCR's JIF quartile compares a journal within a Web of Science category; Q1 is its highest quartile. A journal can occupy different category positions. See [Clarivate's JCR guidance](https://clarivate.libguides.com/jcr). SCImago separately groups journals by SJR within subject categories using Scopus-sourced data; see [SCImago's FAQ](https://www.scimagolab.com/faqs-2/). A Q1 label in one system or category does not establish Q1 in the other. Record journal title, ISSN, metric system, category, data year and retrieval date when selecting a target.

Neither ranking defines a minimum number of experiments, a manuscript novelty score, or an acceptance probability. My assessment is that the empirical foundation is materially stronger and a focused submission is plausible, while claiming all research gaps are closed would exceed the available comparisons. Journal fit and external review remain decisive.

## Verification and evidence pointers

- [Current-patch detailed findings](../../../research_notes/2026-11-10/CURRENT_PATCH_FINDINGS.md) records the outcome interpretation and reproduction paths.
- [Validation summary](../../../research_notes/2026-11-10/VALIDATION_SUMMARY.json) records the final test/build and integrity results.
- The existing single-column style, title, seven-section hierarchy, original figures and original static implementation remain preserved.
