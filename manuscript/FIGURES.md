# CertGraph manuscript figures

The four active figures share an original vector icon set, restrained blue/teal/ochre/rust palette, and explicit relationship routing. The LaTeX class, page grid, typography and section order are unchanged by this figure revision.

| Figure | Publication asset | Width | Purpose |
| --- | --- | --- | --- |
| Identity/PKI graph | `figures/verified_identity_schema.pdf` | One column | Six formal node types and ten relation types, with an illustrative topology and permission key |
| Learning architecture | `figures/certgraph_learning_architecture.pdf` | Two columns | Two four-head attention layers, gated self-skips, template readout and the literal bilinear mechanism |
| CIPG evidence flow | `figures/verified_evidence_pipeline.pdf` | Two columns | Independent collection, issuer-scoped linkage, retained evidence, revision and separate analysis outputs |
| Remediation comparison | `figures/verified_interdiction_results.pdf` | One column | Saved mean disconnection, population SD and adaptive-minus-static gains |

Every publication PDF has a same-name editable SVG and a 300 dpi PNG preview. SVG text, paths, symbols and connectors remain vector objects. The Python renderer is the authoritative source: manual edits to an exported SVG are not imported back automatically. The artwork does not require generated raster images or external icon libraries.

Regenerate from the repository root:

```bash
.venv/bin/python manuscript/scripts/generate_verified_review_figures.py
```

The compatibility entry point calls `scripts/render_certgraph_figures.py`; original reusable symbols are in `scripts/certgraph_vector_icons.py` (both paths relative to this manuscript directory). The renderer requires Matplotlib, Noto Sans and librsvg's `rsvg-convert`. Then compile from the manuscript directory with `bash compile.sh`.

`figures/verified_figures_manifest.json` binds the renderer, icon source, relevant manuscript sections, literal model implementation, saved numerical input, and all twelve exports by SHA-256. The chart reads `thesis_research/results/lineage_constraints/2026-11-10/interdiction_recheck_statistics/results.json` from the repository root. Its lower panel is a difference of the saved means, not a new experiment or an uncertainty estimate.

The learning drawing now describes the matched binary ESC1 study rather than the historical multiclass illustration. The schema is the formal vocabulary, not a claim that the learning experiment includes all six formal node types. CIPG icons represent logical evidence/analysis roles, not a measured machine inventory. Symmetric population SD bars can extend above 100%; they do not indicate an observed disconnection rate above 100%.

Original PNG artwork remains available. The pre-revision PDF, replaced figure exports, sections, and previous generator are preserved in `reviews/2026-11-14/figure_redesign/before/`. Also note that this repository's `manuscript/figures` is a symlink to `thesis_paper/figures`, so Git reports shared asset changes under the latter path.
