# Editable Microsoft Word manuscript

Open `../main.docx` in **Microsoft Word desktop**. This replaces the earlier PDF-derived export. It is built from the LaTeX source, not from PDF text extraction or page screenshots.

The document contains editable prose, real Word data tables, native Office Math (OMML) equations, and the four original figure images. Equations can be selected and edited using Word's Equation tools. Figure images remain image objects, as they are in the LaTeX source; their internal diagram elements are not Word shapes.

The export follows the current single-column A4 layout, one-inch margins, LaTeX text fonts, title block, dark-blue headings, running header, page-number fields, booktabs-style tables and numbered theorem/equation references. The bibliography uses the actual IEEEtran-generated `.bbl` text, with 35 entries. Cross-reference numbers are resolved during export rather than stored as live Word cross-reference fields.

## What has and has not been verified

- 427 native Office Math objects; 34 numbered display equations.
- 15 editable data tables, plus 34 borderless tables used to position display equations and their numbers.
- Four original image objects; six complete embedded font faces.
- Microsoft Open XML SDK 3.3.0 validation targeting Office 2019: **zero schema errors**. See `office_validation.json`.
- Font embedding data, equation numbers, table/image counts and manuscript-source hashes are checked separately.
- The LaTeX sources and `main.pdf` are unchanged.

**Exact 1:1 visual identity has not been established.** Microsoft Word desktop is not available in this environment for final rendering. An available LibreOffice renderer ignores the OMML font sizes on reimport and substitutes equation fonts; its pagination is not a reliable prediction of Word desktop. Schema validity confirms document structure, not visual identity.

Word and LaTeX have different line-breaking and float-placement rules. A few long equations are wrapped or reduced in size in the Word export so their complete mathematical content remains visible. The original PDF itself has an over-wide piecewise cost equation. These changes affect the Word layout only. The Word document is an editable counterpart, not a claim of a pixel-identical LaTeX facsimile.

## Regenerate

Compile requirements: Tectonic. Python dependencies can be isolated with uv:

```bash
uv run --with pypandoc-binary --with python-docx --with pymupdf python manuscript/scripts/export_docx.py
```

The exporter compiles LaTeX into a temporary directory to recover numbering and bibliography entries; it does not replace the manuscript PDF. `--aux /path/to/main.aux` reuses an existing matching LaTeX build for conversion development.

`export_manifest.json` records source hashes and structural checks. `ooxml_property_order.json` records property ordering checked with Microsoft's Open XML SDK, so the Python exporter can write valid properties without requiring .NET.

## Fonts and provenance

Complete font faces are embedded for further editing, rather than only the characters currently used. Original font files and license notices are included in `fonts/` in case a particular Word installation requires local font installation.

- TeX Gyre TermesX text faces: [CTAN newtx distribution](https://ctan.org/pkg/newtx).
- TeX Gyre Termes Math: [CTAN TeX Gyre Math distribution](https://ctan.org/pkg/tex-gyre-math).
- Latin Modern Mono: [CTAN Latin Modern distribution](https://ctan.org/pkg/lm).
- [Microsoft's Word font-part specification](https://learn.microsoft.com/en-us/openspecs/office_standards/ms-oe376/1663dabc-5d98-463f-889e-bcd9b77c3d34) describes the embedded-font format.

Original names, font data and license notices are retained. GUST and LPPL license texts are included alongside the fonts.
