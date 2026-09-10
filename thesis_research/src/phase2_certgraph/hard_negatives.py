#!/usr/bin/env python3
"""
hard_negatives.py — Zero-Shot Adversarial Hard Negative Evaluation
===================================================================
Evaluates true generalization on adversarial hard negatives:
- Models are trained on standard environments containing ONLY normal Safe samples
  (no hard negatives seen during training).
- Evaluated on a held-out test set containing adversarial hard negatives:
  Safe certificate templates that exhibit local vulnerability flags (ESC1/4/13)
  but lack the necessary graph permissions or paths for exploitation.

Compares:
  - CertGraph (Hetero-GAT)
  - MLP (Features only, 10-dim)
  - Random Forest (Features only, 10-dim)
  - Rule-Based (Certipy deterministic rules)
  - Graph-Augmented MLP (14-dim: features + graph counts)
  - Graph-Augmented RF (14-dim: features + graph counts)
  - BloodHound BFS (heuristic graph path traversal)
"""

import os
import json
import numpy as np
import torch
import torch.nn.functional as F
import matplotlib.pyplot as plt
from collections import defaultdict
from sklearn.ensemble import RandomForestClassifier
from torch_geometric.loader import DataLoader

from generator import generate_dataset, CLASS_TO_IDX, NUM_CLASSES, ESC_CLASSES
from model import CertGraph, MLPBaseline, RuleBaseline
from bfs_baseline import BloodHoundBFSBaseline
from train import extract_graph_counts

# Configuration
NUM_TRAIN_ENVS = 1400     # 200 per class (Safe samples are purely Normal, no HNs)
NUM_TEST_ENVS = 600       # Fresh environments with hard negatives enabled
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 70
BATCH_SIZE = 64
SEED = 42

RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
os.makedirs(RESULTS_DIR, exist_ok=True)


def is_hard_negative(data, esc_class, target_idx) -> bool:
    """Identify if a Safe template is a hard negative based on feature flags."""
    if esc_class != "Safe":
        return False
    features = data["Template"].x[target_idx].tolist()
    # Feature indices:
    # 0: enrollee_supplies_subject (looks like ESC1)
    # 7: has_issuance_policy_oid   (looks like ESC13)
    # 8: has_vulnerable_acl        (looks like ESC4)
    has_esc1_flags = (features[0] == 1.0)
    has_esc13_flags = (features[7] == 1.0)
    has_esc4_flags = (features[8] == 1.0)
    return has_esc1_flags or has_esc13_flags or has_esc4_flags


def train_models(train_data):
    """Train all model variants on standard training data."""
    sample = train_data[0][0]

    # 1. CertGraph
    cg_model = CertGraph(
        metadata=sample.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT,
    )

    # 2. MLP (features only, 10-dim)
    mlp_model = MLPBaseline(
        input_dim=10,
        hidden_dim=32,
        num_classes=NUM_CLASSES,
    )

    # 3. Graph-Augmented MLP (14-dim)
    aug_mlp_model = MLPBaseline(
        input_dim=14,
        hidden_dim=32,
        num_classes=NUM_CLASSES,
    )

    # PyG DataLoader for CertGraph
    train_list = [d for d, _, _ in train_data]
    loader = DataLoader(train_list, batch_size=BATCH_SIZE, shuffle=True)

    # Lazy init CertGraph
    with torch.no_grad():
        cg_model.eval()
        _ = cg_model(sample.x_dict, sample.edge_index_dict)

    optimizer_cg = torch.optim.Adam(cg_model.parameters(), lr=LR, weight_decay=1e-4)
    optimizer_mlp = torch.optim.Adam(mlp_model.parameters(), lr=0.01, weight_decay=1e-4)
    optimizer_aug_mlp = torch.optim.Adam(aug_mlp_model.parameters(), lr=0.01, weight_decay=1e-4)

    # Pre-extract tabular data for MLPs
    X_mlp = torch.stack([d["Template"].x[ti] for d, _, ti in train_data])
    y_mlp = torch.tensor([CLASS_TO_IDX[ec] for _, ec, _ in train_data], dtype=torch.long)

    X_aug_mlp_list = []
    for d, _, ti in train_data:
        f10 = d["Template"].x[ti].tolist()
        c4 = extract_graph_counts(d, ti)
        X_aug_mlp_list.append(f10 + c4)
    X_aug_mlp = torch.tensor(X_aug_mlp_list, dtype=torch.float)

    for epoch in range(1, EPOCHS + 1):
        cg_model.train()
        mlp_model.train()
        aug_mlp_model.train()

        # CertGraph training
        for batch in loader:
            optimizer_cg.zero_grad()
            logits_cg = cg_model(batch.x_dict, batch.edge_index_dict)
            ptr = batch["Template"].ptr
            target_indices = ptr[:-1] + batch.target_idx
            loss_cg = F.cross_entropy(logits_cg[target_indices], batch.y_class)
            loss_cg.backward()
            optimizer_cg.step()

        # MLP training
        optimizer_mlp.zero_grad()
        loss_mlp = F.cross_entropy(mlp_model(X_mlp), y_mlp)
        loss_mlp.backward()
        optimizer_mlp.step()

        # Aug MLP training
        optimizer_aug_mlp.zero_grad()
        loss_aug_mlp = F.cross_entropy(aug_mlp_model(X_aug_mlp), y_mlp)
        loss_aug_mlp.backward()
        optimizer_aug_mlp.step()

    # 4. Random Forest (10-dim)
    X_rf = [d["Template"].x[ti].numpy() for d, _, ti in train_data]
    y_rf = [CLASS_TO_IDX[ec] for _, ec, _ in train_data]
    rf_model = RandomForestClassifier(n_estimators=100, random_state=SEED, max_depth=5)
    rf_model.fit(np.array(X_rf), np.array(y_rf))

    # 5. Graph-Augmented Random Forest (14-dim)
    aug_rf_model = RandomForestClassifier(n_estimators=100, random_state=SEED, max_depth=5)
    aug_rf_model.fit(np.array(X_aug_mlp_list), np.array(y_rf))

    # 6. Rule-Based
    rule_model = RuleBaseline()

    # 7. BloodHound BFS
    bfs_model = BloodHoundBFSBaseline()

    return cg_model, mlp_model, aug_mlp_model, rf_model, aug_rf_model, rule_model, bfs_model


def main():
    print("=" * 75)
    print("Adversarial Hard Negatives Evaluation (Zero-Shot Generalization Protocol)")
    print("=" * 75)

    # 1. Generate Training Dataset WITHOUT hard negatives (Pure Normal Safe)
    print(f"\n[1/3] Generating {NUM_TRAIN_ENVS} standard training environments (zero HN exposure)...")
    train_dataset = generate_dataset(
        num_envs=NUM_TRAIN_ENVS, balanced=True, seed=SEED, include_hard_negatives=False
    )
    for data, esc_class, target_idx in train_dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)

    # 2. Generate Test Dataset WITH adversarial hard negatives (Held-out seed)
    print(f"      Generating {NUM_TEST_ENVS} test environments with adversarial hard negatives...")
    test_dataset = generate_dataset(
        num_envs=NUM_TEST_ENVS, balanced=True, seed=SEED + 999, include_hard_negatives=True
    )
    for data, esc_class, target_idx in test_dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)

    # Extract hard negative samples
    hn_test = [x for x in test_dataset if is_hard_negative(x[0], x[1], x[2])]
    print(f"      Total test environments: {len(test_dataset)}")
    print(f"      Extracted Hard Negatives: {len(hn_test)} (Safe templates with ESC configuration flags)")

    # 3. Train all models
    print(f"\n[2/3] Training 7 classifiers on standard training set...")
    cg, mlp, aug_mlp, rf, aug_rf, rule, bfs = train_models(train_dataset)

    # 4. Zero-Shot Evaluation on Hard Negatives subset
    print(f"\n[3/3] Evaluating zero-shot generalization on Hard Negatives subset...")
    cg.eval()
    mlp.eval()
    aug_mlp.eval()

    correct = {
        "CertGraph": 0,
        "MLP (Features)": 0,
        "Random Forest (Features)": 0,
        "Rule-Based": 0,
        "Graph-Augmented MLP": 0,
        "Graph-Augmented RF": 0,
        "BloodHound BFS": 0,
    }

    total = len(hn_test)

    for data, esc_class, t_idx in hn_test:
        y_true = CLASS_TO_IDX[esc_class]  # Safe (6)

        # 1. CertGraph
        with torch.no_grad():
            out_cg = cg(data.x_dict, data.edge_index_dict)
            pred_cg = out_cg[t_idx].argmax().item()
            if pred_cg == y_true:
                correct["CertGraph"] += 1

        # 2. MLP (features)
        with torch.no_grad():
            t_feat = data["Template"].x[t_idx].unsqueeze(0)
            pred_mlp = mlp(t_feat).argmax().item()
            if pred_mlp == y_true:
                correct["MLP (Features)"] += 1

        # 3. RF (features)
        pred_rf = rf.predict([data["Template"].x[t_idx].numpy()])[0]
        if pred_rf == y_true:
            correct["Random Forest (Features)"] += 1

        # 4. Rule-Based
        pred_rule = rule.predict(t_feat)[0].item()
        if pred_rule == y_true:
            correct["Rule-Based"] += 1

        # 5. Graph-Augmented MLP
        with torch.no_grad():
            aug_feat = torch.tensor([data["Template"].x[t_idx].tolist() + extract_graph_counts(data, t_idx)], dtype=torch.float)
            pred_aug_mlp = aug_mlp(aug_feat).argmax().item()
            if pred_aug_mlp == y_true:
                correct["Graph-Augmented MLP"] += 1

        # 6. Graph-Augmented RF
        aug_vec = data["Template"].x[t_idx].tolist() + extract_graph_counts(data, t_idx)
        pred_aug_rf = aug_rf.predict([aug_vec])[0]
        if pred_aug_rf == y_true:
            correct["Graph-Augmented RF"] += 1

        # 7. BloodHound BFS
        pred_bfs = bfs.predict_sample(data, t_idx)
        if pred_bfs == y_true:
            correct["BloodHound BFS"] += 1

    # Print summary
    summary = {}
    print("\n" + "=" * 65)
    print(f"{'Classifier':<30} {'Zero-Shot Accuracy':>20} {'Correct/Total':>12}")
    print("-" * 65)
    for model_name, corr in correct.items():
        acc = corr / total if total > 0 else 0
        summary[model_name] = {
            "accuracy": float(acc),
            "correct": int(corr),
            "total": int(total),
        }
        print(f"{model_name:<30} {acc * 100:>19.2f}% {corr:>7}/{total}")
    print("=" * 65)

    # Save results JSON
    json_path = os.path.join(RESULTS_DIR, "hard_negatives_results.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n      Saved JSON: {json_path}")

    # Plotting
    plt.rcParams.update({
        "figure.facecolor": "#0f172a", "axes.facecolor": "#1e293b",
        "text.color": "white", "axes.labelcolor": "#94a3b8",
        "xtick.color": "#94a3b8", "ytick.color": "#94a3b8",
    })

    fig, ax = plt.subplots(figsize=(10, 5.5))
    models = list(summary.keys())
    accuracies = [summary[m]["accuracy"] * 100 for m in models]
    colors = ["#38bdf8", "#f87171", "#fb923c", "#fbbf24", "#34d399", "#818cf8", "#a78bfa"]

    bars = ax.bar(models, accuracies, color=colors, alpha=0.9, width=0.55, edgecolor="white", linewidth=0.5)
    for bar in bars:
        height = bar.get_height()
        ax.text(
            bar.get_x() + bar.get_width() / 2, height + 2,
            f"{height:.1f}%", ha="center", va="bottom", fontsize=10, fontweight="bold", color="white"
        )

    ax.set_ylabel("Zero-Shot Accuracy (%)", fontsize=11)
    ax.set_ylim(0, 115)
    ax.set_title("Zero-Shot Generalization on Adversarial Hard Negatives (Safe Samples)", fontsize=12, fontweight="bold", pad=15)
    ax.grid(True, axis="y", alpha=0.15, color="#64748b")
    plt.xticks(rotation=20, ha="right", fontsize=9)
    for s in ax.spines.values():
        s.set_color("#334155")

    plot_path = os.path.join(RESULTS_DIR, "hard_negatives_comparison.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"      Saved Plot: {plot_path}")
    print("[✓] Zero-Shot Hard Negatives evaluation complete!")


if __name__ == "__main__":
    main()
