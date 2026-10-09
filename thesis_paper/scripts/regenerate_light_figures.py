#!/usr/bin/env python3
"""
Regenerate figures with clean publication-quality LIGHT THEME and ENLARGED typography:
1. ablation_comparison.png (Fig 5.2) - wider, 12pt fonts
2. hard_negatives_comparison.png (Fig 5.3) - wider, 11-12pt fonts
3. scalability_metrics.png (Fig 7.3) - 2-row layout (2 top, 1 bottom centered)
4. attention_explainability.png (Fig 5.4) - wider, 11-12pt fonts
"""
import os
import json
import matplotlib.pyplot as plt
import numpy as np
from matplotlib.gridspec import GridSpec

OUTPUT_DIRS = [
    '/home/hs32/Desktop/GOAD/thesis_paper/figures',
    '/home/hs32/Desktop/GOAD/thesis_research/results/phase2'
]

# Set clean publication light-theme style with bold readable fonts
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

def save_fig(fig, filename):
    for d in OUTPUT_DIRS:
        os.makedirs(d, exist_ok=True)
        p = os.path.join(d, filename)
        fig.savefig(p, dpi=300, bbox_inches='tight', facecolor='#ffffff')
        print(f"[✓] Saved light-theme plot: {p}")
    plt.close(fig)

# ─────────────────────────────────────────────────────────────
# ─────────────────────────────────────────────────────────────
# 1. ABLATION STUDY COMPARISON (Figure 5.2) - Extra Large Typography
# ─────────────────────────────────────────────────────────────
with open('/home/hs32/Desktop/GOAD/thesis_research/results/phase2/ablation_results.json', 'r') as f:
    ablation_data = json.load(f)

var_names = list(ablation_data.keys())
means = [ablation_data[v]["f1_mean"] for v in var_names]
stds = [ablation_data[v]["f1_std"] for v in var_names]

fig, ax = plt.subplots(figsize=(9.2, 5.2), dpi=300)
colors = ['#1d4ed8', '#dc2626', '#0d9488', '#d97706']  # Blue, Red, Teal, Amber

bars = ax.bar(var_names, means, yerr=stds, color=colors, alpha=0.92,
              edgecolor='#1f2937', linewidth=1.3, capsize=7, width=0.50,
              error_kw=dict(lw=2.0, capthick=2.0, ecolor='#1f2937'))

for bar, val in zip(bars, means):
    ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.04,
            f"{val:.3f}", ha='center', va='bottom', fontsize=13.5, fontweight='bold', color='#0f172a')

ax.set_ylabel("Macro-F1 Score", fontsize=15.0, fontweight='bold', labelpad=12)
ax.set_title("CertGraph Architectural Ablation Study (5-Fold Cross-Validation)", fontsize=16.0, fontweight='bold', pad=16)
ax.set_ylim(0, 1.22)
ax.set_yticks(np.arange(0, 1.25, 0.2))
ax.tick_params(axis='both', which='major', labelsize=13.0)
ax.grid(True, axis='y', linestyle='--', alpha=0.6, color='#e5e7eb')
ax.set_axisbelow(True)

# Add p-value / impact annotations with prominent box
ax.text(1, 0.24, "Catastrophic collapse:\nNo Skip Connections\n(p = 1.3e-6)",
        ha='center', va='center', fontsize=12.5, fontweight='bold', color='#dc2626',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#fee2e2', edgecolor='#dc2626', lw=1.3))

fig.tight_layout()
save_fig(fig, 'ablation_comparison.png')

# ─────────────────────────────────────────────────────────────
# 2. ZERO-SHOT HARD NEGATIVES COMPARISON (Figure 5.3) - Extra Large Typography
# ─────────────────────────────────────────────────────────────
with open('/home/hs32/Desktop/GOAD/thesis_research/results/phase2/hard_negatives_results.json', 'r') as f:
    hn_data = json.load(f)

models = list(hn_data.keys())
accuracies = [hn_data[m]["accuracy"] * 100 for m in models]
hn_colors = [
    '#ef4444',  # CertGraph (collapsed) - Red
    '#9ca3af',  # MLP - Gray
    '#9ca3af',  # RF - Gray
    '#f97316',  # Rule-based - Orange
    '#3b82f6',  # Graph-Augmented MLP - Blue
    '#9ca3af',  # Graph-Augmented RF - Gray
    '#059669',  # BloodHound BFS (Symbolic Oracle) - Green
]

fig, ax = plt.subplots(figsize=(9.8, 5.4), dpi=300)
bars = ax.bar(models, accuracies, color=hn_colors, alpha=0.92, width=0.55, edgecolor='#1f2937', linewidth=1.3)

for bar in bars:
    height = bar.get_height()
    ax.text(
        bar.get_x() + bar.get_width() / 2, height + 3.0,
        f"{height:.1f}%", ha='center', va='bottom', fontsize=12.5, fontweight='bold', color='#0f172a'
    )

ax.set_ylabel("Zero-Shot Accuracy (%)", fontsize=14.5, fontweight='bold', labelpad=12)
ax.set_ylim(0, 130)
ax.set_title("Zero-Shot Generalization on Adversarial Hard Negatives (Safe Samples)", fontsize=15.5, fontweight='bold', pad=16)
ax.grid(True, axis='y', linestyle='--', alpha=0.6, color='#e5e7eb')
ax.set_axisbelow(True)
ax.tick_params(axis='y', which='major', labelsize=13.0)
plt.xticks(rotation=22, ha='right', fontsize=12.5, fontweight='bold')

# Annotation explaining shortcut learning vs symbolic verification
ax.text(0.1, 88, "Neural Shortcut Collapse:\nGNN learns spurious flag shortcuts",
        ha='left', va='center', fontsize=12.0, fontweight='bold', color='#b91c1c',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#fef2f2', edgecolor='#ef4444', lw=1.3))

ax.text(4.8, 110, "Symbolic Path Verification:\nExact graph reachability holds",
        ha='center', va='center', fontsize=12.0, fontweight='bold', color='#047857',
        bbox=dict(boxstyle='round,pad=0.4', facecolor='#ecfdf5', edgecolor='#059669', lw=1.3))

fig.tight_layout()
save_fig(fig, 'hard_negatives_comparison.png')

# ─────────────────────────────────────────────────────────────
# 3. SCALABILITY BENCHMARKS (Figure 7.3) - 2-ROW HIGH-LEGIBILITY LAYOUT
# ─────────────────────────────────────────────────────────────
with open('/home/hs32/Desktop/GOAD/thesis_research/results/phase2/scalability_results.json', 'r') as f:
    scale_data = json.load(f)

node_labels = [r["actual_nodes"] for r in scale_data]
latencies_mean = [r["inference_latency_ms_mean"] for r in scale_data]
latencies_std = [r["inference_latency_ms_std"] for r in scale_data]
memory_usage = [r["memory_usage_mb"] for r in scale_data]
gen_time = [r["generation_time_ms"] for r in scale_data]

fig = plt.figure(figsize=(10.2, 7.8), dpi=300)
gs = GridSpec(2, 4, figure=fig, hspace=0.36, wspace=0.48)

# Subplot 1 (Top Left): Inference Latency
ax1 = fig.add_subplot(gs[0, 0:2])
ax1.plot(node_labels, latencies_mean, marker='o', markersize=8.5, color='#1d4ed8', linewidth=3.2, label="Mean Latency")
ax1.fill_between(node_labels,
                 np.array(latencies_mean) - np.array(latencies_std),
                 np.array(latencies_mean) + np.array(latencies_std),
                 color='#3b82f6', alpha=0.22, label="±1 Std Dev")
ax1.set_title("Model Inference Latency", fontsize=14.5, fontweight='bold', pad=12)
ax1.set_xlabel("Graph Size (Number of Nodes)", fontsize=13.0, fontweight='bold')
ax1.set_ylabel("Latency (ms)", fontsize=13.0, fontweight='bold')
ax1.tick_params(axis='both', which='major', labelsize=12.0)
ax1.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
ax1.set_axisbelow(True)
ax1.legend(loc='upper left', frameon=True, facecolor='#ffffff', edgecolor='#d1d5db', fontsize=12.0)

# Subplot 2 (Top Right): Memory Footprint
ax2 = fig.add_subplot(gs[0, 2:4])
ax2.plot(node_labels, memory_usage, marker='s', markersize=8.5, color='#059669', linewidth=3.2)
ax2.set_title("Peak Resident Memory (RSS)", fontsize=14.5, fontweight='bold', pad=12)
ax2.set_xlabel("Graph Size (Number of Nodes)", fontsize=13.0, fontweight='bold')
ax2.set_ylabel("Memory (MB)", fontsize=13.0, fontweight='bold')
ax2.set_ylim(1000, 1550)
ax2.tick_params(axis='both', which='major', labelsize=12.0)
ax2.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
ax2.set_axisbelow(True)
ax2.text(5000, 1340, "Flat memory footprint:\nNo GPU memory leaks",
         ha='center', va='center', fontsize=12.0, fontweight='bold', color='#047857',
         bbox=dict(boxstyle='round,pad=0.35', facecolor='#ecfdf5', edgecolor='#059669', lw=1.2))

# Subplot 3 (Bottom Center): Generation Time
ax3 = fig.add_subplot(gs[1, 1:3])
ax3.plot(node_labels, gen_time, marker='^', markersize=9.0, color='#d97706', linewidth=3.2)
ax3.set_title("Environment Graph Synthesis Time", fontsize=14.5, fontweight='bold', pad=12)
ax3.set_xlabel("Graph Size (Number of Nodes)", fontsize=13.0, fontweight='bold')
ax3.set_ylabel("Generation Time (ms)", fontsize=13.0, fontweight='bold')
ax3.tick_params(axis='both', which='major', labelsize=12.0)
ax3.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
ax3.set_axisbelow(True)

fig.suptitle("CertGraph Empirical Computational Scalability Benchmarks (100 to 10,000 Nodes)",
             fontsize=16.0, fontweight='bold', y=0.98)
save_fig(fig, 'scalability_metrics.png')

# ─────────────────────────────────────────────────────────────
# 4. ATTENTION WEIGHT EXPLAINABILITY (Figure 5.4) - Extra Large Typography
# ─────────────────────────────────────────────────────────────
labels = [
    "(Group) Group_0 ──[generic_all]──> (Group) Group_14",
    "(Group) Group_0 ──[generic_all]──> (Group) Group_6",
    "(Group) Group_1 ──[member_of]──> (Group) Group_0",
    "(Group) Group_3 ──[generic_all]──> (Group) Group_12",
    "(Group) Group_3 ──[generic_all]──> (Group) Group_7",
    "(Group) Group_2 ──[generic_all]──> (Group) Group_10",
    "(Group) Group_2 ──[generic_all]──> (Group) Group_2",
    "(Group) Group_0 ──[generic_all]──> (Group) Group_5",
    "(Group) Group_11 ──[member_of]──> (Group) Group_2",
    "(Group) Group_4 ──[member_of]──> (Group) Group_3",
]
weights = [0.500, 0.500, 0.505, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000, 1.000]

fig, ax = plt.subplots(figsize=(10.5, 5.6), dpi=300)
bar_colors = ['#dc2626' if w >= 0.99 else '#f97316' for w in weights]

bars = ax.barh(range(len(labels)), weights, color=bar_colors, alpha=0.92, height=0.64,
               edgecolor='#1f2937', linewidth=1.2)
ax.set_yticks(range(len(labels)))
ax.set_yticklabels(labels, fontsize=12.0, fontweight='bold', family='monospace', color='#0f172a')
ax.set_xlabel("Average Relational Attention Coefficient (α)", fontsize=14.5, fontweight='bold', labelpad=12)
ax.set_title("CertGraph Relational Attention Weights — Top Edges in ESC13 Environment", fontsize=15.5, fontweight='bold', pad=14)
ax.set_xlim(0, 1.20)
ax.tick_params(axis='x', which='major', labelsize=12.5)
ax.grid(True, axis='x', linestyle='--', alpha=0.6, color='#e5e7eb')
ax.set_axisbelow(True)

for bar, w in zip(bars, weights):
    ax.text(bar.get_width() + 0.02, bar.get_y() + bar.get_height() / 2,
            f"α = {w:.3f}", va='center', ha='left', fontsize=12.5, fontweight='bold', color='#0f172a')

fig.tight_layout()
save_fig(fig, 'attention_explainability.png')

print("\n[✓] All figures successfully updated and generated!")
