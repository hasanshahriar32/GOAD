# Certificate lineage research extension

This directory develops a substantive research candidate for CIPG. Research claims, evidence tables, and limitations are integrated into the manuscript while retaining its existing style, title, layer structure, and architecture.

The question is whether ADCS provenance can distinguish a **definite** issuance/use and mutation-overlap explanation from a merely **possible** one when CA records are incomplete, timestamps have declared error bounds, and evidence arrives late. Existing `phase3_cipg` joins identifiers with OR and stores taint under unscoped strings. This extension uses issuer-scoped request enrichment, checks every shared identity field for contradictions, treats SKID as a reusable key identifier, retains compatible incomplete candidates, and produces revisable conclusions. A record's success result and PKINIT type are required before it can support successful certificate use.

The research hypothesis is reduced false definitive attribution while preserving uncertain candidates for investigation. This is an engineering and reasoning contribution to be tested against competent correlators. It is not a claim that joins, interval reasoning, abstention, or provenance graphs are individually new.

## Source and reproducibility

- `engine.py`: immutable observations, bounded time intervals, exact template matching, definite/possible overlap, decision updates, retractions, and checkpoint/restore.
- `simulator.py`: 17 named challenge families including a trusted-log violation negative control, plus a variable-size randomized history generator. The randomized simulator retains latent certificate identities and physical times separately from detector input.
- `baselines.py`: four executed local comparators with the same projected evidence. No external security product is impersonated.
- `evaluate.py`: five-seed experiment, JSONL inputs/labels/predictions, per-family/per-seed metrics, order/restart checks, archived GOAD projection, and hashes.
- `verify_results.py`: imports neither detector nor generator; recomputes randomized labels from saved latent histories, checks clock bounds and per-issuer serial uniqueness, and checks output counts/hashes.
- `goad.py`: reads complete XML trees and preserves event success status. Only 4887 is an issuance; 4886 is a received request. Archived use outcomes are reported without inferred exploit labels.
- `clock_audit.py`: checks whether a declared offset and nonnegative audit delay can explain a controlled operation's log timestamp.
- `analyze_capture.py`: verifies frozen capture hashes, independently checks the certificate/CA/KDC chain, reconstructs exact-template mutation windows, and reports whether the timing model survives the controlled-operation checks.
- `repair.py`: exhaustive optional-export deletion hypotheses under an explicit record fault budget; candidate union, certain-link intersection, and witnesses. Abstaining hypotheses remain part of the uncertainty.
- `temporal.py`: exact rational difference constraints with strict inequalities, contradictory-evidence rejection, and deletion-minimal contradictory sets. This uses established temporal-network methods, not a new generic solver.
- `robustness_study.py` / `verify_robustness.py`: a separately frozen, independent factorial generator and a verifier importing none of the engines/generators; 2,700 identity histories, 1,800 temporal histories, 16,200 predictions, and 3,600 complete temporal-oracle queries.
- `analyze_capture_order.py`: a controlled operation-order reconstruction from the frozen synchronous orchestrator. It leaves the failed audit-clock model unresolved and does not prove necessary causation.
- `published_rule_replay.py`: executed SQLite proxy for a published analytic's SAN/principal conditions. Differences from SPL and unsupported records are explicit; this is not a Splunk engine run.
- `lab/`: isolated writable VM overlays and read-only inventory tooling. The source disks are mounted read-only. Guest management NAT uses `restrict=on`, with host forwards bound to localhost; the two guests communicate through a private socket link.

From the GOAD root:

```bash
.venv/bin/python -m unittest thesis_research.tests.test_lineage_constraints -v
.venv/bin/python -m thesis_research.src.lineage_constraints.evaluate \
  --output thesis_research/results/lineage_constraints/new-run \
  --seeds 2011 3019 4021 5023 6029 --per-family 40 --random-per-seed 400
.venv/bin/python -m thesis_research.src.lineage_constraints.verify_results \
  thesis_research/results/lineage_constraints/new-run
.venv/bin/python -m thesis_research.src.lineage_constraints.summarize \
  thesis_research/results/lineage_constraints/new-run
```

Use a new output directory; the evaluator refuses to overwrite a run. The primary saved run is `2026-11-10/confirmation`, with 5,400 cases and 27,000 method/case rows. `confirmation_protocol.json` froze seeds 2011, 3019, 4021, 5023, 6029 and four source hashes before execution; `confirmation/verification.json` records independent artifact verification and matching frozen hashes. This is a local protocol freeze, not external study registration. The earlier `v2` run is exploratory. The 2,000 randomized histories are analyzed separately from the stratified counterexamples. Equal repetitions of handcrafted counterexamples do not provide independent estimates of enterprise prevalence or statistical significance.

The measured tradeoff matters: in the confirmation randomized histories, the prototype outputs 107 correct definite mutation overlaps and no false ones, whereas the point-time conjunctive baseline outputs 310 correct and 51 false overlaps. Both have zero wrong definitive certificate-linkage edges, and the baseline resolves more true links. The prototype retains 99.06% of true links in its possible sets but resolves 55.82% definitively. These are fresh histories under the same synthetic generator, not an independent Windows generalization result. See `research_notes/2026-11-10/RESEARCH_DEVELOPMENT_REPORT.md` for the full analysis and remaining novelty requirements.

## Fresh controlled Windows case

`thesis_research/data/lineage_live/2026-11-10/split_actor_02/` contains a new 49-record case, CA request 25, a public issued certificate, raw step outputs, the executed capture source, and an outcome manifest. Khal modified and restored the template; Viserys enrolled; the exact certificate authenticated as the domain Administrator SID after rollback. Private PFX and credential-cache files are not part of the dataset. `split_actor_01` is an excluded failed transfer attempt with verified state restoration.

The reviewed result is `thesis_research/results/lineage_constraints/2026-11-10/live_case_analysis_reviewed.json`. All three declared timing modes reconstruct the observed chain, but the control-plane audit falsifies use of the earlier calibration as a guaranteed constant bound. Accordingly, the workflow marks strict temporal attribution unsupported. This is an outcome-checked pilot and an assumption-failure example, not a real-world accuracy estimate.

The repaired `scripts/capture_trace7_split_actor_delayed_pkinit.py` now requires a **new** `--output-dir`. It checks transferred bytes, the exact newly issued certificate and key, CA issuance, actor identities, mutation/rollback, and successful KDC authentication before accepting a case. It restores the original flag in `finally`. Endpoint and lab credentials can be configured through CLI URLs and the `GOAD_DC_*` / `GOAD_CA_*` variables. The lab launcher is experimental recovery tooling; its image controller, guest network, and account settings must match the collected inventory rather than comments about a different GOAD address plan.

## New component-study findings and reproduction

The saved `2026-11-10/robustness` study uses a separate generator, fresh seeds, and source hashes frozen before execution. It passed independent artifact/label verification and 3,600 temporal answers checked by direct world enumeration. All 900 deliberately contradictory-order controls were rejected by the order-aware reference. With fully observed additional order, it recovered 138/138 true overlaps in 300 histories; boxes alone recovered 53 and point time recovered 112 with 11 false claims. Full sensor coverage is a designed condition, not an enterprise measurement.

The bridge component intentionally includes a strong ablation: ignoring all optional exports. A budget of two retains all 2,180 true links as possible candidates, but only 602 are certain; the ignore-all comparator resolves 1,757 certainly with the same true-candidate retention. The budget reference is therefore not a demonstrated improvement over this simple comparator. At 49,800 hypotheses it also has a clear combinatorial cost. See the continuation report for the evidence contract and remaining gaps.

```bash
# Create new paths: the frozen study refuses to overwrite a protocol or run.
.venv/bin/python -m thesis_research.src.lineage_constraints.robustness_study freeze /tmp/new-robustness-protocol.json --per-cell 20
.venv/bin/python -m thesis_research.src.lineage_constraints.robustness_study run /tmp/new-robustness-protocol.json /tmp/new-robustness-run
.venv/bin/python -m thesis_research.src.lineage_constraints.verify_robustness /tmp/new-robustness-run
.venv/bin/python -m unittest discover -s thesis_research/tests -v
.venv/bin/python manuscript/scripts/generate_lineage_evidence.py
```

`live_operation_order.json` supports one controlled issuance-between-operations explanation using five explicit order constraints. Removing any one makes the overlap merely possible. The evidence source is the synchronous orchestrator and checked responses, not timestamp sorting or cross-host record numbers. This does not independently establish the CA's effective-policy state.

## Meaning and limits of a conclusion

`resolved` means one strong, temporally ordered candidate among the retained consistent observations. `candidate_ids` retains other possible explanations when the engine cannot make that claim. A definite mutation overlap means every timestamp assignment inside the declared boxes places issuance inside an observed window on the same exact template. It does not prove the mutation was necessary for enrollment or malicious. Effective AD permissions, template OID/name aliases, certificate trust, and authorized delegation require additional verified evidence.

Soundness is conditional on truthful collected identity fields, correct namespace mappings, a captured true issuance, collision-free strong certificate identity, and true times lying inside their bounds. The deliberate consistent-forgery control breaks these assumptions and fools this engine as well as the baselines. This module does not authenticate log sources. It currently recomputes decisions after updates and retains records until explicitly removed; it makes no production scalability or bounded-memory claim.

## Prior work that constrains novelty

CA/KDC event correlation is already described in [In.security's 2023 KQL investigation](https://in.security/2023/03/02/detecting-ad-cs-subjectaltname-san-abuse-using-kql/) and [Splunk's ESC1 authentication analytic](https://research.splunk.com/endpoint/f0306acf-a6ab-437a-bbc6-8628f8d5c97e/). [HADES](https://arxiv.org/abs/2407.18858) addresses AD whole-network provenance. [Heinzl and Nissl's 2026 time-model SoK preprint](https://arxiv.org/abs/2610.35151) explicitly studies clock and delivery assumptions. [RFC 5280](https://www.rfc-editor.org/rfc/rfc5280) defines issuer-scoped serial uniqueness, and [Microsoft's 4768 documentation](https://learn.microsoft.com/en-us/previous-versions/windows/it-pro/windows-10/security/threat-protection/auditing/event-4768) distinguishes failed ticket requests from successful issuance. The narrower combination of certificate-specific uncertainty, mutation-overlap evidence, and revisable attribution is the candidate contribution; literature search and field validation must continue before asserting priority or Q1 readiness.

## Continued live, model and interdiction validation

The authoritative continuation is `research_notes/2026-11-10/LIVE_RESEARCH_AND_NOVELTY_UPDATE.md`. Two final paired matrices, `paired_policy_matrix_02` and `independent_2019_matrix_02`, contain 24 independently checked certificate uses and six administrative outcomes. `adjudicate_policy_matrix.py` checks public bytes, CA evidence and KDC SID/name/domain independently of detector decisions. `verify_paired_policy.py` checks fixed CSR/key and matched policy. `external_sigma.py` runs actual upstream Sigma rules through actual pySigma/SQLite; `analyze_external_policy.py` distinguishes tested-template risk from certificate-use outcomes. `evaluate_live_identity.py` excludes CER/CSR and labels from inference, and requires the observed directory OID/name mapping when names differ.

`literal_bilinear.py` is a separate two-layer, four-head realization of the bilinear edge/self-skip equations, with trainable encoders, attention and gates. `bilinear_study.py` uses paired graph families and typed WL filtering across splits, matched initialization, matched augmentation and validation-only checkpoint selection. Its 5,100 case labels and 10,800 held-out predictions pass independent verification. The additive and bilinear arms have identical classifications; both miss all long-path positives. The historical feature-channel diagnostic and its repeated training archetypes remain separate in `gating_audit/`.

`interdiction_audit.py` preserves candidate-edge metadata and compares the corrected reference against exhaustive small cuts. It remains heuristic. `projection_contract.py` retains every queried pair endpoint and every possible requested path; `projection_repeated.py` includes projection cost in repeated alternating-order timings. At 5,000 actual nodes and 325 pairs, the median ratio is 7.54, not the historical 1,246 ratio that dropped some queried pairs. Original source implementations and artifacts remain intact.

`falsification_controls.py` adds two explicit counterexamples: a false but self-consistent order channel can induce a wrong definite overlap, and six corrupted bridge rows from one failed exporter exceed a two-record budget. `source_faults.py` quantifies whole-source deletions under a supplied failure-domain partition. It retains the true candidate in that control with two hypotheses, compared with 64 for a sufficient six-record budget. The budgets count different units; this is not an equal-assumption superiority or source-authentication claim.

For offline reproduction, use fresh output paths:

```bash
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 .venv/bin/python -m unittest discover -s thesis_research/tests -v
.venv/bin/python -m thesis_research.src.lineage_constraints.bilinear_study freeze /tmp/new-bilinear-protocol.json
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 .venv/bin/python -m thesis_research.src.lineage_constraints.bilinear_study run /tmp/new-bilinear-protocol.json /tmp/new-bilinear-study
OPENBLAS_NUM_THREADS=1 OMP_NUM_THREADS=2 .venv/bin/python -m thesis_research.src.lineage_constraints.verify_bilinear_study /tmp/new-bilinear-study /tmp/new-bilinear-verification.json
.venv/bin/python -m thesis_research.src.lineage_constraints.interdiction_audit /tmp/new-interdiction-study
.venv/bin/python -m thesis_research.src.lineage_constraints.verify_interdiction_audit /tmp/new-interdiction-study /tmp/new-interdiction-verification.json
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m thesis_research.src.lineage_constraints.projection_repeated /tmp/new-projection-study
OPENBLAS_NUM_THREADS=1 .venv/bin/python -m thesis_research.src.lineage_constraints.verify_projection /tmp/new-projection-study /tmp/new-projection-verification.json
.venv/bin/python -m thesis_research.src.lineage_constraints.falsification_controls /tmp/new-falsification-controls
```

Live collectors require the explicitly isolated lab, matching inventory and externally stored private credentials. A frozen protocol checks collector dependencies and required installed Windows build before execution. `lab/` contains image-copy launch, independent forest provisioning, signed official update media and installation helpers. They are lab tools, not deployment automation for an arbitrary Windows domain. No new trial private keys or tickets are retained in the publication dataset.

## Completed October-security-build follow-up

`current_patch_upn_01` and `current_patch_sid_01` contain 24 trials on verified Windows Server 2019 build 17763.9376. The completed review reports verify 18 successful uses (three administrative) and six certificate-bound KDC rejections. The identity reference is unchanged from its precollection freeze. All 24 actual postrollback Certipy scans cease flagging tested-template ESC1. See `research_notes/2026-11-10/CURRENT_PATCH_FINDINGS.md` for exact task boundaries and artifact paths.

The frozen v4 collector skips a subsequent CA export when its selected KDC System interval is empty. Eighteen missing exports are completed using a separately hashed later read-only CA snapshot through `supplement_matrix_evidence.py`; raw captures and manifests stay unchanged. The review checks forest/CA identity and both input manifest sets, fills missing exports only in temporary copies, independently adjudicates certificate outcomes, verifies matched CSRs/policy, and evaluates successful-use identity linkage. A later snapshot is not evidence of historical policy state. Its three preservation/tamper/forest regression tests and the actual `current_patch_export_control_01` empty-query control pass.

The current collector corrects the empty-query case and therefore intentionally differs from the frozen v4 source hash. Historical protocols and saved source snapshots remain intact. Freeze a new protocol for any new collection with the corrected collector; do not rewrite old protocol hashes. Offline analysis of saved matrices needs no running VM and can use the documented supplementary-review command with a new output directory.

## Completed prospective transfer and research-gap cycle

`research_notes/2026-11-10/RESEARCH_GAP_CLOSURE_RESULTS.md` is the newest results guide. `sql_comparison/` checks an actual guarded SQLite realization at 5,423 evaluated prefixes; all 16,269 prediction rows pass the independent set-based verifier. Chronology-erased and forged-source controls remain reported failures. `SQL_IDENTITY_EQUIVALENCE.md` gives the projected-contract argument and its scope.

`transfer_workload_01` contains 24 distinct certificates from a new forest/CA/SID/hostname, two templates and two ordinary enrollers, with four overlapping submission command envelopes in each of six batches. The unchanged detector links 24 successful uses (four administrative). Use the `_adjudication_final.json`, `_identity_final.json`, `_external_final.json` and `_verification_complete.json` results. The final verifier also checks public CA/leaf signatures. Unknown condition names no longer default to a validated legacy mutation history; this reporting correction leaves certificate-use labels unchanged.

`collection_pilot_02` independently verifies 48 legitimate authentications in six paired arms while measuring incremental export/reference updates, Python CPU/RSS and process-envelope cost. The incomplete initial pilot is retained separately. Postmeasurement evidence waits do not enter client timing. This is an isolated-lab pilot with a shared host and finite retained history, not a production performance bound.

`interdiction_recheck/` reproduces historical adaptive/greedy values on the original 30 graphs, then restores full candidate-edge attributes. The correction changes nine of 120 objective outcomes and 24 cut counts. Independent plain-adjacency/cost verification and exact-rank/Holm reanalysis are saved alongside. Current primary-table results use the corrected implementation; original source, figures and data remain intact.

Frozen collection ran from independently hashed cache snapshots to avoid external workspace merges altering active source. Generated passwords, VM disks and private keys are outside the publication dataset. The transfer VM is shut down after restored template readbacks; offline analysis requires no running VM. Both JCR and SJR journal/category/year checks remain part of later target selection.
