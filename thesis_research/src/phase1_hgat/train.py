"""
train.py — Training Loop for HGAT Link Prediction on AD Attack Paths
=====================================================================
Trains the HGAT model to predict the ESC13 escalation path:
    Template --impersonates--> Group (Domain Admins)

Uses binary cross-entropy with negative sampling for contrastive learning.
Saves the trained model checkpoint and prints loss/AUC metrics.
"""

import os
import torch
import torch.nn.functional as F
from sklearn.metrics import roc_auc_score

from dataset import build_ad_graph
from model import HGAT, LinkPredictor


# ---------------------------------------------------------------------------
# Hyperparameters
# ---------------------------------------------------------------------------
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.01
EPOCHS = 200
NEG_RATIO = 3          # negative samples per positive edge
# Resolve output directory dynamically
RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
CHECKPOINT_DIR = os.path.join(RESEARCH_ROOT, "results", "phase1")
TARGET_RELATION = ("Template", "impersonates", "Group")


def generate_negative_edges(
    pos_edge_index: torch.Tensor,
    num_src: int,
    num_dst: int,
    neg_ratio: int = 3,
) -> torch.Tensor:
    """
    Generate random negative edges that do not overlap with positive edges.
    """
    num_pos = pos_edge_index.shape[1]
    num_neg = num_pos * neg_ratio

    # Build set of positive edges for exclusion
    pos_set = set()
    for i in range(num_pos):
        pos_set.add((pos_edge_index[0, i].item(), pos_edge_index[1, i].item()))

    neg_src, neg_dst = [], []
    attempts = 0
    while len(neg_src) < num_neg and attempts < num_neg * 10:
        s = torch.randint(0, num_src, (1,)).item()
        d = torch.randint(0, num_dst, (1,)).item()
        if (s, d) not in pos_set:
            neg_src.append(s)
            neg_dst.append(d)
        attempts += 1

    return torch.tensor([neg_src, neg_dst], dtype=torch.long)


def train():
    """Main training loop."""
    # ------------------------------------------------------------------
    # 1. Load data
    # ------------------------------------------------------------------
    print("=" * 60)
    print("HGAT Training — AD Attack Path Detection (ESC13)")
    print("=" * 60)

    data = build_ad_graph(verbose=True)

    # Verify target relation exists
    if TARGET_RELATION not in data.edge_types:
        raise ValueError(
            f"Target relation {TARGET_RELATION} not found in graph. "
            f"Available: {data.edge_types}"
        )

    pos_edge_index = data[TARGET_RELATION].edge_index
    num_pos = pos_edge_index.shape[1]
    print(f"\n[*] Target relation: {TARGET_RELATION}")
    print(f"[*] Positive edges: {num_pos}")

    if num_pos == 0:
        raise ValueError("No positive edges for target relation!")

    # ------------------------------------------------------------------
    # 2. Initialize model
    # ------------------------------------------------------------------
    model = HGAT(
        metadata=data.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_heads=NUM_HEADS,
        dropout=DROPOUT,
    )
    predictor = LinkPredictor()
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)

    # Lazy init: run one forward pass to initialize weights
    with torch.no_grad():
        model.eval()
        _ = model(data.x_dict, data.edge_index_dict)
    model.train()

    total_params = sum(p.numel() for p in model.parameters())
    print(f"[*] Model parameters: {total_params:,}")
    print(f"[*] Training for {EPOCHS} epochs with lr={LR}\n")

    # ------------------------------------------------------------------
    # 3. Training loop
    # ------------------------------------------------------------------
    src_type, _, dst_type = TARGET_RELATION
    num_src = data[src_type].x.shape[0]
    num_dst = data[dst_type].x.shape[0]

    best_loss = float("inf")
    history = {"epoch": [], "loss": [], "auc": []}

    for epoch in range(1, EPOCHS + 1):
        model.train()
        optimizer.zero_grad()

        # Forward pass: generate node embeddings
        z_dict = model(data.x_dict, data.edge_index_dict)

        # Generate negative edges
        neg_edge_index = generate_negative_edges(
            pos_edge_index, num_src, num_dst, NEG_RATIO
        )

        # Score positive and negative edges
        pos_logits = predictor(z_dict[src_type], z_dict[dst_type], pos_edge_index)
        neg_logits = predictor(z_dict[src_type], z_dict[dst_type], neg_edge_index)

        # Binary cross-entropy loss
        pos_loss = F.binary_cross_entropy_with_logits(
            pos_logits, torch.ones_like(pos_logits)
        )
        neg_loss = F.binary_cross_entropy_with_logits(
            neg_logits, torch.zeros_like(neg_logits)
        )
        loss = pos_loss + neg_loss

        loss.backward()
        optimizer.step()

        # Compute AUC
        with torch.no_grad():
            all_logits = torch.cat([pos_logits, neg_logits]).sigmoid().cpu().numpy()
            all_labels = (
                torch.cat([
                    torch.ones(pos_logits.shape[0]),
                    torch.zeros(neg_logits.shape[0]),
                ])
                .cpu()
                .numpy()
            )
            try:
                auc = roc_auc_score(all_labels, all_logits)
            except ValueError:
                auc = 0.5  # edge case with single class

        history["epoch"].append(epoch)
        history["loss"].append(loss.item())
        history["auc"].append(auc)

        if loss.item() < best_loss:
            best_loss = loss.item()

        if epoch % 10 == 0 or epoch == 1:
            print(
                f"  Epoch {epoch:03d}/{EPOCHS} | "
                f"Loss: {loss.item():.4f} | "
                f"AUC: {auc:.4f} | "
                f"Best: {best_loss:.4f}"
            )

    # ------------------------------------------------------------------
    # 4. Save checkpoint
    # ------------------------------------------------------------------
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)
    ckpt_path = os.path.join(CHECKPOINT_DIR, "hgat_esc13.pt")
    torch.save(
        {
            "model_state_dict": model.state_dict(),
            "optimizer_state_dict": optimizer.state_dict(),
            "metadata": data.metadata(),
            "history": history,
            "hyperparams": {
                "hidden_dim": HIDDEN_DIM,
                "out_dim": OUT_DIM,
                "num_heads": NUM_HEADS,
                "dropout": DROPOUT,
                "lr": LR,
                "epochs": EPOCHS,
            },
        },
        ckpt_path,
    )
    print(f"\n[✓] Model saved to {ckpt_path}")

    # ------------------------------------------------------------------
    # 5. Final evaluation
    # ------------------------------------------------------------------
    model.eval()
    with torch.no_grad():
        z_dict = model(data.x_dict, data.edge_index_dict)

        # Score the actual ESC13 attack path
        pos_scores = predictor(
            z_dict[src_type], z_dict[dst_type], pos_edge_index
        ).sigmoid()

        print(f"\n{'='*60}")
        print(f"Final ESC13 Attack Path Scores:")
        print(f"{'='*60}")
        for i in range(pos_edge_index.shape[1]):
            src_idx = pos_edge_index[0, i].item()
            dst_idx = pos_edge_index[1, i].item()
            score = pos_scores[i].item()
            src_name = data[src_type].names[src_idx] if hasattr(data[src_type], "names") else f"{src_type}[{src_idx}]"
            dst_name = data[dst_type].names[dst_idx] if hasattr(data[dst_type], "names") else f"{dst_type}[{dst_idx}]"
            print(f"  {src_name} --impersonates--> {dst_name}: {score:.4f}")

    # Save training curves and metrics JSON
    import json
    import matplotlib.pyplot as plt

    metrics_path = os.path.join(CHECKPOINT_DIR, "metrics.json")
    with open(metrics_path, "w") as f:
        json.dump({
            "final_loss": history["loss"][-1],
            "final_auc": history["auc"][-1],
            "epochs": EPOCHS,
            "hidden_dim": HIDDEN_DIM,
            "out_dim": OUT_DIM,
            "num_heads": NUM_HEADS,
            "dropout": DROPOUT,
            "lr": LR,
            "loss_history": history["loss"],
            "auc_history": history["auc"]
        }, f, indent=2)
    print(f"[✓] Metrics JSON saved to {metrics_path}")

    # Generate and save the loss and AUC curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(14, 5))
    
    # Loss plot
    ax1.plot(history["epoch"], history["loss"], color="#FF6B6B", lw=2, alpha=0.9)
    ax1.fill_between(history["epoch"], history["loss"], alpha=0.15, color="#FF6B6B")
    ax1.set_title("Training Loss", fontsize=13, fontweight="bold")
    ax1.set_xlabel("Epoch")
    ax1.set_ylabel("BCE Loss")
    ax1.grid(True, alpha=0.1, color="#555")
    
    # AUC plot
    ax2.plot(history["epoch"], history["auc"], color="#4ECDC4", lw=2, alpha=0.9)
    ax2.fill_between(history["epoch"], history["auc"], alpha=0.15, color="#4ECDC4")
    ax2.set_title("ROC-AUC Score", fontsize=13, fontweight="bold")
    ax2.set_xlabel("Epoch")
    ax2.set_ylabel("AUC")
    ax2.set_ylim(0, 1.05)
    ax2.axhline(0.5, color="#666", ls="--", alpha=0.5, label="Random")
    ax2.legend(facecolor="#0e1628", edgecolor="#333", labelcolor="white")
    ax2.grid(True, alpha=0.1, color="#555")
    
    fig.suptitle("HGAT Training — ESC13 Attack Path Prediction", fontsize=15, fontweight="bold", y=1.02)
    plt.tight_layout()
    
    plot_path = os.path.join(CHECKPOINT_DIR, "training_curves.png")
    plt.savefig(plot_path, dpi=300, bbox_inches="tight")
    plt.close()
    print(f"[✓] Training curves saved to {plot_path}")

    print(f"\n[✓] Training complete. Final Loss: {history['loss'][-1]:.4f}, AUC: {history['auc'][-1]:.4f}")

    return model, data, history


if __name__ == "__main__":
    train()
