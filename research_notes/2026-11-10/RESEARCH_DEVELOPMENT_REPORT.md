# Research development toward a defensible journal contribution

**Workspace:** `/home/m4x1d/Desktop/GOAD`  
**Date:** 10 November 2026 (Asia/Dhaka)  
**Scope:** New method, executed experiments, and research validity. The existing manuscript style, title, layer structure, and architecture are retained; research claims and evidence tables are updated in place. The further component studies and manuscript integration are documented in [Q1_GAP_CLOSURE_CONTINUATION.md](Q1_GAP_CLOSURE_CONTINUATION.md).

## 1. Research question and contribution candidate

The useful question is not whether another graph can join CA and KDC events. That is established practice. The question developed here is:

> When certificate telemetry is incomplete, conflicting, or late, which issuance/use and rollback-window explanations are justified as definite, which remain possible, and when must an earlier conclusion be withdrawn?

The new implementation is under `thesis_research/src/lineage_constraints/`. It adds an experimental evidence-consistent lineage engine, four executed local baselines, a simulator with separately saved latent histories, a complete-tree GOAD reader, an independent result verifier, scientific plots, and isolated lab-restoration tools. It is a substantive extension of the CIPG investigation. A result-to-LaTeX generator now integrates saved evidence tables into the existing evaluation section, without changing the manuscript's style or model architecture.

The proposed contribution combines certificate-specific identity constraints, bounded-time reasoning, explicit possible/definite answers, and revisable provenance. These ingredients individually have prior art. The combined design is a **candidate contribution requiring further validation**, not a certified first result or an assurance of Q1 acceptance.

## 2. Prior work and the actual novelty boundary

| Primary source checked | Existing contribution relevant here | Consequence for this project |
|---|---|---|
| [In.security, 2023](https://in.security/2023/03/02/detecting-ad-cs-subjectaltname-san-abuse-using-kql/) | Practical correlation of CA activity with Kerberos ticket events and principal mismatch | A CA-to-KDC join or SAN mismatch alone cannot carry a strong novelty claim. |
| [Splunk ESC1 authentication analytic](https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/) | Published detection logic joining suspicious certificate issuance and authentication | An empirical comparison should execute concrete queries on the same evidence. This work does not claim to have run Splunk. |
| [HADES](https://arxiv.org/abs/2407.18858) | AD whole-network provenance and investigation | Cross-host AD provenance is already a research area; HADES must not be portrayed as inherently restricted to one host. |
| [Heinzl and Nissl, 2026 SoK preprint](https://arxiv.org/abs/2610.35151) | Explicit analysis of time, delivery, identity, and evidence assumptions in intrusion detection | Clock uncertainty and delivery assumptions need precise treatment; their importance is not newly discovered here. |
| [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280) | Certificate identity and issuer-scoped serial uniqueness | Issuer scoping is required semantics, rather than an independent algorithmic invention. |
| [Microsoft event 4768 documentation](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4768) | Successful and failed ticket-request outcomes and certificate fields | A nonzero result must not be counted as successful certificate use. |

The remaining research space is a specific contract for **revisable certificate attribution across rollback**, evaluated against incomplete identities, reused keys, issuer collisions, timing ambiguity, and late contradictory records. A wider comparison with temporal rule engines and other uncertainty-aware provenance work is still necessary before asserting priority.

## 3. Implemented method

Each immutable observation has a stable record ID, event kind, issuer, optional serial/thumbprint/SKID, a time interval, and authentication outcome where applicable. CA database enrichment is scoped by `(issuer, request_id)`. Conflicting nonempty fields remain visible and block a definitive conclusion; they are not silently overwritten.

The engine rejects a candidate when known identity fields contradict each other or when issuance cannot precede authentication under the supplied clock bounds. An incompletely identified but non-contradicted issuance stays in the possible set. A reusable SKID alone cannot establish a certificate identity. Successful certificate authentication, one strong compatible candidate, and definite temporal order are required for a resolved link.

A mutation overlap is definite only when every permitted timestamp assignment puts issuance inside an observed window on the same exact template. Other feasible overlaps remain possible. This is deliberately narrower than claiming a mutation was necessary for privilege escalation. Establishing necessity would require effective authorization/state reconstruction and a policy counterfactual, which this implementation does not yet provide.

The state can be checkpointed and restored. New evidence can resolve an earlier unknown answer, expose ambiguity, or cause a previously resolved link to be retracted. There is no irreversible finality or automatic history deletion. The current implementation recomputes decisions for correctness and makes no production scalability claim.

`METHOD.md` states conditional properties and their assumptions. In particular, unique-link soundness requires a captured true issuance, truthful identity evidence, correct namespaces, collision-free strong identity, and true times inside their bounds. The consistency checks do not authenticate a log source.

## 4. Executed experiment protocol

The primary confirmation run is `thesis_research/results/lineage_constraints/2026-11-10/confirmation/`. The earlier `v2/` run is exploratory: its outcomes were inspected during development, so it is not represented as untouched test evidence.

- Before the confirmation run, `confirmation_protocol.json` froze new seeds **2011, 3019, 4021, 5023, 6029**, case counts, and SHA-256 hashes of the engine, simulator, baselines, and evaluator. The recorded local declaration time is 2026-11-10 03:59:12 UTC. This is a local protocol freeze, not an externally registered study or independently timestamped preregistration.
- All four frozen source hashes match the confirmation manifest and current source. No algorithm tuning followed inspection of confirmation outcomes. The earlier exploratory run used seeds 101, 211, 307, 401, 503; small development runs used seeds 11 and 29.
- 3,200 stratified cases across 16 challenge families, 200 consistent-forgery negative controls, and 2,000 variable-size randomized histories: **5,400 cases total**.
- Five executed methods per case: **27,000 saved prediction rows**.
- Random histories vary the number of certificates, CA namespaces, reused public keys, omitted identifiers, enrichment availability, clock error, authentication delay/outcome, and mutation-window placement.
- Inputs, latent histories/labels, and predictions are saved separately. The independent verifier imports neither detector nor simulator. It recomputes random labels from the saved physical histories, checks per-issuer serial uniqueness and clock-bound containment, and checks reported counts and hashes.
- All 5,400 cases also passed reverse-arrival-order and checkpoint/restore equivalence checks. The confirmation stream produced **175** withdrawals of provisional resolved links; the implementation exposes these updates rather than keeping stale claims.

This is a controlled synthetic challenge. Its chosen mixture proportions are not measurements of enterprise prevalence. Repetition of a handcrafted counterexample under different random IDs does not create independent evidence of generalization. No statistical significance claim is made from that repetition. Fresh seeds test repeatability under the same generator; they do not supply independent Windows configurations or external validation.

## 5. Results, including the costs of caution

The confirmation run's 2,000 randomized histories contain **1,804** successful authentications with a true observed issuance and **539** true mutation overlaps.

| Executed method | Correct definitive links | Wrong definitive edges | True-link coverage | Coverage including possible candidates | Correct definite overlaps | False definite overlaps |
|---|---:|---:|---:|---:|---:|---:|
| OR across certificate identifiers | 1,654 | 2,925 | 91.69% | 91.69% | 374 | 175 |
| Issuer + serial | 1,134 | 115 | 62.86% | 62.86% | 265 | 88 |
| Conjunctive fields + 300-second point window | 860 | 0 | 47.67% | 47.67% | 196 | 34 |
| Conjunctive fields + point time | 1,345 | 0 | 74.56% | 74.56% | 310 | 51 |
| Constraint lineage prototype | 1,007 | 0 | 55.82% | 99.06% | 107 | 0 |

These are edge-level outcomes on generated inputs. They are not exploit precision/recall. An OR comparator can output multiple edges for one authentication, hence more false edges than cases.

The prototype does **not** dominate the competent point-time baseline on definitive link coverage: 55.82% is below 74.56%, and both produced zero wrong definitive linkage edges in this random study. Its measured advantage is more cautious mutation attribution and preservation of unresolved alternatives. It outputs only 107 definite overlaps versus the point baseline's 361 (310 correct plus 51 false). It therefore recovers **19.85%** of the 539 true overlaps definitively, compared with **57.51%** for that baseline. Zero false claims at this coverage is not evidence of a universal detection improvement. Its possible sets retain 1,787 of 1,804 true links across 2,157 candidate edges.

A saved post-confirmation error audit (`confirmation/possible_set_error_audit.json`) examines all 17 missed true candidates directly against the latent physical history. Every miss combines a missing issuance thumbprint with an injected incorrect bridge thumbprint. The corrupt enrichment can contradict the authentication without an independent issuance thumbprint exposing the conflict. Fifteen cases return `no_consistent_candidate`; two retain another weak candidate and return `insufficient_identity`. This is a concrete trusted-enrichment failure, not an absence of physical ground truth. The current soundness property assumes truthful identity fields and does not cover these corrupted inputs. The audit did not change the frozen method or rerun selection. Source reliability and alternative enrichment hypotheses are therefore a specific research limitation rather than a claimed solved problem.

A transparent hypothetical loss `missed definite overlaps + λ × false definite overlaps` makes the tradeoff explicit. Under the confirmation generator the prototype beats the point-time baseline only when a false definitive attribution costs more than approximately **3.98** missed definitive overlaps: `(310 - 107) / 51`. That ratio is a sensitivity calculation, not a measured cost of business disruption or a recommendation to automate remediation. Standalone PDF, SVG, and PNG figures and exact counts are under `confirmation/figures/`.

For comparison, the exploratory run had 1,818 true links and 542 true overlaps: the prototype resolved 55.39% of links, retained 99.12% in possible sets, and returned 85 correct/0 false definite overlaps; the point-time baseline resolved 74.37% and returned 300 correct/60 false overlaps. The fresh confirmation therefore supports the same qualitative coverage/certainty tradeoff, rather than reversing a disappointing development result. Both runs use the same synthetic generator and share its modeling limitations.

The 200 deliberately consistent forged-record cases fooled every method, including this prototype. The engine cannot recover the true lineage when a trusted source is replaced by a self-consistent false history. This negative control is excluded from the main challenge aggregate and reported separately.

## 6. Findings from the existing GOAD archive

The new reader processes complete XML roots rather than splitting on a regex that can accidentally consume an `Events` wrapper. It counts all 586 raw events in seven files, treats 4887 as issuance, preserves 4768 success results, and retains certificate identifiers before any detection rule runs.

Only the split-actor archive currently yields a resolved captured issuance-to-successful-use chain under both point times and an assumed two-second clock-error sensitivity setting. In four other certificate-bearing files, the captured authentication identifiers do not establish a consistent link to the issuance captured in that file. Some refer to certificates whose issuance is outside that capture. These are missing evidence chains; they should not be repaired by joining the nearest event or by widening a template-name wildcard.

The ESC6 archive's certificate-bearing 4768 record has failure result `0x42`, and its preauthentication field is not a successful PKINIT record. The new engine reports failed/unknown authentication. The file's scenario name does not override that observed outcome. Microsoft documents nonzero 4768 results as failed ticket issuance.

These findings limit the existing archive as a source of independently validated attack recall. They also motivate the new task: honest attribution under incomplete histories, rather than interpreting every alert as successful exploitation.

The original `scripts/capture_trace7_split_actor_delayed_pkinit.py` contained a fallback that selected the newest private-key certificate when it could not locate the newly issued one. That can make an experiment authenticate with a different certificate. It is a plausible source of mismatched evidence, although this source inspection alone does not prove which historical run took that branch. The repaired script rejects that fallback, verifies the exact issued certificate and private key, preserves raw step outcomes, requires a new output directory, restores the original template flag in `finally`, and requires matching CA, mutation/rollback, and successful KDC records before marking a controlled case successful. Two new tests check wrong-certificate rejection and rejection of failed or incomplete outcome chains.

## 7. Connected-disk work

The actual GOAD VM images were found on `/dev/sdc4`, a previously unmounted Linux partition, rather than only in the mounted NTFS base-image directory. That partition was mounted read-only. The top images and their backing chain were inspected; new local QCOW2 overlays were created, with all original image paths mounted read-only in the test containers.

The first virtio-block boot encountered a Windows boot-device error. Switching the isolated overlay launch to IDE allowed Windows to boot. Fresh WinRM inventory confirms **Windows Server 2016 build 14393** on MEEREEN and BRAAVOS, and the CA service is running. The restored address plan is DC `192.168.56.23` and CA `192.168.56.22`; launcher comments describing other addresses were not used as evidence of the actual configuration. Recovery used new management NICs and explicit return routes. Management forwards and the temporary Kerberos proxy were local to the test host; the source disks stayed read-only.

### Fresh outcome-checked case

The first strict attempt (`split_actor_01`) stopped at a CSR byte mismatch caused by the old transfer procedure's stale destination artifact. The original template flag was verified restored. The transfer now overwrites through explicit binary writes and verifies the resulting bytes. The failed attempt is preserved and excluded from successful-case counts.

The second attempt, `thesis_research/data/lineage_live/2026-11-10/split_actor_02/`, completed the controlled split-actor case:

- Template change and rollback actor: `ESSOS\khal.drogo`, verified in 5136 records 167478 and 167819.
- Certificate enroller: `ESSOS\viserys.targaryen`, verified in the CA issuance record.
- CA request: **25**, issuance record **65102**.
- Exact new certificate serial: `1d0000001974ed828be3240b17000000000019`.
- Certificate SHA-256: `0615b61e77c082ec284557a4ccec1b6aceee963bce99deffe6315788624f6481`.
- Successful KDC record: **168295**, status `0x0`, preauthentication type `16`, target `Administrator`, matching the domain SID with RID 500 and the exact issued serial/thumbprint.
- Captured evidence: **49 selected raw Security records**, public certificate, CA database export, raw step outputs, source snapshot, and hashes. The host script waited 14 seconds after its rollback step; this is not a live 24-hour-delay experiment.
- The template flag was verified restored to **33554432**. Private PFX and credential-cache files were held in a temporary private directory and are not in the dataset.

This establishes one controlled privileged-certificate authentication outcome independently of the detector's alert. It does not establish field recall, an independent testbed, or a production detection rate.

### A real assumption failure exposed by the case

The pre-capture request/response clock samples gave approximate offset brackets of `[0.087, 0.387]` seconds for the DC and `[0.091, 0.383]` seconds for the CA. These are samples, not guarantees of stable offset across the experiment.

The rollback log timestamp is **23:33:59.440 UTC**, while the host recorded sending that rollback command at **23:34:13.107 UTC**. Under the earlier narrow constant-offset model, the log would precede the command even if arbitrary nonnegative audit delay were allowed. At least one clock, event-association, or synchronous-operation assumption therefore fails. The data do not independently identify the physical cause, so this is not labeled proof of clock drift.

`clock_audit.py` implements this consistency check and is tested against independently enumerated operation/offset/delay assignments. The reviewed reconstruction in `live_case_analysis_reviewed.json` finds the certificate chain and exact-template mutation window under point, assumed two-second, and pre-calibration projections. The workflow nevertheless sets **`strict_temporal_attribution_permitted: false`** because the calibration contract was falsified. It does not promote a plausible conditional answer into a guaranteed timing result.

This makes the next scientific task concrete: recover useful certificate/state attribution while explicitly detecting or accommodating clock epochs, audit delay, and evidence-association failures. Future capture runs include event 4616 for clock-change context. The completed case did not include that additional event type, and a post-case clock collection could not be obtained after the VM containers exited. No missing measurement is filled in retrospectively.

### Verification

The original extension passes **25 tests**: five existing publication-validation tests, fifteen lineage/projection tests, two strict-capture tests, and three clock-audit tests. The continuation adds eleven tests, bringing the full passing suite to **36**. The independent confirmation artifact verifier passed on 5,400 cases, 27,000 predictions, and 2,000 labels recomputed from latent physical histories. `confirmation/verification.json` records that check and verification of all four protocol-frozen source hashes. The live analysis verifies the capture artifact hashes and the frozen executed-source hash before reconstructing the case. The evidence supports a pilot result and an assumption counterexample; it is not a complete Q1 evaluation.

## 8. What makes the project closer to a Q1 contribution, and what remains

The project now has a concrete research question, an implemented candidate answer, executable comparators, explicit assumptions, independently auditable synthetic labels, a failure control, and an honest account of a weaker coverage result. Those are research improvements. Journal quartiles do not turn them into an acceptance guarantee.

The main remaining scientific issue is whether conservative attribution delivers enough operational value over well-configured queries and temporal reasoning to justify a new journal contribution. The current false-attribution/coverage tradeoff needs improvement and field validation. A strong continuation should:

1. Extend the single outcome-checked pilot to a preregistered case matrix with benign controls, repeated runs, multiple enrollment mechanisms, and a second Windows/CA configuration. Preserve failed attempts and distinguish selected event exports from total background traffic.
2. Measure clock-offset intervals and their drift; test whether source ordering or tighter justified bounds recovers useful definitive overlap coverage.
3. Execute relevant existing queries and, where feasible, a real provenance system with equivalent input evidence. The current four baselines are local algorithms only.
4. Distinguish temporal overlap from **necessary enabling change** by replaying effective authorization state and a validated policy counterfactual. A maintenance change that was unnecessary for the certificate must not become a causal explanation merely because its times overlap.
5. Repeat on a second independent Windows/CA configuration and legitimate enrollment/maintenance workloads. Label acquisition, issuer aliases, audit policy, patch level, event loss, and telemetry source trust explicitly.
6. Measure end-to-end systems cost after the reasoning contract is stable. The current update strategy retains all records and recomputes; a bounded-memory, scalable deployment claim would be premature.

The defensible current conclusion is that an uncertainty-aware attribution contribution has been developed and tested, with an explicit empirical tradeoff, a fresh outcome-checked Windows case, and a real counterexample to its original clock assumption. These are substantive research advances and a concrete route to stronger novelty. They do not yet establish that the existing three-pillar manuscript meets Q1 review standards.
