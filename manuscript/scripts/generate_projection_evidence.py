"""Render the repeated same-query timing experiment in the current table style."""
import hashlib
import json
from pathlib import Path
from evidence_table_layout import style_evidence_tables

ROOT=Path(__file__).resolve().parents[2]
base=ROOT/"thesis_research/results/lineage_constraints/2026-11-10/projection_repeated"
for name,expected in json.loads((base/"manifest.json").read_text()).items():
    if hashlib.sha256((base/name).read_bytes()).hexdigest()!=expected:raise ValueError("Projection artifact differs")
rows=json.loads((base/"summary.json").read_text())
text=r'''% Generated from the frozen repeated same-task projection experiment.
\begin{table*}[ht]
\centering
\caption{Path-preserving projection with identical queried pairs: three graph seeds and five alternating-order timing repetitions per seed. Projection time is included. All reported severed-pair outcomes agree; these are hierarchical synthetic graphs on a shared host.}
\label{tab:scalability_bench}
\small
\begin{tabular}{rrrrr}
\toprule
Nodes & Queried pairs & Full (ms) & Projection + solve (ms) & Median ratio \\
\midrule
'''
for row in rows:
    text+=f"{row['nodes']:,} & {row['query_pairs_per_graph']} & {row['median_full_ms']:.2f} & {row['median_projection_inclusive_ms']:.2f} & ${row['median_ratio']:.2f}\\times$ \\\\\n"
text+=r'''\bottomrule
\end{tabular}
\end{table*}
'''
output=ROOT/"manuscript/generated/projection_evidence.tex";output.write_text(style_evidence_tables(text))
(output.parent/"projection_evidence_manifest.json").write_text(json.dumps({"layout_sha256": hashlib.sha256((Path(__file__).parent/"evidence_table_layout.py").read_bytes()).hexdigest(),"input_sha256":hashlib.sha256((base/"manifest.json").read_bytes()).hexdigest(),
    "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"output_sha256":hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+"\n")
print(output)
