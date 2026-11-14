# Overall manuscript arrangement and design review

Reviewed: 14 November 2026. Scope: the current GOAD manuscript PDF, active LaTeX sources, shared style, figures, tables, equations, listing, algorithm, declarations and bibliography. This is a presentation review, not a new assessment of experimental correctness or journal acceptance.

## Overall assessment

The manuscript now has a coherent IEEE visual identity. The new figures use a consistent visual language, table widths match their floats, and the page grid and typography are consistent. The main remaining weakness is information density: substantial space is devoted to derivations, experimental history and repeated qualifications before the central evidence can be understood as a whole. Further improvement should prioritize the order and economy of the argument, rather than adding decoration or reducing the font size.

The submitted-paper narrative should eventually describe the final study directly. Phrases about an earlier draft, corrected historical implementation, a newly added audit or superseded inventory sometimes make the paper read like a research log. Those details matter for evidence integrity, but they can be consolidated into methods notes, artifact documentation or a clearly separated historical-baseline discussion. They should not simply be deleted where they qualify a result.

## Presentation fixes applied in this pass

| Finding | Action | Result |
| --- | --- | --- |
| The XML listing began with a few lines at the bottom of a column and continued on the next page. | Make this listing a single column-width float. Improve line-number size. | The selected record appears as one complete block. |
| A proof opened with only its introductory sentence before the next page. | Reserve five lines before a proof opening. | The opening now stays with the beginning of its argument. A long proof can still continue across pages. |
| The CIPG algorithm appeared before its notation and introduction. | Keep the algorithm in the text at its source position. | Notation precedes pseudocode, followed by the interpretation paragraph. |
| The formal relation vocabulary was squeezed into a small mathematical display. | Break the same ten relation names across four aligned lines. | Larger, readable names without changing the schema. |
| Long remediation expressions lost readability when scaled to the column. | Break the cost cases and define a residual-graph abbreviation for the objective and follower response. | Equivalent expressions fit more naturally. |
| The evaluation mixed many studies under long run-in labels. | Introduce shorter, numbered third-level headings for the major study groups. | Readers can distinguish the literal-model study, component studies, policy matrices, patch controls, SQL comparison, transfer cohort and collection pilot. |
| The validity section used four very long indented numbered items. | Use numbered third-level headings and full-width paragraphs. | More usable text width and clearer topic boundaries. All substantive qualification text is retained. |
| Author contributions ran together as one dense block. | Separate the three author entries. | Names and assigned roles are easier to scan. |
| The introduction's roadmap repeated every section title. | Replace it with a shorter, cross-referenced roadmap. | Less navigation overhead without changing section order. |
| The last page contained only a short continuation of the references. | Balance the final columns, in combination with the improved text flow. | The current build has 21 pages rather than the preceding 22-page table-only build. |

The document class, page geometry, title, authors, section order, four figure designs and table values are preserved. Standard IEEE headings and the bold abstract are intentional template behavior; they were not replaced with a separate visual theme.

## Remaining improvements, in priority order

### 1. Give the reader an early evidence map

The evaluation distinguishes historical synthetic benchmarks, corrected learning audits, frozen lineage histories, four Windows intervention matrices, the transfer workload and collection pilots. A reader currently assembles the relationships from several pages of text and captions. A compact study map, replacing some repeated explanatory prose, would help: study, environment, observation unit, sample size, outcome, and relevant table. It should separate certificate cases from authentications, histories, graph/budget instances and seeds. Do not sum incompatible units or duplicate the existing tables just to add another exhibit.

### 2. Rebalance the exposition around the main contribution

The learning theorem and its proof occupy substantial early space, while the abstract emphasizes certificate-specific evidence handling. The learning experiment also finds no classification advantage for gating. Consider retaining the theorem statement and practical implication in the main text while moving the detailed proof to an appendix, if the eventual journal permits it. That is a substantive organization decision, so this pass preserves the current main-body proof and section order.

### 3. Separate final results from the history of corrections

Several passages explain what the earlier generator, earlier draft or historical implementation got wrong. Present the final evaluated implementation first, then distinguish historical baselines in a consistent methods note. Keep correction details that are necessary to understand a number or a retained artifact. Avoid repeating the same correction in methods, results, discussion and conclusion.

### 4. Shorten repeated result qualifications through structure

The manuscript repeatedly restates that synthetic outcomes do not establish enterprise effectiveness, that symbolic labels are not Windows ground truth, and that the gate is not authorization. These boundaries are scientifically important. A central assumptions/scope subsection plus focused qualifications near each result could reduce repetition while making the boundaries easier to find. Do not remove qualifications merely to shorten the paper.

### 5. Review the title and abstract together after the narrative is settled

The three-line title is visually acceptable, but long. It gives substantial prominence to bilinear gating, whereas the strongest positive results concern evidence linkage and controlled certificate use. Aligning the title with the final contribution would improve the first-page message. The abstract is dense but follows IEEE styling; it would benefit more from selective editorial compression than from changing its font or weight. No title, abstract or claim was changed here.

### 6. Keep captions informative without repeating the whole methods section

The captions identify units and scope, which is valuable. Some are still long enough to compete with the table or figure. A later editing pass can place shared experimental conditions in the surrounding methods and retain only the object, denominator, uncertainty convention and essential qualification in each caption. Avoid shrinking captions to recover space.

### 7. Keep long identifiers and notation under review

AD attribute names, policy strings and mathematical expressions remain naturally difficult in narrow columns. The longest schema and remediation displays were improved. Other derivatives, long theorem headings and code identifiers should be checked again after any future prose revision. The existing automatic equation-fit command is a fallback, not a substitute for deliberate line breaks. Avoid globally reducing mathematical type to conceal a layout problem.

### 8. Make supplementary material a deliberate editorial choice

Raw record excerpts, detailed proofs and extended historical audits are possible appendix candidates. Their placement should follow the target journal's requirements and the central argument. Moving them solely to reduce page count would be a poor criterion. No evidence, figure, result table or limitation was removed in this pass.

### 9. Keep export versions distinct

The current PDF and local LaTeX source bundle are updated. `main.docx` predates these revisions and is not a synchronized version of this layout. A Word submission would need its own export and Microsoft Word desktop verification. The public research archive is a frozen evidence release and was not republished for these visual changes.

## Page-level review

The full pre-change 22-page PDF was inspected, including the figure/table pages reviewed in the preceding passes. The revised 21-page document was checked through complete contact sheets and focused page proofs.

| Final pages | Assessment |
| --- | --- |
| 1--2 | Consistent title/author/abstract styling; introduction and contribution list flow normally. The short roadmap reduces repetition. Schema now accompanies a readable formal vocabulary. The first-page prose remains dense. |
| 3--4 | Threat-model text and the complete XML record remain in order; no fragment of the listing is left at a column foot. Long identifiers remain a natural narrow-column constraint. |
| 4--6 | Architecture, theorem and proof use consistent notation and styling. Proof opening improved. The amount of main-body proof is still an editorial concern. |
| 6--8 | CIPG diagram, invariant definitions, notation and algorithm follow a more logical reading sequence. The algorithm remains readable and complete. |
| 9--10 | Budget formulation and complexity discussion are consistent; long cost/optimization expressions now wrap more deliberately. |
| 11--16 | Tables retain their adaptive widths and values. Numbered study headings improve navigation. The concentration of studies still warrants an early evidence map. |
| 17--18 | Remediation chart, detailed comparison and timing table are consistent. The chart and table are complementary, though the surrounding narrative could be shorter. |
| 19--20 | Validity topics and individual author contributions are easier to scan. Declarations remain distinct and readable. |
| 21 | References finish in balanced columns; the sparse extra page is removed. Long URLs still wrap, as expected in this format. |

## Verification and limits

The build and PDF checks, source/export hashes, table numerical preservation, pagination and reference checks are recorded in `validation.json`; `build.log` preserves compiler output. Before/after PNGs and contact sheets support the visual review. `before/` is the rollback snapshot for this pass.

The review does not establish Q1 readiness or certify that all presentation preferences will match an unspecified journal. The inherited Tectonic bibliography consistency/rerun warning and some typography warnings remain recorded; they are separate from a successful PDF build. No new experiments were performed, no bibliography entries were removed, and no public artifact was changed.
