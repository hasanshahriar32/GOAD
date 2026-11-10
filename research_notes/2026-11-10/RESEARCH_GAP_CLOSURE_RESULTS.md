# Research gap closure: matched reasoning, prospective transfer, collection cost and corrected remediation

This report records the completed continuation in `/home/m4x1d/Desktop/GOAD`. The session is dated November 10 UTC; local time crossed into November 11 in Dhaka. The manuscript retains its single-column style, title, seven main sections, original figures and model layer count.

## What changed scientifically

Four previously open questions now have executed evidence:

| Question | Completed work | Main finding |
|---|---|---|
| Does the evidence contract add something beyond an ordinary join, and can SQL express it? | Equal-input strong and guarded SQLite queries, 1,470 histories, all evaluated prefixes independently checked. | Guarded SQL and the identity reference agree at all 5,423 evaluated prefixes. The contribution is the certificate-specific contract and its evaluated boundaries, rather than unique Python reasoning power. |
| Does the frozen detector transfer beyond the development identities and single-template sequence? | New forest/CA/SID/hostname, two templates, two ordinary enrollers, concurrent batches and reused keys. | All 24 distinct certificate cases are verified and linked without detector changes: 20 self uses, four administrative uses. |
| What does actual periodic collection cost? | Three paired arm orders, eight legitimate authentications per arm, real incremental Security/CA export and identity-reference updates. | All 48 outcomes independently verified. Paired median client process-envelope increases are 48.6, 80.0 and 100.3 ms. |
| Does the edge-metadata bug affect the historical main remediation experiment? | Same 30 generated graphs and four budgets, faithful metadata correction, independent cut/objective checks. | Historical percentages reproduce, but the correction changes nine of 120 objectives and 24 cut counts. Primary manuscript values are updated. |

These are additional research results, rather than layout changes. Negative findings and failed setup attempts remain in the artifact.

## Equal-input relational comparison

`sql_lineage.py` executes two SQL queries through SQLite 3.53.1. Both receive the same canonical observations as the identity reference. The strong join requires a unique, strong, nonconflicting match. The guarded query additionally retains incomplete candidates and relevant conflicting profiles. No certificate outcome label enters either query.

The protocol freezes seeds 72019, 73009 and 74017, challenge counts, source hashes and delivery/removal behavior before execution. Event intervals are set to `[0,0]` and mutation windows omitted for every method. This is an identity/revision subtask; it cannot establish temporal exposure or causation.

The independently checked output contains **16,269 prediction rows** across **5,423 evaluated prefixes** and 1,470 histories. The guarded query and reference agree throughout, including 225 provisional-link retractions each. A separate set-based verifier imports neither correlator and checks all predictions and 450 saved latent random-history labels. The argument in `SQL_IDENTITY_EQUIVALENCE.md` explains why the finite-set identity projection is relationally realizable; it is not a new general query-answering theorem or machine-checked proof.

| Method, main 1,410 histories | Resolved | Correct terminal claims | Wrong terminal claims | True candidate links retained |
|---|---:|---:|---:|---:|
| Identity reference | 820 | 760 | 60 | 1,176 |
| SQL strong join | 912 | 852 | 60 | 852 |
| SQL guarded | 820 | 760 | 60 | 1,176 |

There are 1,241 true successful observed links in this main group. Its 60 wrong terminal claims are the chronology-negative controls: erasing event order removes information needed to reject an impossible issuance-to-use history. A separate group of 60 consistently forged-source controls fools every method. These controls are retained in the reported results, rather than reassigned as successful detections. The guarded contract exchanges definitive coverage for broader candidate retention; it is not universally superior on every metric.

The SQL queries are our implementations in an actual database runtime. They are **not HADES or Splunk executions**. This closes the competent-relational-baseline question for the stated subtask, while leaving full-system comparisons dependent on compatible telemetry and implementations.

Artifacts: `results/lineage_constraints/2026-11-10/sql_comparison/`, `sql_comparison_verification.json`, and `sql_comparison_protocol.json` under `thesis_research/`.

## Prospective new-forest workload

The transfer environment is a writable child overlay of the preserved updated image. Both the seed and original source disks are mounted read-only. The child is demoted and reprovisioned as:

- Forest `q1transfer.test`, NetBIOS `Q1XFER`, hostname `Q1XFER19`.
- Fresh domain SID `S-1-5-21-3576737527-1549231359-1615615133`.
- New CA `Q1-Transfer-CA`, templates `Q1TransferA` and `Q1TransferB`.
- Ordinary enrollers `q1.reader` and `q1.operator`; neither is a Domain Admin.
- Installed Windows Server 2019 security build **17763.9376**.

The new namespace and workload are prospective, but the Windows image family is shared. This is not an independently sourced OS distribution or an enterprise population sample. A researcher Administrator applies the policy interventions; the ordinary users submit the certificate requests.

Before collection, the protocol freezes the detector, parser, collector and transitive helper versions. Six batches each submit four requests through overlapping host command envelopes. Each enroller reuses one RSA key across its certificates, with a fixed signed request for each enroller/target group. This tests repeated issuance with a reused key, not the Windows renewal protocol.

| Policy condition | Distinct certificate cases | Verified self uses | Verified Admin uses |
|---|---:|---:|---:|
| Baseline | 8 | 8 | 0 |
| Subject supply enabled | 8 | 4 | 4 |
| Rollback before request | 8 | 8 | 0 |

All 24 public certificates match their CSR keys and distinct certificate identities. CA database rows, issuance events and successful KDC principal/SID records independently verify every outcome. All six batches have peak overlap of four submission command envelopes. This is evidence of concurrent client operations, not proof the CA signs four requests simultaneously.

The unchanged, precollection-frozen identity detector links all 24 successful uses, with four correct privileged SID divergences and 20 correct nonprivileged results. Certificate/CSR bytes and adjudicator labels remain outside its inference inputs. The independently collected public CA certificate verifies all 24 leaf signatures and its own self-signature. A later directory observation confirms current NTAuth membership; historical acceptance remains grounded in the captured KDC records.

Actual Certipy and Sigma results are counted in **12 template/batch/enroller units**. Two certificate cases share each pre/post enumeration, so their copied files are not separate tool executions. Four enabled units are flagged before issuance; all 12 postrollback units cease flagging the tested template as ESC1. Sigma is executed on six distinct batch exports, which contain **4,544 Security events**, including 1,000 process-creation and 212 service-ticket events. Full Sysmon/file/socket provenance remains outside these captures.

Combined primary-study counts are now **72 certificate cases, 66 successful uses, 13 administrative uses and six certificate-bound rejections**. The separate cost pilot and earlier infrastructure/development attempts are excluded from this primary denominator.

Use the final reports `transfer_workload_01_adjudication_final.json`, `_identity_final.json`, `_external_final.json` and `_verification_complete.json`. The original versions remain available. The final adjudicator does not claim complete mutation-audit validation for the new condition names: its legacy mutation-history logic is inapplicable and those fields are explicitly unset. Verified certificate-use labels are unchanged. Raw before/after template readbacks and the new workload verifier separately check restoration.

## Paired collection-cost pilot

The corrected frozen pilot has three seeded paired arm orders, with eight authentications per arm at a three-second target start period. The polling arm targets a two-second period and performs incremental Security export, CA export, identity-reference updates and checkpoint retention. The idle arm has no periodic collection. Both have a postmeasurement outcome-verification barrier.

| Pair | Idle median client envelope | Polling median client envelope | Difference |
|---|---:|---:|---:|
| 1 | 639.2 ms | 687.8 ms | +48.6 ms |
| 2 | 622.0 ms | 702.0 ms | +80.0 ms |
| 3 | 602.9 ms | 703.2 ms | +100.3 ms |

The independent verifier checks all **48 exact-certificate KDC successes**, every saved latency median, sampled RSS arithmetic, event counts and paired differences. The client envelope includes process startup and network work; it is not packet-level KDC latency. The sample is three pairs on a shared host, so it does not establish a production overhead bound or population-level effect.

There are 33 measured polling iterations. Per-arm median collection-plus-reasoning envelopes range from 1.586 to 1.659 seconds. Sampled Python collector RSS ranges from 56.5 to 59.5 MiB, excluding Certipy child processes and the Windows VM. Each polling arm grows the retained reference from 30 seeded records to 37 records, with a 16,000-byte final checkpoint. These short observations do not establish a lifetime retention bound or maximum sustainable throughput.

The initial pilot (`collection_pilot_01`) exported ground truth too early and captured only seven of eight final KDC records in the idle arms. It remains intact, with incomplete outcome counts. The corrected protocol (`collection_pilot_02`) waits after the measured interval for audit evidence, then independently verifies eight outcomes per arm. The wait does not enter the authentication timing denominator. Final verification of an outcome is distinct from asserting that every tail record had already entered periodic state at the measurement stop.

## Full remediation recheck and corrected primary claims

The original generator reconstructs all 30 historical graphs. The legacy adaptive and static-greedy policies reproduce **all 120 historical percentage values each** across four budgets. The corrected policy is derived from the exact legacy function, changing full edge-attribute restoration and returning its selected cut for inspection. The original source, results and figure bytes remain unchanged.

An independent plain-adjacency verifier checks 120 cuts, assigned-cost budgets, immutable edges and **11,100 reachability queries**. Preserving metadata changes nine disconnection objectives and 24 cut counts.

| Budget | Corrected adaptive mean ± population SD | Static greedy mean ± population SD | Holm paired-t p | Holm exact-rank p |
|---|---|---|---:|---:|
| 6 | 79.0 ± 16.3% | 69.5 ± 16.7% | 0.0000285 | 0.00000763 |
| 12 | 92.3 ± 11.7% | 88.4 ± 9.9% | 0.25 | 0.25 |
| 18 | 98.0 ± 5.1% | 96.1 ± 7.1% | 0.05138 | 0.02344 |
| 24 | 98.5 ± 4.0% | 97.6 ± 6.5% | 0.25 | 0.25 |

At budget 24 the disconnection rate is unchanged, but the corrected mean cut has **5.7 edges**, compared with 10.9 for static greedy: **47.7% fewer revoked edges** under the assigned costs. The historical 6.0-edge/45.0% statement is superseded in the primary text. This is edge count, not measured business disruption.

Exact signed-rank calculations use rational disconnection fractions for tied ranks, zero differences omitted, and integer subset-sum counts over all conditional sign assignments. The eight-test Holm family covers four budgets and two procedures. Budget 6 survives both procedures; budget 18 survives exact signed rank only; budget 24 survives neither. This is an exploratory reanalysis of synthetic graphs, not a universal policy or equilibrium guarantee. The retained historical figure is explicitly labeled historical and is not the corrected primary table.

## Reproducibility and safeguards

External Git merges inserted source conflicts twice during work. Both stages were preserved before resolution. Collection then ran from hashed source snapshots outside the working tree, protecting execution from further merges. No agent commit, push, submission or public artifact release was performed.

All original captures, failed attempts and frozen versions remain available. Generated table manifests record input, output and generator hashes. The current artifact audit covers both old and new generated credential values, private-key/ticket artifacts, frozen source snapshots and preservation of the original style and figures. Final test/build/hash details are recorded in `VALIDATION_SUMMARY.json`.

The transfer VM was shut down normally after both template flags were read back as 33554432; its container exited with code zero and was removed. Writable disks and snapshots remain preserved outside the repository. Private keys/TGTs are excluded from the publication dataset, and generated passwords remain in protected files outside the repository.

## Updated publication assessment

The defensible contribution is certificate-specific evidence assurance with explicit uncertainty, independently grounded security outcomes, prospective workload transfer and measured operational costs. The equal-input relational study makes that contribution more precise: the contract is implementable in SQL and is not a novel general reasoning primitive. Literal bilinear classification superiority and optimal remediation remain unsupported; the manuscript retains their negative results and corrected measurements.

The local research gaps concerning a competent identity baseline, prospective identity/workload transfer, a real collection-cost pilot, public CA-signature checks and the full-size metadata correction now have completed evidence. Broader OS/organization diversity, long-duration high-load operation, analyst productivity and full external-PIDS superiority would require additional studies **if those claims are made**. The current manuscript should not imply those unmeasured claims. Journal fit, author review, release permissions and journal/category/year checks under JCR and SJR remain submission decisions; no acceptance probability is manufactured.


Final validation: **78 tests pass**, the **38-page PDF compiles**, new tables on pages 28 and 30 are visually checked, and there are no unresolved citation/reference markers. `ARTIFACT_AUDIT_GAP_CLOSURE_FINAL.json` passes 11 study groups, eight matrix versions, all seven generated-table manifests, final analysis-source links and both generated-credential privacy scans. Existing compiler font/overfull/six-pass warnings remain recorded. All research containers and owned sleep inhibitors are stopped; private lab state is retained.
