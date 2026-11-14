# Manuscript figure revision

This revision applies the studied soccer_bot/npm vector-illustration workflow to the four active CertGraph figures. It changes artwork, corresponding captions, the figure renderer and local submission bundle. It preserves the IEEE document styling, title, section order, original PNG illustrations and scientific result inputs.

## Changes

1. **Formal identity graph:** replace the vocabulary-only card/list drawing with recognizable identity and PKI glyphs, typed membership/enrollment/issuance/trust links, a permission edge and the remaining relation vocabulary. Six node types and ten relation types match the formal definition. This is explicitly a schematic, not a newly evaluated graph.
2. **Learning architecture:** replace the crowded historical raster pipeline with a vector depiction of two four-head relational attention layers, separate gated self-skips, template readout and a bilinear-message inset. The caption now identifies the matched binary ESC1 experiment. It avoids retaining the old illustration's unsupported multiclass interpretation or presenting the sigmoid gate as exact authorization.
3. **CIPG evidence flow:** replace generic text cards with source/retention/certificate/analysis symbols, visible collection fan-in, issuer-scoped linkage, mutation context and a late-evidence revision route. Separate output branches show investigation and budgeted remediation planning without implying automatic production actuation.
4. **Remediation results:** use the same saved mean and population-SD values in a consistent palette and add a panel showing adaptive-minus-static mean gains. These are differences of saved measurements, not fabricated convergence trajectories or new experiments. The caption explains SD bars extending above 100%.

The graph and quantitative comparison remain one-column figures; the architecture and evidence-flow drawings span both columns. All four have editable SVG masters, vector PDFs and 300 dpi PNG previews. The authoritative renderer is `manuscript/scripts/render_certgraph_figures.py`, with original glyphs in `certgraph_vector_icons.py`; the previous generator entry point remains usable.

## Verification

- Independently recomputed plotted means, population SD and mean paired gains from all 120 saved graph/budget cases. Checked input hashes against the saved statistics record.
- Verified every source/export hash in the figure manifest. All twelve exports are byte-identical across repeated renders.
- Inspected PDF text bounds, replacement characters, embedded fonts and raster content: no out-of-bounds text, replacement characters, Type 3 fonts or raster images in the four figure PDFs; all fonts embedded.
- Rebuilt the manuscript and visually inspected figure pages 2, 5, 8 and 17. The manuscript remains 21 pages. No unresolved-reference markers, overfull-box warnings or missing-character warnings were found.
- Tectonic still reports a `main.bbl` consistency/rerun warning and typography warnings. The build completes and the rendered references are present; this is not a warning-free build claim.
- Updated and checked the existing local source ZIP, including all active figure assets, SVGs and renderer sources. Archive-only metadata from the previous local bundle is retained byte-for-byte. The public research archive was not modified.

See `validation.json` for dimensions, effective minimum font sizes and the local bundle hash. The saved `before/` directory contains the previous manuscript PDF, figure exports, generator, changed sections and source bundle. Regeneration/editing guidance is in `manuscript/FIGURES.md`.

The repository's `manuscript/figures` symlink points to `thesis_paper/figures`; modifications to those shared assets therefore appear under the latter path in Git. No unrelated thesis artwork was rewritten.
