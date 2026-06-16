"""
plot_comparison.py — Visualizing comparative analysis results.
==============================================================
Generates publication-quality charts comparing CertGraph, Certipy, and BloodHound.
"""

import os
import json
import matplotlib.pyplot as plt
import numpy as np

def main():
    research_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    results_dir = os.path.join(research_root, "results", "phase2")
    json_path = os.path.join(results_dir, "tool_comparison_results.json")
    
    if not os.path.exists(json_path):
        print(f"Results file not found: {json_path}")
        return

    with open(json_path, "r") as f:
        results = json.load(f)

    # Prepare data
    datasets = list(results.keys())  # ["Synthetic", "ADSynth (Realistic)"]
    tools = ["Certipy", "BloodHound", "CertGraph"]
    
    # Color palette
    colors = {
        "Certipy": "#d9534f",      # Red-ish
        "BloodHound": "#f0ad4e",   # Orange-ish
        "CertGraph": "#5cb85c"     # Green-ish
    }
    
    # Plot 1: F1-Scores
    fig, ax = plt.subplots(figsize=(8, 5))
    x = np.arange(len(datasets))
    width = 0.25

    for i, tool in enumerate(tools):
        f1_scores = [results[ds][tool]["macro_f1"] for ds in datasets]
        ax.bar(x + i*width, f1_scores, width, label=tool, color=colors[tool], edgecolor="black", alpha=0.85)

    ax.set_ylabel("Macro F1-Score", fontsize=12, fontweight="bold")
    ax.set_title("Vulnerability Classification Performance (F1-Score)", fontsize=13, fontweight="bold", pad=15)
    ax.set_xticks(x + width)
    ax.set_xticklabels(datasets, fontsize=11, fontweight="bold")
    ax.set_ylim(0.5, 1.05)
    ax.grid(axis="y", linestyle="--", alpha=0.7)
    ax.legend(loc="lower left", fontsize=10)

    # Annotate bars
    for i, tool in enumerate(tools):
        f1_scores = [results[ds][tool]["macro_f1"] for ds in datasets]
        for idx, score in enumerate(f1_scores):
            ax.text(idx + i*width, score + 0.01, f"{score:.3f}", ha="center", va="bottom", fontsize=9, fontweight="bold")

    plt.tight_layout()
    chart_path = os.path.join(results_dir, "tool_comparison_f1.png")
    plt.savefig(chart_path, dpi=300)
    plt.close()
    print(f"[✓] Saved comparison chart to: {chart_path}")

if __name__ == "__main__":
    main()
