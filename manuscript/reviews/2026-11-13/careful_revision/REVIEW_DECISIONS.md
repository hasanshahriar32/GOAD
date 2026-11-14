# Context-checked manuscript corrections

Completed November 14, 2026. The broad revision was withdrawn at the author's request. Its pre-pass snapshot was restored byte for byte before this narrower pass (`../reviewer_revision/ROLLBACK.json`). This document describes the active manuscript.

The original title, abstract, introduction, contribution list, section order, document class, typography and two-column journal style are retained. The GNN study remains in the main paper. The leader–follower formulation is retained with its existing explicit boundary: the evaluated policy is a sequential heuristic and supplies no equilibrium certificate.

## Applied after checking the actual files

| Finding | Evidence and limited correction |
|---|---|
| Certipy reference names obsolete releases | Evaluation explicitly uses 5.0.4. Changed that existing reference to the versioned primary release URL and its verified 2025 release year; retained the citation key. |
| Missing DOI metadata/display | Added four verified DOI fields (shortcut learning, original GNN model, multiterminal cuts, directed multiway cuts). The installed IEEEtran bibliography style ignores `doi`, so existing verified journal/conference DOI fields also receive explicit display notes. No papers are swapped or added merely to increase counts. |
| Arrival-process explanation does not match the generator | `thesis_research/src/phase3_cipg/benchmark_suite.py:848` fixes 2,000 arrivals, samples uniform times over T, and selects a maintenance template with probability 0.055 split across fifteen templates. Replaced the unconditional 2,000/hour Poisson interpretation and corrected maintenance durations to [10,35] seconds. The saved zero/three/four false-alarm counts are retained. The independent replay reproduced dataset, ablation and sensitivity counts exactly. |
| Event projection claims fields absent from the listing | The selected 4887 payload demonstrates RequestId, Requester, Subject and Attributes, not SKID or Disposition. Corrected that projection, added CertIssuerName to the KDC projection and separated optional CA-database enrichment. Removed the unsupported field-name-disjointness proposition. |
| Residual proof differentiates through inconsistent initial spaces | Kept the conditional theorem, including its existing exclusion of target-dependent attention. Expressed the residual bound and unrolling in the common initial hidden space; no raw-feature lower bound is asserted. Corrected the first-layer derivative's raw-input variable. |
| RQ wording presupposes a cure or superiority | Reworded RQ1 and RQ4 as measured comparisons. The original neutral gating result and all reported statistical values remain. The skip-ablation heading no longer claims an empirical confirmation of assumptions excluded by the attention model. |
| Figure 1 uses a different vocabulary than the definition | Replaced only that illustration with a six-type/ten-relation vocabulary summary drawn from the actual definition. Narrowed taxonomy language to distinguish candidate modeling categories from evaluated coverage. No ESC1–ESC15 coverage is newly claimed. |
| Pipeline image contains unmeasured latency/scale/optimality claims | Replaced the illustration with certificate-evidence flow and explicit source assumptions. It no longer prints 100K/1M scale, <25 ms, <2.4 s, >95% pruning, zero disruption or optimal revocation. Caption/algorithm context distinguishes independent evidence collection from optional neural screening and the mutation-taint pseudocode. |
| Remediation image has illustrative equilibrium trajectories | Replaced it with a plot read directly from corrected saved adaptive/static-greedy measurements. Cost budgets and population-SD error bars are labeled correctly. The original images remain on disk; they are not embedded in the revised PDF. |
| Missing self-use column | Added counts derived from per-trial verified outcomes. Assertions check every trial is successful and self + admin = trials. The other columns retain their original values. |
| Identifier underscores disappear in PDF extraction | Changed only the underscore glyph command; kept fonts and page geometry. Checked extraction of long ADCS identifiers. |
| Funding and ethics | Added the author's confirmed no-grant statement and an isolated-laboratory ethics/dual-use statement. Existing affiliations and corresponding-author information were already present. Removed the obsolete writing-process declaration as requested. |
| Snapshot equality is expressed as universal zero recall | Retained the projection argument but wrote equality of observable restored states rather than assigning 0% recall to every snapshot detector. This changes a logical overclaim, not an experimental result. |
| Preference-elicitation citation overreach | Clarified that the cited hardening study does not establish administrator preference elicitation in this experiment. |

The schema vocabulary and the single-panel remediation plot fit one column; the evidence pipeline remains full width. These are local float-size changes, not a new manuscript template.

## Report assertions that were not adopted

| Report assertion/suggestion | Context check and decision |
|---|---|
| The current introduction reports 0/63 | It does not. The main file/abstract already reports identical bilinear/additive classifications. The 41/63 diagnostic and its faulty-label/repeated-input boundaries are already described. No headline number was replaced based on the report. |
| Section 3.3 is titled “Multiplicative Gating Cure” | The actual heading is “Shortcut Behavior and Bilinear Gating.” Kept it. Only the remaining RQ1 “cure” wording was changed. |
| [32] is RapSheet but cited as NodeMerge | Neither paper is cited in the restored current bibliography. The report's reference numbers are not a valid mapping to the current source. No unrelated replacement was made. |
| Fixed-parameter and limited-query papers are misrepresented as GNN/preference studies | The described obsolete reference set is absent. The current related work already distinguishes GNN reviews, attack graphs, hardening and provenance systems. Only the remaining preference-elicitation implication was corrected. |
| HADES must have a USENIX 2025 counterpart | No such counterpart was confirmed. Retained the verified journal entry rather than adding an unverified duplicate. |
| CPD issue/page range is wrong | DOI/registry and institutional metadata support TDSC 23(4), 8967–8984. Kept the entry. HADES 23(1), 936–953 is also supported. Primary-source notes/responses are retained under the previous pass's `sources/` directory; an unrelated guessed directed-cut DOI was rejected in favor of the title-matched DOI ending `_92`. |
| Wrong SAN OID in the current introduction | The restored manuscript already uses `szOID_SUBJECT_ALT_NAME2` / 2.5.29.17 where it describes the CSR SAN. Did not invent a new OID correction. |
| Replace all sample SD values with population SD | Both conventions are legitimate for different purposes and were already labeled. Kept 2.19 and 1.00 sample-SD values in the learning table and every original measurement; added an explicit explanation distinguishing them from finite-graph population SD. |
| Move GNN to appendices, change title or split the paper | These are strategic restructuring proposals, not demonstrated factual errors. Did not impose them from a context-mismatched review. |
| Add many missing conference systems/model references | The bibliography already satisfies the author's maximum of three conference references and has a journal majority. No citation padding or concealed reclassification of conference papers was introduced. Additional direct model/PIDS comparisons would require a separate scientific decision and, for performance claims, actual experiments. |
| Affiliation and corresponding author missing | Both were already present. Preserved them. |
| Replace every draft-history phrase throughout | Some phrases distinguish flawed controls from valid reruns and prevent relabeling old results as corrected measurements. Preserved scientifically meaningful provenance of the experiments rather than hiding those distinctions. |

## Verification and remaining work

The independent confirmation, component, SQL, checkpoint and interdiction verification reports obtained November 13 are retained here. They check 27,000 confirmation predictions, 16,200 component predictions, 16,269 SQL predictions, 10,800 checkpoint predictions and 11,100 interdiction reachability queries. The manuscript-only corrections do not modify those frozen inputs or results. The final audit binds the revised PDF and generated tables and checks that existing table values are preserved.

`FINAL_CHECKS.json` records compilation, citation counts, figure sources, table checks and PDF identifier extraction. `CHANGES_FROM_RESTORED_SNAPSHOT.diff` shows the source changes against the author's actual pre-pass version, independently of older Git changes.

The public-artifact item was completed after this review on November 14, 2026: https://doi.org/10.5281/zenodo.24212038. The public ZIP was downloaded without authentication and matched the tested local SHA-256. See `../../../release/2026-11-14/RELEASE_COMPLETION.md` and the public verification report. No new live cases, production deployment, independent Windows image family or journal submission is claimed. Controlled laboratory scale and the other scientific boundaries remain as stated.
