# Manuscript layout revision — 13 November 2026

The journal text remains in IEEE two-column format. Tables are selected by their actual content: 14 use one column, and the remediation comparison spans both columns. The four existing diagrams/paired plots remain full width to keep their internal labels readable. Pseudocode is now one column, with its abbreviations and stored fields defined immediately before it.

Changes include compact table headers, controlled row spacing, explicit wrapping rather than blanket table scaling, shorter captions with qualifications retained in the surrounding evaluation text, and removal of repeated archive/recall columns whose common meaning is stated in the caption. The long provenance and cost expressions are broken over lines. Operational cost explanations are prose following the formula. The attention expression uses an explicitly defined scalar logit to display the same formula legibly.

Related Work, Discussion and Limitations, and Conclusion are separate sections. Unnumbered paragraph headings remove the repeated fourth-level letter prefixes and doubled colons. Bottom alignment no longer stretches paragraphs vertically to fill a column.

The evidence generators use `scripts/evidence_table_layout.py`, and generated manifests record its hash. All numerical bodies of the twelve generated evidence tables match the tracked research version. Original experiment inputs and outcomes were not changed. The regenerated document has no overfull boxes, oversized-float warnings or unresolved citation/reference warnings. See `LAYOUT_CHECKS.json` and `BUILD_LOG.txt`.

No QuillBot account was accessed and no manuscript text was uploaded to an external paraphrasing service. Wording was edited directly. This does not establish a new Turnitin result or independently human authorship. A fresh institutional review remains necessary. The older Word copy has not been regenerated for this layout.

The final math pass also removes artificial two-field alignment that was causing already split equations to shrink. Long lines now use centered multiline groups. The identity-discrepancy definition names its requester and authenticated identities before using them in the formula; no new detection condition is added. Equation numbering remains 1–34. The related-work, discussion and conclusion sequence now forms Sections VII, VIII and IX.

Subsequent language-editing update: QuillBot has now been used for seven selected abstract/introduction/conclusion passages. See `../quillbot/REVIEW.md` for actual service outputs, accepted edits and the updated disclosure. The earlier no-QuillBot statement describes the layout revision before that language pass.
