# Active Directory GNN Thesis Research

This repository contains GNN models for Active Directory Certificate Services (ADCS) ESC privilege escalation path detection. It is divided into two phases:

- **Phase 1: HGAT ESC13 Analysis** — A Heterogeneous Graph Attention Network (HGAT) trained to detect the ESC13 attack path using link prediction (binary classification) on real BloodHound Active Directory graphs.
- **Phase 2: CertGraph ESC Classification** — A novel, certificate-aware heterogeneous GNN (CertGraph) trained for multi-class ESC vulnerability node classification on template nodes (predicting ESC1, ESC2, ESC3, ESC4, ESC9, ESC13, or Safe), evaluated against Rule-based, MLP, and Random Forest baselines using 5-fold cross-validation.

---

## Directory Structure

```
thesis_research/
├── README.md                      # This documentation guide
├── requirements.txt               # Python package dependencies
├── build_notebooks.py             # Compiler to generate Jupyter Notebooks
├── notebooks/                     # Compiled Jupyter Notebooks
│   ├── 01_HGAT_ESC13_Analysis.ipynb
│   └── 02_CertGraph_ESC_Classification.ipynb
├── src/                           # Python source modules
│   ├── phase1_hgat/               # Phase 1 code (HGAT link prediction)
│   │   ├── dataset.py
│   │   ├── model.py
│   │   ├── train.py
│   │   └── visualize.py
│   └── phase2_certgraph/          # Phase 2 code (CertGraph multi-class node classification)
│       ├── generator.py
│       ├── model.py
│       ├── train.py
│       ├── ablation.py            # GNN architecture ablation studies (Skip, Heads, Graph)
│       ├── explain.py             # Attention weight explainability and visualization
│       ├── hard_negatives.py      # Evaluation on adversarial hard negatives
│       └── scale_test.py          # Scalability and performance benchmarks
├── results/                       # Generated outputs
│   ├── phase1/                    # Phase 1 checkpoints and figures
│   └── phase2/                    # Phase 2 CV results, ablation, explainability, scale benchmarks
└── notes/                         # Planning, logs, and installation guides
```

---

## Setup & Dependencies

1. **Virtual Environment**:
   It is recommended to use the virtual environment in the parent directory (`../.venv`).
   ```bash
   source ../.venv/bin/activate
   ```

2. **Dependencies**:
   Alternatively, install the required packages using pip:
   ```bash
   pip install -r requirements.txt
   ```

---

## Compilation

The Jupyter Notebooks are compiled directly from the python source files in `src/` to ensure the codebase remains clean and DRY. To compile both notebooks:
```bash
python3 build_notebooks.py
```
This generates:
- `notebooks/01_HGAT_ESC13_Analysis.ipynb`
- `notebooks/02_CertGraph_ESC_Classification.ipynb`

---

## Running Notebooks & Validation

You can run the notebooks inside Jupyter:
```bash
jupyter notebook notebooks/01_HGAT_ESC13_Analysis.ipynb
```

Or execute them from the CLI to validate they run completely end-to-end:
```bash
# Validate Phase 1
jupyter nbconvert --to notebook --execute notebooks/01_HGAT_ESC13_Analysis.ipynb --output /tmp/p1_val.ipynb

# Validate Phase 2
jupyter nbconvert --to notebook --execute notebooks/02_CertGraph_ESC_Classification.ipynb --output /tmp/p2_val.ipynb
```

---

## Running Source Scripts Directly

You can also run the GNN pipelines as standalone python modules:

### Phase 1 (HGAT ESC13 Link Prediction)
```bash
python3 src/phase1_hgat/train.py
python3 src/phase1_hgat/visualize.py
```
Outputs (training curves, t-SNE projections, checkpoints) will be written to `results/phase1/`.

### Phase 2 (CertGraph Multi-Class Classification & Evaluation)

1. **Train Model & Run 5-Fold Cross Validation**:
   ```bash
   python3 src/phase2_certgraph/train.py
   ```
   Generates cross-validation performance tables, per-class classification reports, and statistical significance p-values against baselines. Saves results to `results/phase2/cv_results.json`.

2. **Run Architecture Ablation Studies**:
   ```bash
   python3 src/phase2_certgraph/ablation.py
   ```
   Trains and compares full CertGraph, no-skip connection GNN, single-attention head GNN, and graph-less GNN variants. Generates `results/phase2/ablation_comparison.png` and `results/phase2/ablation_results.json`.

3. **Run Explainability & Attention Analysis**:
   ```bash
   python3 src/phase2_certgraph/explain.py
   ```
   Extracts relation attention coefficients in the target template's 2-hop local subgraph and produces attention attribution plots at `results/phase2/explainability_attention.png` (or `explain_attention.png`).

4. **Evaluate on Adversarial Hard Negatives**:
   ```bash
   python3 src/phase2_certgraph/hard_negatives.py
   ```
   Tests CertGraph against baselines on hard negative samples (templates with vulnerable features but blocked graph path permissions). Saves results to `results/phase2/hard_negatives_results.json`.

5. **Run Performance and Scalability Benchmarking**:
   ```bash
   python3 src/phase2_certgraph/scale_test.py
   ```
   Measures time complexity, model inference latency, and peak memory footprint (max RSS or peak CUDA GPU memory) across graph sizes up to 10,000 nodes. Generates `results/phase2/scalability_metrics.png` and `results/phase2/scalability_results.json`.

## Reproducibility & Environment Details

To ensure exact reproducibility of the results presented in our evaluations:

- **Python Version**: `3.11.11` (managed via pyenv).
- **Deep Learning Frameworks**: 
  - `torch==2.3.0`
  - `torch_geometric==2.5.3`
- **Machine Learning & Stats Libraries**:
  - `scikit-learn==1.4.2`
  - `scipy==1.13.0`
- **Hardware Profile**:
  - Experiments were run on a CPU system (CUDA optional and automatically leveraged if available).
  - Benchmarks measured peak Resident Set Size (RSS) process memory footprint and GPU max memory allocation if active.
- **Random Seeds**:
  - Global random seeds (`42` for python `random`, `numpy`, and `torch`) are set in all training scripts to guarantee identical synthetic data folds, initialization weights, and baseline comparisons.
