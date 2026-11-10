"""Generate the matched diagnostic table without changing manuscript styling."""
import hashlib
import json
from pathlib import Path

ROOT=Path(__file__).resolve().parents[2]
base=ROOT/"thesis_research/results/lineage_constraints/2026-11-10"
verification=base/"gating_audit_verification.json"
data=json.loads(verification.read_text())
manifest=base/"gating_audit/manifest.json"
if hashlib.sha256(manifest.read_bytes()).hexdigest()!=data["input_manifest_sha256"]:raise ValueError("Verification manifest differs")
for name,expected in json.loads(manifest.read_text()).items():
    if hashlib.sha256((manifest.parent/name).read_bytes()).hexdigest()!=expected:raise ValueError("Gating artifact differs")
rows=[]
for key,label,augmentation in (("additive/aug=0","Additive","0"),("additive/aug=0.3","Additive","0.3"),
                               ("feature_channel_gate/aug=0","Feature-channel gate","0"),("feature_channel_gate/aug=0.3","Feature-channel gate","0.3")):
    r=data["pooled"][key]
    rows.append(f"{label} & {augmentation} & {100*r['exact_class_accuracy']:.2f}\\% & {r['false_positive']} & {r['false_negative']} \\\\")
text=r'''% Generated from independently verified saved checkpoint predictions.
\begin{table}[ht]
\centering
\caption{Matched two-step implementation diagnostic: 1,500 paired test cases per arm across three seeds, with 750 positive and 750 negative labels. Training archetypes repeat across splits; these are synthetic diagnostic outcomes, not enterprise rates.}
\label{tab:hard_negatives}
\small
\begin{tabular}{llrrr}
\toprule
Implementation & Augmentation & Correct & False positive & False negative \\
\midrule
'''+"\n".join(rows)+r'''
\bottomrule
\end{tabular}
\end{table}
'''
output=ROOT/"manuscript/generated/gating_evidence.tex";output.write_text(text)
(output.parent/"gating_evidence_manifest.json").write_text(json.dumps({"input_sha256":hashlib.sha256(verification.read_bytes()).hexdigest(),
    "source_sha256":hashlib.sha256(Path(__file__).read_bytes()).hexdigest(),"output_sha256":hashlib.sha256(output.read_bytes()).hexdigest()},indent=2)+"\n")
print(output)
