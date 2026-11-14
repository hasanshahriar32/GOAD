"""Generate the literal bilinear study table from verified checkpoints."""
import hashlib
import json
import math
from pathlib import Path
from evidence_table_layout import style_evidence_tables

ROOT=Path(__file__).resolve().parents[2]
base=ROOT/"thesis_research/results/lineage_constraints/2026-11-10"
verification=base/"bilinear_study_verification.json";data=json.loads(verification.read_text())
manifest=base/"bilinear_study/manifest.json"
if data["status"]!="passed" or hashlib.sha256(manifest.read_bytes()).hexdigest()!=data["input_manifest_sha256"]:raise ValueError("Verification input differs")
for name,expected in json.loads(manifest.read_text()).items():
    if hashlib.sha256((manifest.parent/name).read_bytes()).hexdigest()!=expected:raise ValueError("Study artifact differs")
text=r'''% Generated from verified literal bilinear checkpoint predictions.
\begin{table*}[ht]
\centering
\caption{Literal two-layer attention comparison: mean accuracy (\%) and population standard deviation across three seeds, with 150 paired families per test cohort per seed. Every arm starts with identical parameter values. Augmentation is matched; typed whole-graph hashes and family IDs are disjoint across splits within each seed.}
\label{tab:literal_bilinear}
\small
\begin{tabular}{llrrr}
\toprule
Model & Augmentation & IID & Long paths & Larger background \\
\midrule
'''
for name,label in (("additive","Additive attention"),("bilinear","Bilinear attention")):
    for augmentation in ("0","0.3"):
        cells=[]
        for split in ("iid","long_paths","larger_background"):
            r=data["by_arm_and_split"][name+"/aug="+augmentation+"/"+split]
            # Three fixed seeds: convert the saved sample SD to the same
            # finite-set population convention as the remediation table.
            population_sd = r['accuracy_sample_sd'] * math.sqrt(2 / 3)
            cells.append(f"${100*r['accuracy_mean']:.2f} \\pm {100*population_sd:.2f}$")
        text+=" & ".join([label,augmentation]+cells)+" \\\\\n"
text+=r'''\bottomrule
\end{tabular}
\end{table*}
'''
output=ROOT/"manuscript/generated/bilinear_evidence.tex";output.write_text(style_evidence_tables(text))
(output.parent/"bilinear_evidence_manifest.json").write_text(json.dumps({"layout_sha256": hashlib.sha256((Path(__file__).parent/"evidence_table_layout.py").read_bytes()).hexdigest(),"verification_sha256":hashlib.sha256(verification.read_bytes()).hexdigest(),
    "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"output_sha256":hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+"\n")
print(output)
