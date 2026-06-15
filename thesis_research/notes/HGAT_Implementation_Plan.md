# HGAT → CertGraph: Research Implementation Plan

## Status: Active — Extended to Novel Research Direction

---

## Phase 1: Original HGAT Pipeline ✅ COMPLETE

**Goal**: Build a working HGAT for ESC13 attack path detection using real BloodHound data.

| Component | File | Status |
|-----------|------|--------|
| Data Pipeline | `dataset.py` | ✅ Parses BH JSON + ESC templates → HeteroData |
| Model | `model.py` | ✅ 2-layer HGAT with HeteroConv (91K params) |
| Training | `train.py` | ✅ 200 epochs, AUC=1.0 on ESC13 link prediction |
| Visualization | `visualize.py` | ✅ t-SNE, training curves, attack path ranking |
| Notebook | `HGAT_ESC13_Analysis.ipynb` | ✅ Self-contained, fully executed |

**Limitation**: Single positive edge, no baselines, not publication-worthy.

---

## Phase 2: CertGraph Research Extension 🔄 IN PROGRESS

### Novelty Assessment (Literature Review)

**Why Phase 1 is NOT novel for Q1 publication:**
1. GNN on AD graphs already published (Physics-Informed GNN 2025, IDS-HGAT 2025, ATHITD 2025)
2. Trivial evaluation (1 positive edge, AUC=1.0)
3. No baseline comparisons, no cross-validation
4. Static snapshot only — field has moved to temporal/dynamic

### Novel Contribution: CertGraph

**"First GNN-based multi-class ADCS vulnerability classifier"**

Key innovations:
1. **Certificate-aware graph schema** — `Template`, `CA`, `IssuancePolicy` as first-class nodes
2. **Multi-class ESC classification** — ESC1/ESC2/ESC3/ESC4/ESC9/ESC13/Safe (7 classes)
3. **Synthetic dataset generation** — 700+ environments with varying topology
4. **10-dim template feature vector** — covering all ESC-distinguishing PKI flags
5. **4 comparison baselines** — Rule-based, MLP, Random Forest, CertGraph

### Implementation Status

| Component | File | Status |
|-----------|------|--------|
| Synthetic Generator | `certgraph_generator.py` | ✅ Generates 700 balanced environments |
| CertGraph Model | `certgraph_model.py` | ✅ HGAT + MLP classifier + projection layers |
| Training Pipeline | `certgraph_train.py` | ✅ 5-fold CV with all baselines |
| **Notebook** | `CertGraph_ESC_Classification.ipynb` | ✅ All-in-one self-contained notebook |
| Baselines | In `certgraph_model.py` | ✅ Rule-based, MLP, Random Forest |

### Architecture

```
Node Types:  User(6d), Group(2d), Computer(3d), CA(3d), Template(10d)
Edge Types:  member_of, generic_all, write_dacl, enrolls, issued_by, linked_to

Template(10d) ──→ HeteroConv Layer 1 (4-head GAT per relation)
              ──→ ReLU + Dropout
              ──→ HeteroConv Layer 2 (1-head GAT)
              ──→ MLP Classifier
              ──→ [ESC1, ESC2, ESC3, ESC4, ESC9, ESC13, Safe]
```

### Template Feature Vector (10 dimensions)

| # | Feature | ESC Relevance |
|---|---------|---------------|
| 0 | enrollee_supplies_subject | ESC1 |
| 1 | no_manager_approval | ESC1, ESC2, ESC3 |
| 2 | no_security_extension | ESC9 |
| 3 | has_client_auth | ESC1, ESC9, ESC13 |
| 4 | has_any_purpose | ESC2 |
| 5 | has_cert_req_agent | ESC3 |
| 6 | ra_signature_required | ESC3 |
| 7 | has_issuance_policy_oid | ESC13 |
| 8 | has_vulnerable_acl | ESC4 |
| 9 | schema_version_normalized | Context |

### Target Venues (Q1)

| Venue | Type | Fit |
|-------|------|-----|
| IEEE TDSC | Journal, Q1 | Identity & access security |
| Computers & Security (Elsevier) | Journal, Q1 | Applied security + ML |
| USENIX Security | Conference, Top-tier | Systems security |

---

## How to Run

### Phase 1 (Original HGAT)
```bash
cd ~/Desktop/GOAD
jupyter notebook HGAT_ESC13_Analysis.ipynb
```

### Phase 2 (CertGraph — Novel Research)
```bash
cd ~/Desktop/GOAD
jupyter notebook CertGraph_ESC_Classification.ipynb
```
Run all cells in order. Training takes ~30-40 minutes on CPU.

---

## File Structure

```
~/Desktop/GOAD/
├── HGAT_ESC13_Analysis.ipynb        # Phase 1 notebook (original HGAT)
├── CertGraph_ESC_Classification.ipynb  # Phase 2 notebook (novel research) ⭐
├── dataset.py                       # Phase 1: BH data pipeline
├── model.py                         # Phase 1: HGAT model
├── train.py                         # Phase 1: training loop
├── visualize.py                     # Phase 1: thesis figures
├── certgraph_generator.py           # Phase 2: synthetic AD environment generator
├── certgraph_model.py               # Phase 2: CertGraph + baselines
├── certgraph_train.py               # Phase 2: 5-fold CV pipeline
├── checkpoints/                     # Saved model weights
├── certgraph_results/               # CV metrics JSON
├── thesis_figures/                  # Generated PNG figures
├── Thesis_Data/                     # Raw BloodHound JSON exports
└── ansible/roles/adcs_templates/    # Real GOAD ESC template definitions
```

---

## Next Steps

- [ ] Run `CertGraph_ESC_Classification.ipynb` end-to-end
- [ ] Analyze results: does CertGraph outperform baselines?
- [ ] If training F1 is low, tune hyperparameters (LR, EPOCHS, add noise to features)
- [ ] Add ablation study cells to notebook
- [ ] Generate final thesis figures from notebook outputs
- [ ] Write LaTeX paper using results
