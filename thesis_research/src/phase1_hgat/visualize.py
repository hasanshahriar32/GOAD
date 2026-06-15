"""
visualize.py — Thesis Visualization for HGAT AD Attack Path Analysis
=====================================================================
Generates publication-quality figures for the thesis:
  1. t-SNE embedding visualization (colored by node type & privilege)
  2. Training loss & AUC curves
  3. Attack path score ranking

Requires a trained checkpoint from train.py.
"""

import os
import torch
import numpy as np
import matplotlib

matplotlib.use("Agg")  # Non-interactive backend for headless rendering
import matplotlib.pyplot as plt
from matplotlib.lines import Line2D
from sklearn.manifold import TSNE

from dataset import build_ad_graph
from model import HGAT, LinkPredictor

# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------
# Resolve output directories dynamically
RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHECKPOINT_PATH = os.path.join(RESEARCH_ROOT, "results", "phase1", "hgat_esc13.pt")
FIGURE_DIR = os.path.join(RESEARCH_ROOT, "results", "phase1")
DPI = 200


def ensure_dirs():
    os.makedirs(FIGURE_DIR, exist_ok=True)


# ---------------------------------------------------------------------------
# 1. t-SNE Embedding Visualization
# ---------------------------------------------------------------------------
def plot_tsne_embeddings(
    z_dict: dict[str, torch.Tensor],
    data,
    save_path: str,
):
    """
    Project all node embeddings into 2D with t-SNE and color by type +
    privilege level.
    """
    # Concatenate all embeddings
    all_embeddings = []
    all_labels = []     # node type
    all_names = []      # node name
    all_privilege = []   # 0=normal, 1=privileged

    type_order = ["User", "Group", "Computer", "Template"]
    colors = {
        "User": "#4ECDC4",       # teal
        "Group": "#FF6B6B",      # coral
        "Computer": "#45B7D1",   # sky blue
        "Template": "#FFA07A",   # light salmon
    }
    priv_markers = {0: "o", 1: "*"}  # circle vs star

    for ntype in type_order:
        if ntype not in z_dict:
            continue
        emb = z_dict[ntype].detach().cpu().numpy()
        all_embeddings.append(emb)

        names = getattr(data[ntype], "names", [f"{ntype}_{i}" for i in range(emb.shape[0])])

        for i in range(emb.shape[0]):
            all_labels.append(ntype)
            all_names.append(names[i] if i < len(names) else f"{ntype}_{i}")

            # Determine privilege level
            if ntype == "User":
                is_priv = data[ntype].x[i, 5].item() > 0  # admincount
            elif ntype == "Group":
                is_priv = data[ntype].x[i, 0].item() > 0  # highvalue
            elif ntype == "Template":
                is_priv = data[ntype].x[i, 0].item() > 0  # client_auth
            else:
                is_priv = False
            all_privilege.append(1 if is_priv else 0)

    all_embeddings = np.vstack(all_embeddings)

    # t-SNE projection
    perplexity = min(30, max(2, len(all_embeddings) - 1))
    tsne = TSNE(n_components=2, random_state=42, perplexity=perplexity, n_iter=1000)
    coords = tsne.fit_transform(all_embeddings)

    # Plot
    fig, ax = plt.subplots(1, 1, figsize=(12, 9))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    for i, (x, y) in enumerate(coords):
        ntype = all_labels[i]
        priv = all_privilege[i]
        color = colors.get(ntype, "#FFFFFF")
        marker = priv_markers[priv]
        size = 200 if priv else 80
        alpha = 1.0 if priv else 0.7
        edgecolor = "#FFD700" if priv else "none"
        linewidth = 2 if priv else 0

        ax.scatter(
            x, y,
            c=color,
            marker=marker,
            s=size,
            alpha=alpha,
            edgecolors=edgecolor,
            linewidths=linewidth,
            zorder=3 if priv else 2,
        )

        # Label privileged nodes
        if priv:
            name_short = all_names[i].split("@")[0] if "@" in all_names[i] else all_names[i]
            ax.annotate(
                name_short,
                (x, y),
                fontsize=7,
                color="#FFFFFF",
                fontweight="bold",
                ha="left",
                va="bottom",
                xytext=(5, 5),
                textcoords="offset points",
            )

    # Legend
    legend_elements = [
        Line2D([0], [0], marker="o", color="w", markerfacecolor=colors[t],
               markersize=10, label=t, linestyle="None")
        for t in type_order if t in z_dict
    ]
    legend_elements.append(
        Line2D([0], [0], marker="*", color="w", markerfacecolor="#FFD700",
               markersize=14, label="Privileged", linestyle="None")
    )
    ax.legend(
        handles=legend_elements,
        loc="upper right",
        fontsize=10,
        facecolor="#0e1628",
        edgecolor="#333",
        labelcolor="white",
    )

    ax.set_title(
        "HGAT Node Embeddings — Active Directory Attack Surface",
        fontsize=14,
        fontweight="bold",
        color="white",
        pad=15,
    )
    ax.set_xlabel("t-SNE Dimension 1", color="#aaa", fontsize=11)
    ax.set_ylabel("t-SNE Dimension 2", color="#aaa", fontsize=11)
    ax.tick_params(colors="#666")
    for spine in ax.spines.values():
        spine.set_color("#333")

    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  [✓] t-SNE plot saved to {save_path}")


# ---------------------------------------------------------------------------
# 2. Training Curves
# ---------------------------------------------------------------------------
def plot_training_curves(history: dict, save_path: str):
    """Plot loss and AUC over training epochs."""
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    fig.patch.set_facecolor("#1a1a2e")

    for ax in (ax1, ax2):
        ax.set_facecolor("#16213e")
        ax.tick_params(colors="#aaa")
        for spine in ax.spines.values():
            spine.set_color("#333")

    epochs = history["epoch"]

    # Loss curve
    ax1.plot(epochs, history["loss"], color="#FF6B6B", linewidth=2, alpha=0.9)
    ax1.fill_between(epochs, history["loss"], alpha=0.15, color="#FF6B6B")
    ax1.set_title("Training Loss", fontsize=13, fontweight="bold", color="white")
    ax1.set_xlabel("Epoch", color="#aaa", fontsize=11)
    ax1.set_ylabel("BCE Loss", color="#aaa", fontsize=11)
    ax1.grid(True, alpha=0.1, color="#555")

    # AUC curve
    ax2.plot(epochs, history["auc"], color="#4ECDC4", linewidth=2, alpha=0.9)
    ax2.fill_between(epochs, history["auc"], alpha=0.15, color="#4ECDC4")
    ax2.set_title("ROC-AUC Score", fontsize=13, fontweight="bold", color="white")
    ax2.set_xlabel("Epoch", color="#aaa", fontsize=11)
    ax2.set_ylabel("AUC", color="#aaa", fontsize=11)
    ax2.set_ylim(0.0, 1.05)
    ax2.axhline(y=0.5, color="#666", linestyle="--", alpha=0.5, label="Random baseline")
    ax2.legend(facecolor="#0e1628", edgecolor="#333", labelcolor="white")
    ax2.grid(True, alpha=0.1, color="#555")

    fig.suptitle(
        "HGAT Training — ESC13 Attack Path Prediction",
        fontsize=15,
        fontweight="bold",
        color="white",
        y=1.02,
    )
    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, facecolor=fig.get_facecolor(), bbox_inches="tight")
    plt.close()
    print(f"  [✓] Training curves saved to {save_path}")


# ---------------------------------------------------------------------------
# 3. Attack Path Score Ranking
# ---------------------------------------------------------------------------
def plot_attack_scores(
    z_dict: dict[str, torch.Tensor],
    data,
    save_path: str,
):
    """
    Score all possible Template→Group edges and rank by predicted
    attack probability. Highlights the actual ESC13 path.
    """
    predictor = LinkPredictor()
    num_templates = data["Template"].x.shape[0]
    num_groups = data["Group"].x.shape[0]

    # Score all possible template→group edges
    all_src = []
    all_dst = []
    for t in range(num_templates):
        for g in range(num_groups):
            all_src.append(t)
            all_dst.append(g)

    all_edge_index = torch.tensor([all_src, all_dst], dtype=torch.long)
    with torch.no_grad():
        scores = predictor(
            z_dict["Template"], z_dict["Group"], all_edge_index
        ).sigmoid()

    # Build ranking
    ranked = []
    for i in range(len(all_src)):
        t_idx = all_src[i]
        g_idx = all_dst[i]
        t_name = data["Template"].names[t_idx] if hasattr(data["Template"], "names") and t_idx < len(data["Template"].names) else f"T{t_idx}"
        g_name = data["Group"].names[g_idx] if hasattr(data["Group"], "names") and g_idx < len(data["Group"].names) else f"G{g_idx}"
        ranked.append((t_name, g_name, scores[i].item()))

    ranked.sort(key=lambda x: -x[2])

    # Plot top-20 paths
    top_n = min(20, len(ranked))
    top = ranked[:top_n]

    fig, ax = plt.subplots(1, 1, figsize=(12, max(6, top_n * 0.4)))
    fig.patch.set_facecolor("#1a1a2e")
    ax.set_facecolor("#16213e")

    labels = [f"{t} → {g}" for t, g, _ in reversed(top)]
    values = [s for _, _, s in reversed(top)]

    # Color actual ESC13 path differently
    actual_pos = data["Template", "impersonates", "Group"].edge_index
    actual_pairs = set()
    for i in range(actual_pos.shape[1]):
        t_idx = actual_pos[0, i].item()
        g_idx = actual_pos[1, i].item()
        t_name = data["Template"].names[t_idx] if hasattr(data["Template"], "names") and t_idx < len(data["Template"].names) else f"T{t_idx}"
        g_name = data["Group"].names[g_idx] if hasattr(data["Group"], "names") and g_idx < len(data["Group"].names) else f"G{g_idx}"
        actual_pairs.add(f"{t_name} → {g_name}")

    bar_colors = []
    for label in labels:
        if label in actual_pairs:
            bar_colors.append("#FF6B6B")  # red for actual attack path
        else:
            bar_colors.append("#4ECDC4")  # teal for predicted

    bars = ax.barh(range(len(labels)), values, color=bar_colors, alpha=0.85, height=0.6)
    ax.set_yticks(range(len(labels)))
    ax.set_yticklabels(labels, fontsize=8, color="white")
    ax.set_xlabel("Predicted Probability", color="#aaa", fontsize=11)
    ax.set_title(
        "Template → Group Attack Path Ranking",
        fontsize=14,
        fontweight="bold",
        color="white",
        pad=15,
    )
    ax.tick_params(colors="#aaa")
    for spine in ax.spines.values():
        spine.set_color("#333")
    ax.grid(True, axis="x", alpha=0.1, color="#555")

    # Legend
    legend_elements = [
        Line2D([0], [0], color="#FF6B6B", linewidth=8, label="Actual ESC13 path"),
        Line2D([0], [0], color="#4ECDC4", linewidth=8, label="Predicted path"),
    ]
    ax.legend(
        handles=legend_elements,
        loc="lower right",
        facecolor="#0e1628",
        edgecolor="#333",
        labelcolor="white",
    )

    plt.tight_layout()
    plt.savefig(save_path, dpi=DPI, facecolor=fig.get_facecolor())
    plt.close()
    print(f"  [✓] Attack path ranking saved to {save_path}")


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------
def main():
    ensure_dirs()

    print("=" * 60)
    print("HGAT Thesis Visualization")
    print("=" * 60)

    # Load checkpoint
    if not os.path.exists(CHECKPOINT_PATH):
        print(f"[!] No checkpoint found at {CHECKPOINT_PATH}")
        print("[!] Run `python3 train.py` first.")
        return

    checkpoint = torch.load(CHECKPOINT_PATH, map_location="cpu", weights_only=False)
    print(f"[+] Loaded checkpoint from {CHECKPOINT_PATH}")

    # Rebuild data and model
    data = build_ad_graph(verbose=False)
    hyperparams = checkpoint["hyperparams"]
    model = HGAT(
        metadata=data.metadata(),
        hidden_channels=hyperparams["hidden_dim"],
        out_channels=hyperparams["out_dim"],
        num_heads=hyperparams["num_heads"],
        dropout=hyperparams["dropout"],
    )

    # Lazy init then load weights
    with torch.no_grad():
        model.eval()
        _ = model(data.x_dict, data.edge_index_dict)
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()

    # Generate embeddings
    with torch.no_grad():
        z_dict = model(data.x_dict, data.edge_index_dict)

    history = checkpoint["history"]

    # Generate figures
    print("\n[*] Generating thesis figures...\n")

    plot_tsne_embeddings(
        z_dict, data,
        os.path.join(FIGURE_DIR, "tsne_embeddings.png"),
    )

    plot_training_curves(
        history,
        os.path.join(FIGURE_DIR, "training_curves.png"),
    )

    plot_attack_scores(
        z_dict, data,
        os.path.join(FIGURE_DIR, "attack_path_ranking.png"),
    )

    print(f"\n[✓] All figures saved to {FIGURE_DIR}/")
    print(f"    - tsne_embeddings.png")
    print(f"    - training_curves.png")
    print(f"    - attack_path_ranking.png")


if __name__ == "__main__":
    main()
