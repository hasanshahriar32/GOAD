#!/usr/bin/env python3
"""
Regenerate Figure 7.2 (robustness_analysis.png) in a 2-row publication layout:
- Top Left: Edge Perturbation Sensitivity
- Top Right: Feature Noise Sensitivity
- Bottom Center: GNN Learning Curve Convergence
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

def main():
    json_path = "/home/hs32/Desktop/GOAD/thesis_research/results/phase2/robustness_results.json"
    with open(json_path, "r") as f:
        data = json.load(f)

    edge_rates = data["edge_perturbation"]["rates"]
    edge_f1s = data["edge_perturbation"]["f1s"]

    feat_rates = data["feature_noise"]["rates"]
    feat_f1s = data["feature_noise"]["f1s"]

    train_sizes = data["learning_curve"]["sizes"]
    lc_f1s = data["learning_curve"]["f1s"]

    plt.style.use('default')
    plt.rcParams.update({
        'figure.facecolor': '#ffffff',
        'axes.facecolor': '#ffffff',
        'savefig.facecolor': '#ffffff',
        'text.color': '#111827',
        'axes.labelcolor': '#1f2937',
        'xtick.color': '#374151',
        'ytick.color': '#374151',
        'font.family': 'sans-serif',
        'font.size': 11.5,
        'axes.edgecolor': '#9ca3af',
        'axes.linewidth': 1.1,
    })

    fig = plt.figure(figsize=(10.5, 7.8), dpi=300)
    gs = GridSpec(2, 4, figure=fig, hspace=0.38, wspace=0.56)

    # 1. Edge Perturbation plot (Top Left)
    ax1 = fig.add_subplot(gs[0, 0:2])
    ax1.plot(edge_rates, edge_f1s, marker="o", markersize=8.5, color="#dc2626", linewidth=3.2, label="Macro F1")
    ax1.set_title("Edge Perturbation Sensitivity", fontsize=14.5, fontweight="bold", pad=12)
    ax1.set_xlabel("Edge Drop Rate (Dropped Relations)", fontsize=13.0, fontweight="bold")
    ax1.set_ylabel("Macro F1-Score", fontsize=13.0, fontweight="bold")
    ax1.set_ylim(0.55, 1.05)
    ax1.set_xlim(-0.02, 0.35)
    ax1.tick_params(axis='both', which='major', labelsize=12.0)
    ax1.grid(True, linestyle="--", alpha=0.6, color="#e5e7eb")
    ax1.set_axisbelow(True)
    ax1.text(0.02, 0.62, "High topological resilience:\nRetains >94% F1 at 30% drop",
             fontsize=11.5, fontweight="bold", color="#991b1b",
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#fef2f2', edgecolor='#dc2626', lw=1.2))

    # 2. Feature Noise plot (Top Right)
    ax2 = fig.add_subplot(gs[0, 2:4])
    ax2.plot(feat_rates, feat_f1s, marker="s", markersize=8.5, color="#d97706", linewidth=3.2, label="Macro F1")
    ax2.set_title("Configuration Feature Noise Sensitivity", fontsize=14.5, fontweight="bold", pad=12)
    ax2.set_xlabel("Feature Bit-Flip Rate (Attribute Noise)", fontsize=13.0, fontweight="bold")
    ax2.set_ylabel("Macro F1-Score", fontsize=13.0, fontweight="bold")
    ax2.set_ylim(0.55, 1.05)
    ax2.set_xlim(-0.02, 0.25)
    ax2.tick_params(axis='both', which='major', labelsize=12.0)
    ax2.grid(True, linestyle="--", alpha=0.6, color="#e5e7eb")
    ax2.set_axisbelow(True)
    ax2.text(0.08, 0.86, "Attribute vulnerability:\nFlags corrupted → F1 drops",
             fontsize=11.5, fontweight="bold", color="#b45309",
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#fffbeb', edgecolor='#d97706', lw=1.2))

    # 3. Learning Curve plot (Bottom Center)
    ax3 = fig.add_subplot(gs[1, 1:3])
    ax3.plot(train_sizes, lc_f1s, marker="^", markersize=9.0, color="#059669", linewidth=3.2, label="Macro F1")
    ax3.set_title("GNN Sample Efficiency & Learning Curve", fontsize=14.5, fontweight="bold", pad=12)
    ax3.set_xlabel("Training Set Size (Enterprise Domains)", fontsize=13.0, fontweight="bold")
    ax3.set_ylabel("Macro F1-Score", fontsize=13.0, fontweight="bold")
    ax3.set_ylim(0.75, 1.05)
    ax3.tick_params(axis='both', which='major', labelsize=12.0)
    ax3.grid(True, linestyle="--", alpha=0.6, color="#e5e7eb")
    ax3.set_axisbelow(True)
    ax3.text(180, 0.82, "Fast sample convergence:\nCrosses 0.98 F1 with 80 domains",
             fontsize=11.8, fontweight="bold", color="#047857",
             bbox=dict(boxstyle='round,pad=0.35', facecolor='#ecfdf5', edgecolor='#059669', lw=1.2))

    fig.suptitle("CertGraph Empirical Sensitivity, Noise Robustness, and Learning Scaling",
                 fontsize=16.0, fontweight="bold", y=0.98)

    out_paths = [
        "/home/hs32/Desktop/GOAD/thesis_research/results/phase2/robustness_analysis.png",
        "/home/hs32/Desktop/GOAD/thesis_paper/figures/robustness_analysis.png"
    ]
    for p in out_paths:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        fig.savefig(p, dpi=300, bbox_inches='tight', facecolor='#ffffff')
        print(f"[✓] Saved 2-row robustness plot: {p}")
    plt.close()

if __name__ == "__main__":
    main()
