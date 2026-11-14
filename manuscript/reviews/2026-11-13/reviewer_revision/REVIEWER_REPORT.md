# Reviewer report: *CertGraph: Cryptographic Invariant Provenance and Multiplicative Bilinear Gating for ADCS Escalation Interdiction*

**Recommendation: Major revision.** The certificate-evidence work is carefully done. The manuscript as a whole is not yet submission-ready, for the reasons below.

## 1. Reference section

I read the references as IEEE-style numeric. I checked formatting and consistency against the text. I could not verify existence or details of the 2026-dated sources ([12], [13], [20], [24], [26], [27]) and recommend you confirm them by DOI or URL.

**Most serious: citation and content mismatches** (these matter more than typography)
- **[32] is the wrong paper.** "Tactical provenance analysis for EDR systems" (S&P 2020) is RapSheet, but Section 7.1 cites it as **NodeMerge**. NodeMerge is a separate CCS 2018 paper.
- **[6] is cited as a GNN application** (Intro and 7.1), but its title is about fixed-parameter algorithms for attack-graph defense. [8] is reinforcement learning, and [28] and [29] are generic GCN and GAT papers, not cyber-defense applications.
- **[9] is cited for "human-in-the-loop preference elicitation"** (Section 7.3), but its title is "Limited query graph connectivity test."
- **[33] and [34] are cited as "network interdiction models."** [34] is multiterminal cuts and [33] is a security-games book.
- **[3], [4] and [5] have version or title problems.**
  - [5] cites Certipy releases "v2.0–v4.8.2", but your experiments run **Certipy 5.0.4**.
  - Please verify the exact title of [4]. The DEF CON talk title, as I remember it, ends "…accelerate red team operations".
- **Cross-check HADES [12].** I recall a USENIX Security 2025 version. If the TDSC paper is an extension, cite both. Also check [13]'s page range: pp. 8967–8984 in issue 4 looks odd.

**Formatting inconsistencies**

| Issue | Where | Fix |
|---|---|---|
| Thousands-space in page range | [9]: "pp. 20 718–20 725" | `20718–20725` |
| Author initials differ | Nguyen is "H. Nguyen" in [6], [9], [10], [11], [22] but "H. X. Nguyen" in [35] | Use one form |
| Access-date formats mixed | "accessed 2026-11-10" ([3], [26], [27]) vs "accessed November 10, 2026" ([14], [15], [23]) | IEEE: `Accessed: Nov. 10, 2026.` |
| Months not abbreviated or missing | [1] "June 2006"; [2], [16] have no month | `Jun. 2006`, `May 2008` |
| URL pattern differs | [5] has an inline URL with no `[Online]. Available:`; [16] uses `rfc-editor.org/...txt` while [1] uses `www.rfc-editor.org/rfc/...`; [20] has no URL | One pattern throughout |
| Publisher/location inconsistent | Only [35] ("New York, NY, USA: ACM"), [8] ("Springer, Cham") and [21] give it | Include for all or none |
| Proper nouns lowercased in titles | "kerberos" [1]; "windows" [3]; "active directory" [2], [4], [6], [8], [9], [22], [35] | Protect in BibTeX: `{A}ctive {D}irectory` |
| Editorial commentary inside entries | [3] "Compatibility and enforcement depend…", [20] "preprint, submitted…", [23], [24], [26] "vendor investigation, not a peer-reviewed…" | Move to the text |
| Author type mixed | [26] mixes "Microsoft Security Research" with named authors; [27] "Unit 42" vs "Palo Alto Networks" | Standardize corporate authors |
| Ranges | "[6], [7], [8], [9], [10], [11]" | IEEE: `[6]–[11]` |
| No DOIs | About 20 journal and conference entries | Add DOIs (Q1 journals expect them) |
| Missing pages/venue details | [11] pages; [19] pages and location; [4] city and date | Complete them |

**Style versus target journal.** Your front matter (CRediT, Data availability, Declaration of competing interest) follows Elsevier conventions, but the references are IEEE-style. Pick the target journal first, then use its template (`elsarticle-num` or `IEEEtran`). Let Zotero or BibTeX generate the list from Crossref data so it stays consistent.

**Corrected examples**
- **[9]:** M. Guo, M. Ward, D. Goel, A. Neumann, F. Neumann, and H. Nguyen, "Limited query graph connectivity test," in *Proc. AAAI Conf. Artif. Intell.*, vol. 38, no. 18, 2024, pp. 20718–20725, doi: \<add\>.
- **[3]:** Microsoft, "KB5014754: Certificate-based authentication changes on Windows domain controllers," Microsoft Support. Accessed: Nov. 10, 2026. [Online]. Available: \<URL\>
- **[20]:** R. Heinzl and M. Nissl, "SoK: Timestamps are not a time model: Rethinking temporal reasoning in host-based intrusion detection," arXiv:2610.35151, Oct. 2026.

**Coverage gaps**
- **Non-archival sources.** About 12 of 35 references are blogs, vendor pages, software or preprints ([2]–[5], [14], [15], [20], [23]–[27]). Reviewers will want more peer-reviewed support.
- **ESC taxonomy.** You claim ESC1–ESC15 scoping, but the only primary source is [2], which covers ESC1–ESC8. Cite the original write-ups for ESC9–ESC15.
- **Machine learning.** Missing R-GCN, GATv2, gated GNNs, and "shortcut learning" (Geirhos et al.), which are core to your Section 3 claims.
- **Provenance IDS and interdiction.** Missing provenance-based intrusion detection systems (Kairos, Holmes, Flash) and classical network-interdiction work (Wood; Israeli & Wood).
- **Software.** Cite Certipy, Sigma and pySigma as software, with version and archived DOI, not only as GitHub URLs.

## 2. Major scientific concerns

1. **The title and Section 3.3 contradict the results.** Section 3.3 is headed "the Multiplicative Gating Cure". Table 2 shows bilinear and additive models with identical classifications, and both miss all 450 long-path positives. The gating contribution should be reframed as a negative or neutral result, or retitled. The Section 6 RQ1 phrasing "eliminate shortcut memorization" has the same problem.
2. **Internal inconsistency in the headline number.** The Intro reports 0.00% (0/63) on hard negatives. Section 6.3 reports **41/63** safe-label agreement.
3. **The static GNN evidence is weak.**
   - Labels come from the same symbolic rule used to generate the data.
   - There are only 22 unique training inputs per seed, 21 of them also in validation.
   - There are no real-world graphs, for example BloodHound or GOAD exports.
   - I suggest moving the GNN to an appendix or adding a real-data evaluation.
4. **Theorem 3.1 does not cover the model as defined.** Eq. 11's attention uses target features, which the theorem's hypotheses exclude. The authors acknowledge this. The result is close to trivial: no self-loop implies no dependence on own features.
5. **"Stackelberg" is a misnomer.** Your own text says the method gives no equilibrium certificate and that the utility ignores which path the follower picks. This is a sequential multicut heuristic. In the 60-case audit the corrected version matches the optimum in 43/60 cases, below the historical version's 46/60. At B=24 the improvement is not significant (Holm-adjusted p = 0.25 under both tests; I spot-checked the Holm arithmetic and it is consistent). Theorem 5.1 is correctly presented as specializing known hardness.
6. **Scale of live evidence.** There are 72 certificate cases, mostly ESC1, on one Windows image family, with one split-actor pilot. No HADES or Splunk was actually executed. Claims should be limited to "controlled lab outcomes", as the manuscript mostly does.
7. **Three loosely coupled contributions** (GNN, provenance, game theory). The paper needs one unifying thesis, or should be split. Section 7 also bundles related work, discussion and conclusion, and related work belongs near the front.

## 3. Specific technical and consistency issues

- **Wrong OID in the Intro.** It names `szOID_ENROLL_CERTTYPE_EXTENSION` as the SAN carrier, which is the template-name extension. Section 2.3 correctly uses `szOID_SUBJECT_ALT_NAME2`.
- **Poisson arithmetic.** λ = 2,000/hr ≈ 0.56/s gives 1 − e^(−λΔt) ≈ 99.6% at Δt = 10 s, but you report 0/50 collisions. State that the rate applies only to matching template and principal events.
- **Figure 1 versus Definition 2.1.** Figure 1 shows 5 classes and 16 relations (including ManageCA, LinksPolicy and PublishedTo). The definition has 6 node types and 10 edge types.
- **Figure 3 claims.** Unsupported by any experiment: "<2.4 s full sweep", "<25 ms per 1,000 nodes", "100K+ nodes, 1M+ edges".
- **Figure 4 (left).** Illustrative curves labeled as convergence to equilibrium should be removed.
- **Proposition 2.1 versus the text.** π_KDC omits CertIssuerName, yet the text relies on the KDC issuer. Listing 1 shows no Disposition or SKID, although π_CA includes them.
- **Table 9** lacks a "Self uses" column.
- **Standard deviations.** Population SD is used in Table 14 and sample SD in Table 2. Be consistent.
- **Identifier rendering.** Check that `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT`, `EDITF_ATTRIBUTESUBJECTALTNAME2` and similar names show their underscores. The extracted text drops them.

## 4. Presentation and compliance

- **Draft-history language** throughout: "earlier draft", "legacy", "historical", "now", "new". Rewrite as a clean paper, with a single appendix for corrections if needed.
- **Hedging.** The abstract and text over-qualify (nearly every sentence has a "does not establish…" clause), which buries the real contributions. Cut the abstract to about 200 words and state three claims plainly.
- **AI declaration.** It reads as a to-do ("The authors must review…"). Replace it with an actual declaration in the journal's format.
- **Data availability.** "Publication… has not been verified" will not pass review. Deposit code and artifacts in Zenodo or a similar archive with a DOI.
- **Missing sections.** Add affiliations, a corresponding author, a funding statement, and an ethics and dual-use statement (certificate abuse tooling, lab-only).
- **Typos.** "Cyberbed" and "Cyber-Range Cyberbed".

## 5. Strengths

- The issuer-scoped, possible-versus-definite evidence contract is a good idea.
- The paired fixed-CSR interventions are well controlled.
- The reported numbers are internally consistent. I checked 42 + 24 = 66 successes, 13 administrative uses, the Table 13 deltas, and the Holm values.
- Negative results are reported honestly.

If you'd like, I can look up the post-2026 references (HADES, CPD, the SoK, KB5126651, and the Microsoft and Unit 42 posts) to confirm they exist and the details match, or draft a cleaned `.bib` file in your target journal's style.