# Q1 research gap closure: component studies and manuscript integration

Workspace: `/home/m4x1d/Desktop/GOAD`  
Date: 10 November 2026  
Primary artifacts: `thesis_research/results/lineage_constraints/2026-11-10/robustness/`, `live_operation_order.json`, and `published_rule_proxy.json`.

## Assessment

The work now has a better specified research problem, two implemented reasoning components, an independently audited second synthetic generator, a controlled operation-order result, and evidence tables integrated into the current manuscript. The title, page style, model depth, layer structure, and static/provenance/interdiction architecture are retained.

This closes implementation and reporting gaps. It does **not** establish general novelty or Q1 submission readiness. The most important new negative finding is that the bridge-budget method does not beat a simple optional-export ablation on the new grid. The most useful positive finding is that an explicitly observed order channel can recover temporal certainty without an assumed cross-host clock alignment, including in the controlled pilot. The assumptions and instrumentation cost of that channel now need independent validation.

## 1. Closest primary sources checked

| Source | What it already establishes | Appropriate boundary for CertGraph |
|---|---|---|
| [Dechter, Meiri and Pearl, Temporal Constraint Networks, 1991](https://www.sciencedirect.com/science/article/pii/0004370291900066) | A formal and algorithmic basis for temporal difference constraints | The new solver is an established reasoning component, not a new generic temporal algorithm. |
| [Amarilli et al., TIME 2017](https://drops.dagstuhl.de/entities/document/10.4230/LIPIcs.TIME.2017.4) | Possible/certain query answers with partially ordered information | Possible/definite reasoning and partial order alone are not original contributions. |
| [Fagin et al., KR 2023](https://arxiv.org/abs/2303.07469) | Entity resolution and query answering with conflicting attribute values | Certificate-specific fault assumptions and measured practical benefits must distinguish the application. |
| [HADES, published TDSC version identified through its author record](https://arxiv.org/abs/2407.18858) | Whole-network Active Directory provenance; journal reference and DOI are recorded by the authors | It must not be described as a host-only baseline or assumed unable to detect the tested attack without execution. |
| [Heinzl and Nissl, October 2026 SoK preprint](https://arxiv.org/abs/2610.35151) | Explicit analysis of time and evidence assumptions in intrusion detection | This is close conceptual prior work and is cited as a preprint, rather than an established journal result. |
| [In.security SAN-abuse investigation, 2023](https://in.security/2023/03/02/detecting-ad-cs-subjectaltname-san-abuse-using-kql/) | Existing practical ADCS correlation | Do not claim first CA/KDC event correlation. |
| [Splunk ESC1 analytic, version 10](https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/) | A concrete SAN/principal association query and its required input fields | Compare actual field requirements and tasks; the semantic proxy executed here does not establish Splunk runtime performance. |

These sources constrain the novelty claim more tightly than a comparison only with graph scanners. The credible candidate is an auditable, revisable certificate-attribution contract that makes source faults, temporal ambiguity, and unsupported explanations measurable. A new combination still needs demonstrated benefit; implementation alone is insufficient.

## 2. Optional-source fault reasoning

`repair.py` considers every deletion of at most `k` optional CA bridge records. Raw issuance and authentication records remain trusted. Each hypothesis is evaluated with the earlier unchanged lineage engine.

- The possible set is the union of the retained-hypothesis candidates.
- A certain link requires the same resolved issuance in **every** hypothesis.
- An abstaining or conflicting hypothesis is retained as uncertainty. It is not discarded because another hypothesis yields a convenient explanation.
- Each candidate has an explicit deletion witness.
- Increasing the fault budget cannot shrink the possible set or create a new certain link, because the hypothesis family only grows.
- The explicit hypothesis limit fails visibly rather than silently approximating a guarantee.

**Conditional retention argument.** If the true issuance was captured, raw identity and time bounds are correct, and no more than `k` bridge records are faulty, the hypothesis deleting all faulty records is included. In that hypothesis, truthful remaining identifiers cannot contradict the true issuance, and correct time bounds cannot rule out its real order. The true issuance therefore remains in the union. This does not imply certain resolution, handle missing true issuances, or tolerate forged raw records. A single compromised CA export source may corrupt more than `k` records; record and source fault budgets must not be conflated.

This is an exhaustive reference. With `b` optional records, it examines `sum(comb(b,j), j=0..min(k,b))` hypotheses and recomputes each retained evidence set. It is not a scalable deployment algorithm.

## 3. Exact temporal reasoning

`temporal.py` accepts effective-operation intervals and explicitly supplied inequalities `left - right <= bound`. Exact rational arithmetic and a strictness bit avoid an arbitrary floating-point epsilon. The closure determines feasibility, possible overlap, definite overlap, and inconsistency. It can report one deletion-minimal contradictory constraint set; this is not necessarily a smallest-cardinality explanation.

No edge is inferred by comparing record numbers from different hosts. An order edge is evidence only when the collection protocol or another justified source supplies it. The solver does not authenticate that source. An inconsistent network produces an inconsistency result, not vacuous certainty.

Nine new component tests cover fault-budget failure controls, monotonicity, abstaining hypotheses, order-channel ablations, exact tiny fractional boundaries, contradictory constraints, and 240 independently enumerated strict-order cases. The earlier 25 tests also pass. Two additional published-rule proxy tests cover missing textual SAN, principal normalization, failed KDC outcomes, and unsupported multivalue input.

## 4. Separately frozen factorial study

`robustness_protocol.json` was written before execution and hashes the engine, bridge-budget component, temporal component, and study program. The earlier simulator is not imported. The new generator is structurally independent code, while still a synthetic model authored in this project; it is not an external testbed.

- Seeds: **7103, 8111, 9109, 10111, 11113**.
- 20 histories per cell per seed.
- Identity grid: 1/4/8 certificates, raw-thumbprint omission probabilities 0/0.5/1, and 0/1/2 corrupt target-export records: **2,700 histories**.
- Temporal grid: interval widths 0/2/5, explicit-order observation probabilities 0/0.5/1, and valid/contradictory sensor conditions: **1,800 histories**.
- Four identity methods and three temporal methods yield **16,200 predictions**.
- Inputs, latent truth, predictions, frozen sources, and hashes are saved separately.
- Evaluation execution took approximately **14.67 seconds** on this host, excluding the later independent verifier. This is script runtime, not an ingestion-throughput measurement.

`verify_robustness.py` imports none of the generator, engine, repair wrapper, or temporal solver. It checks latent identity labels, actual injected fault counts, raw-field fidelity, namespace uniqueness, bounds, hashes, saved metrics, and **4,346 within-budget true-link checks**. It independently enumerates the complete bounded temporal assignments for **3,600** method/query combinations. Integer witnesses suffice for this study's integer-bounded, non-strict difference constraints; separate tests use rational grids for strict boundaries.

The verifier passed. Its scope explicitly excludes proving optimality or completeness of repair candidate sets; there is no claim of an independently verified general repair algorithm.

### Identity component results

There are 2,180 true successful observed links across 2,700 histories.

| Method | Retained true candidates | Certain true links | Wrong certain links | Hypotheses |
|---|---:|---:|---:|---:|
| Budget 0 | 1,440 | 721 | 0 | 2,700 |
| Budget 1 | 1,811 | 602 | 0 | 15,300 |
| Budget 2 | 2,180 | 602 | 0 | 49,800 |
| Ignore all optional exports | 2,180 | 1,757 | 0 | 2,700 |

Budgets below two include histories outside their stated fault assumption, intentionally. The budget-two method achieves full possible retention here, but the ignore-all comparator achieves the same retention and substantially better certain-link coverage. The reference therefore **does not demonstrate superiority** on this grid. The data do not justify presenting fault-budget reasoning as a solved novelty result.

One reason is that uncertainty about whether an export should be trusted cannot be removed merely because a different deletion yields an answer. A useful next study would vary independently corroborated exports and missing raw serials/SKIDs, while testing correlated source failures. Such a study is not included in the reported evidence. The original frozen results are retained rather than tuned away after inspecting this negative result.

### Temporal component results

The following valid-sensor groups each contain 300 histories. Cases are paired across methods within a group; the random histories differ across observation-rate groups.

| Order observation probability | True overlaps | Point-time correct/false definite | Interval-box correct/false definite | Interval-and-order correct/false definite |
|---|---:|---:|---:|---:|
| 0 | 122 | 93 / 18 | 54 / 0 | 54 / 0 |
| 0.5 | 148 | 104 / 12 | 59 / 0 | 88 / 0 |
| 1 | 138 | 112 / 11 | 53 / 0 | 138 / 0 |

The order-aware method rejects **all 900 deliberately contradictory sensor controls**. Those controls inject an explicit contradiction; success on them is a contract test, not evidence that arbitrary false order information can be detected. A false but self-consistent order channel can still mislead the solver. Full order observation supplies the queried ordering almost directly; it is a designed upper-bound condition, not a surprising algorithmic discovery or an estimate of enterprise observability.

The useful result is the measured recovery of certainty when an additional justified source is available, together with explicit rejection when constraints cannot jointly hold. Benefits must be stated alongside the extra evidence requirements.

## 5. Clock-independent controlled-operation pilot

`analyze_capture_order.py` verifies the original capture hashes, frozen executed source, successful outcome adjudication, and restoration. It checks the reviewed source's direct synchronous phase sequence: mutation, CSR, submission, rollback.

Five explicit order constraints place the effective mutation before submission, issuance inside synchronous submission, and successful certificate retrieval before rollback. The variables have **no Windows audit timestamp bounds**. Their network supports a definite issuance-between-controlled-operations explanation. Removing any one of these five constraints changes the result to possible overlap.

This closes a narrower gap than repairing clock calibration. It uses the controlled orchestrator as an additional evidence source. It assumes the recorded execution and successful remote responses are truthful and the new certificate was issued in the identified synchronous request. It does not establish the CA's exact template-policy read time, exclude every unseen state change, or prove necessity of the mutation. `clock_alignment_repaired` remains `false`; the earlier audit-clock inconsistency remains in the dataset and paper.

The result is saved in `live_operation_order.json` with analysis-source snapshots and evidence identifiers. It is one controlled case, not a new passive-log accuracy estimate.

## 6. Published analytic semantic proxy

The checked [Splunk analytic](https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/) requires textual SAN/UPN and template attributes in issuance records, a certificate-bearing authentication record, and principal association. `published_rule_replay.py` executes a candidate-set proxy in SQLite across the seven archive files plus the new pilot.

Only the ESC6 archive has an issuance satisfying the textual SAN prerequisite. Literal association returns zero pairs. A separate explicitly adapted short-name normalization produces one association, and its KDC result is the observed failure `0x42`. The successful new pilot has no textual SAN attribute to satisfy the query prerequisite.

The proxy does not reproduce SPL scheduling, macros, default `join max=1` truncation, or multivalue execution; unsupported multivalue cases are listed. The normalization variant is not represented as the published query. [Splunk's join documentation](https://help.splunk.com/en/splunk-cloud-platform/spl-search-reference/10.1.2507/search-commands/join) describes relevant join behavior. These differences prevent claims of exact reproduction, platform accuracy, or runtime comparison. The artifact closes the field-requirement audit gap while leaving the actual external-system benchmark open.

## 7. Manuscript changes within the retained design

The existing article class, title, styling package, seven main sections, figures, model equations, layer structure, and static/provenance/interdiction components are retained. Necessary substantive edits include:

1. Introduced issuer-scoped identity, success checks, possible/definite attribution, revision, source-fault assumptions, and operation-order reasoning in the existing CIPG section.
2. Replaced the unsupported seven-success/24-hour live table with actual archive counts and evidence statuses. Added the exact-certificate pilot with its measured 14-second configured delay.
3. Added three tables generated directly from saved result artifacts. The generator checks input result hashes and records its own source/input/output hashes.
4. Distinguished synthetic stress labels and legacy replay timing from new reference performance, live outcomes, enterprise prevalence, and bounded-memory claims.
5. Added six verified bibliography entries and corrected comparisons with CA/KDC correlation, HADES, uncertain querying, and temporal reasoning.
6. Restricted the gradient theorem to the assumptions needed by its derivative argument: target-independent coefficients, bias-free zero-preserving aggregation, compatible skip maps, and an explicitly controlled non-skip derivative. Corrected a singular-value equality and removed an unsupported generic path-product bound.
7. Corrected the claim that graph disconnection mathematically forces a learned sigmoid gate to zero. With zero embeddings and zero bias, the gate is one half. The model itself is unchanged; its guarantee is narrowed to conditional message attenuation and measured benchmark behavior.
8. Replaced unsupported whole-directory snapshot digest measurements with a scoped indistinguishability argument. Retained the existing mechanism, without inferring whole-database equality from a restored configuration projection.
9. Identified revoked-edge count and assigned disruption costs separately from measured operational disruption, and removed an all-budget significance claim.
10. Updated the draft AI-assistance description to reflect code, analysis, and research-writing assistance. It does not assert that authors have already reviewed material they have not yet reviewed.

The earlier development report describes the original constraint confirmation. This continuation is the authoritative account of the new component studies and manuscript integration. Build and final verification details are saved in `VALIDATION_SUMMARY.json` after checking the finished artifact.

## 8. JCR and SJR readiness

[Clarivate](https://clarivate.com/academia-government/blog/a-primer-on-ties-in-the-jcr/) assigns a JIF rank and quartile per subject category. [SCImago](https://www.scimagolab.com/scimago-journal-quartiles-evaluation/) also describes quartiles by category, using its SJR framework. They are different ranking systems. A journal's category and year must accompany any Q1 statement; a manuscript itself does not receive a JCR or SJR quartile.

No journal-specific current JCR/SJR rank is asserted here. HADES's publication in TDSC is a relevant research comparator, not proof of that journal's current quartile or of acceptance prospects for CertGraph.

| Scientific gate relevant to a strong submission | Current status | Evidence still needed |
|---|---|---|
| Defensible novelty against the closest reasoning literature | Better scoped, open | Show an operational advantage beyond applying known uncertain-query/STN concepts. |
| Precise assumptions and useful falsification controls | Substantially improved | Challenge self-consistent false order channels and correlated source compromise. |
| Reproducible comparisons and independent checking | Implemented for local component studies | Actual external-system runs with matched evidence and documented configuration. |
| Independent empirical generalization | Open | Second patched Windows/CA configuration, independent collection, and repeated benign/attack outcomes. |
| Necessary enabling-state attribution | Open | Effective-policy reconstruction and paired mutation/no-mutation intervention under equivalent enrollment conditions. |
| Operational cost and scale | Open | End-to-end collection/polling cost, record growth, update latency, and source-collection overhead. |
| Static-model and interdiction evidence | Existing results retained; claim scope corrected | Training/configuration audit, stronger topology-family splits and counterfactual baselines, and review of all proof assumptions. |

The project is closer to a defensible research submission, but the evidence does not justify declaring every Q1 gap closed. The next decisive advance is empirical: independently repeat the controlled certificate and benign-maintenance matrix, establish the order channel's real availability and cost, and demonstrate benefit against matched concrete systems. The current artifact makes those requirements explicit and prevents unsupported results from carrying the manuscript's central claims.
