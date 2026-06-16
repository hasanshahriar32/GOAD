#!/usr/bin/env python3
"""
hard_negatives.py — Hard Negative Evaluation for CertGraph GNN
============================================================
Compares CertGraph against MLP, Random Forest, and Rule-Based baselines
on "Adversarial Hard Negatives": Safe certificate templates that look like
vulnerabilities based on local flags, but lack the necessary graph paths.
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

# Config
NUM_ENVS = 3000
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 80
BATCH_SIZE = 64
SEED = 42

RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
os.makedirs(RESULTS_DIR, exist_ok=True)


def is_hard_negative(data, esc_class, target_idx) -> bool:
    """Identify if a Safe template is a hard negative based on feature flags."""
    if esc_class != "Safe":
        return False
    features = data['Template'].x[target_idx].tolist()
    # Feature indices:
    # 0: enrollee_supplies_subject
    # 7: has_issuance_policy_oid
    # 8: has_vulnerable_acl
    has_esc1_flags = (features[0] == 1.0)
    has_esc13_flags = (features[7] == 1.0)
    has_esc4_flags = (features[8] == 1.0)
    return has_esc1_flags or has_esc13_flags or has_esc4_flags


def train_models(train_data):
    """Train CertGraph, MLP, and RF on train data."""
    sample = train_data[0][0]
    
    # 1. CertGraph
    cg_model = CertGraph(
        metadata=sample.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT
    )
    
    # 2. MLP
    mlp_model = MLPBaseline(
        input_dim=10,
        hidden_dim=32,
        num_classes=NUM_CLASSES
    )
    
    # Prepare PyG DataLoader
    train_list = [d for d, _, _ in train_data]
    loader = DataLoader(train_list, batch_size=BATCH_SIZE, shuffle=True)
    
    # Lazy init CertGraph
    with torch.no_grad():
        cg_model.eval()
        _ = cg_model(sample.x_dict, sample.edge_index_dict)
        
    optimizer_cg = torch.optim.Adam(cg_model.parameters(), lr=LR, weight_decay=1e-4)
    optimizer_mlp = torch.optim.Adam(mlp_model.parameters(), lr=LR, weight_decay=1e-4)
    
    for epoch in range(1, EPOCHS + 1):
        cg_model.train()
        mlp_model.train()
        for batch in loader:
            # Train CertGraph
            optimizer_cg.zero_grad()
            logits_cg = cg_model(batch.x_dict, batch.edge_index_dict)
            ptr = batch['Template'].ptr
            target_indices = ptr[:-1] + batch.target_idx
            loss_cg = F.cross_entropy(logits_cg[target_indices], batch.y_class)
            loss_cg.backward()
            optimizer_cg.step()
            
            # Train MLP
            optimizer_mlp.zero_grad()
            t_feats = batch['Template'].x[target_indices]
            logits_mlp = mlp_model(t_feats)
            loss_mlp = F.cross_entropy(logits_mlp, batch.y_class)
            loss_mlp.backward()
            optimizer_mlp.step()
            
    # 3. Random Forest
    X_train = []
    y_train = []
    for d, esc_class, t_idx in train_data:
        X_train.append(d['Template'].x[t_idx].numpy())
        y_train.append(CLASS_TO_IDX[esc_class])
        
    rf_model = RandomForestClassifier(n_estimators=100, random_state=SEED)
    rf_model.fit(X_train, y_train)
    
    # 4. Rule-Based
    rule_model = RuleBaseline()
    
    return cg_model, mlp_model, rf_model, rule_model


def main():
    print("=" * 70)
    print("Adversarial Hard Negatives Evaluation")
    print("=" * 70)
    
    # 1. Generate and split dataset
    print(f"\n[1/3] Generating {NUM_ENVS} AD environments...")
    dataset = generate_dataset(num_envs=NUM_ENVS, balanced=True, seed=SEED)
    
    for data, esc_class, target_idx in dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)
        
    # Split into 80% train, 20% test
    split_idx = int(len(dataset) * 0.8)
    train_data = dataset[:split_idx]
    test_data = dataset[split_idx:]
    
    # 2. Extract Hard Negatives from test data
    hn_test = [x for x in test_data if is_hard_negative(x[0], x[1], x[2])]
    print(f"      Total test samples: {len(test_data)}")
    print(f"      Hard Negatives:     {len(hn_test)} (labeled Safe but having vulnerable features)")
    
    if len(hn_test) == 0:
        print("      No hard negatives found. Retrying with full dataset.")
        hn_test = [x for x in dataset if is_hard_negative(x[0], x[1], x[2])]
        print(f"      Hard Negatives from full dataset: {len(hn_test)}")
        
    # 3. Train models
    print(f"\n[2/3] Training classifiers on standard training set...")
    cg, mlp, rf, rule = train_models(train_data)
    
    # 4. Evaluate on Hard Negatives subset
    print(f"\n[3/3] Evaluating on Hard Negatives subset...")
    cg.eval()
    mlp.eval()
    
    correct = {
        "CertGraph": 0,
        "MLP": 0,
        "Random Forest": 0,
        "Rule-Based": 0
    }
    
    total = len(hn_test)
    
    for data, esc_class, t_idx in hn_test:
        y_true = CLASS_TO_IDX[esc_class] # Safe (6)
        
        # CertGraph
        with torch.no_grad():
            out_cg = cg(data.x_dict, data.edge_index_dict)
            pred_cg = out_cg[t_idx].argmax().item()
            if pred_cg == y_true:
                correct["CertGraph"] += 1
                
        # MLP
        with torch.no_grad():
            t_feat = data['Template'].x[t_idx].unsqueeze(0)
            out_mlp = mlp(t_feat)
            pred_mlp = out_mlp.argmax().item()
            if pred_mlp == y_true:
                correct["MLP"] += 1
                
        # RF
        pred_rf = rf.predict([data['Template'].x[t_idx].numpy()])[0]
        if pred_rf == y_true:
            correct["Random Forest"] += 1
            
        # Rule-Based
        t_feat = data['Template'].x[t_idx].unsqueeze(0)
        pred_rule = rule.predict(t_feat)[0].item()
        if pred_rule == y_true:
            correct["Rule-Based"] += 1
            
    # Compute accuracy
    summary = {}
    print("\n" + "=" * 50)
    print(f"{'Classifier':<20} {'Accuracy on Hard Negatives':>25}")
    print("-" * 48)
    for model_name, corr in correct.items():
        acc = corr / total if total > 0 else 0
        summary[model_name] = acc
        print(f"{model_name:<20} {acc * 100:.2f}% ({corr}/{total})")
    print("=" * 50)
    
    # Save results JSON
    json_path = os.path.join(RESULTS_DIR, "hard_negatives_results.json")
    with open(json_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n      Saved JSON: {json_path}")
    
    # Plotting
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e", "axes.facecolor": "#16213e",
        "text.color": "white", "axes.labelcolor": "#aaa",
        "xtick.color": "#666", "ytick.color": "#666",
    })
    
    fig, ax = plt.subplots(figsize=(8, 5))
    models = list(summary.keys())
    accuracies = [summary[m] * 100 for m in models]
    colors = ["#4ECDC4", "#FF6B6B", "#FFA07A", "#45B7D1"]
    
    bars = ax.bar(models, accuracies, color=colors, alpha=0.85, width=0.5, edgecolor="white", linewidth=0.5)
    for bar in bars:
        ax.text(bar.get_x() + bar.get_width()/2, bar.get_height() + 2,
                f"{bar.get_height():.1f}%", ha="center", va="bottom", fontsize=11, fontweight="bold", color="white")
                
    ax.set_ylabel("Accuracy (%)", fontsize=11)
    ax.set_ylim(0, 115)
    ax.set_title("Classifier Accuracy on Adversarial Hard Negatives (Safe Samples)", fontsize=12, fontweight="bold", pad=15)
    ax.grid(True, axis="y", alpha=0.1, color="#555")
    for s in ax.spines.values():
        s.set_color("#333")
        
    plot_path = os.path.join(RESULTS_DIR, "hard_negatives_comparison.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"      Saved Plot: {plot_path}")
    print("[✓] Hard Negatives analysis complete!")


if __name__ == "__main__":
    main()
