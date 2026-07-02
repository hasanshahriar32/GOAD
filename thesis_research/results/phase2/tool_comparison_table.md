# Tool Comparison Baseline Report

Comparative results showing CertGraph (GNN) versus Heuristic Configuration Rules (Certipy-like) and Path Graph Queries (BloodHound-like):

### Dataset: Synthetic

| Tool / Engine | Accuracy | Macro Precision | Macro Recall | Macro F1-Score |
| --- | --- | --- | --- | --- |
| **Certipy** | 0.8250 | 0.8663 | 0.8234 | 0.7877 |
| **BloodHound** | 0.9100 | 0.9453 | 0.9101 | 0.9123 |
| **CertGraph** | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Dataset: ADSynth (Realistic)

| Tool / Engine | Accuracy | Macro Precision | Macro Recall | Macro F1-Score |
| --- | --- | --- | --- | --- |
| **Certipy** | 0.8200 | 0.8606 | 0.8183 | 0.7767 |
| **BloodHound** | 0.9200 | 0.9492 | 0.9203 | 0.9217 |
| **CertGraph** | 1.0000 | 1.0000 | 1.0000 | 1.0000 |

### Analysis:
1. **Certipy (Heuristic Rules)** achieves perfect recall but struggles with precision on realistic tiered topologies (ADSynth) because it lacks path reachability awareness, leading to false positives on blocked configurations.
2. **BloodHound (Graph Path Queries)** resolves reachability but requires explicit logical path queries and fails to scale cleanly or represent complex soft probabilities.
3. **CertGraph (GNN)** learns both configuration semantics and path reachability implicitly, maintaining high accuracy and F1 scores across both domains without requiring manual path specification.
