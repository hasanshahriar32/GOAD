"""
train_gnn_baselines.py — Benchmark GNN Architecture Baselines for CertGraph
===========================================================================
Trains and evaluates CertGraph (Hetero-GAT) against:
  - Homogeneous GCN
  - Heterogeneous GCN (HeteroGCN)
  - Heterogeneous GraphSAGE (HeteroSAGE)

Saves comparison metrics to JSON and plots performance results.
"""

import os
import json
import time
import warnings
import numpy as np
import torch
import torch.nn as nn
import torch.nn.functional as F
from collections import defaultdict
import matplotlib.pyplot as plt
from sklearn.metrics import f1_score, accuracy_score
from sklearn.model_selection import StratifiedKFold
from torch_geometric.loader import DataLoader

from generator import (
    generate_dataset, ESC_CLASSES, CLASS_TO_IDX, NUM_CLASSES,
)
from model import (
    CertGraph, GCNBaseline, HeteroGCNBaseline, HeteroSAGEBaseline,
)

warnings.filterwarnings("ignore", category=UserWarning)

# Configuration
NUM_ENVS = 700
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 100
N_FOLDS = 5
BATCH_SIZE = 64
RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")

os.makedirs(RESULTS_DIR, exist_ok=True)


def train_gnn_fold(
    model_name: str,
    model_class: nn.Module,
    train_data: list,
    test_data: list,
    fold: int,
) -> dict:
    """Train a specific GNN baseline for one fold."""
    train_list = [d for d, _, _ in train_data]
    test_list = [d for d, _, _ in test_data]

    train_loader = DataLoader(train_list, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_list, batch_size=BATCH_SIZE, shuffle=False)

    sample = train_list[0]
    
    # Initialize the model dynamically
    if model_name == "CertGraph":
        model = model_class(
            metadata=sample.metadata(),
            hidden_channels=HIDDEN_DIM,
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            num_heads=NUM_HEADS,
            dropout=DROPOUT,
        )
    else:
        # GCN, HeteroGCN, HeteroSAGE baselines
        model = model_class(
            metadata=sample.metadata(),
            hidden_channels=HIDDEN_DIM * NUM_HEADS,  # match hidden dimension size
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            dropout=DROPOUT,
        )

    # Lazy init on a sample batch
    with torch.no_grad():
        model.eval()
        _ = model(sample.x_dict, sample.edge_index_dict)
    model.train()

    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        for batch in train_loader:
            optimizer.zero_grad()
            logits = model(batch.x_dict, batch.edge_index_dict)

            # Target template prediction
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

    test_f1 = f1_score(test_labels, test_preds, average="macro", zero_division=0)
    test_acc = accuracy_score(test_labels, test_preds)

    return {"f1": test_f1, "acc": test_acc}


def main():
    print("=" * 80)
    print("GNN Architecture Baselines Cross-Validation Benchmark")
    print("=" * 80)

    # 1. Generate Dataset
    print(f"\n[1/3] Generating {NUM_ENVS} AD environments...")
    dataset = generate_dataset(num_envs=NUM_ENVS, balanced=True, seed=42)

    # Set up DataLoader attributes
    for data, esc_class, target_idx in dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)

    labels = [CLASS_TO_IDX[esc_class] for _, esc_class, _ in dataset]
    indices = np.arange(len(dataset))

    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

    gnn_models = {
        "CertGraph": CertGraph,
        "Homogeneous GCN": GCNBaseline,
        "Hetero-GCN": HeteroGCNBaseline,
        "Hetero-SAGE": HeteroSAGEBaseline,
    }

    results = {name: defaultdict(list) for name in gnn_models}

    # 2. Cross-Validation
    print(f"\n[2/3] Running {N_FOLDS}-fold CV across all GNN models...")
    for fold, (train_idx, test_idx) in enumerate(skf.split(indices, labels), 1):
        print(f"\n--- Fold {fold}/{N_FOLDS} ---")
        train_data = [dataset[i] for i in train_idx]
        test_data = [dataset[i] for i in test_idx]

        for model_name, model_class in gnn_models.items():
            t0 = time.time()
            res = train_gnn_fold(model_name, model_class, train_data, test_data, fold)
            elapsed = time.time() - t0
            print(f"  [{model_name:<16}] F1: {res['f1']:.4f} | Acc: {res['acc']:.4f} ({elapsed:.1f}s)")
            results[model_name]["f1"].append(res["f1"])
            results[model_name]["acc"].append(res["acc"])

    # 3. Summarize results
    print("\n" + "=" * 80)
    print("BENCHMARK SUMMARY")
    print("=" * 80)
    
    summary = {}
    for name in gnn_models:
        f1_mean = np.mean(results[name]["f1"])
        f1_std = np.std(results[name]["f1"])
        acc_mean = np.mean(results[name]["acc"])
        acc_std = np.std(results[name]["acc"])
        print(f"{name:<16} | Macro-F1: {f1_mean:.4f} ± {f1_std:.4f} | Acc: {acc_mean:.4f} ± {acc_std:.4f}")
        
        summary[name] = {
            "f1_mean": float(f1_mean),
            "f1_std": float(f1_std),
            "acc_mean": float(acc_mean),
            "acc_std": float(acc_std),
            "f1_folds": [float(x) for x in results[name]["f1"]],
            "acc_folds": [float(x) for x in results[name]["acc"]],
        }

    # Save to JSON
    json_path = os.path.join(RESULTS_DIR, "gnn_baselines_results.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=4)
    print(f"\n[3/3] Results saved to: {json_path}")

    # Plot results
    model_names = list(gnn_models.keys())
    f1_means = [summary[name]["f1_mean"] for name in model_names]
    f1_stds = [summary[name]["f1_std"] for name in model_names]
    acc_means = [summary[name]["acc_mean"] for name in model_names]
    acc_stds = [summary[name]["acc_std"] for name in model_names]

    x = np.arange(len(model_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(8, 5))
    rects1 = ax.bar(x - width/2, f1_means, width, yerr=f1_stds, label='Macro-F1', capsize=5, color='#1f77b4')
    rects2 = ax.bar(x + width/2, acc_means, width, yerr=acc_stds, label='Accuracy', capsize=5, color='#aec7e8')

    ax.set_ylabel('Scores')
    ax.set_title('GNN Architecture Baseline Comparison')
    ax.set_xticks(x)
    ax.set_xticklabels(model_names)
    ax.set_ylim(0.0, 1.1)
    ax.legend(loc='lower right')
    ax.grid(axis='y', linestyle='--', alpha=0.7)

    # Attach labels above bars
    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 3),  # 3 points vertical offset
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=9)

    autolabel(rects1)
    autolabel(rects2)

    plt.tight_layout()
    plot_path = os.path.join(RESULTS_DIR, "gnn_baselines_comparison.png")
    plt.savefig(plot_path, dpi=300)
    plt.close()
    print(f"      Comparison plot saved to: {plot_path}")
    print("\n[✓] Benchmark complete!")


if __name__ == "__main__":
    main()
