#!/usr/bin/env python3
"""
Regenerate Figure 5.1 components with large, high-visibility publication fonts:
- figures/confusion_matrix.png
- figures/gnn_baselines_comparison.png
"""
import os
import json
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_DIRS = [
    '/home/hs32/Desktop/GOAD/thesis_paper/figures',
    '/home/hs32/Desktop/GOAD/thesis_research/results/phase2'
]

ESC_CLASSES = ["ESC1", "ESC2", "ESC3", "ESC4", "ESC9", "ESC13", "Safe"]

def generate_confusion_matrix():
    cm = np.array([
        [29,  0,  0,  0,  0,  0,  0],
        [ 0, 29,  0,  0,  0,  0,  0],
        [ 0,  0, 29,  0,  0,  0,  0],
        [ 0,  0,  0, 29,  0,  0,  0],
        [ 0,  0,  0,  0, 28,  0,  0],
        [ 0,  0,  0,  0,  0, 28,  0],
        [ 0,  0,  0,  0,  0,  0, 28]
    ])

    fig, ax = plt.subplots(figsize=(7.5, 6.2), dpi=300)
    im = ax.imshow(cm, interpolation='nearest', cmap=plt.cm.Blues)
    cbar = ax.figure.colorbar(im, ax=ax, fraction=0.046, pad=0.04)
    cbar.ax.tick_params(labelsize=11)
    cbar.set_label("Sample Count", fontsize=12, fontweight='bold', labelpad=10)

    ax.set_xticks(np.arange(len(ESC_CLASSES)))
    ax.set_yticks(np.arange(len(ESC_CLASSES)))
    ax.set_xticklabels(ESC_CLASSES, fontsize=12, fontweight='bold', rotation=38, ha="right", rotation_mode="anchor")
    ax.set_yticklabels(ESC_CLASSES, fontsize=12, fontweight='bold')
    
    ax.set_title("CertGraph Confusion Matrix (Test Set, N=200)", fontsize=14, fontweight='bold', pad=15)
    ax.set_ylabel("True Vulnerability Class", fontsize=13, fontweight='bold', labelpad=10)
    ax.set_xlabel("Predicted Vulnerability Class", fontsize=13, fontweight='bold', labelpad=10)

    thresh = cm.max() / 2.
    for i in range(cm.shape[0]):
        for j in range(cm.shape[1]):
            val = cm[i, j]
            color = "white" if val > thresh else "#334155"
            weight = 'bold' if val > 0 else 'normal'
            fontsize = 13.5 if val > 0 else 11.5
            ax.text(j, i, str(val), ha="center", va="center",
                    color=color, fontsize=fontsize, fontweight=weight)

    fig.tight_layout()
    for d in OUTPUT_DIRS:
        p = os.path.join(d, "confusion_matrix.png")
        fig.savefig(p, dpi=300, bbox_inches='tight')
        print(f"[✓] Saved {p}")
    plt.close()


def generate_gnn_baselines():
    json_path = '/home/hs32/Desktop/GOAD/thesis_research/results/phase2/gnn_baselines_results.json'
    with open(json_path, 'r') as f:
        summary = json.load(f)

    model_names = list(summary.keys())
    f1_means = [summary[name]["f1_mean"] for name in model_names]
    f1_stds = [summary[name]["f1_std"] for name in model_names]
    acc_means = [summary[name]["acc_mean"] for name in model_names]
    acc_stds = [summary[name]["acc_std"] for name in model_names]

    x = np.arange(len(model_names))
    width = 0.35

    fig, ax = plt.subplots(figsize=(9.8, 5.6), dpi=300)
    rects1 = ax.bar(x - width/2, f1_means, width, yerr=f1_stds, label='Macro-F1 Score',
                    capsize=6, color='#1d4ed8', edgecolor='#1f2937', linewidth=1.1, alpha=0.9)
    rects2 = ax.bar(x + width/2, acc_means, width, yerr=acc_stds, label='Accuracy',
                    capsize=6, color='#60a5fa', edgecolor='#1f2937', linewidth=1.1, alpha=0.9)

    ax.set_ylabel('Performance Score (0.0 to 1.0)', fontsize=13, fontweight='bold', labelpad=10)
    ax.set_title('GNN Architecture Baseline Comparison (5-Fold Cross-Validation)', fontsize=14, fontweight='bold', pad=15)
    ax.set_xticks(x)
    ax.set_xticklabels(model_names, fontsize=12, fontweight='bold')
    ax.tick_params(axis='y', labelsize=11)
    ax.set_ylim(0.0, 1.15)
    ax.legend(loc='lower right', fontsize=11.5, frameon=True, facecolor='#ffffff', edgecolor='#d1d5db')
    ax.grid(axis='y', linestyle='--', alpha=0.6, color='#e5e7eb')
    ax.set_axisbelow(True)

    def autolabel(rects):
        for rect in rects:
            height = rect.get_height()
            ax.annotate(f'{height:.3f}',
                        xy=(rect.get_x() + rect.get_width() / 2, height),
                        xytext=(0, 4),
                        textcoords="offset points",
                        ha='center', va='bottom', fontsize=10.5, fontweight='bold')

    autolabel(rects1)
    autolabel(rects2)

    fig.tight_layout()
    for d in OUTPUT_DIRS:
        p = os.path.join(d, "gnn_baselines_comparison.png")
        fig.savefig(p, dpi=300, bbox_inches='tight')
        print(f"[✓] Saved {p}")
    plt.close()


if __name__ == '__main__':
    generate_confusion_matrix()
    generate_gnn_baselines()
    print("Successfully regenerated Figure 5.1 components with large fonts.")
