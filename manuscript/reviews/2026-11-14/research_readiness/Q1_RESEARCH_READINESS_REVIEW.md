# CertGraph: research contribution and Q1 submission-readiness review

Review date: 14 November 2026. Reviewed project: `/home/m4x1d/Desktop/GOAD`, specifically the current manuscript, all seven section sources, generated evidence tables, bibliography, release documentation and selected verification outputs. File hashes are in `reviewed_snapshot.json`.

## 1. Recommendation

**Do not submit this version yet as a broad, superior graph-learning/provenance/interdiction system. Develop it into a focused certificate-evidence investigation paper.** There is a credible publication opportunity, but Q1 readiness is not established. The strongest material is the issuer-scoped, uncertainty-aware and revisable certificate evidence contract, supported by controlled Windows outcomes and independently checkable artifacts. The weakest part is the mismatch between that contribution and a title/architecture emphasizing bilinear gating and Stackelberg interdiction.

This is a research assessment, not an acceptance prediction. Q1 journals can accept carefully scoped empirical or systems contributions without a new mathematical primitive. Conversely, combining established techniques, adding proofs and producing attractive figures does not establish novelty. No defensible acceptance percentage can be calculated from this review.

The practical obstacle is no longer an absence of experiments. It is that several completed experiments undermine the claimed importance of particular components:

- Literal bilinear and additive attention have identical held-out classifications; both miss all 450 long-path positive cases per arm.
- Guarded SQL agrees with the identity reference at all 5,423 tested prefixes.
- Ignoring optional bridge exports resolves 1,757 true links certainly, versus 602 for the two-record repair reference, while both retain all 2,180 true links in that component grid.
- The adaptive remediation policy remains heuristic; the budget-24 comparison does not survive the reported multiple-comparison analysis.

These findings should determine the paper's scope. They are valuable results, not defects to hide. The next experiments should establish when the certificate evidence contract improves an investigator's decisions over competent alternatives.

## 2. What Q1 means, and what it does not mean

Q1 is a **journal-level, category-and-year-dependent ranking**, not a certification assigned to an individual manuscript. JCR's JIF quartile and SCImago's SJR quartile use different systems and must be checked separately. A journal may have different quartiles across categories; the release year and metric year also need to be recorded. Clarivate explains category-specific ranking and quartiles in its [JCR glossary](https://journalcitationreports.zendesk.com/hc/en-gb/articles/28351666061457-Glossary) and [ranking guidance](https://clarivate.com/academia-government/blog/a-primer-on-ties-in-the-jcr/).

There is no universal Q1 minimum for sample size, number of figures, percentage improvement, reference count, or amount of mathematics. Useful readiness criteria are originality, importance, technical correctness, appropriate evidence, fair comparisons, reproducibility, clarity, and journal fit. The following judgments use those criteria; they are not official publisher scores.

| Criterion | Assessment of this manuscript | What would change the assessment |
|---|---|---|
| Importance of problem | Strong | Demonstrate the frequency or consequences of ambiguous certificate attribution in a realistic workload |
| Distinct contribution | Promising but insufficiently isolated | A precise claim and measured benefit beyond guarded correlation and established uncertain-query reasoning |
| Technical correctness | Improved, with unresolved exposition/contract issues | Reconcile the five invariants, algorithm, current reference and evaluated assumptions |
| Controlled empirical evidence | Substantial laboratory evidence | Broader independent conditions and a justified operational workload |
| External validity | Limited | Independent administration, policy diversity, longer retention and benign activity diversity |
| Baseline fairness | Better than early versions, still incomplete | Equal-input and equal-resource comparisons on the primary task; real runtime comparison where product claims are retained |
| Statistical interpretation | Some careful corrections; incomplete uncertainty reporting | Cluster-aware intervals, predeclared primary endpoints and task-specific denominators |
| Learning contribution | No demonstrated classification benefit | Either a useful verified cost/coverage advantage or a clearly framed negative result |
| Remediation contribution | Supporting experiment, weak headline novelty | Strong optimization baseline and defensible action/cost semantics |
| Reproducibility | A relative strength | A fresh third-party reproduction and version-matched manuscript/artifact claims |
| Paper coherence | Main weakness | One central research question, with supporting experiments organized around it |
| Presentation | Improved | Presentation is no longer the principal acceptance blocker |

## 3. Evidence reviewed and limits of this assessment

This review inspected the current source and generated tables rather than relying on the older readiness reports. It also read the lineage extension's implementation/evaluation documentation and the frozen release README and reproduction results. A fresh run of `verify_public_certificate_evidence.py` passed against the local public export. The new output, `public_live_recheck.json`, confirms 72 certificate cases, 66 successful uses, 13 administrative uses, six rejections, 72 signed-request checks, 24 transfer leaf-signature checks and 18 later-supplemented CA exports.

This is an offline check of selected exported evidence. It does not authenticate an untrusted collector, recover missing historical policy, or independently repeat the Windows experiments. Existing release records report successful checks of the synthetic, SQL, bilinear and interdiction artifacts; those full studies were not rerun during this review. No new live experiments, retraining, VM operation or public upload was performed.

The literature search covered AD provenance, AD graph hardening, certificate correlation, temporal/incomplete-data reasoning, and recent provenance evaluation research. Primary publisher, author and institutional sources were preferred. Some publisher/ranking pages blocked direct access; accessible abstracts and indexed primary-source records were used where noted. This is a targeted comparative review, not a systematic review or proof that no equivalent work exists. Numerical cross-paper superiority is not claimed.

## 4. Novelty compared with published work

| Prior work | Established contribution relevant here | Consequence for CertGraph |
|---|---|---|
| HADES, TDSC, DOI 10.1109/TDSC.2025.3611866 | AD-specific whole-network provenance and investigation | AD provenance or cross-source investigation alone is not new. Explain what certificate identity and uncertainty semantics add to its different task. |
| Splunk ESC1 authentication analytic | Published 4887/4768 correlation, with textual SAN and principal conditions | Joining issuance and authentication is established. Missing-SAN cases support an input-contract distinction, not a general product defeat. |
| Amarilli et al., TCS 2019 | Possible/certain answers over order-incomplete data | Possible versus definite reasoning is established. The contribution must be the security contract, application, implementation or empirically demonstrated benefit. |
| Goel et al., ACM TELO 2025 | AD hardening using an attacker–defender model and learned/evolutionary policies | Stackelberg framing and AD edge blocking are not sufficient novelty. A task-aligned comparison or a narrower supporting role is needed. |
| Euler, ACM TOPS 2023 | Scalable temporal graph modeling for lateral-movement detection | It provides a graph-security evaluation reference, but solves a different task from the resolved-permission ESC1 predicate. Do not compare raw accuracy across those tasks. |
| Attack structure matters, Computers & Security 2025 | Evaluation of reconstructed attack structure and causal dependencies | Link counts alone do not assess the correctness of the complete investigation explanation. Add a task-appropriate structural evaluation. |
| SecTracer, Computers & Security 2026 | Network-level provenance and root-cause analysis | Multi-host evidence and root-cause claims need a specific distinction; certificate lineage is a narrower potential contribution. |
| Multi-source log semantic analysis, Computers & Security 2025 | Combining application/OS evidence and reducing provenance graphs | Multi-source ingestion and repeated-event compression are not distinctive by themselves. |

Sources for the table: [HADES publisher record](https://xplorestaging.ieee.org/document/11175589), [author manuscript](https://dartlab.org/assets/pdf/hades.pdf), [Splunk analytic](https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/), [TCS journal paper](https://doi.org/10.1016/j.tcs.2019.05.013), [Goel institutional record](https://research-repository.uwa.edu.au/en/publications/hardening-active-directory-graphs-via-evolutionary-diversity-opti/), [Euler publisher record](https://doi.org/10.1145/3588771), [attack-structure paper](https://doi.org/10.1016/j.cose.2025.104578), [SecTracer](https://doi.org/10.1016/j.cose.2025.104760), [multi-source investigation](https://doi.org/10.1016/j.cose.2024.104303). These comparisons concern published descriptions and accessible texts; the systems were not executed for this review.

### 4.1 The most defensible contribution

A useful candidate claim is:

> CertGraph specifies and evaluates a certificate-specific evidence contract that distinguishes supported issuance-to-use identity, possible mutation overlap, definite overlap under stated assumptions, and contradictory or withdrawn explanations when evidence changes.

This is narrower than a new cryptographic primitive, general causal discovery method, or universally better detector. Its potential significance comes from preventing confidently wrong explanations while keeping uncertainty useful and tractable for analysts.

To make this publishable, establish all three points:

1. The evidence failures occur under meaningful ADCS conditions, not only deliberately constructed counterexamples.
2. The contract changes a consequential investigative decision compared with competent equal-input methods.
3. The improvement remains useful after accounting for abstention, candidate-set size, collection cost and delay.

SQL equivalence does not invalidate the contract. It rules out claiming that a graph representation is uniquely necessary for the tested identity projection. The graph may still be a useful explanation interface, but that is a different hypothesis to evaluate.

### 4.2 Components that currently should not carry the novelty claim

**Bilinear gating:** The displayed attenuation proposition follows from multiplying a bounded message by a vanishing scalar. It does not establish that training learns the desired gate. The conditional sensitivity theorem excludes target-dependent attention in its first part, whereas the surrounding GAT equation uses target-dependent attention. Its gradient lower bound can be vacuous when the residual graph term is large. These are limited supporting observations, not a demonstrated solution to shortcut learning. The literal study's equal classifications are decisive for the current empirical claim.

**Interdiction:** Reachability-based defender utility does not change with the follower's choice among surviving paths. The current section already acknowledges this. Calling the implemented sequential heuristic co-adaptive Stackelberg optimization can suggest a strategic result not measured here. Standard hardness and assigned edge costs do not establish a new optimization contribution.

**Compression and projection:** The equal-query projection experiment is more meaningful than the discarded unequal-query headline. However, reachability-based pruning is conceptually straightforward. The 7.54-times result is an instance-specific implementation result, not evidence of a new general algorithmic class. Compression needs query-preservation checks for the current contract, not only reduced element counts.

## 5. Scientific issues that should be resolved before submission

### 5.1 The main method is not described at the same level as the main results — critical

Section IV opens with five invariants and a mutation-taint automaton, while the strongest evaluation concerns a broader reference that retains unmutated issuances, revises links and reasons over uncertain evidence. A short paragraph acknowledges this difference, but the reader still cannot derive the evaluated reference from the presented algorithm.

Provide a single versioned contract: input schemas, identifier normalization, source trust, candidate construction, contradiction handling, strong identity, ordering, overlap, abstention and retraction. Separate certificate identity from mutation context and maliciousness. Give pseudocode for the actual current reference and map each result table to an implementation/version. Keep the older streaming automaton as a clearly separate historical diagnostic or appendix.

### 5.2 The strongest result measures a trade-off, not dominance — critical

The confirmation table gives 107 correct definite overlaps out of 539 true overlaps (about 19.9%), with zero false overlap claims. The point-time method gives 310 correct and 51 false overlaps. Candidate retention of 99.06% and definite-link coverage of 55.82% concern different outcomes; neither is a blanket attack-detection recall.

The central missing question is whether that abstention is operationally worthwhile. Report candidate-set sizes, false definite claims, time to correct resolution, explanation changes, analyst workload and coverage at comparable error tolerance. A method returning every possible certificate can retain true candidates without helping an investigator; candidate retention must be evaluated alongside ambiguity.

### 5.3 Additional evidence and stronger reasoning are confounded — high

The order-aware method receives an extra explicit sensor channel. Its fully observed condition recovers all 138 overlaps in the selected component cell, but that cannot establish an advantage due only to the solver. Compare methods with the same channels; separately measure the marginal value and operational cost of each channel. The orchestrator is a controlled trusted source, not an already-deployed enterprise sensor.

### 5.4 Bridge repair currently loses to a simple ablation — high

The ignore-export comparator is an essential baseline, and the present grid favors it in certain-link coverage. Do not remove it. Construct a prospective mix of useful corroborated exports, irrelevant exports, missing fields, reused keys, issuer collisions and correlated faulty exports. Define source reliability before seeing outcomes. Evaluate whether optional evidence helps enough to justify repair cost. If it does not, simplify the system and publish that design finding.

### 5.5 Live evidence is meaningful but clustered and narrow — high

The 72 certificates are not 72 independent enterprises, attack families or policy environments. Repeated matched requests, shared images and batch/template structure limit the effective diversity. The new forest is useful namespace transfer, not independent organizational replication. The 18 retrospective CA supplements are explicitly documented, which is good, but cannot establish contemporaneous availability or historical template policy.

A stronger study needs independently configured policy conditions, varied benign enrollment workflows, different issuers and renewal/key-reuse behavior, realistic retention gaps, and independently adjudicated outcomes. More identical repetitions alone would not fix external validity. Keep failed attempts in the artifact and specify exclusion rules prospectively.

### 5.6 No realistic false-alert burden has been established — high

An event-level false-positive percentage can look tiny even when many maintenance windows generate alerts. The legacy stream has four false alarms in 50 maintenance windows. Report alerts per administration session, certificate lifecycle, host-day and analyst review unit where meaningful. Include authorized delegation, enrollment agents and legitimate identity differences before interpreting requester/target mismatch as malicious escalation. Splunk's own analytic identifies authorized SAN workflows as a false-positive consideration; that is relevant to the threat model, not an excuse to exclude benign cases. [Published analytic](https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/).

### 5.7 Streaming and storage claims refer to different implementations — high

The 13,192.4 events/s and 6.91 MB figures belong to the legacy implementation. The reference recomputes retained evidence; fault reasoning enumerates deletion hypotheses. The three-pair pilot measures a short collection workload, not sustainable operation. Evaluate the actual current reasoner under growing retained history, burst arrivals, duplicates, delayed exports, restarts and collector outages. Include child processes, CA/DC resource use, end-to-end resolution latency and storage growth. A safe retention policy must explain which future queries it preserves.

### 5.8 Learned filtering needs a purpose — high if retained as a main contribution

For labels defined by a tractable resolved-permission reachability predicate, a neural predictor must justify its use against direct symbolic evaluation. Measure runtime, memory and missed critical cases against BFS/closure on identical inputs. A neural-positive-only verifier demonstrably misses the tested long paths. Adding a fallback may restore correctness, but then measure whether the neural stage saves any work. If it does not, remove it from the operational path and retain the experiment as a negative finding. Avoid tuning until an attractive accuracy number appears.

### 5.9 Remediation does not yet show remediation of an already issued credential — high

Removing an enrollment permission can prevent future issuance without invalidating an existing certificate. That distinction matters because post-rollback certificate use motivates the paper. Demonstrate the scope of each recommended action: prevention of new issuance, interruption of future use, or investigation only. If post-issuance response is claimed, validate the relevant revocation/account/mapping actions and propagation behavior under controlled conditions. Do not infer response effectiveness from path cuts alone.

For the optimization experiment, report the lambda setting, attack-weight role, immutable-edge enforcement and exact objective evaluated. Add an exact solver or certified bound where feasible, dynamic cost-aware greedy, and an appropriate published hardening comparator only when action semantics align. Measure cost sensitivity; assigned weights are not measured business disruption.

### 5.10 Several statements remain broader than their support — medium/high

Targeted examples in the current sources:

- Section II asserts enterprise extraction every 6–24 hours without a supporting source or deployment measurement.
- Section IV describes the 30-minute window as configured in enterprise SOC policies without evidence for that generalization.
- Invariant II says strict monotone progression but uses non-strict inequalities; also, a preceding mutation is not part of every ordinary certificate lifecycle.
- Invariant III treats privilege-increasing identity divergence as a violation without a complete authorized-delegation model.
- The field list includes `nTDSDSOptions`; check its intended directory-object scope rather than treating it as a generic certificate-template ACL attribute.
- The polling discussion says CA database enrichment is strictly required; the defensible statement concerns the selected captured fields and tested enrichment path, not every possible certificate telemetry source.
- The graph-compaction discussion claims preservation of taint information without showing preservation of the current identity, contradiction, ordering and revision queries.
- Scalar gating is written with bold-vector notation and a Hadamard product, while sigma denotes different activations in nearby formulas. Define these explicitly.

These are manuscript/contract audit items, not declarations that every underlying implementation is wrong.

## 6. Statistical and evaluation plan

Use the independent experimental unit appropriate to each result: forest/configuration block for live transfer claims, graph family for learned generalization, graph topology for remediation, and independent stream/run for throughput. Predictions, prefixes and repeated authentications are not automatically independent samples.

Recommended reporting:

- Counts and denominators for identity correctness, mutation overlap and attack intent separately.
- Confidence intervals with clustering or hierarchical resampling where justified; do not pool repeated challenge templates as independent real-world draws.
- Coverage–error and ambiguity–cost curves, including median and upper-tail candidate-set sizes.
- Paired differences and uncertainty for matched method comparisons. Predeclare primary endpoints and the multiple-testing family.
- Per-environment and per-policy results before pooled aggregates.
- Timing distributions, p95/p99 where supported, independent repetitions and resource definitions.
- Negative controls outside assumptions retained separately from within-assumption guarantees.

For scale intuition only: observing zero errors in n independent Bernoulli trials gives a one-sided 95% upper bound of approximately 3/n. At n=300 that is about 1%, and at n=3,000 about 0.1%. These are planning illustrations, not validity claims for the current clustered histories. Choose study size from the error tolerance and clustering structure; there is no Q1-mandated sample size.

## 7. Concrete next-work program

The following are proposed experiments, not completed results. Freeze data-generation assumptions, endpoints, baselines and exclusions before the confirmatory run.

| Priority/work package | Design and comparator | Required output / decision gate |
|---|---|---|
| P0: contract reconciliation | Align the current engine, pseudocode, invariants and evidence versions | Every primary table traceable to a specified method; no unresolved guarantee mismatch |
| P0: claim and reference audit | Replace unsupported global claims; correct metadata; map novelty to prior work | A contribution statement that remains true after reading the negative results |
| P1: equal-input attribution study | Current reference, guarded SQL, strong exact join, interval baseline, ignore-export ablation; same evidence per comparison | A meaningful advantage or a justified simplicity/equivalence conclusion; report ambiguity and latency |
| P1: evidence-value factorial | Missingness, late arrival, issuer/key reuse, false bridges, time uncertainty and sensor availability varied independently | Explain which channels and rules cause the benefit; avoid confounding additional data with a better algorithm |
| P1: independent live replication | New administrative setup/policy mix; frozen engine; benign delegation and concurrent issuance; blind adjudication | Reproduce the central contract benefit outside the development workflow |
| P1: investigator usefulness | Blinded case tasks comparing baseline evidence with CertGraph explanations, counterbalanced order | Correct conclusions, review time and harmful overconfidence; participant design/ethics as applicable |
| P1: current-engine scalability | Growing history and load; indexed SQL comparison; restart, delay and retention tests | Sustainable operating envelope and preservation of needed queries |
| P2: learning decision | Symbolic-only versus neural-plus-complete-fallback; matched tasks/resources | Keep neural stage only if it has measured utility; otherwise report the negative result compactly |
| P2: remediation decision | Exact/bounded solver, dynamic greedy and task-compatible published method; cost sensitivity | Establish quality/runtime trade-offs and prevention versus post-issuance scope |
| P2: explanation structure | Ground-truth certificate lifecycle graphs, wrong-edge/order/retraction measures | Evaluate complete explanations, informed by attack-structure evaluation literature |
| P3: independent artifact reproduction | Fresh checkout/environment and another researcher following only README | Reproduce primary claims without private context; list unavailable deployment evidence |

The most efficient order is P0, then the first two P1 studies. If the reference offers no useful benefit over guarded SQL or simpler contracts at matched error tolerance, an incremental implementation improvement is unlikely to rescue a broad novelty claim. Reframe around the contract and empirical failure taxonomy, or reconsider the contribution before investing in more graph learning.

An analyst study is one way to demonstrate usefulness, not an absolute requirement. A convincing automated decision-cost evaluation or independent operational case study may be a suitable alternative. Similarly, production deployment is valuable but not universally required; a well-designed, diverse controlled study can support a carefully bounded systems contribution.

## 8. Recommended manuscript direction

**Preferred route: certificate-evidence contract and investigation.** Retain the technical results but reorganize their importance. Lead with the real evidence ambiguity and a worked example; specify the contract; show implementation and equal-input alternatives; evaluate correctness, uncertainty, useful resolution and cost; then discuss boundaries. Put the learning negative result and auxiliary interdiction work in shorter supporting sections or appendices if the selected venue permits.

Possible title, subject to author choice:

> CertGraph: Revisable Certificate Lineage for ADCS Investigation under Incomplete Evidence

This is a positioning suggestion, not a claim that renaming creates novelty. An alternative is an empirical paper on ADCS attribution failure modes and verified controls, if the evaluation shows the main insight is what existing evidence can and cannot establish.

Keeping all three components as equal headline contributions is possible only if their integration has measured value. At present, evidence acquisition deliberately bypasses neural predictions, and the remediation experiment is largely separate from certificate-history reasoning. Integration should be demonstrated through a task and ablation, not inferred from a diagram.

A coherent main-text structure would be: problem and competing approaches; evidence/threat model; contract and semantics; implementation; experimental design; identity and temporal correctness; live validation and operational cost; related work and limitations. Preserve the present visual style unless the selected journal requires otherwise. Keep the full correction history in the artifact; present the final method and necessary caveats in the paper.

## 9. Bibliography audit and professor's requirement

The current 32 cited entries comprise **17 journal articles, three conference papers, one book, two technical reports and nine miscellaneous sources**. Journal articles are a narrow numerical majority (53.1%). The three conference entries meet the stated cap of three. Standards, vendor documentation and tool references remain important primary evidence; do not replace them with unrelated journal citations to inflate a percentage.

Two specific actions emerged from the fresh search:

1. **Correct Euler metadata.** The current bibliography gives DOI `10.1145/3588401` and article 32. The publisher and deposited article identify **DOI `10.1145/3588771`, volume 26, issue 3, article 35, 36 pages (2023)**. [Publisher](https://doi.org/10.1145/3588771), [public deposited paper](https://par.nsf.gov/servlets/purl/10440905).
2. **Use the relevant journal version of order-incomplete queries.** Amarilli et al., *Computing possible and certain answers over order-incomplete data*, Theoretical Computer Science 797 (2019), 42–76, DOI **10.1016/j.tcs.2019.05.013**, is a substantive journal source relevant to the present citation. Read the journal version and confirm the exact proposition cited before replacing the TIME entry. This would reduce conferences to two and increase journals to eighteen without adding an irrelevant citation. [Publisher](https://doi.org/10.1016/j.tcs.2019.05.013), [author PDF](https://pierre.senellart.com/publications/amarilli2019computing.pdf).

Consider the recent attack-structure and multi-source investigation papers where they materially change the evaluation/positioning. A further cited-work metadata audit remains worthwhile; the two findings above are not a certification that all other entries are correct. Conference origin does not make a technical result unsuitable for a journal manuscript; the cap is the professor's preference, not a universal Q1 rule.

## 10. Journal fit and ranking verification

**Computers & Security is the most plausible first venue to investigate for the focused applied-security version.** Its recent publications include provenance investigation and evaluation-method papers closely relevant to this problem. This is a fit assessment, not a claim that its acceptance standard is easy. The indexed official SCImago record reports **SJR 2025: 1.598, Q1** and lists Computer Science (miscellaneous) and Law. Direct access was blocked during the follow-up fetch, so a saved category/year record should still be obtained before submission. [Official SCImago record](https://www.scimagojr.com/journalsearch.php?clean=0&q=28898&tip=sid).

**IEEE TDSC is a substantially more demanding stretch target for this manuscript as it stands.** Its official scope includes security mechanisms, evaluation and dependable systems, so topical fit exists. A submission would need a much clearer method contribution and stronger operational validation relative to closely related AD investigation work. [Official scope](https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing), [topic list](https://www.computer.org/digital-library/journals/tq/tdsc-topics).

**ACM TOPS is a topic-fit comparator, not a verified dual-Q1 recommendation in this review.** Euler demonstrates relevant graph-security work there, but no current official JCR/SJR category record was verified for TOPS here. Reputation and quartile eligibility must not be conflated.

| Candidate | Research fit | SJR verification in this review | JCR verification in this review |
|---|---|---|---|
| Computers & Security | Best initial fit for focused certificate investigation | Official indexed 2025 record reports Q1; category-detail capture still recommended | No authenticated official category-year record obtained |
| IEEE TDSC | Strong topic fit; stretch on contribution/evaluation | Not verified from an accessible official record in this review | Not verified |
| ACM TOPS | Relevant security-methods comparator | Not verified from an official record in this review | Not verified |

Before committing to a target, obtain its official JCR profile through the institution and record the **JIF quartile, category and metric year**, separately from the **SJR category and year**. If both are required, both must qualify. Also check current article type, length, supplementary-material, artifact and disclosure requirements. A currently unverified ranking is not evidence that the journal is outside Q1; it is a verification task left open rather than a guessed label.

## 11. Likely reviewer objections and adequate responses

**“Why is this more than a careful SQL join?”** Present the security contract, difficult cases, revision behavior and measurable consequences. A relational implementation can validate portability; do not claim uniqueness of graph execution.

**“Why is gating in the title if it does not improve classification?”** Change the contribution hierarchy or establish a different predeclared benefit. More favorable narrative cannot overturn the current matched experiment.

**“Are 72 certificates enough?”** Explain the mechanism coverage and independent units. Expand missing policy/environment dimensions rather than citing the aggregate as a generalization guarantee.

**“Is the certainty gain just abstention?”** Show error versus coverage, candidate ambiguity and investigation cost at matched evidence access.

**“Does this detect attacks or recognize risky templates?”** Separate configuration, issuance identity, successful authentication, privilege divergence, mutation overlap and malicious intent. Give each its own labels and denominator.

**“Is the provenance cryptographically trustworthy?”** Certificate identifiers do not authenticate audit logs. State which signatures are verified and which source facts are trusted. Do not imply tamper resistance from hashes alone.

**“Does remediation stop the credential already issued?”** Distinguish preventive graph changes from post-issuance response and test any response claim directly.

**“Why should the legacy throughput apply to the current method?”** It should not. Measure the current implementation or keep the legacy measurement clearly supplementary.

## 12. Submission gate

A credible next submission decision should require:

- One central contribution that remains significant after the SQL equivalence and negative learning results are acknowledged.
- A precise current-method specification with all reported guarantees tied to assumptions and implementation versions.
- A task-aligned comparison demonstrating useful investigative benefit, or a compelling empirical result explaining when simpler methods suffice.
- Independent or meaningfully diverse live validation, with benign controls and prospectively defined outcomes.
- Current-engine resource measurements commensurate with the deployment claims.
- Appropriate uncertainty estimates and no pooling of incompatible denominators.
- Correct references, including the identified Euler correction, and an updated prior-work comparison.
- Reproducible primary results and a clear boundary between public verification and trusted collection.
- Verified target-journal scope and required JCR/SJR category-year eligibility.

**Final judgment:** This is a serious, auditable research prototype with useful controlled evidence and an identifiable publication path. It is not presently a convincing three-part novelty paper centered on bilinear gating and Stackelberg interdiction. The strongest route toward a Q1 submission is to make certificate-specific uncertainty and revision the central contribution, demonstrate its practical value over strong simple alternatives, and let the actual results determine which auxiliary components remain.
