# Current-patch ADCS evidence study — completed collection

Workspace: `/home/m4x1d/Desktop/GOAD`. Date: 2026-11-10. This report supplements the earlier live/novelty update and preserves its older-build results.

## Finding and publication significance

An independently provisioned Windows Server 2019 forest, updated to **17763.9376**, produces different authentication outcomes for UPN-only and UPN-plus-SID-URL requests. In the latter form, three certificates issued while the template's subject-supply bit is enabled subsequently authenticate as Administrator after template restoration, CA refresh and a Certipy scan that no longer flags the template as ESC1. The UPN-only form produces certificate-bound rejection for both enabled administrative and enabled legitimate-self requests.

The useful research result is the measured separation among configuration risk, request/certificate identity, mapping acceptance and realized principal. SID-URL mapping and template rollback are established concepts; these experiments do not discover a new attack or cryptographic mechanism. The result strengthens the paper's certificate-evidence contract and supplies modern-patch controls that were previously absent.

## Environment and design

- Fresh forest `q1lab.test`, separate CA `Q1-Evidence-CA`, template `Q1Evidence`, ordinary enroller `q1.enroller`.
- Signed Microsoft July prerequisite and October KB5126651 installed in a writable research copy. Post-reboot readiness records build 17763.9376, no pending reboot, running KDC/CertSvc and enabled Defender. The original source image stays read-only.
- No strong-binding compatibility override, explicit administrator certificate mapping, or enroller Domain Admin membership was introduced.
- Two protocols frozen before collection: `independent_2019_current_patch_upn_protocol_v4.json` and `independent_2019_current_patch_sid_protocol_v4.json` in `thesis_research/results/lineage_constraints/2026-11-10/`.
- Each protocol has three shuffled four-condition blocks. Administrative baseline/enabled/rollback-first conditions reuse identical signed CSR bytes and the same RSA key within a block/form. SHA-256 signatures and issued-public-key equality are independently verified. Keys differ between forms.
- Recorded template policy fields other than the subject-supply bit remain equal within matched blocks. Baseline flag is 33554432, enabled flag is 33554433.
- All current-patch conditions include post-issuance baseline readback, CA refresh, low-privilege RPC readiness and actual postrollback Certipy enumeration before certificate authentication.
- The updated workflow differs from the older-build workflow. Old versus new data therefore do not isolate a patch-only causal effect.

## Independently checked outcomes

Each row has three trials. All recorded final baseline readbacks are restored.

| Form | Condition | Self use | Administrator use | Certificate-bound rejection | ESC1 before request | ESC1 after rollback |
|---|---|---:|---:|---:|---:|---:|
| UPN only | Baseline/admin SAN requested | 3 | 0 | 0 | 0 | 0 |
| UPN only | Subject supply enabled/admin SAN | 0 | 0 | 3 | 3 | 0 |
| UPN only | Rollback before request | 3 | 0 | 0 | 0 | 0 |
| UPN only | Enabled legitimate self request | 0 | 0 | 3 | 3 | 0 |
| UPN + SID URL | Baseline/admin SAN requested | 3 | 0 | 0 | 0 | 0 |
| UPN + SID URL | Subject supply enabled/admin SAN | 0 | 3 | 0 | 3 | 0 |
| UPN + SID URL | Rollback before request | 3 | 0 | 0 | 0 | 0 |
| UPN + SID URL | Enabled legitimate self request | 3 | 0 | 0 | 3 | 0 |

Totals: **24 attempts, 18 successful exact-certificate authentications, three administrative uses, six exact-certificate rejections**. Combined with the two final older-build matrices: **48 trials, 42 successful exact-certificate authentications, nine administrative uses and six rejections**. Earlier interrupted/development attempts are retained separately and excluded from these totals.

Success requires public certificate identifiers, a matching CA database row, a matching trial issuance event, and a successful certificate-bearing KDC record with a consistent target name/domain/SID. Diagnostic tool output alone does not label success. Rejection requires issuance evidence plus the public certificate serial and thumbprint in a KDC System diagnostic. All six current-patch rejections match event 39.

Observed baseline/rollback-first certificates contain the enroller security SID extension. Enabled UPN-only certificates lack it and are rejected, including legitimate self requests. Enabled SID-URL certificates lack that extension but contain the requested matching SID URL and authenticate. This is observed certificate content, not a universal claim that every template with a particular bit behaves identically.

The fixed-request verifier supports three conditional enabling-bit contrasts for the SID-URL form. It supports zero privileged-use contrasts for the UPN-only form, whose enabled administrative requests are rejected. The two forms do not use the same keys, so the cross-form comparison is not represented as a same-key isolated intervention.

The identity detector's source is frozen before collection. It links all 18 successful new authentications, with three correct privileged SID divergences and 15 correct nonprivileged outcomes. It sees raw logs, CA export, observed directory OID/name mapping and domain SID context; certificate/CSR bytes and adjudicator outcomes do not enter inference. Rejections are excluded from this successful-use linkage denominator, not silently counted as successful detections.

Actual Certipy 5.0.4 and three unmodified Sigma rules through pySigma/SQLite execute on both new matrices. The pre-request configuration findings agree with the older-build pattern. All 24 postrollback scans cease flagging the exact template as ESC1. This is a correct configuration observation, not an attack false negative: certificate use is a different task. No full Splunk or HADES execution is claimed.

## Collector failure, evidence completion and source integrity

An unfinished Git merge initially inserted conflict markers in manuscript/code files and stopped collection before the first trial. Both versions were backed up under the user's cache, and the newer verified version was restored. All frozen v4 source hashes then matched before the actual experiments started. No commit or publication was performed by this continuation.

The frozen collector contains a no-event export defect: `Get-WinEvent` returns a failing shell status for an empty selected System interval, which skipped the following CA export. This occurs in 18 successful trials. Their matching successful KDC records were already captured, but the first UPN adjudication correctly leaves six chains incomplete rather than manufacturing CA evidence.

After both matrices finished, a new read-only export from the same CA was separately captured in `current_patch_ca_supplement_01/`, with context, exact script, executed source and hashes. `supplement_matrix_evidence.py` checks source manifests and forest/CA identity, creates temporary copies, fills only missing CA exports, and records original manifest hashes and the supplemented trial list. Existing per-trial exports are retained. No raw capture or raw manifest is overwritten.

The later CA export supplies identity bridges, not historical template state or clock calibration. Complete chains are independently adjudicated from the supplemented views. Original incomplete adjudication remains available. Three regression tests check unchanged originals, preservation of an existing export, supplement tampering and forest mismatch. The collector now handles only `NoMatchingEventsFound` as normal empty output and propagates other query errors. `current_patch_export_control_01/` records a successful actual empty-query control followed by CA export. Frozen v4 source snapshots remain unchanged; the corrected current collector intentionally has a different hash, and new collections must freeze a new protocol.

## Artifact paths and analysis reproduction

Raw matrices and supplementary observations are under:

```text
thesis_research/data/lineage_live/2026-11-10/
  current_patch_upn_01/
  current_patch_sid_01/
  current_patch_ca_supplement_01/
  current_patch_export_control_01/
  independent_2019_setup/
```

Analysis artifacts are under `thesis_research/results/lineage_constraints/2026-11-10/`:

```text
current_patch_upn_01_adjudication.json      # Original incomplete-chain report
current_patch_upn_01_review/               # Completed adjudication, CSR/policy and identity checks
current_patch_sid_01_review/
current_patch_upn_01_sigma/                # Actual upstream rules, queries, versions and results
current_patch_sid_01_sigma/
current_patch_upn_01_external.json
current_patch_sid_01_external.json
```

Offline outcome/identity reanalysis requires no running VM. From the repository root, use a **new output directory**:

```bash
.venv/bin/python -m thesis_research.src.lineage_constraints.supplement_matrix_evidence review \
  thesis_research/data/lineage_live/2026-11-10/current_patch_upn_01 \
  thesis_research/data/lineage_live/2026-11-10/current_patch_ca_supplement_01 \
  /tmp/new-upn-review
```

Replace `upn` with `sid` to reproduce the other matrix. Inference timing naturally varies; verified outcome/identity counts and matched-request checks should agree. The table generator is `manuscript/scripts/generate_current_patch_evidence.py`; its saved manifest checks all table inputs and output bytes.

The restored lab was shut down normally with baseline flag 33554432 read back, and its container exited with code zero before removal. The writable research disk and cold preupdate snapshot remain preserved. Private keys/TGTs and generated passwords are excluded from the new publication dataset.

## Primary sources checked

- [Microsoft KB5126651](https://support.microsoft.com/en-us/servicing/os/windows-10/2026/10/kb5126651-windows-10-1809-security-update): measured October security build and Server 2019 applicability.
- [Microsoft KB5014754](https://support.microsoft.com/en-us/servicing/os/windows-server/2022/05/kb5014754-certificate-based-authentication-changes-on-windows-domain-controllers): strong-binding enforcement and certificate-mapping diagnostics.
- [Microsoft MS-PKCA SID section](https://learn.microsoft.com/en-us/openspecs/windows_protocols/ms-pkca/e8fd2c1d-50d3-493a-9b58-5e453850c567): SID-URL mapping format and mapping constraints.

These sources establish expected semantics. Actual experimental counts above come from local saved evidence, not from vendor descriptions.
