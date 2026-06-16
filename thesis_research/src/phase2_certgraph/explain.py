#!/usr/bin/env python3
"""
explain.py — Explainability & Attention Analysis for CertGraph GNN
=================================================================
Extracts and visualizes edge attention coefficients (alpha) from GATConv layers.
This demonstrates the model's reliance on security relationships (edges)
rather than just flat properties (nodes) for classifying ADCS vulnerabilities.
"""

import os
import torch
import torch.nn.functional as F
import numpy as np
import matplotlib.pyplot as plt
from collections import defaultdict
from generator import generate_dataset, CLASS_TO_IDX, NUM_CLASSES, ESC_CLASSES
from model import CertGraph

# Config
NUM_ENVS = 200  # small dataset for fast self-contained execution
EPOCHS = 60
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005

RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
os.makedirs(RESULTS_DIR, exist_ok=True)


def train_explain_model(dataset) -> CertGraph:
    """Train a quick model to learn meaningful attention weights."""
    print("      Training GNN to learn attention weights...")
    sample = dataset[0][0]
    model = CertGraph(
        metadata=sample.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT
    )
    
    # Lazy init
    with torch.no_grad():
        model.eval()
        _ = model(sample.x_dict, sample.edge_index_dict)
        
    model.train()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    
    for epoch in range(1, EPOCHS + 1):
        model.train()
        for data, esc_class, target_idx in dataset:
            optimizer.zero_grad()
            logits = model(data.x_dict, data.edge_index_dict)
            y = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)
            loss = F.cross_entropy(logits[target_idx].unsqueeze(0), y)
            loss.backward()
            optimizer.step()
            
    print("      Model trained successfully.")
    return model


def main():
    print("=" * 70)
    print("CertGraph GNN Attention Explainability Analysis")
    print("=" * 70)
    
    # 1. Generate dataset
    print(f"\n[1/3] Generating sample environments...")
    dataset = generate_dataset(num_envs=NUM_ENVS, balanced=True, seed=42)
    
    # 2. Train model
    print(f"\n[2/3] Preparing model...")
    model = train_explain_model(dataset)
    model.eval()
    
    # 3. Find a sample of interest (e.g. ESC13)
    print(f"\n[3/3] Extracting attention weights...")
    target_sample = None
    target_cls = "ESC13"
    
    for data, esc_class, target_idx in dataset:
        if esc_class == target_cls:
            target_sample = (data, esc_class, target_idx)
            break
            
    if target_sample is None:
        target_sample = dataset[0]  # fallback
        
    data, esc_class, target_idx = target_sample
    print(f"      Selected sample: Class={esc_class}, Target node=Template_{target_idx}")
    
    # Extract attention weights dictionary
    # dict: edge_type -> (edge_index, alpha)
    attentions = model.get_attention_weights(data.x_dict, data.edge_index_dict)
    
    # Identify 2-hop neighborhood of the target template node to filter relevant edges
    nodes_in_neighborhood = {("Template", target_idx)}
    
    # 1-hop connections (either incoming or outgoing from the target Template node)
    for edge_type, (edge_index, _) in attentions.items():
        src_type, _, dst_type = edge_type
        for i in range(edge_index.shape[1]):
            src_idx = edge_index[0, i].item()
            dst_idx = edge_index[1, i].item()
            if (src_type == "Template" and src_idx == target_idx) or (dst_type == "Template" and dst_idx == target_idx):
                nodes_in_neighborhood.add((src_type, src_idx))
                nodes_in_neighborhood.add((dst_type, dst_idx))
                
    # 2-hop connections
    added_nodes = set()
    for edge_type, (edge_index, _) in attentions.items():
        src_type, _, dst_type = edge_type
        for i in range(edge_index.shape[1]):
            src_idx = edge_index[0, i].item()
            dst_idx = edge_index[1, i].item()
            if (src_type, src_idx) in nodes_in_neighborhood or (dst_type, dst_idx) in nodes_in_neighborhood:
                added_nodes.add((src_type, src_idx))
                added_nodes.add((dst_type, dst_idx))
    nodes_in_neighborhood.update(added_nodes)

    # Aggregate and name edges in the 2-hop neighborhood
    edge_records = []
    
    for edge_type, (edge_index, alpha) in attentions.items():
        src_type, rel_type, dst_type = edge_type
        alpha_mean = alpha.mean(dim=-1).detach().cpu().numpy()  # average over heads
        
        # Get source/destination names
        src_names = getattr(data[src_type], "names", [f"{src_type}_{i}" for i in range(data[src_type].x.shape[0])])
        dst_names = getattr(data[dst_type], "names", [f"{dst_type}_{i}" for i in range(data[dst_type].x.shape[0])])
        
        for i in range(edge_index.shape[1]):
            src_idx = edge_index[0, i].item()
            dst_idx = edge_index[1, i].item()
            
            # Filter to only edges within the 2-hop neighborhood of target
            if (src_type, src_idx) not in nodes_in_neighborhood or (dst_type, dst_idx) not in nodes_in_neighborhood:
                continue
                
            src_name = src_names[src_idx]
            dst_name = dst_names[dst_idx]
            weight = float(alpha_mean[i])
            
            # Label cleanups
            src_clean = src_name.split("@")[0] if "@" in src_name else src_name
            dst_clean = dst_name.split("@")[0] if "@" in dst_name else dst_name
            
            edge_label = f"({src_type}) {src_clean} ──[{rel_type}]──> ({dst_type}) {dst_clean}"
            edge_records.append((edge_label, weight))
            
    # Sort by attention weight
    ranked = sorted(edge_records, key=lambda x: -x[1])
    
    print("\nTop 5 Attended Edges:")
    for label, weight in ranked[:5]:
        print(f"  {weight:.4f} : {label}")
        
    # Plot top-10 attended edges
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e", "axes.facecolor": "#16213e",
        "text.color": "white", "axes.labelcolor": "#aaa",
        "xtick.color": "#666", "ytick.color": "#666",
    })
    
    top_n = min(10, len(ranked))
    top_edges = ranked[:top_n]
    labels = [x[0] for x in reversed(top_edges)]
    weights = [x[1] for x in reversed(top_edges)]
    
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.barh(range(len(labels)), weights, color="#FF6B6B", alpha=0.85, height=0.6, edgecolor="white", linewidth=0.5)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8, color="white")
    ax.set_xlabel("Average Attention Coefficient (α)", fontsize=11)
    ax.set_title("CertGraph Attention Weights — Top Edges in ESC13 Environment", fontsize=13, fontweight="bold", pad=15)
    ax.grid(True, axis="x", alpha=0.1, color="#555")
    for s in ax.spines.values():
        s.set_color("#333")
        
    plot_path = os.path.join(RESULTS_DIR, "attention_explainability.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    
    print(f"\n      Attention Plot: {plot_path}")
    print("[✓] Explainability analysis complete!")


if __name__ == "__main__":
    main()
