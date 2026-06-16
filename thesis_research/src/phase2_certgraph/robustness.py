"""
robustness.py — Robustness, Learning Curves & Confusion Matrix Evaluations
========================================================================
Performs GNN sensitivity analysis under edge perturbation and feature noise.
Generates learning curves (performance vs. training set size) and confusion matrices.
"""

import os
import json
import random
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix, f1_score, accuracy_score
from torch_geometric.loader import DataLoader
from torch_geometric.utils import dropout_edge

from generator import generate_dataset, CLASS_TO_IDX, NUM_CLASSES, ESC_CLASSES
from model import CertGraph

# Configs matching training
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 60
BATCH_SIZE = 64

def perturb_edges(data, p):
    """Randomly drop p fraction of edges from the graph."""
    if p == 0.0:
        return data
    perturbed = data.clone()
    for edge_type in perturbed.edge_types:
        edge_index = perturbed[edge_type].edge_index
        if edge_index.shape[1] > 0:
            # We can use PyG's dropout_edge
            new_edge_index, _ = dropout_edge(edge_index, p=p, training=True)
            perturbed[edge_type].edge_index = new_edge_index
    return perturbed

def inject_feature_noise(data, p):
    """Randomly flip binary feature values with probability p."""
    if p == 0.0:
        return data
    perturbed = data.clone()
    for node_type in perturbed.node_types:
        x = perturbed[node_type].x
        if x.numel() > 0:
            # Generate a mask of features to flip
            mask = torch.rand(x.shape) < p
            # For simplicity, if flag is >0.5, make it 0.0, else 1.0 (flip it)
            flipped = torch.where(x > 0.5, torch.zeros_like(x), torch.ones_like(x))
            perturbed[node_type].x = torch.where(mask, flipped, x)
    return perturbed

def evaluate_robustness(model, dataset, test_case, p):
    model.eval()
    preds = []
    labels = []
    
    classes_idx = {c: idx for idx, c in enumerate(ESC_CLASSES)}

    with torch.no_grad():
        for data, esc_class, target_idx in dataset:
            labels.append(classes_idx[esc_class])
            
            # Apply perturbation
            if test_case == "edge":
                graph = perturb_edges(data, p)
            elif test_case == "feature":
                graph = inject_feature_noise(data, p)
            else:
                graph = data
                
            logits = model(graph.x_dict, graph.edge_index_dict)
            pred_idx = logits[target_idx].argmax().item()
            preds.append(pred_idx)
            
    f1 = f1_score(labels, preds, average="macro", zero_division=0)
    acc = accuracy_score(labels, preds)
    return f1, acc, preds, labels

def main():
    research_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    checkpoint_path = os.path.join(research_root, "results", "phase2", "certgraph_best.pt")
    results_dir = os.path.join(research_root, "results", "phase2")
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 75)
    print("ROBUSTNESS & SENSITIVITY EVALUATION")
    print("=" * 75)

    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found at: {checkpoint_path}. Train the model first.")

    # Load test dataset
    print("[*] Generating test dataset for sensitivity analysis...")
    test_dataset = generate_dataset(num_envs=200, balanced=True, seed=200)

    # Load GNN
    print("[*] Loading best GNN checkpoint...")
    checkpoint = torch.load(checkpoint_path, weights_only=False)
    sample_graph = test_dataset[0][0]
    model = CertGraph(
        metadata=sample_graph.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT,
    )
    with torch.no_grad():
        model.eval()
        _ = model(sample_graph.x_dict, sample_graph.edge_index_dict)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # 1. Edge Perturbation Analysis
    print("\n[*] Running Edge Perturbation Experiment...")
    edge_rates = [0.0, 0.05, 0.10, 0.20, 0.30]
    edge_f1s = []
    for r in edge_rates:
        f1, acc, _, _ = evaluate_robustness(model, test_dataset, "edge", r)
        edge_f1s.append(f1)
        print(f"  - Edge Drop Rate: {r:<5} | Macro-F1: {f1:.4f} | Acc: {acc:.4f}")

    # 2. Feature Noise Analysis
    print("\n[*] Running Feature Noise Experiment...")
    feature_rates = [0.0, 0.05, 0.10, 0.20]
    feat_f1s = []
    for r in feature_rates:
        f1, acc, _, _ = evaluate_robustness(model, test_dataset, "feature", r)
        feat_f1s.append(f1)
        print(f"  - Feature Flip Rate: {r:<5} | Macro-F1: {f1:.4f} | Acc: {acc:.4f}")

    # 3. Generate Confusion Matrix
    print("\n[*] Generating Confusion Matrix...")
    _, _, preds, labels = evaluate_robustness(model, test_dataset, "none", 0.0)
    cm = confusion_matrix(labels, preds)
    
    # Plot Confusion Matrix
    fig, ax = plt.subplots(figsize=(6, 5))
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    ax.figure.colorbar(im, ax=ax)
    ax.set(xticks=np.arange(cm.shape[1]),
           yticks=np.arange(cm.shape[0]),
           xticklabels=ESC_CLASSES, yticklabels=ESC_CLASSES,
           title="CertGraph Confusion Matrix",
           ylabel="True Label",
           xlabel="Predicted Label")
    
    # Rotate labels
    plt.setp(ax.get_xticklabels(), rotation=45, ha="right", rotation_mode="anchor")

    # Annotate numbers
    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            ax.text(j, i, format(cm[i, j], 'd'),
                    ha="center", va="center",
                    color="white" if cm[i, j] > thresh else "black")
    fig.tight_layout()
    cm_path = os.path.join(results_dir, "confusion_matrix.png")
    plt.savefig(cm_path, dpi=300)
    plt.close()
    print(f"    Saved Confusion Matrix to: {cm_path}")

    # 4. Learning Curve Analysis
    print("\n[*] Running Learning Curve Analysis...")
    train_sizes = [40, 80, 160, 320]
    lc_f1s = []
    
    for size in train_sizes:
        print(f"  - Training on size={size} environments...")
        # Generate training dataset of specific size
        train_dataset = generate_dataset(num_envs=size, balanced=True, seed=300)
        
        # Prepare loaders
        for data, esc_class, target_idx in train_dataset:
            data.target_idx = torch.tensor([target_idx], dtype=torch.long)
            data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)
        
        train_list = [d for d, _, _ in train_dataset]
        train_loader = DataLoader(train_list, batch_size=BATCH_SIZE, shuffle=True)
        
        # Fresh model
        lc_model = CertGraph(
            metadata=sample_graph.metadata(),
            hidden_channels=HIDDEN_DIM,
            out_channels=OUT_DIM,
            num_classes=NUM_CLASSES,
            num_heads=NUM_HEADS,
            dropout=DROPOUT,
        )
        with torch.no_grad():
            lc_model.eval()
            _ = lc_model(sample_graph.x_dict, sample_graph.edge_index_dict)
            
        optimizer = torch.optim.Adam(lc_model.parameters(), lr=LR, weight_decay=1e-4)
        
        # Mini training loop
        for epoch in range(1, EPOCHS + 1):
            lc_model.train()
            for batch in train_loader:
                optimizer.zero_grad()
                logits = lc_model(batch.x_dict, batch.edge_index_dict)
                ptr = batch['Template'].ptr
                target_indices = ptr[:-1] + batch.target_idx
                target_logits = logits[target_indices]
                loss = F.cross_entropy(target_logits, batch.y_class)
                loss.backward()
                optimizer.step()
                
        # Evaluate on standard test set
        f1, acc, _, _ = evaluate_robustness(lc_model, test_dataset, "none", 0.0)
        lc_f1s.append(f1)
        print(f"    Size: {size:<4} | Macro-F1: {f1:.4f}")

    # Plot Learning Curve & Sensitivity Charts
    fig, axs = plt.subplots(1, 3, figsize=(15, 4.5))
    
    # 1. Edge Perturbation plot
    axs[0].plot(edge_rates, edge_f1s, marker="o", color="#d9534f", linewidth=2)
    axs[0].set_title("Edge Perturbation Sensitivity", fontweight="bold")
    axs[0].set_xlabel("Edge Drop Rate", fontweight="bold")
    axs[0].set_ylabel("Macro F1-Score", fontweight="bold")
    axs[0].grid(linestyle="--")
    axs[0].set_ylim(0.5, 1.05)

    # 2. Feature Noise plot
    axs[1].plot(feature_rates, feat_f1s, marker="s", color="#f0ad4e", linewidth=2)
    axs[1].set_title("Feature Noise Sensitivity", fontweight="bold")
    axs[1].set_xlabel("Feature Flip Rate", fontweight="bold")
    axs[1].set_ylabel("Macro F1-Score", fontweight="bold")
    axs[1].grid(linestyle="--")
    axs[1].set_ylim(0.5, 1.05)

    # 3. Learning Curve plot
    axs[2].plot(train_sizes, lc_f1s, marker="^", color="#5cb85c", linewidth=2)
    axs[2].set_title("GNN Learning Curve", fontweight="bold")
    axs[2].set_xlabel("Training Set Size (Domains)", fontweight="bold")
    axs[2].set_ylabel("Macro F1-Score", fontweight="bold")
    axs[2].grid(linestyle="--")
    axs[2].set_ylim(0.5, 1.05)

    plt.tight_layout()
    lc_chart_path = os.path.join(results_dir, "robustness_analysis.png")
    plt.savefig(lc_chart_path, dpi=300)
    plt.close()
    print(f"\n[✓] Saved robustness analysis chart: {lc_chart_path}")

    # Save results to JSON
    out_json = os.path.join(results_dir, "robustness_results.json")
    results = {
        "edge_perturbation": {
            "rates": edge_rates,
            "f1s": edge_f1s
        },
        "feature_noise": {
            "rates": feature_rates,
            "f1s": feat_f1s
        },
        "learning_curve": {
            "sizes": train_sizes,
            "f1s": lc_f1s
        }
    }
    with open(out_json, "w") as f:
        json.dump(results, f, indent=2)
    print(f"[✓] Saved JSON results: {out_json}")

if __name__ == "__main__":
    main()
