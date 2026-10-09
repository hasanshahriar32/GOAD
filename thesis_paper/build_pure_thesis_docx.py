#!/usr/bin/env python3
"""
Publication-Grade Pure Thesis DOCX Builder (from Source LaTeX)
Produces a 100% native Word document with:
  - 0 rasterized/image equations (Pure Office Math ML <m:oMath>)
  - Official HSTU frontmatter (Cover, Certificate, Declaration, Dedication,
    Acknowledgements, Abstract, TOC, List of Tables, List of Figures, Acronyms)
  - Full typography styling (Times New Roman, 12pt, 1.5 line spacing, black headings)
  - Centered figures with captions
  - Clean booktabs tables with equations in cells
  - Formatted algorithm boxes (Algorithms 1, 2, 3, 4)
  - Numbered IEEE citations [1], [2], ...
"""

import os
import sys
import re
import shutil
import subprocess
import docx
from docx.shared import Inches, Pt, RGBColor
from docx.enum.text import WD_ALIGN_PARAGRAPH
from docx.enum.table import WD_TABLE_ALIGNMENT
from docx.oxml import OxmlElement, parse_xml
from docx.oxml.ns import qn, nsdecls
from docxcompose.composer import Composer

# ─────────────────────────────────────────────────────────────
# 1. CROSS-REFERENCE & CAPTION MAPPINGS
# ─────────────────────────────────────────────────────────────
REF_MAP = {
    # Figures
    "fig:adcs_schema": "2.1",
    "fig:esc13_path": "2.2",
    "fig:certgraph_arch": "3.1",
    "fig:feature_heatmap": "4.1",
    "fig:conf_matrix": "5.1(a)",
    "fig:gnn_family": "5.1(b)",
    "fig:empirical_eval": "5.1",
    "fig:ablation_fig": "5.2",
    "fig:hn_fig": "5.3",
    "fig:attention_exp": "5.4",
    "fig:goad_topology": "6.1",
    "fig:goad_paths": "6.2",
    "fig:tool_comp": "7.1",
    "fig:robustness_fig": "7.2",
    "fig:scalability_fig": "7.3",
    "fig:neuro_pipeline": "8.1",
    "fig:game_sim": "9.1",
    # Tables
    "tab:esc_taxonomy": "2.1",
    "tab:dt_rules": "4.1",
    "tab:leakage_audit": "4.2",
    "tab:hyperparams": "5.1",
    "tab:cv_results": "5.2",
    "tab:per_class": "5.3",
    "tab:imbalanced_results": "5.4",
    "tab:ablation_results": "5.5",
    "tab:hn_results": "5.6",
    "tab:goad_results": "6.1",
    "tab:community_results": "6.2",
    "tab:transfer_matrix": "7.1",
    "tab:edge_perturbation": "7.2",
    "tab:scalability_table": "7.3",
    "tab:dichotomy": "8.1",
    "tab:threshold_sensitivity": "8.2",
    "tab:marl_hyperparams": "9.1",
    "tab:game_simulation_results": "9.2",
    # Algorithms
    "alg:certgraph_layer": "1",
    "alg:certgraph_infer": "2",
    "alg:neuro_symbolic": "3",
    "alg:greedy_sever": "4",
    # Theorems
    "thm:representation_preservation": "1",
    "thm:nphardness": "2",
    "proof:theorem1": "Theorem 1",
    "proof:theorem2": "Theorem 2",
    # Chapters
    "ch:introduction": "1",
    "ch:background": "2",
    "ch:methodology": "3",
    "ch:audit": "4",
    "ch:evaluation": "5",
    "ch:case_study": "6",
    "ch:robustness": "7",
    "ch:neuro_symbolic": "8",
    "ch:game_theory": "9",
    "ch:conclusion": "10",
    "app:proofs": "A",
    # Sections
    "sec:esc_scoping": "2.3.1",
    "sec:research_questions": "1.6",
    "sec:theorem1_discussion": "3.5",
    "sec:cv_results": "5.2",
    "sec:class_imbalance": "5.2.2",
    "sec:ablation_results": "5.3",
    "sec:hard_negatives": "5.4",
    "sec:attention_weights": "5.5",
    "sec:gnn_lateral_adversarial": "6.2.2",
    "subsec:threshold_sensitivity": "8.3",
    "sec:marl_architecture": "9.3",
    "sec:game_simulation": "9.5",
    "sec:defense_findings": "9.5.1",
    "sec:future_work": "10.3",
}

# Explicit caption replacements to ensure exact numbered captions
CAPTION_REPLACEMENTS = [
    # Ch 02
    (r"\\caption\{Heterogeneous Active Directory Certificate Services \(ADCS\) Graph Schema",
     r"\\caption{\\textbf{Figure 2.1:} Heterogeneous Active Directory Certificate Services (ADCS) Graph Schema"),
    (r"\\caption\{Comprehensive Comparative Taxonomy of ADCS Privilege Escalation Vectors",
     r"\\caption{\\textbf{Table 2.1:} Comprehensive Comparative Taxonomy of ADCS Privilege Escalation Vectors"),
    (r"\\caption\{Two-hop ESC13 privilege escalation attack path",
     r"\\caption{\\textbf{Figure 2.2:} Two-hop ESC13 privilege escalation attack path"),
    # Ch 03
    (r"\\caption\{CertGraph end-to-end Hetero-GAT pipeline",
     r"\\caption{\\textbf{Figure 3.1:} CertGraph end-to-end Hetero-GAT pipeline"),
    # Ch 04
    (r"\\caption\{Correlation and separability heatmap",
     r"\\caption{\\textbf{Figure 4.1:} Correlation and separability heatmap"),
    (r"\\caption\{Exact Decision Logic of the 7-Node Decision Tree Counterexample\.",
     r"\\caption{\\textbf{Table 4.1:} Exact Decision Logic of the 7-Node Decision Tree Counterexample."),
    (r"\\caption\{Empirical Distribution of Administrative Group Allocation Across 700 Independent Environments\.",
     r"\\caption{\\textbf{Table 4.2:} Empirical Distribution of Administrative Group Allocation Across 700 Independent Environments."),
    # Ch 05
    (r"\\caption\{Hyperparameter Specifications for Model Training and Optimization\.",
     r"\\caption{\\textbf{Table 5.1:} Hyperparameter Specifications for Model Training and Optimization."),
    (r"\\caption\{5-Fold Cross-Validation Performance Across 7 Evaluated Models",
     r"\\caption{\\textbf{Table 5.2:} 5-Fold Cross-Validation Performance Across 7 Evaluated Models"),
    (r"\\caption\{CertGraph 7-Class Confusion Matrix showing near-perfect diagonal alignment",
     r"\\caption{\\textbf{Figure 5.1(a):} CertGraph 7-Class Confusion Matrix showing near-perfect diagonal alignment"),
    (r"\\caption\{Macro-F1 and Accuracy baseline comparison across evaluated GNN architectures",
     r"\\caption{\\textbf{Figure 5.1(b):} Macro-F1 and Accuracy baseline comparison across evaluated GNN architectures"),
    (r"\\caption\{CertGraph Per-Class Precision, Recall, and F1 Scores under 5-Fold Cross-Validation\.",
     r"\\caption{\\textbf{Table 5.3:} CertGraph Per-Class Precision, Recall, and F1 Scores under 5-Fold Cross-Validation."),
    (r"\\caption\{Model Performance and Calibration Under Realistic Enterprise Class Imbalance",
     r"\\caption{\\textbf{Table 5.4:} Model Performance and Calibration Under Realistic Enterprise Class Imbalance"),
    (r"\\caption\{Systematic Architectural Ablation Study of CertGraph Components",
     r"\\caption{\\textbf{Table 5.5:} Systematic Architectural Ablation Study of CertGraph Components"),
    (r"\\caption\{Ablation study comparison highlighting the performance collapse",
     r"\\caption{\\textbf{Figure 5.2:} Ablation study comparison highlighting the performance collapse"),
    (r"\\caption\{Zero-Shot Adversarial Hard Negative Benchmark Results",
     r"\\caption{\\textbf{Table 5.6:} Zero-Shot Adversarial Hard Negative Benchmark Results"),
    (r"\\caption\{Zero-shot adversarial evaluation demonstrating the collapse",
     r"\\caption{\\textbf{Figure 5.3:} Zero-shot adversarial evaluation demonstrating the collapse"),
    (r"\\caption\{Localized 2-hop attention weight attribution",
     r"\\caption{\\textbf{Figure 5.4:} Localized 2-hop attention weight attribution"),
    # Ch 06
    (r"\\caption\{Architecture and trust relationship schema of the Game of Active Directory",
     r"\\caption{\\textbf{Figure 6.1:} Architecture and trust relationship schema of the Game of Active Directory"),
    (r"\\caption\{Comparative Auditing Performance on Live Ingested GOAD Topologies\.",
     r"\\caption{\\textbf{Table 6.1:} Comparative Auditing Performance on Live Ingested GOAD Topologies."),
    (r"\\caption\{End-to-end multi-hop compromise and privilege escalation attack graph",
     r"\\caption{\\textbf{Figure 6.2:} End-to-end multi-hop compromise and privilege escalation attack graph"),
    (r"\\caption\{Classification Accuracy on External Community-Collected Enterprise Topologies\.",
     r"\\caption{\\textbf{Table 6.2:} Classification Accuracy on External Community-Collected Enterprise Topologies."),
    # Ch 07
    (r"\\caption\{Comparative performance \(CertGraph vs BloodHound vs Certipy\)",
     r"\\caption{\\textbf{Figure 7.1:} Comparative performance (CertGraph vs BloodHound vs Certipy)"),
    (r"\\caption\{Bidirectional Domain Generalization Matrix Between Synthetic and ADSynth Topologies\.",
     r"\\caption{\\textbf{Table 7.1:} Bidirectional Domain Generalization Matrix Between Synthetic and ADSynth Topologies."),
    (r"\\caption\{GNN robustness evaluation under systematic edge deletions",
     r"\\caption{\\textbf{Figure 7.2:} GNN robustness evaluation under systematic edge deletions"),
    (r"\\caption\{Model Performance Degradation under Systematic Topological Edge Deletions\.",
     r"\\caption{\\textbf{Table 7.2:} Model Performance Degradation under Systematic Topological Edge Deletions."),
    (r"\\caption\{Scalability benchmarks showing empirical inference latency",
     r"\\caption{\\textbf{Figure 7.3:} Scalability benchmarks showing empirical inference latency"),
    (r"\\caption\{Inference Latency, Memory Footprint, and Throughput Across Enterprise Graph Scales\.",
     r"\\caption{\\textbf{Table 7.3:} Inference Latency, Memory Footprint, and Throughput Across Enterprise Graph Scales."),
    # Ch 08
    (r"\\caption\{Comparison of Statistical GNNs vs Symbolic Deduction in Identity Auditing\.",
     r"\\caption{\\textbf{Table 8.1:} Comparison of Statistical GNNs vs Symbolic Deduction in Identity Auditing."),
    (r"\\caption\{The Two-Tier Neuro-Symbolic Architecture, pairing fast CertGraph GNN screening",
     r"\\caption{\\textbf{Figure 8.1:} The Two-Tier Neuro-Symbolic Architecture, pairing fast CertGraph GNN screening"),
    (r"\\caption\{Empirical Threshold Sensitivity and Latency Trade-offs of the Two-Tier Auditor",
     r"\\caption{\\textbf{Table 8.2:} Empirical Threshold Sensitivity and Latency Trade-offs of the Two-Tier Auditor"),
    # Ch 09
    (r"\\caption\{Hyperparameter and Architectural Specifications for the Stackelberg MARL Defense Framework\.",
     r"\\caption{\\textbf{Table 9.1:} Hyperparameter and Architectural Specifications for the Stackelberg MARL Defense Framework."),
    (r"\\caption\{Autonomous cyber defense evaluation: \(a\) Notional two-timescale policy learning",
     r"\\caption{\\textbf{Figure 9.1:} Autonomous cyber defense evaluation: (a) Notional two-timescale policy learning"),
    (r"\\caption\{Evaluation of autonomous edge-interdiction defense policies",
     r"\\caption{\\textbf{Table 9.2:} Evaluation of autonomous edge-interdiction defense policies"),
]

# Formatted algorithm replacement tables preserving pure LaTeX math
ALG_REPLACEMENTS = {
    "alg:certgraph_layer": r"""
\begin{table}[ht]
\centering
\begin{tabular}{|p{0.95\textwidth}|}
\hline
\textbf{Algorithm 1: CertGraph Heterogeneous Attention Layer Forward Pass} \\
\hline
\textbf{Require:} Heterogeneous Multigraph $G = (V, E, \tilde{\mathcal{T}}_E)$; Input hidden states $\{h_v^{(l-1)}\}_{v \in V}$; Projection matrices $\{W_{\text{src}}^{(l, r)}, W_{\text{dst}}^{(l, r)}\}$; Attention vectors $\{\mathbf{a}_k^{(l, r)}\}$; Skip projections $\{W_{\text{skip}}^{(l, \tau)}\}$. \\
\textbf{Ensure:} Updated hidden representations $\{h_v^{(l)}\}_{v \in V}$. \\
\textbf{1:} \textbf{for} each canonical relation $r = (\tau_s, \text{rel}, \tau_t) \in \tilde{\mathcal{T}}_E$ \textbf{do} \\
\quad \textbf{2:} Compute projected representations: \\
\quad\quad \textbf{3:} $z_u^{(l, r)} \gets W_{\text{src}}^{(l, r)} h_u^{(l-1)}$ for all $u \in V_{\tau_s}$ \\
\quad\quad \textbf{4:} $z_v^{(l, r)} \gets W_{\text{dst}}^{(l, r)} h_v^{(l-1)}$ for all $v \in V_{\tau_t}$ \\
\quad \textbf{5:} \textbf{for} each attention head $k \in \{1, \dots, K\}$ \textbf{do} \\
\quad\quad \textbf{6:} \textbf{for} each edge $(u, r, v) \in E_r$ \textbf{do} \\
\quad\quad\quad \textbf{7:} $e_{vu}^{(k, l, r)} \gets \operatorname{LeakyReLU} \left( \mathbf{a}_k^{(l, r) T} [z_v^{(k, l, r)} \,\|\, z_u^{(k, l, r)}] \right)$ \\
\quad\quad \textbf{8:} \textbf{end for} \\
\quad\quad \textbf{9:} \textbf{for} each target node $v \in V_{\tau_t}$ \textbf{do} \\
\quad\quad\quad \textbf{10:} Normalize: $\alpha_{vu}^{(k, l, r)} \gets \frac{\exp(e_{vu}^{(k, l, r)})}{\sum_{w \in \mathcal{N}_r(v)} \exp(e_{vw}^{(k, l, r)})}$ \\
\quad\quad \textbf{11:} \textbf{end for} \\
\quad \textbf{12:} \textbf{end for} \\
\quad \textbf{13:} \textbf{for} each target node $v \in V_{\tau_t}$ \textbf{do} \\
\quad\quad \textbf{14:} Compute head concatenation: $\mu_{v, r}^{(l)} \gets \prod_{k=1}^K \left( \sum_{u \in \mathcal{N}_r(v)} \alpha_{vu}^{(k, l, r)} z_u^{(k, l, r)} \right)$ \\
\quad \textbf{15:} \textbf{end for} \\
\textbf{16:} \textbf{end for} \\
\textbf{17:} \textbf{for} each entity $v \in V$ \textbf{do} \\
\quad \textbf{18:} Semantic aggregation: $h_{v, \text{agg}}^{(l)} \gets \sum_{r \in \mathcal{R}_{\text{in}}(\tau(v))} \mu_{v, r}^{(l)}$ \\
\quad \textbf{19:} Additive residual skip: $\tilde{h}_v^{(l)} \gets h_{v, \text{agg}}^{(l)} + W_{\text{skip}}^{(l, \tau(v))} h_v^{(l-1)}$ \\
\quad \textbf{20:} Non-linear activation: $\bar{h}_v^{(l)} \gets \operatorname{ELU}(\tilde{h}_v^{(l)})$ \\
\quad \textbf{21:} Normalization \& Regularization: $h_v^{(l)} \gets \operatorname{Dropout}(\operatorname{LayerNorm}(\bar{h}_v^{(l)}), p = 0.2)$ \\
\textbf{22:} \textbf{end for} \\
\textbf{23:} \textbf{return} $\{h_v^{(l)}\}_{v \in V}$ \\
\hline
\end{tabular}
\end{table}
""",
    "alg:certgraph_infer": r"""
\begin{table}[ht]
\centering
\begin{tabular}{|p{0.95\textwidth}|}
\hline
\textbf{Algorithm 2: CertGraph Enterprise Vulnerability Screening and Risk Prioritization} \\
\hline
\textbf{Require:} Enterprise Active Directory Graph $G = (V, E)$; Trained CertGraph model $\mathcal{M}_\Theta$; Risk threshold $\tau_{\text{risk}} \in [0, 1]$. \\
\textbf{Ensure:} Prioritized list of high-risk certificate templates $\mathcal{R}_{\text{alerts}}$. \\
\textbf{1:} Extract node feature tensors $\{x_v\}_{v \in V}$ from LDAP and DACL attributes \\
\textbf{2:} Construct reverse relations $r^{-1}$ for all $r \in \mathcal{T}_E$ to form augmented graph $\tilde{G}$ \\
\textbf{3:} Initialize $h_v^{(0)} \gets x_v$ for all $v \in V$ \\
\textbf{4:} \textbf{for} layer $l = 1$ to $L=2$ \textbf{do} \\
\quad \textbf{5:} $\{h_v^{(l)}\}_{v \in V} \gets \operatorname{CertGraphLayerForward}(\tilde{G}, \{h_v^{(l-1)}\}_{v \in V}, \Theta^{(l)})$ \\
\textbf{6:} \textbf{end for} \\
\textbf{7:} Initialize empty alert queue $\mathcal{R}_{\text{alerts}} \gets []$ \\
\textbf{8:} \textbf{for} each published template $t \in V_{\text{Template}}$ \textbf{do} \\
\quad \textbf{9:} Forward embedding $h_t^{(L)}$ to classification head: $\hat{y}_t \gets \operatorname{Softmax}(W_2 \operatorname{ReLU}(W_1 h_t^{(L)} + b_1) + b_2)$ \\
\quad \textbf{10:} Compute composite risk score: $S_{\text{risk}}(t) \gets 1.0 - \hat{y}_t[\text{Safe}]$ \\
\quad \textbf{11:} Determine predicted vector: $c_{\text{pred}} \gets \operatorname{argmax}_{c} \hat{y}_t[c]$ \\
\quad \textbf{12:} \textbf{if} $S_{\text{risk}}(t) \ge \tau_{\text{risk}}$ and $c_{\text{pred}} \neq \text{Safe}$ \textbf{then} \\
\quad\quad \textbf{13:} Append $(t, c_{\text{pred}}, S_{\text{risk}}(t), \hat{y}_t)$ to $\mathcal{R}_{\text{alerts}}$ \\
\quad \textbf{14:} \textbf{end if} \\
\textbf{15:} \textbf{end for} \\
\textbf{16:} Sort $\mathcal{R}_{\text{alerts}}$ in descending order of risk score $S_{\text{risk}}(t)$ \\
\textbf{17:} \textbf{return} $\mathcal{R}_{\text{alerts}}$ \\
\hline
\end{tabular}
\end{table}
""",
    "alg:neuro_symbolic": r"""
\begin{table}[ht]
\centering
\begin{tabular}{|p{0.95\textwidth}|}
\hline
\textbf{Algorithm 3: Two-Tier Neuro-Symbolic Vulnerability Auditor} \\
\hline
\textbf{Require:} Active Directory Graph $G = (V, E)$; Trained CertGraph model $\mathcal{M}$; Risk screening threshold $\tau_{\text{threshold}} \in (0, 1)$; Low-privileged user set $V_{\text{low-priv}}$. \\
\textbf{Ensure:} Confirmed vulnerability alerts $\mathcal{A}_{\text{verified}}$ with deterministic proof traces. \\
\textbf{1:} Initialize alert queue $\mathcal{A}_{\text{verified}} \gets []$ \\
\textbf{2:} \textbf{Tier 1: Fast Inductive Neural Screening} \\
\textbf{3:} Compute model logits across all published templates: $\mathbf{Z} \gets \mathcal{M}(G)$ \\
\textbf{4:} Compute risk vector: $\mathbf{S}_{\text{risk}} \gets 1.0 - \operatorname{Softmax}(\mathbf{Z}, \text{dim}=-1)[:, \text{Safe}]$ \\
\textbf{5:} Identify candidate suspects: $\mathcal{Q}_{\text{suspect}} \gets \{t \in V_{\text{Template}} \mid \mathbf{S}_{\text{risk}}[t] \ge \tau_{\text{threshold}}\}$ \\
\textbf{6:} \textbf{Tier 2: Targeted Deductive Symbolic Verification} \\
\textbf{7:} \textbf{for} each template $t \in \mathcal{Q}_{\text{suspect}}$ \textbf{do} \\
\quad \textbf{8:} Predicted class: $c \gets \operatorname{argmax}_k \mathbf{Z}[t, k]$ \\
\quad \textbf{9:} Extract 2-hop backward authorization subgraph: $G_t \gets \operatorname{ExtractSubgraph}(G, t, \text{hops}=2)$ \\
\quad \textbf{10:} Execute targeted BFS verification: $(\text{is\_valid}, \text{proof\_trace}) \gets \operatorname{SymbolicBFS}(G_t, V_{\text{low-priv}}, t, c)$ \\
\quad \textbf{11:} \textbf{if} $\text{is\_valid} = \text{True}$ \textbf{then} \\
\quad\quad \textbf{12:} Append $(t, c, \mathbf{S}_{\text{risk}}[t], \text{proof\_trace})$ to $\mathcal{A}_{\text{verified}}$ \\
\quad \textbf{13:} \textbf{else} \\
\quad\quad \textbf{14:} Log anomalous configuration: $\operatorname{LogHardNegative}(t, c, \mathbf{S}_{\text{risk}}[t])$ \\
\quad \textbf{15:} \textbf{end if} \\
\textbf{16:} \textbf{end for} \\
\textbf{17:} \textbf{return} $\mathcal{A}_{\text{verified}}$ \\
\hline
\end{tabular}
\end{table}
""",
    "alg:greedy_sever": r"""
\begin{table}[ht]
\centering
\begin{tabular}{|p{0.95\textwidth}|}
\hline
\textbf{Algorithm 4: Greedy Capacity-Disruption Edge Severing Heuristic} \\
\hline
\textbf{Require:} Active Directory Graph $G = (V, E)$; Forbidden pairs $\mathcal{P}_{\text{forbidden}}$; Disruption cost function $c: E \to \mathbb{R}^+$; Maximum budget $B_{\text{ops}}$. \\
\textbf{Ensure:} Reconfigured graph $G' = (V, E \setminus E_{\text{cut}})$ with severed attack paths. \\
\textbf{1:} Initialize edge cut set $E_{\text{cut}} \gets \emptyset$, cumulative disruption $C_{\text{total}} \gets 0$ \\
\textbf{2:} \textbf{while} $\exists (s, t) \in \mathcal{P}_{\text{forbidden}} \text{ with path } \mathcal{P} \text{ from } s \text{ to } t \text{ in } G$ \textbf{do} \\
\quad \textbf{3:} Compute path centrality across all active paths: $\forall e \in E, \, \phi(e) \gets \sum_{\mathcal{P} \in \Pi(\mathcal{P}_{\text{forbidden}})} \mathbb{I}(e \in \mathcal{P})$ \\
\quad \textbf{4:} Compute cost-efficiency ratio for each candidate edge: $\rho(e) \gets \frac{\phi(e)}{c(e)}$ \\
\quad \textbf{5:} Identify optimal candidate: $e^* \gets \operatorname{argmax}_{e \in E \setminus E_{\text{cut}}} \rho(e)$ \\
\quad \textbf{6:} \textbf{if} $C_{\text{total}} + c(e^*) > B_{\text{ops}}$ \textbf{then} \\
\quad\quad \textbf{7:} \textbf{break} (Budget constraint reached) \\
\quad \textbf{8:} \textbf{end if} \\
\quad \textbf{9:} Sever edge: $E \gets E \setminus \{e^*\}$ \\
\quad \textbf{10:} Update sets: $E_{\text{cut}} \gets E_{\text{cut}} \cup \{e^*\}$, $C_{\text{total}} \gets C_{\text{total}} + c(e^*)$ \\
\textbf{11:} \textbf{end while} \\
\textbf{12:} \textbf{return} $G' = (V, E), E_{\text{cut}}, C_{\text{total}}$ \\
\hline
\end{tabular}
\end{table}
"""
}

def preprocess_latex_file(src_path, dst_path):
    with open(src_path, "r", encoding="utf-8") as f:
        content = f.read()

    # 1. Replace all cross references \ref{...}
    for ref_key, ref_val in REF_MAP.items():
        content = re.sub(r"\\ref\{" + re.escape(ref_key) + r"\}", ref_val, content)

    # 2. Replace figure and table captions
    for pat, repl in CAPTION_REPLACEMENTS:
        content = re.sub(pat, repl, content)

    # 3. Replace algorithm environments with formatted tables
    for alg_key, alg_tex in ALG_REPLACEMENTS.items():
        pat = r"\\begin\{algorithm\}\[ht\]\s*\\caption\{[^}]*\}\s*\\label\{" + re.escape(alg_key) + r"\}\s*\\begin\{algorithmic\}\[\d+\](.*?)(\\end\{algorithmic\}\s*\\end\{algorithm\})"
        content = re.sub(pat, lambda m: alg_tex, content, flags=re.DOTALL)

    # 4. Standardize sidewaysfigure / sidewaystable to figure / table
    content = re.sub(r"\\begin\{sidewaysfigure\}(\[[^\]]*\])?", r"\\begin{figure}[ht]", content)
    content = re.sub(r"\\end\{sidewaysfigure\}", r"\\end{figure}", content)
    content = re.sub(r"\\begin\{sidewaystable\}(\[[^\]]*\])?", r"\\begin{table}[ht]", content)
    content = re.sub(r"\\end\{sidewaystable\}", r"\\end{table}", content)

    # 5. Standardize all graphics widths to full textwidth
    content = re.sub(r"width=[\d\.]+\\textheight(,[^\]]*)?", r"width=1.0\\textwidth", content)
    content = re.sub(r"width=0\.\d+\\textwidth", r"width=1.0\\textwidth", content)

    with open(dst_path, "w", encoding="utf-8") as f:
        f.write(content)

def set_cell_margins(cell, top=60, bottom=60, left=100, right=100):
    tcPr = cell._tc.get_or_add_tcPr()
    tcMar = OxmlElement('w:tcMar')
    for m, val in [('top', top), ('bottom', bottom), ('left', left), ('right', right)]:
        node = OxmlElement(f'w:{m}')
        node.set(qn('w:w'), str(val))
        node.set(qn('w:type'), 'dxa')
        tcMar.append(node)
    tcPr.append(tcMar)

def remove_table_borders(table):
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        if child.tag.endswith('tblBorders'):
            tblPr.remove(child)
    tblBorders = OxmlElement('w:tblBorders')
    for b in ['top', 'left', 'bottom', 'right', 'insideH', 'insideV']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'none')
        tblBorders.append(node)
    tblPr.append(tblBorders)

def build_frontmatter_doc(output_path):
    """
    Constructs the official HSTU Front Matter document matching thesis.pdf.
    """
    doc = docx.Document()
    
    # A4 Margins: Left 1.25", Right 1.0", Top 1.0", Bottom 1.0"
    sec = doc.sections[0]
    sec.page_width = Inches(8.27)
    sec.page_height = Inches(11.69)
    sec.top_margin = Inches(1.0)
    sec.bottom_margin = Inches(1.0)
    sec.left_margin = Inches(1.25)
    sec.right_margin = Inches(1.0)

    def p(text="", size=12, bold=False, italic=False, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_before=0, space_after=6, line_spacing=1.5):
        par = doc.add_paragraph()
        par.alignment = align
        par.paragraph_format.space_before = Pt(space_before)
        par.paragraph_format.space_after = Pt(space_after)
        par.paragraph_format.line_spacing = line_spacing
        if text:
            r = par.add_run(text)
            r.font.name = "Times New Roman"
            r.font.size = Pt(size)
            r.bold = bold
            r.italic = italic
            r.font.color.rgb = RGBColor(0, 0, 0)
        return par

    # ─────────────────────────────────────────────────────────────
    # PAGE 1: COVER PAGE
    # ─────────────────────────────────────────────────────────────
    p("CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense",
      size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=16, space_after=18, line_spacing=1.2)
      
    p("Course Code: ECE 452        Course Title: Project and Thesis",
      size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18)
      
    p("Submitted By—", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=8)
    
    p("Student ID: 2002126        Level: 4, Semester: II", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, line_spacing=1.15)
    p("Student ID: 2002138        Level: 4, Semester: II", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=2, line_spacing=1.15)
    p("Student ID: 2102151        Level: 4, Semester: II", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14, line_spacing=1.15)
    
    # HSTU Logo
    logo_par = doc.add_paragraph()
    logo_par.alignment = WD_ALIGN_PARAGRAPH.CENTER
    logo_par.paragraph_format.space_before = Pt(6)
    logo_par.paragraph_format.space_after = Pt(14)
    if os.path.exists("figures/hstu_logo.png"):
        logo_par.add_run().add_picture("figures/hstu_logo.png", width=Inches(1.2))
        
    p("Submitted To—", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    p("Department of Electronics and Communication Engineering", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    p("in partial fulfillment of the requirements for the degree of", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    p("Bachelor of Science in Electronics and Communication Engineering", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=14)
    p("Hajee Mohammad Danesh Science and Technology University (HSTU)", size=13, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=3)
    p("Dinajpur-5200, Bangladesh", size=11, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=6)
    p("October, 2026", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0)
    
    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 2: CERTIFICATE
    # ─────────────────────────────────────────────────────────────
    p("Certificate", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)
    
    p("This is to certify that the thesis work entitled “CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense” is carried by the following ID numbers: 2002126, 2002138, 2102151. To the fullest extent of our knowledge, we assert that this undertaking is an authentic and original contribution to the field. We certify that this thesis has not been previously submitted for the award of any other degree or diploma at this or any other institution.",
      size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=20, line_spacing=1.5)
      
    p("Signed by the Final Examining committee:", size=12, bold=True, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=32)
    
    tbl_cert = doc.add_table(rows=3, cols=2)
    remove_table_borders(tbl_cert)
    tbl_cert.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_cert.autofit = False
    
    cert_rows = [
        ("………………………………………………\nChairman", "………………………………………………\nSupervisor"),
        ("………………………………………………\nExternal Member", "………………………………………………\nCo-Supervisor"),
        ("………………………………………………\nInternal Member", "")
    ]
    for idx, (c1, c2) in enumerate(cert_rows):
        row = tbl_cert.rows[idx]
        row.cells[0].width = Inches(3.0)
        row.cells[1].width = Inches(3.0)
        set_cell_margins(row.cells[0], top=100, bottom=180, left=40, right=40)
        set_cell_margins(row.cells[1], top=100, bottom=180, left=40, right=40)
        p1 = row.cells[0].paragraphs[0]
        p1.paragraph_format.line_spacing = 1.3
        r1 = p1.add_run(c1)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(11)
        r1.bold = True
        r1.font.color.rgb = RGBColor(0, 0, 0)
        if c2:
            p2 = row.cells[1].paragraphs[0]
            p2.paragraph_format.line_spacing = 1.3
            r2 = p2.add_run(c2)
            r2.font.name = "Times New Roman"
            r2.font.size = Pt(11)
            r2.bold = True
            r2.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 3: CANDIDATE'S DECLARATION
    # ─────────────────────────────────────────────────────────────
    p("Candidate's Declaration", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=18)
    
    p("We declare that the research presented in this thesis, entitled “CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense,” represents our own work conducted under the guidance of our supervisors in the Department of Electronics and Communication Engineering at Hajee Mohammad Danesh Science and Technology University (HSTU), Dinajpur-5200, Bangladesh.",
      size=12, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=12, line_spacing=1.5)
      
    p("We confirm that:", size=12, align=WD_ALIGN_PARAGRAPH.LEFT, space_after=8)
    
    points = [
        "This manuscript has not been submitted in whole or in part for any other degree or diploma at this or any other academic institution.",
        "All external ideas, datasets, software utilities, and mathematical formulations have been cited in accordance with standard academic referencing conventions.",
        "The experimental scripts, synthetic benchmark environments, and model implementations described in this work were developed in compliance with academic research standards and ethical computing practices."
    ]
    for idx, pt in enumerate(points, 1):
        par_pt = p(f"{idx}.  {pt}", size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=6, line_spacing=1.3)
        par_pt.paragraph_format.left_indent = Inches(0.25)
        
    p("", space_after=32)
    tbl_dec = doc.add_table(rows=1, cols=2)
    remove_table_borders(tbl_dec)
    tbl_dec.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_dec.autofit = False
    
    r0 = tbl_dec.rows[0]
    r0.cells[0].width = Inches(3.0)
    r0.cells[1].width = Inches(3.0)
    p_d1 = r0.cells[0].paragraphs[0]
    p_d1.paragraph_format.line_spacing = 1.3
    r_d1 = p_d1.add_run("Date: October, 2026\nPlace: HSTU, Dinajpur")
    r_d1.bold = True
    r_d1.font.name = "Times New Roman"
    r_d1.font.size = Pt(11)
    r_d1.font.color.rgb = RGBColor(0, 0, 0)
    
    p_d2 = r0.cells[1].paragraphs[0]
    p_d2.paragraph_format.line_spacing = 1.3
    r_d2 = p_d2.add_run("Student ID: 2002126\nStudent ID: 2002138\nStudent ID: 2102151\nDepartment of ECE, HSTU")
    r_d2.font.name = "Times New Roman"
    r_d2.font.size = Pt(11)
    r_d2.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 4: DEDICATION
    # ─────────────────────────────────────────────────────────────
    p("", space_before=120)
    p("Dedication", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=24)
    p("This thesis is dedicated to our beloved parents,\nwhose endless sacrifices, prayers, and unconditional love\nhave been the guiding light of our lives.",
      size=12.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=18, line_spacing=1.4)
    p("And to all our teachers and mentors,\nwho inspired our passion for computer science and scientific discovery.",
      size=12.5, italic=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_after=0, line_spacing=1.4)
      
    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 5: ACKNOWLEDGEMENTS
    # ─────────────────────────────────────────────────────────────
    p("Acknowledgements", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=16)
    
    p("We begin by thanking the Almighty for granting us the health, resolve, and clarity of thought to bring this undergraduate project and thesis to completion.",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.4)
    p("We wish to express our heartfelt gratitude to our thesis supervisor and co-supervisor in the Department of Electronics and Communication Engineering at Hajee Mohammad Danesh Science and Technology University (HSTU). Throughout the research process—from initial problem formulation and mathematical proofs to the debugging of graph neural networks and manuscript preparation—their constructive criticism, technical feedback, and steady encouragement were vital to our progress.",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.4)
    p("We also thank the Chairman and the faculty members of the Department of Electronics and Communication Engineering for their instruction, academic support, and the computing facilities provided to us over the course of our undergraduate studies.",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.4)
    p("This work builds heavily on the contributions of the broader security and machine learning research communities. In particular, we acknowledge Will Schroeder and Lee Christensen (SpecterOps) for their foundational analysis of ADCS vulnerabilities; Oliver Lyak, Andy Robbins, and the BloodHound team for their offensive graph tools; the creators of the Game of Active Directory (GOAD) testing environment; and the maintainers of PyTorch Geometric and NetworkX.",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.4)
    p("Finally, we are deeply grateful to our parents and families. Their patience, moral support, and sacrifices made our education possible. We also thank our classmates, lab partners, and friends whose discussions, technical debates, and camaraderie helped us navigate the challenges of completing this degree.",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=20, line_spacing=1.4)
      
    tbl_ack = doc.add_table(rows=1, cols=2)
    remove_table_borders(tbl_ack)
    tbl_ack.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_ack.autofit = False
    
    r_ack = tbl_ack.rows[0]
    r_ack.cells[0].width = Inches(3.0)
    r_ack.cells[1].width = Inches(3.0)
    p_a1 = r_ack.cells[0].paragraphs[0]
    p_a1.paragraph_format.line_spacing = 1.3
    r_a1 = p_a1.add_run("HSTU, Dinajpur\nOctober, 2026")
    r_a1.bold = True
    r_a1.font.name = "Times New Roman"
    r_a1.font.size = Pt(11)
    r_a1.font.color.rgb = RGBColor(0, 0, 0)
    
    p_a2 = r_ack.cells[1].paragraphs[0]
    p_a2.paragraph_format.line_spacing = 1.3
    r_a2 = p_a2.add_run("Student ID: 2002126\nStudent ID: 2002138\nStudent ID: 2102151\nDepartment of ECE, HSTU")
    r_a2.font.name = "Times New Roman"
    r_a2.font.size = Pt(11)
    r_a2.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 6: ABSTRACT
    # ─────────────────────────────────────────────────────────────
    p("Abstract", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14)
    
    p("Active Directory Certificate Services (ADCS) forms the cryptographic backbone of enterprise identity, issuing credentials for domain authentication and single sign-on. Misconfigured certificate templates, access control lists (ACLs), and issuance policies introduce systemic privilege escalation vectors (ESC1–ESC15+) that enable unprivileged accounts to compromise entire Active Directory domains. Signature-based scanners (e.g., Certipy, BloodHound) evaluate flags in isolation and incur high traversal overhead on large topologies. In this thesis, we present CertGraph, a heterogeneous Graph Attention Network (Hetero-GAT) that models enterprise identity as a typed multigraph G = (V, E, T_V, T_E) to detect structural escalation paths across core vectors (ESC1, ESC2, ESC3, ESC4, ESC9, and ESC13).",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.4)
      
    p("Grounding our evaluation in the security machine learning framework of Arp et al. (USENIX Security 2022), we identify and resolve three systemic pitfalls in synthetic identity datasets: positional index leakage, baseline feature asymmetry, and rule saturation. We prove mathematically (Theorem 1) that residual skip-connections are indispensable for preventing representation collapse on identity graphs; omitting them makes template representations independent of input flags, reducing classification Macro-F1 from 0.9986 to 0.4768. On an audited 700-environment enterprise benchmark evaluated under 5-fold cross-validation with Nadeau-Bengio corrected variance, CertGraph achieves a Macro-F1 of 0.9986, substantially outperforming flat classifiers (0.8600) and signature heuristics (0.7791).",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=8, line_spacing=1.4)
      
    p("However, when evaluated against an adversarial Zero-Shot Hard Negative suite (n = 63) containing benign templates with dangerous flags, pure neural models collapse to 1.59% accuracy due to shortcut learning on isolated attributes, whereas symbolic graph traversal achieves 84.13%. To resolve this dichotomy, we formulate a Two-Tier Neuro-Symbolic architecture pairing rapid GNN candidate screening (filtering > 89% of benign templates) with a localized symbolic verification oracle to eliminate false positives by construction. Finally, we model identity privilege revocation as a Stackelberg security game, prove its NP-hardness via reduction from Directed Multiway Cut, and demonstrate a greedy capacity-disruption heuristic that severs up to 68.6% of compromise paths under bounded operational budgets (p < 10^-8).",
      size=11.5, align=WD_ALIGN_PARAGRAPH.JUSTIFY, space_after=14, line_spacing=1.4)
      
    par_kw = p("", size=11, space_after=0)
    r_kwh = par_kw.add_run("Keywords: ")
    r_kwh.bold = True
    r_kwh.font.name = "Times New Roman"
    r_kwh.font.color.rgb = RGBColor(0, 0, 0)
    r_kwt = par_kw.add_run("Active Directory Certificate Services (ADCS), Graph Attention Networks, Heterogeneous Graphs, Identity and Access Management, Neuro-Symbolic Security, Autonomous Cyber Defense.")
    r_kwt.font.name = "Times New Roman"
    r_kwt.font.color.rgb = RGBColor(0, 0, 0)
    
    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGES 7-8: CONTENTS (TOC with OpenXML Dot Leader Tabs)
    # ─────────────────────────────────────────────────────────────
    p("Contents", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14)
    
    toc_entries = [
        ("List of Acronyms", "xiv", False, 0),
        ("1  Introduction", "1", True, 0),
        ("1.1  Enterprise Identity Fabric and Demise of Perimeter Security", "1", False, 1),
        ("1.2  The Economics and Anatomy of Identity-Based Lateral Movement", "2", False, 1),
        ("1.3  Active Directory Certificate Services: The Unseen Attack Surface", "3", False, 1),
        ("1.4  Capabilities and Limitations of Existing Auditing Tools", "4", False, 1),
        ("1.5  The Promise and Pitfalls of Machine Learning for Identity Security", "5", False, 1),
        ("1.6  Research Questions and Formal Objectives", "7", False, 1),
        ("1.7  Summary of Thesis Contributions", "7", False, 1),
        ("1.8  Thesis Organization and Roadmap", "8", False, 1),
        ("2  Literature Review and Domain Background", "10", True, 0),
        ("2.1  Evolution of Identity-Based Lateral Movement in Enterprise Networks", "10", False, 1),
        ("2.2  Graph-Theoretic Modeling of Active Directory Security", "11", False, 1),
        ("2.3  Graph Representation Learning in Security", "12", False, 1),
        ("2.4  Active Directory Architecture and Cryptographic Primitives", "15", False, 1),
        ("2.5  Active Directory Certificate Services (ADCS) Mechanics", "17", False, 1),
        ("2.6  Exhaustive Taxonomy of ADCS Vulnerability Classes (ESC1–ESC15)", "19", False, 1),
        ("2.7  Formal Threat Model", "21", False, 1),
        ("3  Formal Methodology and CertGraph Architecture", "23", True, 0),
        ("3.1  Mathematical Formalization of Enterprise Identity Multigraphs", "23", False, 1),
        ("3.2  Node Feature Vector Spaces and Semantic Encodings", "24", False, 1),
        ("3.3  The CertGraph Hetero-GAT Architecture", "27", False, 1),
        ("3.4  Formal Algorithmic Specifications", "30", False, 1),
        ("3.5  Theoretical Analysis: Intrinsic Attribute Preservation and Bounds", "31", False, 1),
        ("3.6  Computational Complexity and Scalability Analysis", "33", False, 1),
        ("4  Forensic Audit: Unmasking Experimental Illusions in Security ML", "35", True, 0),
        ("4.1  The Methodological Crisis of Security Machine Learning", "35", False, 1),
        ("4.2  The Four Experimental Illusions", "36", False, 1),
        ("4.3  Complete Generator Sanitization and Protocol Redesign", "40", False, 1),
        ("4.4  Statistical Verification of Generator Sanitization", "40", False, 1),
        ("4.5  Methodological Guidelines for Security Graph Learning", "41", False, 1),
        ("5  Empirical Evaluation and Benchmarks", "43", True, 0),
        ("5.1  Experimental Configuration and Benchmarking Setup", "43", False, 1),
        ("5.2  In-Distribution 5-Fold Cross-Validation", "44", False, 1),
        ("5.3  Systematic Architectural Ablation Studies", "49", False, 1),
        ("5.4  The Zero-Shot Adversarial Hard Negative Benchmark", "50", False, 1),
        ("5.5  Attention Weight Explainability and Graph Interpretability", "52", False, 1),
        ("6  Real-World Case Study: Game of Active Directory (GOAD)", "54", True, 0),
        ("6.1  Multi-Domain Environment Topology and Target Scope", "54", False, 1),
        ("6.2  End-to-End Attack Emulation", "57", False, 1),
        ("6.3  Comparative Auditing Performance on Live Ingested Topologies", "60", False, 1),
        ("6.4  Generalization to External Community Enterprise Topologies", "61", False, 1),
        ("7  Robustness, Scalability, and Deployment Considerations", "63", True, 0),
        ("7.1  Cross-Domain Generalization (ADSynth Benchmark)", "63", False, 1),
        ("7.2  Topological Noise Robustness and Incomplete Audits", "66", False, 1),
        ("7.3  Scalability, Memory Complexity, and Real-Time Inference", "68", False, 1),
        ("7.4  Enterprise Deployment Considerations", "70", False, 1),
        ("8  Neuro-Symbolic Hybridization for Identity Auditing", "71", True, 0),
        ("8.1  The Dichotomy of Statistical and Symbolic Security Reasoning", "71", False, 1),
        ("8.2  Two-Tier Neuro-Symbolic Architecture", "73", False, 1),
        ("8.3  Empirical Performance and Verification Overhead", "75", False, 1),
        ("8.4  Complexity and Efficiency Profiling", "76", False, 1),
        ("8.5  Algorithmic Specification of the Hybrid Pipeline", "77", False, 1),
        ("8.6  Enterprise Security Operations Center (SOC) Orchestration", "77", False, 1),
        ("9  Game-Theoretic Autonomous Defense and Edge Interdiction", "79", True, 0),
        ("9.1  From Passive Auditing to Active Autonomous Defense", "79", False, 1),
        ("9.2  The Stackelberg Security Game Formulation", "79", False, 1),
        ("9.3  Theoretical Complexity: NP-Hardness of Edge-Severing", "81", False, 1),
        ("9.4  Polynomial-Time Heuristic Approximation Algorithms", "82", False, 1),
        ("9.5  Convergence Dynamics via Two-Timescale Stochastic Approx.", "83", False, 1),
        ("9.6  Defense Evaluation and Remediation Trade-offs", "86", False, 1),
        ("10 Conclusion, Limitations, and Future Horizons", "89", True, 0),
        ("10.1 Summary of Thesis Contributions", "89", False, 1),
        ("10.2 Synthesis: Answers to Research Questions", "91", False, 1),
        ("10.3 Practical Implementation Playbook for Enterprise Defenders", "92", False, 1),
        ("10.4 Honest Limitations to Acknowledge", "93", False, 1),
        ("10.5 Ethical Considerations and Dual-Use Analysis", "94", False, 1),
        ("10.6 Future Research Horizons", "94", False, 1),
        ("10.7 Concluding Remarks", "95", False, 1),
        ("A  Formal Mathematical Proofs", "96", True, 0),
        ("A.1 Proof of Theorem 1: Intrinsic Attribute Preservation", "96", False, 1),
        ("A.2 Proof of Theorem 2: NP-Hardness of Access Interdiction", "101", False, 1),
        ("References", "104", True, 0)
    ]

    for title, page_no, is_chap, level in toc_entries:
        par = doc.add_paragraph()
        pPr = par._p.get_or_add_pPr()
        tabs = parse_xml(r'<w:tabs %s><w:tab w:val="right" w:leader="dot" w:pos="8640"/></w:tabs>' % nsdecls('w'))
        pPr.append(tabs)
        par.paragraph_format.line_spacing = 1.05
        par.paragraph_format.space_before = Pt(3 if is_chap else 0.5)
        par.paragraph_format.space_after = Pt(2 if is_chap else 0.5)
        if level == 1:
            par.paragraph_format.left_indent = Inches(0.2)
            
        r1 = par.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(10 if is_chap else 9.0)
        r1.bold = is_chap
        r1.font.color.rgb = RGBColor(0, 0, 0)
        
        r_tab = par.add_run()
        r_tab._r.append(parse_xml(r'<w:tab %s/>' % nsdecls('w')))
        
        r_p = par.add_run(str(page_no))
        r_p.font.name = "Times New Roman"
        r_p.font.size = Pt(10 if is_chap else 9.0)
        r_p.bold = is_chap
        r_p.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 9: LIST OF TABLES
    # ─────────────────────────────────────────────────────────────
    p("List of Tables", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14)
    
    lot_entries = [
        ("Table 2.1: Comprehensive Comparative Taxonomy of ADCS Privilege Escalation Vectors", "19"),
        ("Table 4.1: Exact Decision Logic of the 7-Node Decision Tree Counterexample", "38"),
        ("Table 4.2: Empirical Distribution of Administrative Group Allocation Across 700 Environments", "41"),
        ("Table 5.1: Hyperparameter Specifications for Model Training and Optimization", "44"),
        ("Table 5.2: 5-Fold Cross-Validation Performance Across 7 Evaluated Models on 700 Domains", "45"),
        ("Table 5.3: CertGraph Per-Class Precision, Recall, and F1 Scores under 5-Fold Cross-Validation", "45"),
        ("Table 5.4: Model Performance and Calibration Under Realistic Enterprise Class Imbalance", "48"),
        ("Table 5.5: Systematic Architectural Ablation Study of CertGraph Components", "49"),
        ("Table 5.6: Zero-Shot Adversarial Hard Negative Benchmark Results (n = 63 Environments)", "51"),
        ("Table 6.1: Comparative Auditing Performance on Live Ingested GOAD Topologies", "58"),
        ("Table 6.2: Classification Accuracy on External Community-Collected Enterprise Topologies", "61"),
        ("Table 7.1: Bidirectional Domain Generalization Matrix Between Synthetic and ADSynth Topologies", "65"),
        ("Table 7.2: Model Performance Degradation under Systematic Topological Edge Deletions", "67"),
        ("Table 7.3: Inference Latency, Memory Footprint, and Throughput Across Enterprise Graph Scales", "68"),
        ("Table 8.1: Comparison of Statistical GNNs vs Symbolic Deduction in Identity Auditing", "72"),
        ("Table 8.2: Empirical Threshold Sensitivity and Latency Trade-offs of the Two-Tier Auditor", "75"),
        ("Table 9.1: Hyperparameter and Architectural Specifications for Stackelberg MARL Defense", "85"),
        ("Table 9.2: Evaluation of Autonomous Edge-Interdiction Defense Policies Across 30 AD Topologies", "88")
    ]
    for title, page_no in lot_entries:
        par = doc.add_paragraph()
        pPr = par._p.get_or_add_pPr()
        tabs = parse_xml(r'<w:tabs %s><w:tab w:val="right" w:leader="dot" w:pos="8640"/></w:tabs>' % nsdecls('w'))
        pPr.append(tabs)
        par.paragraph_format.line_spacing = 1.05
        par.paragraph_format.space_before = Pt(1.5)
        par.paragraph_format.space_after = Pt(1.5)
        par.paragraph_format.left_indent = Inches(0.25)
        par.paragraph_format.first_line_indent = Inches(-0.25)
        
        r1 = par.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.0)
        r1.font.color.rgb = RGBColor(0, 0, 0)
        
        r_tab = par.add_run()
        r_tab._r.append(parse_xml(r'<w:tab %s/>' % nsdecls('w')))
        
        r_p = par.add_run(str(page_no))
        r_p.font.name = "Times New Roman"
        r_p.font.size = Pt(9.0)
        r_p.bold = True
        r_p.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 10: LIST OF FIGURES
    # ─────────────────────────────────────────────────────────────
    p("List of Figures", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14)
    
    lof_entries = [
        ("Figure 2.1: Heterogeneous Active Directory Certificate Services (ADCS) Graph Schema", "18"),
        ("Figure 2.2: Two-hop ESC13 privilege escalation attack path", "21"),
        ("Figure 3.1: CertGraph end-to-end Hetero-GAT pipeline", "27"),
        ("Figure 4.1: Correlation and separability heatmap of template configuration flags", "38"),
        ("Figure 5.1: Empirical classification results: (a) Confusion matrix; (b) GNN comparisons", "46"),
        ("Figure 5.2: Ablation study comparison highlighting performance collapse without skip-connections", "49"),
        ("Figure 5.3: Zero-shot adversarial evaluation demonstrating shortcut collapse of pure neural models", "50"),
        ("Figure 5.4: Localized 2-hop attention weight attribution for an ESC13 template", "52"),
        ("Figure 6.1: Architecture and trust relationship schema of the Game of Active Directory (GOAD)", "56"),
        ("Figure 6.2: End-to-end multi-hop compromise and privilege escalation attack graph across GOAD", "60"),
        ("Figure 7.1: Comparative performance across synthetic and ADSynth realistic tiered topologies", "65"),
        ("Figure 7.2: GNN robustness evaluation under systematic edge deletions and attribute noise", "66"),
        ("Figure 7.3: Scalability benchmarks showing empirical inference latency scaling near-linearly", "69"),
        ("Figure 8.1: The Two-Tier Neuro-Symbolic Architecture pairing fast GNN screening with BFS oracle", "74"),
        ("Figure 9.1: Autonomous cyber defense evaluation: policy learning dynamics and edge interdiction", "87")
    ]
    for title, page_no in lof_entries:
        par = doc.add_paragraph()
        pPr = par._p.get_or_add_pPr()
        tabs = parse_xml(r'<w:tabs %s><w:tab w:val="right" w:leader="dot" w:pos="8640"/></w:tabs>' % nsdecls('w'))
        pPr.append(tabs)
        par.paragraph_format.line_spacing = 1.05
        par.paragraph_format.space_before = Pt(2)
        par.paragraph_format.space_after = Pt(2)
        par.paragraph_format.left_indent = Inches(0.25)
        par.paragraph_format.first_line_indent = Inches(-0.25)
        
        r1 = par.add_run(title)
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.0)
        r1.font.color.rgb = RGBColor(0, 0, 0)
        
        r_tab = par.add_run()
        r_tab._r.append(parse_xml(r'<w:tab %s/>' % nsdecls('w')))
        
        r_p = par.add_run(str(page_no))
        r_p.font.name = "Times New Roman"
        r_p.font.size = Pt(9.0)
        r_p.bold = True
        r_p.font.color.rgb = RGBColor(0, 0, 0)

    doc.add_page_break()

    # ─────────────────────────────────────────────────────────────
    # PAGE 11: LIST OF ACRONYMS (Borderless 2-Column Table, No Blank Spill)
    # ─────────────────────────────────────────────────────────────
    p("List of Acronyms", size=18, bold=True, align=WD_ALIGN_PARAGRAPH.CENTER, space_before=10, space_after=14)
    
    acronyms = [
        ("ACL", "Access Control List"),
        ("AD", "Active Directory"),
        ("ADCS", "Active Directory Certificate Services"),
        ("BFS", "Breadth-First Search"),
        ("CA", "Certificate Authority"),
        ("CSR", "Certificate Signing Request"),
        ("CV", "Cross-Validation"),
        ("DACL", "Discretionary Access Control List"),
        ("DC", "Domain Controller"),
        ("ECE", "Electronics and Communication Engineering"),
        ("EKU", "Extended Key Usage"),
        ("ESC", "Escalation Vector (ADCS Misconfiguration Primitive)"),
        ("GAT", "Graph Attention Network"),
        ("GCN", "Graph Convolutional Network"),
        ("GNN", "Graph Neural Network"),
        ("GOAD", "Game of Active Directory"),
        ("H-MARL", "Hierarchical Multi-Agent Reinforcement Learning"),
        ("Hetero-GAT", "Heterogeneous Graph Attention Network"),
        ("HSTU", "Hajee Mohammad Danesh Science and Technology University"),
        ("IAM", "Identity and Access Management"),
        ("KDC", "Key Distribution Center"),
        ("LDAP", "Lightweight Directory Access Protocol"),
        ("ML", "Machine Learning"),
        ("MLP", "Multi-Layer Perceptron"),
        ("NP", "Nondeterministic Polynomial Time"),
        ("ODE", "Ordinary Differential Equation"),
        ("OID", "Object Identifier"),
        ("PAC", "Privilege Attribute Certificate"),
        ("PKI", "Public Key Infrastructure"),
        ("RF", "Random Forest"),
        ("SAN", "Subject Alternative Name"),
        ("SID", "Security Identifier"),
        ("SOC", "Security Operations Center"),
        ("TGS", "Ticket Granting Service"),
        ("TGT", "Ticket Granting Ticket"),
        ("XAI", "Explainable Artificial Intelligence")
    ]
    
    tbl_acr = doc.add_table(rows=len(acronyms), cols=2)
    remove_table_borders(tbl_acr)
    tbl_acr.alignment = WD_TABLE_ALIGNMENT.CENTER
    tbl_acr.autofit = False
    
    for idx, (acr, full) in enumerate(acronyms):
        row = tbl_acr.rows[idx]
        row.cells[0].width = Inches(1.8)
        row.cells[1].width = Inches(4.2)
        set_cell_margins(row.cells[0], top=35, bottom=35, left=40, right=40)
        set_cell_margins(row.cells[1], top=35, bottom=35, left=40, right=40)
        
        p1 = row.cells[0].paragraphs[0]
        p1.paragraph_format.line_spacing = 1.05
        p1.paragraph_format.space_before = Pt(0.5)
        p1.paragraph_format.space_after = Pt(0.5)
        r1 = p1.add_run(acr)
        r1.bold = True
        r1.font.name = "Times New Roman"
        r1.font.size = Pt(9.5)
        r1.font.color.rgb = RGBColor(0, 0, 0)
        
        p2 = row.cells[1].paragraphs[0]
        p2.paragraph_format.line_spacing = 1.05
        p2.paragraph_format.space_before = Pt(0.5)
        p2.paragraph_format.space_after = Pt(0.5)
        r2 = p2.add_run(full)
        r2.font.name = "Times New Roman"
        r2.font.size = Pt(9.5)
        r2.font.color.rgb = RGBColor(0, 0, 0)

    # Crucial: NO doc.add_page_break() here! Avoids blank page before body.
    doc.save(output_path)
    print(f"[✓] Built frontmatter document: '{output_path}'")

def set_cell_bottom_border(cell, sz="6", color="000000"):
    tcPr = cell._tc.get_or_add_tcPr()
    for child in list(tcPr):
        if child.tag.endswith('tcBorders'):
            tcPr.remove(child)
    tcBorders = OxmlElement('w:tcBorders')
    bottom = OxmlElement('w:bottom')
    bottom.set(qn('w:val'), 'single')
    bottom.set(qn('w:sz'), sz)
    bottom.set(qn('w:space'), '0')
    bottom.set(qn('w:color'), color)
    tcBorders.append(bottom)
    for b in ['top', 'left', 'right']:
        node = OxmlElement(f'w:{b}')
        node.set(qn('w:val'), 'none')
        tcBorders.append(node)
    tcPr.append(tcBorders)

def style_academic_table(table):
    """
    Applies classic publication-grade booktabs borders and header formatting.
    No inside gridlines, thick 1.5pt top/bottom rules, 0.75pt sub-header rule,
    repeating headers across pages, cantSplit rows, and pure white background.
    """
    table.alignment = WD_TABLE_ALIGNMENT.CENTER
    table.autofit = False
    
    # Check if this is a side-by-side figure container (e.g. Table 6 with drawings)
    has_drawing = any('w:drawing' in c._tc.xml for row in table.rows for c in row.cells)
    if has_drawing:
        remove_table_borders(table)
        for row in table.rows:
            trPr = row._tr.get_or_add_trPr()
            trPr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
            for cell in row.cells:
                for child in list(cell._tc.get_or_add_tcPr()):
                    if child.tag.endswith('shd'):
                        cell._tc.tcPr.remove(child)
                set_cell_margins(cell, top=20, bottom=20, left=40, right=40)
        return

    # Check if this is an algorithm table (1 column)
    is_algorithm = len(table.columns) == 1 and ("Algorithm" in table.rows[0].cells[0].text)

    # 1. Header row formatting
    hdr_row = table.rows[0]
    hdr_trPr = hdr_row._tr.get_or_add_trPr()
    hdr_trPr.append(parse_xml(r'<w:tblHeader %s/>' % nsdecls('w')))
    hdr_trPr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
    
    for c_idx, cell in enumerate(hdr_row.cells):
        for child in list(cell._tc.get_or_add_tcPr()):
            if child.tag.endswith('shd'):
                cell._tc.tcPr.remove(child)
        set_cell_margins(cell, top=60, bottom=60, left=80, right=80)
        set_cell_bottom_border(cell, sz="6", color="000000")
        for p in cell.paragraphs:
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.05
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT if is_algorithm else (WD_ALIGN_PARAGRAPH.CENTER if c_idx > 0 else WD_ALIGN_PARAGRAPH.LEFT)
            for r in p.runs:
                r.bold = True
                r.font.name = "Times New Roman"
                r.font.size = Pt(9.5)
                r.font.color.rgb = RGBColor(0, 0, 0)

    # 2. Data rows formatting
    for r_idx in range(1, len(table.rows)):
        row = table.rows[r_idx]
        trPr = row._tr.get_or_add_trPr()
        trPr.append(parse_xml(r'<w:cantSplit %s/>' % nsdecls('w')))
        for c_idx, cell in enumerate(row.cells):
            for child in list(cell._tc.get_or_add_tcPr()):
                if child.tag.endswith('shd'):
                    cell._tc.tcPr.remove(child)
            set_cell_margins(cell, top=45, bottom=45, left=75, right=75)
            for p in cell.paragraphs:
                p.paragraph_format.space_before = Pt(2)
                p.paragraph_format.space_after = Pt(2)
                p.paragraph_format.line_spacing = 1.05
                if not is_algorithm:
                    if c_idx > 0 and len(cell.paragraphs) == 1 and len(p.text.strip()) < 15:
                        p.alignment = WD_ALIGN_PARAGRAPH.CENTER
                    else:
                        p.alignment = WD_ALIGN_PARAGRAPH.LEFT
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(9.0)
                    r.font.color.rgb = RGBColor(0, 0, 0)

    # 3. Pure Booktabs Outer Borders
    tblPr = table._tbl.tblPr
    for child in list(tblPr):
        if child.tag.endswith('tblBorders'):
            tblPr.remove(child)
            
    borders = parse_xml(
        r'<w:tblBorders %s>'
        r'  <w:top w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        r'  <w:bottom w:val="single" w:sz="12" w:space="0" w:color="000000"/>'
        r'  <w:insideH w:val="none"/>'
        r'  <w:insideV w:val="none"/>'
        r'  <w:left w:val="none"/>'
        r'  <w:right w:val="none"/>'
        r'</w:tblBorders>' % nsdecls('w')
    )
    tblPr.append(borders)

def post_process_body_document(raw_docx_path, styled_docx_path):
    """
    Applies publication-grade thesis styles to headings, paragraphs, figures,
    captions, and tables across the Pandoc compiled document.
    """
    doc = docx.Document(raw_docx_path)
    
    # 1. Configure Page Margins across all sections
    for sec in doc.sections:
        sec.page_width = Inches(8.27)
        sec.page_height = Inches(11.69)
        sec.top_margin = Inches(1.0)
        sec.bottom_margin = Inches(1.0)
        sec.left_margin = Inches(1.25)
        sec.right_margin = Inches(1.0)
        sec.header_distance = Inches(0.5)
        sec.footer_distance = Inches(0.5)

    # Configure Normal Style defaults
    normal_style = doc.styles['Normal']
    normal_style.font.name = 'Times New Roman'
    normal_style.font.size = Pt(12)
    normal_style.font.color.rgb = RGBColor(0, 0, 0)
    normal_style.paragraph_format.line_spacing = 1.5
    normal_style.paragraph_format.space_after = Pt(6)
    normal_style.paragraph_format.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY

    # 2. Format Headings & Paragraphs
    for p in doc.paragraphs:
        style_name = p.style.name
        xml_str = p._p.xml
        has_drawing = ('w:drawing' in xml_str or 'w:pict' in xml_str)
        has_display_math = ('m:oMathPara' in xml_str) or (len(p.text.strip()) == 0 and 'm:oMath' in xml_str)
        is_list_item = p._p.pPr is not None and p._p.pPr.find("{http://schemas.openxmlformats.org/wordprocessingml/2006/main}numPr") is not None

        # Chapter Headings (Heading 1)
        if style_name.startswith("Heading 1"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.page_break_before = True
            p.paragraph_format.space_before = Pt(20)
            p.paragraph_format.space_after = Pt(18)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = Pt(0)
            
            txt = p.text.strip()
            chap_m = re.match(r"^(\d+)\t(.*)$", txt)
            if chap_m:
                chap_num = int(chap_m.group(1))
                chap_title = chap_m.group(2)
                if chap_num <= 10:
                    p.text = f"Chapter {chap_num}\n{chap_title}"
                else:
                    p.text = chap_title
            elif "Appendix A" in txt:
                p.text = "Appendix A\nFormal Mathematical Proofs"
            elif txt == "References":
                p.text = "References"
                
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(16)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
                
        # Main Section Headings (Heading 2)
        elif style_name.startswith("Heading 2"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(16)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = Pt(0)
            
            # Clean up Appendix subsections if Pandoc prepended "11.1\t" or "11.2\t"
            if "Proof of Theorem 1" in p.text:
                p.text = re.sub(r'^(11\.1\t|Proof)', 'A.1  Proof', p.text)
            elif "Proof of Theorem 2" in p.text:
                p.text = re.sub(r'^(11\.2\t|Proof)', 'A.2  Proof', p.text)
            else:
                p.text = re.sub(r'^(\d+\.\d+)\t', r'\1  ', p.text)
                        
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(14)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
                
        # Sub-heading (Heading 3)
        elif style_name.startswith("Heading 3"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(12)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = Pt(0)
            p.text = re.sub(r'^(\d+\.\d+\.\d+)\t', r'\1  ', p.text)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)
                
        # Sub-sub-heading (Heading 4)
        elif style_name.startswith("Heading 4"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(10)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = Pt(0)
            p.text = re.sub(r'^(\d+\.\d+\.\d+\.\d+)\t', r'\1  ', p.text)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.italic = True
                r.font.color.rgb = RGBColor(0, 0, 0)

        # Minor headings (Heading 5)
        elif style_name.startswith("Heading 5"):
            p.alignment = WD_ALIGN_PARAGRAPH.LEFT
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(2)
            p.paragraph_format.keep_with_next = True
            p.paragraph_format.line_spacing = 1.15
            p.paragraph_format.first_line_indent = Pt(0)
            p.text = re.sub(r'^\d+(\.\d+){3,}\t?', '', p.text)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
                r.bold = True
                r.font.color.rgb = RGBColor(0, 0, 0)

        # Table Captions
        elif "table caption" in style_name.lower():
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(14)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5)
                r.font.color.rgb = RGBColor(0, 0, 0)
                
        # Figure Captions
        elif "image caption" in style_name.lower():
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(4)
            p.paragraph_format.space_after = Pt(14)
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10)
                r.font.color.rgb = RGBColor(0, 0, 0)

        # Figures (Drawings / Images)
        elif has_drawing:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(8)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.keep_with_next = True

            # Scale figure drawings to full 6.00 inch printable text width
            max_w_emu = int(6.00 * 914400)
            max_h_emu = int(6.80 * 914400)
            for ext in p._p.xpath('.//wp:extent'):
                cx = int(ext.get('cx', 0))
                cy = int(ext.get('cy', 0))
                if cx > int(2.0 * 914400):
                    ratio = cy / cx
                    new_cx = max_w_emu
                    new_cy = int(new_cx * ratio)
                    if new_cy > max_h_emu:
                        new_cy = max_h_emu
                        new_cx = int(new_cy / ratio)
                    ext.set('cx', str(new_cx))
                    ext.set('cy', str(new_cy))
            for a_ext in p._p.xpath('.//a:ext'):
                cx = int(a_ext.get('cx', 0))
                cy = int(a_ext.get('cy', 0))
                if cx > int(2.0 * 914400):
                    ratio = cy / cx
                    new_cx = max_w_emu
                    new_cy = int(new_cx * ratio)
                    if new_cy > max_h_emu:
                        new_cy = max_h_emu
                        new_cx = int(new_cy / ratio)
                    a_ext.set('cx', str(new_cx))
                    a_ext.set('cy', str(new_cy))

        # Display Math Formulas
        elif has_display_math:
            p.alignment = WD_ALIGN_PARAGRAPH.CENTER
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.15

        # Bibliography Entries
        elif style_name == "Bibliography":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.35)
            p.paragraph_format.first_line_indent = -Inches(0.35)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(4)
            p.paragraph_format.line_spacing = 1.15
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(10.5)
                r.font.color.rgb = RGBColor(0, 0, 0)

        # Block Quotes
        elif "block" in style_name.lower():
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.left_indent = Inches(0.4)
            p.paragraph_format.right_indent = Inches(0.4)
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(6)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.25
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(11)
                r.italic = True
                r.font.color.rgb = RGBColor(0, 0, 0)

        # First Paragraph after heading (Flush left, fully justified)
        elif style_name == "First Paragraph":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Pt(0)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.5
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(0, 0, 0)

        # Body Text (Indented, fully justified)
        elif style_name == "Body Text":
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.first_line_indent = Inches(0.25)
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(6)
            p.paragraph_format.line_spacing = 1.5
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(0, 0, 0)

        # List Items (Normal with numPr)
        elif is_list_item:
            p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
            p.paragraph_format.space_before = Pt(0)
            p.paragraph_format.space_after = Pt(3)
            p.paragraph_format.line_spacing = 1.25
            for r in p.runs:
                r.font.name = "Times New Roman"
                r.font.size = Pt(12)
                r.font.color.rgb = RGBColor(0, 0, 0)

        # Other regular paragraphs
        elif style_name == "Normal":
            if p.text.strip():
                p.alignment = WD_ALIGN_PARAGRAPH.JUSTIFY
                p.paragraph_format.first_line_indent = Inches(0.25)
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(6)
                p.paragraph_format.line_spacing = 1.5
                for r in p.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(12)
                    r.font.color.rgb = RGBColor(0, 0, 0)
            else:
                p.paragraph_format.space_before = Pt(0)
                p.paragraph_format.space_after = Pt(0)

    # 3. Insert "References" Heading 1 before the bibliography entries if not already present
    has_ref_heading = any(p.text.strip() == "References" and p.style.name.startswith("Heading 1") for p in doc.paragraphs)
    if not has_ref_heading:
        for p in doc.paragraphs:
            if p.text.strip().startswith("[1]") and "Schroeder" in p.text:
                ref_h = p.insert_paragraph_before()
                ref_h.style = doc.styles["Heading 1"]
                ref_h.text = "References"
                ref_h.alignment = WD_ALIGN_PARAGRAPH.LEFT
                ref_h.paragraph_format.page_break_before = True
                ref_h.paragraph_format.space_before = Pt(20)
                ref_h.paragraph_format.space_after = Pt(18)
                for r in ref_h.runs:
                    r.font.name = "Times New Roman"
                    r.font.size = Pt(16)
                    r.bold = True
                    r.font.color.rgb = RGBColor(0, 0, 0)
                break

    # 4. Style all tables
    for t in doc.tables:
        style_academic_table(t)

    doc.save(styled_docx_path)
    print(f"[✓] Styled body document: '{styled_docx_path}'")

def main():
    repo_dir = "/home/hs32/Desktop/GOAD/thesis_paper"
    os.chdir(repo_dir)
    print("==================================================================")
    print("   COMPILING PURE ACADEMIC THESIS DOCX (OFFICE MATH ML NATIVE)    ")
    print("==================================================================")

    scratch_dir = "/tmp/thesis_build_pure"
    os.makedirs(scratch_dir, exist_ok=True)

    # ─────────────────────────────────────────────────────────────
    # Step 1: Preprocess Chapters & Proofs
    # ─────────────────────────────────────────────────────────────
    print("\n[Step 1/5] Preprocessing LaTeX chapters and resolving cross-references...")
    
    chapter_files = [
        "chapters/ch01_introduction.tex",
        "chapters/ch02_background_threat.tex",
        "chapters/ch03_formal_methodology.tex",
        "chapters/ch04_forensic_audit.tex",
        "chapters/ch05_empirical_benchmarks.tex",
        "chapters/ch06_real_world_case_study.tex",
        "chapters/ch07_robustness_scalability.tex",
        "chapters/ch08_neuro_symbolic_hybrid.tex",
        "chapters/ch09_game_theoretic_defense.tex",
        "chapters/ch10_conclusion.tex",
    ]
    
    preprocessed_inputs = []
    for rel_path in chapter_files:
        base_name = os.path.basename(rel_path)
        out_path = os.path.join(scratch_dir, base_name)
        preprocess_latex_file(rel_path, out_path)
        preprocessed_inputs.append(out_path)
        print(f"  • Preprocessed: {rel_path} -> {out_path}")

    # Prepare Appendix Master file
    print("  • Creating Appendix Master for formal mathematical proofs...")
    app_out_path = os.path.join(scratch_dir, "appendix_master.tex")
    
    proof1_path = os.path.join(scratch_dir, "theorem1.tex")
    proof2_path = os.path.join(scratch_dir, "theorem2.tex")
    preprocess_latex_file("proofs/theorem1_representation_collapse.tex", proof1_path)
    preprocess_latex_file("proofs/theorem2_edge_blocking_nphardness.tex", proof2_path)
    
    with open(app_out_path, "w", encoding="utf-8") as f_app:
        f_app.write(r"\chapter{Appendix A: Formal Mathematical Proofs}" + "\n")
        f_app.write(r"\label{app:proofs}" + "\n\n")
        with open(proof1_path, "r", encoding="utf-8") as p1:
            f_app.write(p1.read() + "\n\n")
        with open(proof2_path, "r", encoding="utf-8") as p2:
            f_app.write(p2.read() + "\n\n")
            
    preprocessed_inputs.append(app_out_path)

    # ─────────────────────────────────────────────────────────────
    # Step 2: Build Front Matter
    # ─────────────────────────────────────────────────────────────
    print("\n[Step 2/5] Constructing verified HSTU Front Matter...")
    front_docx = os.path.join(scratch_dir, "frontmatter.docx")
    build_frontmatter_doc(front_docx)

    # ─────────────────────────────────────────────────────────────
    # Step 3: Compile Body with Pandoc
    # ─────────────────────────────────────────────────────────────
    print("\n[Step 3/5] Compiling LaTeX source to Word via Pandoc (Pure OMML math)...")
    body_raw_docx = os.path.join(scratch_dir, "body_raw.docx")
    
    pandoc_cmd = [
        "pandoc",
        *preprocessed_inputs,
        "--top-level-division=chapter",
        "--number-sections",
        "--citeproc",
        "--bibliography=references.bib",
        "--csl=ieee.csl",
        "-o", body_raw_docx
    ]
    res = subprocess.run(pandoc_cmd, capture_output=True, text=True)
    if res.returncode != 0:
        print(f"[-] Pandoc failed:\n{res.stderr}")
        sys.exit(1)
    print(f"[✓] Pandoc compiled body successfully: '{body_raw_docx}'")

    # ─────────────────────────────────────────────────────────────
    # Step 4: Post-Process Body Styling
    # ─────────────────────────────────────────────────────────────
    print("\n[Step 4/5] Post-processing body document styles, tables, and figures...")
    body_styled_docx = os.path.join(scratch_dir, "body_styled.docx")
    post_process_body_document(body_raw_docx, body_styled_docx)

    # ─────────────────────────────────────────────────────────────
    # Step 5: Stitch Front Matter & Body
    # ─────────────────────────────────────────────────────────────
    print("\n[Step 5/5] Stitching frontmatter and body into master monograph...")
    master = docx.Document(front_docx)
    
    # 1. Front Matter Section Configuration:
    sec_fm = master.sections[0]
    sec_fm.different_first_page_header_footer = True
    sec_fm.first_page_header.paragraphs[0].text = ""
    sec_fm.first_page_footer.paragraphs[0].text = ""
    sec_fm.header.paragraphs[0].text = ""
    
    # Roman page numbers starting at 1
    pgNumType_fm = parse_xml(r'<w:pgNumType %s w:fmt="roman" w:start="1"/>' % nsdecls('w'))
    sec_fm._sectPr.append(pgNumType_fm)
    
    f_p_fm = sec_fm.footer.paragraphs[0]
    f_p_fm.alignment = WD_ALIGN_PARAGRAPH.CENTER
    run_fm = f_p_fm.add_run()
    run_fm.font.name = "Times New Roman"
    run_fm.font.size = Pt(10)
    run_fm.font.color.rgb = RGBColor(0, 0, 0)
    fld_fm = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="20"/></w:rPr><w:t>ii</w:t></w:r></w:fldSimple>')
    run_fm._r.append(fld_fm)

    # 2. Add explicit section break before appending body
    master.add_section(docx.enum.section.WD_SECTION.NEW_PAGE)

    # 3. Append styled body document
    composer = Composer(master)
    composer.append(docx.Document(body_styled_docx))
    
    # 4. Configure Headers and Footers for all body sections
    for idx in range(1, len(master.sections)):
        sec = master.sections[idx]
        sec.different_first_page_header_footer = True
        
        if idx == 1:
            # First body section: decouple completely from Front Matter
            sec.header.is_linked_to_previous = False
            sec.footer.is_linked_to_previous = False
            sec.first_page_header.is_linked_to_previous = False
            sec.first_page_footer.is_linked_to_previous = False
            
            # Start Arabic page numbering at 1
            pgNumType_body = parse_xml(r'<w:pgNumType %s w:fmt="decimal" w:start="1"/>' % nsdecls('w'))
            sec._sectPr.append(pgNumType_body)
            
            # First page footer (Chapter opening): Centered Arabic page number
            fpf = sec.first_page_footer.paragraphs[0]
            fpf.alignment = WD_ALIGN_PARAGRAPH.CENTER
            fld_fpf = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="20"/></w:rPr><w:t>1</w:t></w:r></w:fldSimple>')
            fpf._p.append(fld_fpf)
            sec.first_page_header.paragraphs[0].text = ""
            
            # Subsequent pages header: running title + right tab + page number + 0.5pt bottom rule
            hdr = sec.header.paragraphs[0]
            hdr.alignment = WD_ALIGN_PARAGRAPH.LEFT
            pPr = hdr._p.get_or_add_pPr()
            pPr.append(parse_xml(f'<w:tabs {nsdecls("w")}><w:tab {nsdecls("w")} w:val="right" w:pos="8640"/></w:tabs>'))
            pPr.append(parse_xml(f'<w:pBdr {nsdecls("w")}><w:bottom {nsdecls("w")} w:val="single" w:sz="4" w:space="2" w:color="000000"/></w:pBdr>'))
            
            r_title = hdr.add_run("CertGraph: ADCS Vulnerability Detection & Autonomous Defense")
            r_title.font.name = "Times New Roman"
            r_title.font.size = Pt(9.5)
            r_title.italic = True
            r_title.font.color.rgb = RGBColor(0, 0, 0)
            
            hdr.add_run()._r.append(parse_xml(f'<w:tab {nsdecls("w")}/>'))
            
            r_pg = hdr.add_run()
            fld_hdr = parse_xml(f'<w:fldSimple {nsdecls("w")} w:instr="PAGE"><w:r><w:rPr><w:rFonts w:ascii="Times New Roman" w:hAnsi="Times New Roman"/><w:sz w:val="19"/></w:rPr><w:t>2</w:t></w:r></w:fldSimple>')
            hdr._p.append(fld_hdr)
            
            # Subsequent pages footer: empty!
            sec.footer.paragraphs[0].text = ""
        else:
            # Subsequent chapters inherit header/footer styling and continue numbering
            sec.header.is_linked_to_previous = True
            sec.footer.is_linked_to_previous = True
            sec.first_page_header.is_linked_to_previous = True
            sec.first_page_footer.is_linked_to_previous = True
            
            # Remove any w:start attribute so page numbers continue continuously
            for child in list(sec._sectPr):
                if child.tag.endswith('pgNumType'):
                    sec._sectPr.remove(child)

    final_docx_path = "thesis.docx"
    composer.save(final_docx_path)
    
    desktop_copy = "/home/hs32/Desktop/thesis.docx"
    shutil.copyfile(final_docx_path, desktop_copy)
    
    size_mb = os.path.getsize(final_docx_path) / (1024 * 1024)
    print("\n==================================================================")
    print(f" [✓] COMPLETED SUCCESSFULLY: '{final_docx_path}' ({size_mb:.2f} MB)")
    print(f" [✓] COPIED TO DESKTOP: '{desktop_copy}'")
    print("==================================================================")

if __name__ == "__main__":
    main()
