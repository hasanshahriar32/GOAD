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
│       └── train.py
├── results/                       # Generated outputs
│   ├── phase1/                    # Phase 1 checkpoints and figures
│   └── phase2/                    # Phase 2 confusion matrices, metrics JSON, and checkpoints
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

### Phase 2 (CertGraph Multi-Class Classification)
```bash
python3 src/phase2_certgraph/train.py
```
Outputs (cross-validation metrics JSON, best model checkpoints) will be written to `results/phase2/`.
