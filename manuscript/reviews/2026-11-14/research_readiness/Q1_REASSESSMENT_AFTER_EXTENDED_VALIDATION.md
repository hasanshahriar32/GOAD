# Q1 readiness reassessment after extended validation

Date: 14 November 2026. Scope: current 23-page manuscript, revised contract and contribution statements, extended-validation results, reproducibility records, and earlier comparative literature review. The PDF hash matches the extended-validation snapshot: `c4407e682656a34993e69b3e0cf231a5591d4e8e536dcd6061fc9e5b46ef526c`. This is a reassessment of completed results; experiments were not rerun unnecessarily during the review. No manuscript changes were made.

## Verdict

**Substantially stronger research credibility; still not a confident Q1 submission recommendation in its current form.** The most plausible route is a focused applied-security paper on certificate evidence requirements and revisable investigation. A claim of superior graph learning, robust repair or adaptive remediation is not supported by the comparative results.

The recent work closes several implementation and comparison gaps. It does not automatically increase novelty: stronger controls also show that some complex components offer less benefit than simpler alternatives. That is valuable scientific evidence, but it changes what the paper can contribute.

This assessment is a reviewer-style judgment, not an official journal score or acceptance probability. Q1 is a journal/category/year ranking; no paper becomes Q1 by passing a fixed number of tests.

## What changed since the earlier review

| Criterion | Current assessment | Evidence and remaining boundary |
|---|---|---|
| Problem relevance | Strong | Post-rollback certificate use and incomplete evidence are concrete security investigation problems |
| Claim alignment | Much improved | Revised title and current-method algorithm now emphasize certificate lineage |
| Implementation reliability | Strong within tested scope | 78 tests; independently checked labels; full checkpoint prediction reproduction |
| Reproducibility | Strong local artifact | Fresh-extraction checks pass; revision supplements remain separate from public frozen DOI |
| Equal-input comparisons | Materially improved | New five-method factorial experiment and 35,055 incremental reference/SQL comparisons |
| Uncertainty characterization | Improved | Candidate-size distributions, fault conditions, retractions and illustrative loss threshold reported |
| Core novelty | Promising but incremental | Security contract/application may be publishable; underlying matching and uncertainty techniques are established |
| Empirical superiority | Mixed, task-dependent | No method dominates all measured attribution outcomes |
| External validity | Still limited | 72 existing laboratory certificate cases; new work adds synthetic cases, not independent deployments |
| Operational performance | Partially established | Current-reference snapshots and serial replay measured; longer Windows collection remains untested |
| Investigator usefulness | Not established | No measured improvement in analyst conclusions, effort or harmful overconfidence |
| Learning novelty | Unsupported as a positive advance | Literal gating and additive attention have identical classifications |
| Remediation novelty | Weaker after stronger comparison | Two-edge lookahead matches 56/60 optima versus adaptive 43/60 |
| Narrative focus | Still needs substantial editing | Long learning/optimization material precedes or competes with the central evidence contribution |

## What the new results actually establish

The new generator supplies 432 designed identity histories, 864 stages and 4,320 method/stage predictions. It is separately implemented, but remains an author-designed synthetic experiment. It is not independent organizational validation.

The current reference and guarded SQL both correctly resolve 260 cases and retain the true candidate in 404. Strong SQL resolves 292 and retains 292. Ignoring exports resolves 176 and retains all 432; one-record repair resolves 131 and retains all 432. No method makes a wrong resolved claim in this grid. Reference candidate loss under corrupt optional evidence is therefore a real observed weakness, and the repair method's extra complexity is not justified by better certain-resolution coverage here.

The incremental study demonstrates consistent identity answers through delayed enrichment, duplicate delivery, recovery and conflict/retraction. Its 35,055 checks are repeated prefix decisions across nine streams, not 35,055 independent attack trials. The measured implementation costs are useful, but compare this reference and this SQLite implementation on one serial identity workload. They do not prove a general graph-versus-database advantage or production throughput.

The stronger optimization baseline is a decisive scope signal: two-edge lookahead reaches the exact count in 56/60 small instances, adaptive in 43/60 and static greedy in 21/60. This does not prove lookahead is best on large graphs or under equal compute budgets. It does prevent presenting the adaptive policy as the demonstrated leading method on the exact benchmark.

## The remaining central reviewer objection

“Why is this an important new security contribution beyond a carefully specified, guarded correlation system?”

The paper now answers how the system operates and where its assumptions fail. It still needs a stronger answer about what meaningful investigation outcome becomes possible, safer or cheaper because of the contract.

SQL equivalence is not a reason to reject a security contract. It supports implementation portability. But the paper must locate novelty in the evidence requirements, failure taxonomy, verified application or measured investigative consequences. It cannot rely on a graph representation, standard interval constraints, a sigmoid gate or a renamed interdiction problem as sufficient novelty.

The current loss sensitivity is informative: conservative overlap attribution becomes preferable under the stated simplified loss only when a false definite claim costs over approximately 3.98 missed definite claims. Those costs were not elicited, and candidate-review/time costs are omitted. This illustrates when benefit might occur; it does not demonstrate real-world benefit.

## Changes that should precede submission

1. **Concentrate the main paper on the evidence contribution.** Move or substantially shorten the learning theorem/negative experiment and the generic interdiction proof. Retain the negative findings and reproducible details in supplementary material. The main narrative should make the method, failure modes and practical meaning apparent before extended supporting mathematics.
2. **Demonstrate usefulness with an independent evidence source.** Prefer an independently configured live environment with realistic benign workflows, or independently adjudicated operational cases. Measure whether explanations change decisions correctly. A well-designed analyst study is one option, not a mandatory requirement of all Q1 journals.
3. **Evaluate authorized and ambiguous behavior.** Include delegation, enrollment-on-behalf, renewal/key reuse, competing issuances and concurrent maintenance. Certificate identity and privileged authentication are not sufficient labels for malicious intent.
4. **Measure the current collection pipeline over a meaningful duration.** Quantify resource use, missing/late observations, backlog, retention and recovery. The new snapshot and replay experiments narrow this gap but do not close it.
5. **Choose an appropriate evidence claim, not a better-looking score.** If simpler methods remain preferable, publish the security lessons and design boundaries. Do not tune repeatedly until a favored component wins, remove unfavorable baselines or add complexity solely to claim novelty.
6. **Finish submission-specific details.** Verify the target's current category/year ranking, length and supplementary-material rules. Archive/version the revision-specific artifacts appropriately when preparing the final submission. The existing public DOI must not be described as containing later experiments it does not contain.

These are submission recommendations for this paper, not universal Q1 requirements. There is no mandatory enterprise sample count, production deployment or participant count. The required evidence depends on the scope of the final claim.

## Journal fit

**Computers & Security remains the most plausible initial target to investigate** for a focused certificate-investigation paper. The official indexed SCImago record reports SJR 2025 = 1.598, Q1. Its profile covers computer-security research and practical security work. This is a journal-level ranking observation, not an acceptance prediction. [Official SCImago record](https://www.scimagojr.com/journalsearch.php?clean=0&q=28898&tip=sid).

**IEEE TDSC remains a stretch target in the current state.** Its systems-security scope is relevant, but the core methodological/empirical advance needs to be more compelling relative to closely related investigation research. This is my assessment of this manuscript, not a ranking inferred from test counts. [IEEE scope description](https://cybersecurity.ieee.org/read/).

Official JCR category/year eligibility was not authenticated in this review. Third-party JCR claims should not be treated as a verified official record. If both JCR and SJR Q1 are required, confirm each separately through institutional JCR access and SCImago before target selection. No current dual-Q1 status is certified here.

## Decision

- **Ready for supervisor/coauthor scientific review:** yes.
- **Ready for a focused revision and targeted external expert feedback:** yes.
- **Ready to claim broad method superiority or deployment effectiveness:** no.
- **Would I recommend submitting this exact 23-page version to a selective Q1 security journal today?** No; the contribution remains diluted and practical significance is insufficiently demonstrated.
- **Is a Q1 publication path still plausible?** Yes, through a focused evidence-contract or empirical-security paper with convincing independent/usefulness evidence. More repetitions of the same synthetic experiments alone are unlikely to resolve the central objection.

The quality of the evidence and honesty of the manuscript have improved. The next priority is to establish the importance and usefulness of the central contribution and reduce the prominence of unsupported auxiliary novelty claims.
