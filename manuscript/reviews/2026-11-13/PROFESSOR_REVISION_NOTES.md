# Professor review revision — 13 November 2026

The supplied reports show **2% overall similarity** (26 not-cited-or-quoted matches), **68% AI-writing detection**, and **77 replaced characters across 27 pages**. These are the submitted reports, not scores for the revised document. A new institutional Turnitin run is required to measure any change.

Revision principles: write from the actual methods and outcomes; remove unsupported superlatives; attribute prior work accurately; keep numerical results, negative results, experimental boundaries and AI-use disclosure. No paraphrasing service or detector-evasion procedure was used. A detector score cannot establish authorship or be guaranteed by editing.

The supplied HADES PDF is a published IEEE TDSC article, not an editable journal template. The revision uses IEEEtran journal formatting with two columns, IEEE title/author/abstract/index terms and standard heading styles. Its publication banner, DOI, copyright statement, author biographies and claims are not copied. Wide figures and tables span both columns.

Bibliography changes are recorded in `reference_audit.json`. Newly resolved journal records are retained in `verified_journal_metadata.json`. The three retained conference sources cover graph attention, order-incomplete query answers and the directed-multiway-cut hardness source; their publication types are not relabelled as journals. The manuscript now owns its bibliography rather than editing the shared thesis bibliography through a symlink. Standards, software and patch documentation remain where needed to support reproducibility.

The opening and related-work sections are rewritten around the actual certificate-attribution question. Claims that the historical 0/63 case establishes general GNN failure are removed from the introduction. General surveys are cited for general background, not presented as empirical replacements for specific removed conference results. Journal references are not added simply to make the bibliography longer.

The replaced-character flag needs interpretation: mathematical Greek and mathematical italic characters in a typeset PDF are legitimate notation. A source-script scan distinguishes those from accidental Cyrillic/Greek substitutions in prose; no mathematical symbols should be removed merely to change a detector score.

The existing Word exporter was written for the former single-column source. Its previous output is not an updated copy of this revision until the exporter is adapted and regenerated. Likewise, old readiness reports and submission archives describe earlier versions.

## Final revision status

The final bibliography contains **32 references: 17 journal articles, three conference papers, one book, nine miscellaneous technical sources and two reports**. Journals comprise 53.1% of all references and 81.0% of the 21 journal/conference/book sources. The three conference keys are `velickovic2018graph`, `amarilli2017order` and `garg1994multiway`. A background GCN citation was replaced by a clearly identified journal review; the proof retains its original directed-cut source instead of substituting a less relevant journal paper.

The abstract, introduction, contribution summary, related work and conclusion have substantive wording revisions. Other sections receive targeted wording and layout edits. Numerical experiments were not rerun, and no detector score is claimed. AI-use disclosure remains present. The final LaTeX build succeeds with 32 resolved bibliography entries, no overfull boxes and no unresolved citation/reference warnings. Standard font-substitution and underfull-spacing warnings remain.

Source and PDF scans find no Cyrillic characters. This does not prove that Turnitin will clear its replaced-character flag: legitimate Greek and mathematical italic glyphs must still be reviewed in its report. The 26 reported similarity matches and the AI-writing result require a fresh institutional review of the revised document. The supplied similarity report excludes bibliography, quotations and cited text.

The Word document and older submission archives are earlier versions; use the revised PDF and `submission_files/CertGraph_IEEE_Professor_Revision.zip` for this revision.
