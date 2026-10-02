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
    paper_fig_dir = "/home/hs32/Desktop/GOAD/thesis_paper/figures"
    json_path = os.path.join(results_dir, "tool_comparison_results.json")
    
    if not os.path.exists(json_path):
        print(f"Results file not found: {json_path}")
        return

    with open(json_path, "r") as f:
        results = json.load(f)

    # Prepare data
    datasets = list(results.keys())  # ["Synthetic", "ADSynth (Realistic)"]
    tools = ["Certipy", "BloodHound", "CertGraph"]
    
    # Modern publication color palette
    colors = {
        "Certipy": "#dc2626",      # Vibrant red
        "BloodHound": "#d97706",   # Amber / Orange
        "CertGraph": "#1d4ed8"     # Deep primary blue
    }
    
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

    # Plot: F1-Scores - Wider canvas & large typography
    fig, ax = plt.subplots(figsize=(11.0, 5.6), dpi=300)
    x = np.arange(len(datasets))
    width = 0.24

    for i, tool in enumerate(tools):
        f1_scores = [results[ds][tool]["macro_f1"] for ds in datasets]
        ax.bar(x + i*width, f1_scores, width, label=tool, color=colors[tool],
               edgecolor="#1f2937", linewidth=1.2, alpha=0.9)

    ax.set_ylabel("Macro F1-Score", fontsize=13, fontweight="bold", labelpad=10)
    ax.set_title("Vulnerability Classification Performance Across Tools and Domain Topologies",
                 fontsize=14, fontweight="bold", pad=16)
    ax.set_xticks(x + width)
    ax.set_xticklabels(datasets, fontsize=12.5, fontweight="bold")
    ax.set_ylim(0.48, 1.12)
    ax.tick_params(axis='both', which='major', labelsize=11.5)
    ax.grid(axis="y", linestyle="--", alpha=0.6, color="#e5e7eb")
    ax.set_axisbelow(True)
    ax.legend(loc="lower left", fontsize=11.5, frameon=True, facecolor="#ffffff", edgecolor="#d1d5db")

    # Annotate bars
    for i, tool in enumerate(tools):
        f1_scores = [results[ds][tool]["macro_f1"] for ds in datasets]
        for idx, score in enumerate(f1_scores):
            ax.text(idx + i*width, score + 0.015, f"{score:.3f}",
                    ha="center", va="bottom", fontsize=11.5, fontweight="bold", color="#111827")

    plt.tight_layout()
    chart_paths = [
        os.path.join(results_dir, "tool_comparison_f1.png"),
        os.path.join(paper_fig_dir, "tool_comparison_f1.png")
    ]
    for cp in chart_paths:
        os.makedirs(os.path.dirname(cp), exist_ok=True)
        plt.savefig(cp, dpi=300, bbox_inches='tight')
        print(f"[✓] Saved comparison chart to: {cp}")
    plt.close()

if __name__ == "__main__":
    main()
