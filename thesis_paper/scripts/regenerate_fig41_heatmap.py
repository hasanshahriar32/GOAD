#!/usr/bin/env python3
"""
Regenerate Figure 4.1: Feature Correlation & Separability Heatmap
with optimized canvas proportions and large, high-visibility typography.
"""
import os
import numpy as np
import matplotlib.pyplot as plt

OUTPUT_PATHS = [
    "/home/hs32/Desktop/GOAD/thesis_paper/figures/feature_heatmap.png",
    "/home/hs32/Desktop/GOAD/thesis_research/results/phase2/feature_heatmap.png"
]

ESC_CLASSES = ["ESC1", "ESC2", "ESC3", "ESC4", "ESC9", "ESC13", "Safe"]

TEMPLATE_FEATURE_NAMES = [
    "enrollee_supplies_subject",
    "no_manager_approval",
    "no_security_extension",
    "has_client_auth",
    "has_any_purpose",
    "has_cert_req_agent",
    "ra_signature_required",
    "has_issuance_policy_oid",
    "has_vulnerable_acl",
    "schema_version_norm"
]

mean_feats = np.array([
    [1.00, 1.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50],
    [0.00, 1.00, 0.00, 0.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.50],
    [0.00, 1.00, 0.00, 0.43, 0.00, 0.57, 1.00, 0.00, 0.00, 0.50],
    [0.00, 0.67, 0.00, 0.34, 0.00, 0.00, 0.56, 0.00, 1.00, 0.50],
    [0.00, 1.00, 1.00, 1.00, 0.00, 0.00, 0.00, 0.00, 0.00, 0.50],
    [0.00, 1.00, 0.00, 1.00, 0.00, 0.00, 0.00, 1.00, 0.00, 0.50],
    [0.22, 0.88, 0.00, 0.58, 0.00, 0.00, 0.25, 0.28, 0.26, 0.51]
])

def main():
    plt.style.use('default')
    fig, ax = plt.subplots(figsize=(10.5, 5.8), dpi=300)

    im = ax.imshow(mean_feats, cmap="YlOrRd", aspect="auto", vmin=0, vmax=1)
    ax.set_xticks(range(len(TEMPLATE_FEATURE_NAMES)))
    ax.set_xticklabels(TEMPLATE_FEATURE_NAMES, rotation=35, ha="right", fontsize=12.5, fontweight="bold", rotation_mode="anchor")
    ax.set_yticks(range(len(ESC_CLASSES)))
    ax.set_yticklabels(ESC_CLASSES, fontsize=13.5, fontweight="bold")

    # Annotate cells with bold, large text
    for i in range(len(ESC_CLASSES)):
        for j in range(len(TEMPLATE_FEATURE_NAMES)):
            val = mean_feats[i, j]
            color = "white" if val > 0.55 else "#0f172a"
            ax.text(j, i, f"{val:.2f}", ha="center", va="center", color=color, fontsize=13.0, fontweight="bold")

    cbar = plt.colorbar(im, ax=ax, fraction=0.035, pad=0.03)
    cbar.set_label("Mean Feature Value", fontsize=13.5, fontweight="bold", labelpad=12)
    cbar.ax.tick_params(labelsize=12.0)
    
    ax.set_title("Template Feature Distribution by ESC Vulnerability Class", fontsize=15.5, fontweight="bold", pad=16)
    plt.tight_layout()

    for p in OUTPUT_PATHS:
        os.makedirs(os.path.dirname(p), exist_ok=True)
        plt.savefig(p, dpi=300, bbox_inches="tight")
        print(f"[✓] Saved high-contrast heatmap: {p}")
    plt.close()

if __name__ == "__main__":
    main()
