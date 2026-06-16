#!/usr/bin/env python3
"""
ablation.py — Ablation Studies for CertGraph GNN Architecture
============================================================
Evaluates four model configurations under 5-fold CV to test:
  1. Full CertGraph
  2. No Skip Connections (residual links disabled)
  3. Single-head GAT (vs 4-head attention)
  4. No Graph Structure (zeroed relation edges)
"""

import os
import json
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.model_selection import StratifiedKFold
from sklearn.metrics import f1_score, accuracy_score
from torch_geometric.loader import DataLoader
from generator import generate_dataset, CLASS_TO_IDX, NUM_CLASSES, ESC_CLASSES
from model import CertGraph

# Config
NUM_ENVS = 700
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 80
N_FOLDS = 5
BATCH_SIZE = 64
SEED = 42

RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
os.makedirs(RESULTS_DIR, exist_ok=True)


def train_variant(train_data, test_data, variant_name, fold) -> dict:
    """Train a specific variant for one fold."""
    # Set seed for reproducibility of model initialization and batching
    torch.manual_seed(SEED + fold)
    np.random.seed(SEED + fold)
    
    sample = train_data[0][0]
    
    # Configure model depending on variant
    if variant_name == "CertGraph (Full)":
        model = CertGraph(
            metadata=sample.metadata(),
            hidden_channels=HIDDEN_DIM,
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            num_heads=NUM_HEADS,
            dropout=DROPOUT,
            skip_connections=True
        )
    elif variant_name == "CertGraph (No Skip)":
        model = CertGraph(
            metadata=sample.metadata(),
            hidden_channels=HIDDEN_DIM,
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            num_heads=NUM_HEADS,
            dropout=DROPOUT,
            skip_connections=False
        )
    elif variant_name == "CertGraph (Single-Head)":
        model = CertGraph(
            metadata=sample.metadata(),
            hidden_channels=HIDDEN_DIM,  # reduce capacity to single head of standard width
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            num_heads=1,
            dropout=DROPOUT,
            skip_connections=True
        )
    elif variant_name == "CertGraph (No Graph)":
        model = CertGraph(
            metadata=sample.metadata(),
            hidden_channels=HIDDEN_DIM,
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            num_heads=NUM_HEADS,
            dropout=DROPOUT,
            skip_connections=True
        )
    
    # Extract Graph lists for DataLoader
    train_list = [d for d, _, _ in train_data]
    test_list = [d for d, _, _ in test_data]
    
    # If variant is No Graph, strip all edges
    if variant_name == "CertGraph (No Graph)":
        train_list = [strip_edges(d) for d in train_list]
        test_list = [strip_edges(d) for d in test_list]
        sample = train_list[0]
        
    train_loader = DataLoader(train_list, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_list, batch_size=BATCH_SIZE, shuffle=False)
    
    # Lazy init
    with torch.no_grad():
        model.eval()
        _ = model(sample.x_dict, sample.edge_index_dict)
    
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    
    for epoch in range(1, EPOCHS + 1):
        model.train()
        for batch in train_loader:
            optimizer.zero_grad()
            logits = model(batch.x_dict, batch.edge_index_dict)
            ptr = batch['Template'].ptr
            target_indices = ptr[:-1] + batch.target_idx
            target_logits = logits[target_indices]
            loss = F.cross_entropy(target_logits, batch.y_class)
            loss.backward()
            optimizer.step()
            
    # Evaluation
    model.eval()
    test_preds = []
    test_labels = []
    
    with torch.no_grad():
        for batch in test_loader:
            logits = model(batch.x_dict, batch.edge_index_dict)
            ptr = batch['Template'].ptr
            target_indices = ptr[:-1] + batch.target_idx
            target_logits = logits[target_indices]
            test_preds.extend(target_logits.argmax(dim=1).cpu().tolist())
            test_labels.extend(batch.y_class.cpu().tolist())
            
    f1 = f1_score(test_labels, test_preds, average="macro", zero_division=0)
    acc = accuracy_score(test_labels, test_preds)
    return {"f1": f1, "acc": acc}


def strip_edges(data):
    """Create a copy of PyG HeteroData with all edge indices cleared."""
    data_copy = data.clone()
    for et in data_copy.edge_types:
        data_copy[et].edge_index = torch.empty((2, 0), dtype=torch.long)
    return data_copy


def main():
    print("=" * 70)
    print("CertGraph Ablation Studies — 5-Fold Cross-Validation")
    print("=" * 70)
    
    # 1. Generate dataset
    print(f"\n[1/3] Generating {NUM_ENVS} AD environments...")
    dataset = generate_dataset(num_envs=NUM_ENVS, balanced=True, seed=SEED)
    
    for data, esc_class, target_idx in dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)
        
    labels = [CLASS_TO_IDX[esc_class] for _, esc_class, _ in dataset]
    indices = np.arange(len(dataset))
    
    variants = [
        "CertGraph (Full)",
        "CertGraph (No Skip)",
        "CertGraph (Single-Head)",
        "CertGraph (No Graph)"
    ]
    
    results = {v: defaultdict(list) for v in variants}
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=SEED)
    
    # 2. Run CV
    print(f"\n[2/3] Evaluating variants across {N_FOLDS} folds...")
    for fold, (train_idx, test_idx) in enumerate(skf.split(indices, labels)):
        print(f"\n  ── Fold {fold+1}/{N_FOLDS} ──")
        train_data = [dataset[i] for i in train_idx]
        test_data = [dataset[i] for i in test_idx]
        
        for var in variants:
            res = train_variant(train_data, test_data, var, fold)
            results[var]["f1"].append(res["f1"])
            results[var]["acc"].append(res["acc"])
            print(f"    {var:<24} → Macro-F1: {res['f1']:.4f} | Acc: {res['acc']:.4f}")
            
    # 3. Summarize & Save
    print(f"\n[3/3] Saving results...")
    
    # Calculate significance vs CertGraph (Full)
    from scipy.stats import ttest_rel
    cg_f1s = results["CertGraph (Full)"]["f1"]
    p_values = {}
    for var in variants:
        if var == "CertGraph (Full)":
            p_values[var] = 1.0
            continue
        var_f1s = results[var]["f1"]
        _, p_val = ttest_rel(cg_f1s, var_f1s)
        if np.isnan(p_val):
            p_val = 1.0
        p_values[var] = p_val

    summary = {}
    for var in variants:
        summary[var] = {
            "f1_mean": float(np.mean(results[var]["f1"])),
            "f1_std": float(np.std(results[var]["f1"])),
            "acc_mean": float(np.mean(results[var]["acc"])),
            "acc_std": float(np.std(results[var]["acc"])),
            "f1_per_fold": [float(x) for x in results[var]["f1"]],
            "acc_per_fold": [float(x) for x in results[var]["acc"]],
            "p_value_vs_full": float(p_values[var]),
        }
        
    # Save JSON
    json_path = os.path.join(RESULTS_DIR, "ablation_results.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"      Ablation JSON: {json_path}")
    
    # Print Table
    print("\n" + "=" * 80)
    print(f"{'Variant':<26} {'Macro-F1':>12} {'Accuracy':>12} {'p-val (vs Full)':>18}")
    print("-" * 75)
    for var in variants:
        f_mean, f_std = summary[var]["f1_mean"], summary[var]["f1_std"]
        a_mean, a_std = summary[var]["acc_mean"], summary[var]["acc_std"]
        p_str = f"{p_values[var]:.4e}" if var != "CertGraph (Full)" else "Reference"
        print(f"{var:<26} {f_mean:.4f}±{f_std:.4f} {a_mean:.4f}±{a_std:.4f} {p_str:>18}")
    print("=" * 80)
    
    # Plotting
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e", "axes.facecolor": "#16213e",
        "text.color": "white", "axes.labelcolor": "#aaa",
        "xtick.color": "#666", "ytick.color": "#666",
    })
    
    var_names = list(summary.keys())
    means = [summary[v]["f1_mean"] for v in var_names]
    stds = [summary[v]["f1_std"] for v in var_names]
    colors = ["#FF6B6B", "#4ECDC4", "#FFA07A", "#45B7D1"]
    
    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.bar(var_names, means, yerr=stds, color=colors, alpha=0.85,
                  edgecolor="white", linewidth=0.5, capsize=5)
    
    for bar, val in zip(bars, means):
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 0.02,
                f"{val:.3f}", ha="center", va="bottom", fontsize=12, fontweight="bold", color="white")
                
    ax.set_ylabel("Macro-F1 Score", fontsize=12)
    ax.set_title("CertGraph Ablation Study — Architecture Comparison", fontsize=14, fontweight="bold", pad=15)
    ax.set_ylim(0, 1.15)
    for s in ax.spines.values():
        s.set_color("#333")
    ax.grid(True, axis="y", alpha=0.1, color="#555")
    
    plot_path = os.path.join(RESULTS_DIR, "ablation_comparison.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"      Ablation Plot: {plot_path}")
    print("[✓] Ablation studies completed!")


if __name__ == "__main__":
    main()
