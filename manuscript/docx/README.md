# Word copy matching the compiled manuscript

`../main.docx` is converted directly from `../main.pdf`, using **pdf2docx**, the same approach implemented in `thesis_paper/convert_to_docx.py` for `thesis_paper/thesis.docx`. It prioritizes the LaTeX PDF's typography, page geometry, tables, figures, headers and equation appearance.

After compiling an updated PDF, regenerate from the repository root:

```bash
uv run --with pdf2docx python manuscript/scripts/export_docx.py
```

This replaces the earlier Pandoc export. The LaTeX sources and PDF are not changed. Overlap deletion is disabled to retain mathematical superscripts and other deliberately overlapping glyphs. Conversion uses a temporary output and replaces the Word file only after successful completion.

PDF-derived equations and complex layouts are less suitable for semantic editing than native Word equations. Word and LibreOffice may paginate differently; compare the final Word display with the PDF before submission. The PDF remains the authoritative typeset copy. Structural checks are recorded in `export_manifest.json`; they do not establish pixel-identical rendering in Word.
