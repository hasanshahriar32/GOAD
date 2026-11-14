# CertGraph research artifact, version 0.2.0

CertGraph: Revisable Certificate Lineage for Active Directory Certificate Services under Incomplete Evidence

This version collects the original v0.1.0 research evidence, subsequent revision analyses and extended validation, and the current anonymous manuscript PDF and LaTeX sources. Nested archives preserve each study's original paths, manifests and verification instructions; extract each into a separate directory. The public archive retains the existing record's authorship. The manuscript itself uses anonymous author placeholders for review.

## Changes since 0.1.0

- Ambiguity/illustrative loss analysis and retained-history benchmark.
- Independent generated evidence-value study: 432 histories and 4,320 saved predictions.
- Incremental identity replay: 35,055 reference/guarded-SQL comparisons.
- Stronger remediation baselines on 60 saved small instances.
- Revised manuscript framing, organization and figures, including explicit negative results.

No new Windows certificate cases or investigator participants are claimed. The existing public laboratory evidence still covers 72 cases. SQL equivalence and stronger competing heuristics constrain novelty claims. Generated workloads and shared-host timings do not establish enterprise effectiveness or journal acceptance.

## Verification

The original archive README supplies six verification commands and dependency versions. Each supplement includes its own README and hash manifest. From a fresh extraction of the extended-validation ZIP run:

    python manuscript/scripts/verify_evidence_value.py
    python manuscript/scripts/verify_streaming_identity.py

The manuscript ZIP contains editable LaTeX and vector figure assets; the PDF is supplied separately. No DOCX is included because the existing Word export does not match the current manuscript.

Historical reports and manifests retain their original version-specific wording and source hashes. Statements that Zenodo was unchanged refer to the time those analyses were created. This outer release is the subsequent collection of those artifacts. Unkeyed file hashes establish integrity, not source authenticity.

The software retains the existing GNU GPL v3 license, with the public record's explicit GPL-3.0-only terms. Dependencies are not bundled. Private keys, authentication tokens, guest disks and complete credential-bearing capture trees are excluded.
