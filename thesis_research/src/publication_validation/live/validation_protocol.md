# Controlled Windows validation protocol

## Evidence hierarchy

1. Collected configuration: observed templates, ACLs, publication and policy links.
2. Independent effective-access check: resolve the selected principal's token, inherited/deny ACL semantics and both CA and template enrollment.
3. CA outcome: certificate issued, pending approval, denied, or unsupported template. Preserve request IDs and returned error codes.
4. Authentication and authorization: certificate authentication succeeds and grants the intended test authorization. Issuance alone is insufficient to label ESC13 escalation.

Report which level each case reaches. Do not treat a tool's detection as independent ground truth for evaluating that same tool. Do not label an absent prerequisite or collection error as a blanket safe domain.

## Baseline and isolation

The original ESSOS baseline was collected before provisioning: no templates/CAs existed and BRAAVOS lacked the CA role. Powered-off internal snapshots named `publication-pre-adcs-20261014` were then taken for both DC03 and SRV03. The planned CA is `CertGraph-Lab-CA`, restricted to this existing user-owned GOAD lab. Preserve both snapshots until review. Restore them together while both guests are stopped if reverting the experiment; do not restore one directory participant independently without considering replication/trust state.

Keep original and provisioned observations in separate directories. Record Windows build, collection time, source hashes, tool versions, request outcomes and exact intervention. All later generated configurations are **controlled lab cases**, not independently sampled enterprise deployments.

## Initial case matrix

| Case | Changed prerequisite | Expected direct enrollment outcome | What this alone proves |
|---|---|---|---|
| Positive control | None | Issued | Enrollment prerequisites are met |
| Approval control | Manager approval required | Pending | Issuance gate affects this request |
| Signature control | Authorized signature required | Denied without signature | Signature gate affects this request |
| Enrollment control | Selected principal lacks template enroll | Denied | Template effective access is enforced |
| Publication control | Template not published on selected CA | Unsupported/denied | Publication is required |
| Policy-link control | Issuance-policy group link absent | May still issue | Issuance is not proof of group authorization |
| Authentication control | No authentication-capable EKU | May still issue | Issuance is not proof of successful authentication |
| Remote membership pair | Change membership path, same local template | Issued versus denied if no alternate grant | Principal-conditioned path matters |

Freeze expected outcomes and task definitions before attempts. Save unexpected outcomes and errors without relabeling them to match predictions. Positive and negative members of a family must remain in the same split. Expand beyond one hand-constructed family before reporting detection rates or confidence intervals.

## Tool comparison rules

Use the same principal and configuration snapshot, with exact executable/version and arguments saved. Certipy enumeration, CA request outcomes and graph model predictions answer different questions; define an explicit mapping before reporting accuracy. Count an unsupported output separately from negative. Include collection and feature-extraction time in any deployment-cost claim. Never substitute a local rule implementation for a branded tool.

## Submission gate

A working CA and several expected enrollment outcomes are integration evidence, not a generalization benchmark. A high-end empirical submission still needs independently configured environments, a larger locked test set, meaningful competing methods, realistic missing/overlapping conditions and a contribution beyond reproducing a known locality limitation.
