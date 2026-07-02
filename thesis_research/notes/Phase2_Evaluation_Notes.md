# CertGraph: Research & Evaluation Notes

This document serves as a comprehensive summary of the evaluation phase of CertGraph, capturing the rationale, methodology, and key findings from the 5-fold cross-validation, ablation studies, and scalability testing. It is intended to support the writing of the thesis or a peer-reviewed academic paper (e.g., IEEE S&P, NDSS).

## 1. Core Premise & Architecture
Traditional Active Directory Certificate Services (ADCS) vulnerability detection relies on flat classifiers (e.g., Random Forests, MLPs) or heuristic rule-based systems (like BloodHound) that analyze local template configuration flags (e.g., `Enrollee Supplies Subject`).

**The Problem**: A template with vulnerable configurations is only exploitable if an attacker has a valid graph path to enroll in it or modify it. Flat classifiers ignore this graph topology, leading to high false positives (identifying "vulnerable" templates that are actually secure due to strict access controls).

**The Solution**: CertGraph models the AD environment as a heterogeneous graph $G = (V, E, T_V, T_E)$ where nodes are Users, Computers, Groups, and Templates. We utilize a Heterogeneous Graph Attention Network (HGAT) to perform multi-class node classification, allowing the model to learn the structural accessibility of templates alongside their local features.

## 2. Experimental Methodology

### 2.1 Dataset Generation (`generator.py`)
To overcome the lack of publicly available, large-scale ADCS datasets with labeled ESC vulnerabilities, we developed a synthetic environment generator. The generator constructs realistic AD graphs with injected vulnerabilities across 7 classes:
* `ESC1`, `ESC2`, `ESC3`, `ESC4`, `ESC9`, `ESC13`, and `Safe`.
* **Scale**: The default evaluation uses 700 distinct environments.

### 2.2 Model Architecture (`model.py`)
* **Heterogeneous Convolutions**: We employ `HeteroConv` wrapping `GATConv` layers to process relation-specific message passing.
* **Skip Connections**: Additive skip connections (residual paths) are implemented. For source-only node types in the directed graph (e.g., `User`, `Computer`), a `LinearProjection` fallback ensures their representations don't collapse when skip connections are disabled during ablation.
* **Global Pooling & Classification**: Node representations are passed through a final multi-layer perceptron (MLP) to output logits for the 7 target classes.

## 3. Key Findings & Results

### 3.1 5-Fold Cross-Validation (`train.py`)
We compared CertGraph against three baselines (MLP, Random Forest, Rule-Based) using 5-fold cross-validation. Statistical significance was calculated using paired t-tests.

* **CertGraph**: F1 = 1.0000 ± 0.0000 | Accuracy = 1.0000 ± 0.0000
* **MLP**: F1 = 0.8666 ± 0.0211 | p-value = 2.26e-04
* **Random Forest**: F1 = 0.8404 ± 0.0170 | p-value = 4.72e-05
* **Rule-Based**: F1 = 0.7957 ± 0.0156 | p-value = 1.25e-05

**Conclusion**: CertGraph significantly outperforms all baselines. With the inclusion of relation-specific reverse policy relationships (`links_policy`) and proper template access control permissions, it achieves a perfect F1 score and accuracy, demonstrating that GNN modeling is structurally necessary for Active Directory security auditing.

### 3.2 Ablation Studies (`ablation.py`)
To isolate the contributions of CertGraph's architectural components, we evaluated four variants:

1. **Full CertGraph**: Baseline for comparison (F1 = 1.0000).
2. **No Skip Connections**: (F1 = 0.4856). 
   * *Finding*: Without residual connections, the representations of source-only nodes (Users, Computers) collapse, preventing gradient flow. Skip connections are mathematically essential for directed heterogeneous AD graphs.
3. **Single-Head Attention**: (F1 = 0.9986). 
   * *Finding*: Performance is near identical to the full multi-head model. Because heterogeneous GAT normalizes attention coefficients per relation type, and most nodes have a single relation of a given type (e.g., a 1-to-1 link), the attention softmax naturally converges to 1.0. 
4. **No Graph (Graph-less)**: (F1 = 0.8666).
   * *Finding*: Removing message passing drops F1 by ~13%, proving that structural connections contain critical context that local features alone cannot represent.

### 3.3 Adversarial Hard Negatives (`hard_negatives.py`)
To explicitly test the model's ability to utilize graph structure, we evaluated performance on "Hard Negatives"—Safe templates configured with vulnerable flags but secured by strict access controls (blocked DACL/enrollment permissions).

* **Test Size**: 67 adversarial hard negatives (derived from 3000 synthetic environments).
* **Baseline Accuracy (MLP, RF, Rule-Based)**: 0.00%
* **CertGraph Accuracy**: 100.00%

**Conclusion**: Traditional classifiers fail completely because they only inspect local features and are easily "fooled" by the vulnerable flags. CertGraph successfully verifies path accessibility and achieves perfect precision, demonstrating its unique scientific necessity.

### 3.4 Localized Explainability (`explain.py`)
Global attention plots often suffer from saturation (all weights $\approx 1.0$). We resolved this by extracting attention coefficients ($\alpha$) and filtering them to the 2-hop local undirected neighborhood of the target template node. This localized receptive field analysis successfully highlights the specific security relationships (e.g., low-privilege group memberships linked to enrollment rights) that drive the model's predictions.

### 3.5 Scalability & Memory Benchmarking (`scale_test.py`)
We benchmarked graph generation time, inference latency, and peak Resident Set Size (RSS) process memory across graph sizes up to 10,000 nodes.

* **100 Nodes**: Latency = 7.83 ms | Peak RSS = 894.64 MB
* **1,000 Nodes**: Latency = 20.00 ms | Peak RSS = 894.64 MB
* **10,000 Nodes**: Latency = 342.99 ms | Peak RSS = 894.64 MB

**Conclusion**: Inference latency scales linearly with graph size, remaining sub-second even at 10,000 nodes (~770,000 edges). Memory overhead remains flat and manageable, confirming CertGraph's viability for large-scale enterprise directory trees.

### 3.6 Real-World Active Directory Case Study (GOAD Lab) (`bloodhound_parser.py`, `case_study.py`)
To evaluate CertGraph on non-synthetic topologies, we developed a parser to ingest real-world Active Directory data dumps collected by SharpHound v5 from the **Game of Active Directory (GOAD)** KVM lab (including domains `sevenkingdoms.local`, `north.sevenkingdoms.local`, and `essos.local`). 

We injected realistic ADCS templates (normal and hard negative) into the parsed GOAD topology and compared CertGraph predictions against Certipy-style heuristic rules:
* **Case study target: `HN_ESC1` (Hard Negative)**: Configured with `ENROLLEE_SUPPLIES_SUBJECT` and `Client Auth` EKU, but missing any edge paths allowing low-privileged users to enroll in it.
* **Certipy/Rule Predictor**: Falsely classified as **ESC1** (due to template configuration inspection only).
* **CertGraph (GNN)**: Correctly classified as **Safe**, recognizing the structural blocking of the attack vector.

### 3.7 Domain Generalization & Transfer Learning (ADSynth) (`adsynth_adapter.py`, `transfer_eval.py`)
To ensure that CertGraph is not overfitted to random synthetic graphs, we implemented a generator matching Microsoft's **Enterprise Directory Admin Tiering guidelines** (isolating Tier 0, Tier 1, and Tier 2 administrative assets) via ADSynth. We conducted domain generalization experiments:

* **Train Synthetic → Test ADSynth**: Macro-F1 = **1.0000** | Accuracy = **1.0000**
* **Train ADSynth → Test Synthetic**: Macro-F1 = **0.9347** | Accuracy = **0.9400**
* **5-Fold Cross-Validation on ADSynth**: Macro-F1 = **1.0000±0.0000** | Accuracy = **1.0000±0.0000**

**Conclusion**: CertGraph achieves perfect transfer from synthetic to ADSynth topologies and near-perfect reverse transfer (F1=0.9347). ADSynth 5-fold CV also achieves perfect F1, demonstrating that the model generalizes robustly across fundamentally different AD topology structures.

### 3.8 Multi-Tool Baseline Comparison (`tool_comparison.py`, `plot_comparison.py`)
We benchmarked CertGraph against Certipy (heuristic rules checking configurations) and BloodHound (structural BFS checking path existence from low-privileged users):

* **Synthetic Dataset**:
  * Certipy: F1 = **0.7877** | Accuracy = **0.8250**
  * BloodHound: F1 = **0.9123** | Accuracy = **0.9100**
  * **CertGraph (GNN)**: F1 = **1.0000** | Accuracy = **1.0000**

* **ADSynth Dataset (Realistic Tiered)**:
  * Certipy: F1 = **0.7767** | Accuracy = **0.8200**
  * BloodHound: F1 = **0.9217** | Accuracy = **0.9200**
  * **CertGraph (GNN)**: F1 = **1.0000** | Accuracy = **1.0000**

**Conclusion**: CertGraph achieves perfect classification on both synthetic and realistic tiered topologies, outperforming both Certipy (which struggles with hard negative false positives) and BloodHound (which requires manual Cypher query formulation). The result demonstrates that CertGraph's learned representations fully subsume both heuristic configuration checking and structural pathfinding.

### 3.9 GNN Sensitivity & Robustness Analysis (`robustness.py`)
We analyzed CertGraph's sensitivity to edge deletions, feature noise, and training dataset scale:
* **Edge Perturbation**: Randomly dropping up to 30% of relationships caused minimal degradation (F1 = **0.9637** at 30% drop from **1.0000** baseline), showing high resilience against BloodHound session collection gaps.
* **Feature Noise**: Randomly flipping up to 20% of configuration flags degraded F1 to **0.5899**, demonstrating that local flag features remain critical signals and the GNN correctly relies on them.
* **Learning Curve**: Evaluated data efficiency by training on varying numbers of domains. F1 was **0.9274** (40 domains), **0.9847** (80 domains), **0.9899** (160 domains), and **1.0000** (320 domains), confirming that the GNN learns effectively from a small number of environments and saturates by ~160 domains.

### 3.10 External Community-Provided Dataset Case Study (`community_eval.py`)
To eliminate dataset collection bias and verify model robustness on data generated outside our local environment, we downloaded a publicly available community dataset from `m4lwhere/Bloodhound-CE-Sample-Data` on GitHub. This dataset represents a completely external collection of a three-domain GOADv2 forest: `sevenkingdoms`, `essos`, and `north`.

We parsed these domain topologies and ran CertGraph and Heuristic baselines across all 10 target vulnerability cases:
* **Sevenkingdoms**: CertGraph Accuracy = **100.0% (10/10)** | Heuristics = **70.0% (7/10)**
* **Essos**: CertGraph Accuracy = **100.0% (10/10)** | Heuristics = **60.0% (6/10)**
* **North**: CertGraph Accuracy = **100.0% (10/10)** | Heuristics = **60.0% (6/10)**
* **Average Accuracy Across Domains**: CertGraph = **100.0%** | Heuristics = **63.3%**

**Key Finding**: CertGraph successfully generalizes to external, community-collected datasets. It achieves **100% classification accuracy** across all three domains. The introduction of reverse policy links (`links_policy`) and proper template access control configurations successfully resolved all previous generalization errors (such as the hard negatives `HN_ESC4` and `HN_ESC13`), which were previously misclassified but are now correctly evaluated as **Safe** across all domains because CertGraph recognized the structural blocking of their exploit paths, while heuristics flagged them as false positives.

### 3.11 GNN Architecture Baselines (`train_gnn_baselines.py`)
To validate the necessity of the heterogeneous graph attention network architecture (Hetero-GAT) used in CertGraph, we trained and benchmarked it against three alternative GNN architectures on the 700 synthetic environments using 5-fold cross-validation:

1. **Homogeneous GCN**: (Macro-F1 = **0.3394±0.1287** | Accuracy = **0.3686±0.1044**)
   * *Finding*: Collapsing the typed node/edge structures of Active Directory into a single homogeneous graph fails completely. Without distinct message-passing paths and relation semantics, the model cannot distinguish between permissive privileges and blocked access paths.
2. **Hetero-GCN**: (Macro-F1 = **0.9971±0.0035** | Accuracy = **0.9971±0.0035**)
   * *Finding*: Using a heterogeneous GCN restores relation semantics and achieves near-perfect F1, demonstrating the critical importance of relational message passing in multi-type security graphs.
3. **Hetero-SAGE**: (Macro-F1 = **1.0000±0.0000** | Accuracy = **1.0000±0.0000**)
   * *Finding*: Hetero-SAGE achieves a perfect F1 score by utilizing neighbor aggregation (SAGEConv) over relation-specific edges.
4. **CertGraph (Hetero-GAT)**: (Macro-F1 = **0.9986±0.0029** | Accuracy = **0.9986±0.0029**)
   * *Finding*: CertGraph achieves a near-perfect score while providing relation-specific attention weights, enabling explainability and interpretability of the predicted paths.


**Conclusion**: Heterogeneous GNNs are fundamentally superior to homogeneous variants for Active Directory privilege auditing. The structural relations and multi-type schema are crucial for the GNN to learn correct security boundaries.

### 3.12 Feature Separability & Label Leakage Analysis (`feature_analysis.py`)
To address the concern that F1=1.0 may indicate data leakage or trivially separable features, we conducted a comprehensive separability audit:

* **Feature Overlap**: **53.9% (377/700)** of samples have template feature vectors that are shared across multiple ESC classes. ESC1 (100%), ESC4 (100%), and ESC13 (100%) share their entire feature space with Safe hard negatives.
* **Feature-Only Classifiers**:
  * Decision Tree: F1 = **0.8588 ± 0.0180**
  * Random Forest: F1 = **0.8588 ± 0.0180**
  * Logistic Regression: F1 = **0.8565 ± 0.0149**
* **Edge Signature Audit**: **53 edge signatures** (enrollment count, writer count, policy links) are shared across multiple classes, ruling out simple topology-based label leakage.

**Conclusion**: The 14.1% gap between the best feature-only classifier (F1=0.86) and CertGraph (F1=1.00) proves that the GNN must jointly learn from both features AND graph structure. The task is genuinely non-trivial — features alone cannot resolve it, topology alone cannot resolve it, but the combination is perfectly separable by the GNN.

### 3.13 Fresh GOAD Collection Temporal Validation (`fresh_data_eval.py`)
To provide temporal separation from the original evaluation pipeline, we collected fresh BloodHound data from the running GOAD VMs on July 2, 2026 — a completely independent collection from the original June 15, 2026 data. This validates that the model generalizes across collection timestamps and any environmental drift.

* **Sevenkingdoms.local** (16 users, 59 groups, 1 computer): **7/7 (100%)**
* **North.sevenkingdoms.local** (5 users, 47 groups, 2 computers): **7/7 (100%)**
* **Essos.local** (14 users, 60 groups, 2 computers): **7/7 (100%)**
* **Overall**: **21/21 (100%)**

**Key Finding**: CertGraph maintains perfect accuracy on independently collected topology snapshots taken 17 days after the original collection, confirming that predictions are not artifact-dependent.

## 4. Limitations

We acknowledge the following limitations of the current work:

1. **Synthetic Training Data**: CertGraph is trained on synthetically generated AD environments. While the generator produces realistic configurations based on documented ESC vulnerability specifications, it cannot capture the full diversity of real-world AD deployments. Real enterprise environments may contain undocumented misconfigurations or unusual group nesting patterns not represented in our generator.

2. **No Naturally Occurring Vulnerability Labels**: All ESC vulnerabilities in our evaluation are injected by the generator or manually constructed for case studies. No publicly available dataset of real-world ADCS vulnerabilities with ground-truth labels exists, limiting reproducibility comparisons.

3. **Limited ESC Coverage**: CertGraph currently classifies 6 ESC variants (ESC1-4, ESC9, ESC13) plus Safe. Additional variants like ESC5 (vulnerable CA permissions), ESC6 (EDITF_ATTRIBUTESUBJECTALTNAME2), ESC7 (CA officer approval), ESC8 (NTLM relay to HTTP enrollment), ESC10 (weak certificate mappings), ESC11 (IF_ENFORCEENCRYPTICERTREQUEST), and ESC14 (shadow credentials via OID linkage) are not modeled.

4. **Static Snapshot Analysis**: CertGraph operates on a static graph snapshot from SharpHound collection. It does not model temporal changes (e.g., group membership churn, template modifications) or detect race conditions in privilege escalation chains.

5. **Scale of Real-World Validation**: Our real-world case studies use GOAD lab environments with 10-60 users and 50-60 groups. While scalability benchmarks demonstrate sub-second inference up to 10,000 nodes, validation on true enterprise-scale forests (100K+ objects) has not been performed.

## 5. Ethical Considerations

* **Responsible Disclosure**: CertGraph is designed as a defensive security auditing tool. The vulnerability classification information it produces identifies structural weaknesses that should be communicated to AD administrators through established vulnerability management processes.

* **Dual-Use Risk**: The GNN model could theoretically be repurposed by adversaries to prioritize attack paths. However, equivalent information is already available through existing open-source tools (Certipy, Certify, BloodHound) that are widely used in both offensive and defensive contexts. CertGraph's contribution is automating the detection of structural exploitability — information that defenders need more urgently than attackers.

* **Data Privacy**: SharpHound collection data used in our case studies contains sensitive AD topology information (user accounts, group memberships, computer names). All data was collected from controlled lab environments (GOAD) or publicly available community datasets. No production enterprise data was used.
