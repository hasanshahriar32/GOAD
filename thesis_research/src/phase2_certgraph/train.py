"""
certgraph_train.py — Training & Evaluation Pipeline for CertGraph
===================================================================
5-fold cross-validation with multi-class ESC vulnerability classification.
Compares CertGraph against:
  - Feature-only baselines: Rule-based, MLP, Random Forest
  - Graph-Augmented baselines: Graph-Augmented MLP, Graph-Augmented RF
  - Graph Traversal baseline: BloodHound BFS path checker

Outputs:
    - Per-fold and averaged metrics (Macro-F1, Accuracy, per-class P/R/F1)
    - Statistical significance tests (paired t-test vs CertGraph)
    - Confusion matrix
    - Training history
    - Saved model checkpoint & results JSON
"""

import os
import json
import time
import warnings
import numpy as np
import torch
import torch.nn.functional as F
from collections import defaultdict
from sklearn.metrics import (
    f1_score, accuracy_score, classification_report,
    confusion_matrix as sk_confusion_matrix,
)
from sklearn.model_selection import StratifiedKFold
from sklearn.ensemble import RandomForestClassifier
from torch_geometric.loader import DataLoader
from torch_geometric.data import HeteroData

from generator import (
    generate_dataset, ESC_CLASSES, CLASS_TO_IDX, NUM_CLASSES,
    TEMPLATE_FEATURE_DIM,
)
from model import CertGraph, MLPBaseline, RuleBaseline
from bfs_baseline import BloodHoundBFSBaseline

warnings.filterwarnings("ignore", category=UserWarning)

# ─────────────────────────────────────────────────────────────────────
# Configuration
# ─────────────────────────────────────────────────────────────────────
NUM_ENVS = 700            # total synthetic environments (100 per class)
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 100
N_FOLDS = 5
BATCH_SIZE = 64
RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
CHECKPOINT_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")


def extract_graph_counts(data: HeteroData, target_idx: int) -> list[float]:
    """
    Extract 4 key structural graph indicators for a certificate template:
    1. n_lowpriv_enroll: count of low-privileged users who can enroll in this template
    2. n_lowpriv_dacl: count of low-privileged users with write_dacl on this template
    3. links_to_highvalue_group: 1.0 if template links to a high-value group via issuance policy
    4. has_issuance_policy_link: 1.0 if template links to any group via issuance policy
    """
    user_x = data["User"].x
    is_admin = (user_x[:, 5] > 0.5)

    # 1. Enrolls
    n_lp_enroll = 0
    if ("User", "enrolls", "Template") in data.edge_types:
        ei = data["User", "enrolls", "Template"].edge_index
        target_mask = (ei[1] == target_idx)
        enrollers = ei[0][target_mask]
        n_lp_enroll = (~is_admin[enrollers]).sum().item()

    # 2. Write DACL
    n_lp_dacl = 0
    if ("User", "write_dacl", "Template") in data.edge_types:
        ei = data["User", "write_dacl", "Template"].edge_index
        target_mask = (ei[1] == target_idx)
        writers = ei[0][target_mask]
        n_lp_dacl = (~is_admin[writers]).sum().item()

    # 3 & 4. Issuance Policy links
    links_hv = 0.0
    has_policy = 0.0
    if ("Template", "linked_to", "Group") in data.edge_types:
        ei = data["Template", "linked_to", "Group"].edge_index
        target_mask = (ei[0] == target_idx)
        linked_groups = ei[1][target_mask]
        if len(linked_groups) > 0:
            has_policy = 1.0
            group_x = data["Group"].x
            is_hv = (group_x[linked_groups, 0] > 0.5)
            if is_hv.any().item():
                links_hv = 1.0

    return [float(n_lp_enroll), float(n_lp_dacl), links_hv, has_policy]


def train_certgraph_fold(
    train_data: list[tuple],
    test_data: list[tuple],
    fold: int,
    verbose: bool = True,
) -> dict:
    """Train CertGraph for one CV fold using batched DataLoader."""
    train_list = [d for d, _, _ in train_data]
    test_list = [d for d, _, _ in test_data]

    train_loader = DataLoader(train_list, batch_size=BATCH_SIZE, shuffle=True)
    test_loader = DataLoader(test_list, batch_size=BATCH_SIZE, shuffle=False)

    sample = train_list[0]
    model = CertGraph(
        metadata=sample.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT,
    )

    # Lazy init
    with torch.no_grad():
        model.eval()
        _ = model(sample.x_dict, sample.edge_index_dict)
    model.train()

    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)
    history = {"loss": [], "train_f1": []}

    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        all_preds = []
        all_labels = []

        for batch in train_loader:
            optimizer.zero_grad()
            logits = model(batch.x_dict, batch.edge_index_dict)

            # Extract target logits using offset indices
            ptr = batch["Template"].ptr
            target_indices = ptr[:-1] + batch.target_idx
            target_logits = logits[target_indices]

            loss = F.cross_entropy(target_logits, batch.y_class)
            loss.backward()
            optimizer.step()

            total_loss += loss.item() * batch.num_graphs
            all_preds.extend(target_logits.argmax(dim=1).cpu().tolist())
            all_labels.extend(batch.y_class.cpu().tolist())

        avg_loss = total_loss / len(train_list)
        train_f1 = f1_score(all_labels, all_preds, average="macro", zero_division=0)
        history["loss"].append(avg_loss)
        history["train_f1"].append(train_f1)

        if verbose and (epoch % 25 == 0 or epoch == 1):
            print(f"    Epoch {epoch:03d}/{EPOCHS} | Loss: {avg_loss:.4f} | Train F1: {train_f1:.4f}")

    # Evaluation on test set
    model.eval()
    test_preds = []
    test_labels = []

    with torch.no_grad():
        for batch in test_loader:
            logits = model(batch.x_dict, batch.edge_index_dict)
            ptr = batch["Template"].ptr
            target_indices = ptr[:-1] + batch.target_idx
            target_logits = logits[target_indices]

            test_preds.extend(target_logits.argmax(dim=1).cpu().tolist())
            test_labels.extend(batch.y_class.cpu().tolist())

    test_f1 = f1_score(test_labels, test_preds, average="macro", zero_division=0)
    test_acc = accuracy_score(test_labels, test_preds)
    cm = sk_confusion_matrix(test_labels, test_preds, labels=list(range(NUM_CLASSES)))
    report = classification_report(
        test_labels, test_preds,
        target_names=ESC_CLASSES, output_dict=True, zero_division=0,
    )

    return {
        "model": model,
        "test_f1": test_f1,
        "test_acc": test_acc,
        "confusion_matrix": cm,
        "report": report,
        "history": history,
        "test_preds": test_preds,
        "test_labels": test_labels,
    }


def train_mlp_fold(train_data, test_data) -> dict:
    """Train standard MLP baseline (features only, 10-dim)."""
    model = MLPBaseline(input_dim=TEMPLATE_FEATURE_DIM, hidden_dim=32, num_classes=NUM_CLASSES)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)

    X_train = torch.stack([d["Template"].x[ti] for d, _, ti in train_data])
    y_train = torch.tensor([CLASS_TO_IDX[ec] for _, ec, _ in train_data], dtype=torch.long)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        optimizer.zero_grad()
        logits = model(X_train)
        loss = F.cross_entropy(logits, y_train)
        loss.backward()
        optimizer.step()

    model.eval()
    X_test = torch.stack([d["Template"].x[ti] for d, _, ti in test_data])
    y_test = [CLASS_TO_IDX[ec] for _, ec, _ in test_data]

    with torch.no_grad():
        preds = model(X_test).argmax(dim=1).cpu().tolist()

    return {
        "test_f1": f1_score(y_test, preds, average="macro", zero_division=0),
        "test_acc": accuracy_score(y_test, preds),
        "test_preds": preds,
        "test_labels": y_test,
    }


def train_augmented_mlp_fold(train_data, test_data) -> dict:
    """Train Graph-Augmented MLP baseline (14-dim: 10 flags + 4 graph counts)."""
    model = MLPBaseline(input_dim=14, hidden_dim=32, num_classes=NUM_CLASSES)
    optimizer = torch.optim.Adam(model.parameters(), lr=0.01, weight_decay=1e-4)

    X_train_list, y_train_list = [], []
    for d, esc_class, ti in train_data:
        feat10 = d["Template"].x[ti].tolist()
        cnt4 = extract_graph_counts(d, ti)
        X_train_list.append(feat10 + cnt4)
        y_train_list.append(CLASS_TO_IDX[esc_class])

    X_train = torch.tensor(X_train_list, dtype=torch.float)
    y_train = torch.tensor(y_train_list, dtype=torch.long)

    for epoch in range(1, EPOCHS + 1):
        model.train()
        optimizer.zero_grad()
        logits = model(X_train)
        loss = F.cross_entropy(logits, y_train)
        loss.backward()
        optimizer.step()

    model.eval()
    X_test_list, y_test = [], []
    for d, esc_class, ti in test_data:
        feat10 = d["Template"].x[ti].tolist()
        cnt4 = extract_graph_counts(d, ti)
        X_test_list.append(feat10 + cnt4)
        y_test.append(CLASS_TO_IDX[esc_class])

    X_test = torch.tensor(X_test_list, dtype=torch.float)
    with torch.no_grad():
        preds = model(X_test).argmax(dim=1).cpu().tolist()

    return {
        "test_f1": f1_score(y_test, preds, average="macro", zero_division=0),
        "test_acc": accuracy_score(y_test, preds),
        "test_preds": preds,
        "test_labels": y_test,
    }


def eval_rule_baseline(test_data) -> dict:
    """Evaluate rule-based baseline."""
    rule = RuleBaseline()
    preds, labels = [], []

    for data, esc_class, target_idx in test_data:
        feat = data["Template"].x[target_idx].unsqueeze(0)
        pred = rule.predict(feat)[0].item()
        preds.append(pred)
        labels.append(CLASS_TO_IDX[esc_class])

    return {
        "test_f1": f1_score(labels, preds, average="macro", zero_division=0),
        "test_acc": accuracy_score(labels, preds),
        "test_preds": preds,
        "test_labels": labels,
    }


def train_rf_fold(train_data, test_data) -> dict:
    """Train Random Forest baseline (features only, 10-dim)."""
    X_train, y_train = [], []
    for data, esc_class, target_idx in train_data:
        X_train.append(data["Template"].x[target_idx].numpy())
        y_train.append(CLASS_TO_IDX[esc_class])
    X_test, y_test = [], []
    for data, esc_class, target_idx in test_data:
        X_test.append(data["Template"].x[target_idx].numpy())
        y_test.append(CLASS_TO_IDX[esc_class])

    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    rf.fit(np.array(X_train), np.array(y_train))
    preds = rf.predict(np.array(X_test)).tolist()

    return {
        "test_f1": f1_score(y_test, preds, average="macro", zero_division=0),
        "test_acc": accuracy_score(y_test, preds),
        "test_preds": preds,
        "test_labels": y_test,
    }


def train_augmented_rf_fold(train_data, test_data) -> dict:
    """Train Graph-Augmented Random Forest baseline (14-dim)."""
    X_train, y_train = [], []
    for d, esc_class, ti in train_data:
        feat10 = d["Template"].x[ti].tolist()
        cnt4 = extract_graph_counts(d, ti)
        X_train.append(feat10 + cnt4)
        y_train.append(CLASS_TO_IDX[esc_class])

    X_test, y_test = [], []
    for d, esc_class, ti in test_data:
        feat10 = d["Template"].x[ti].tolist()
        cnt4 = extract_graph_counts(d, ti)
        X_test.append(feat10 + cnt4)
        y_test.append(CLASS_TO_IDX[esc_class])

    rf = RandomForestClassifier(n_estimators=100, random_state=42, max_depth=5)
    rf.fit(np.array(X_train), np.array(y_train))
    preds = rf.predict(np.array(X_test)).tolist()

    return {
        "test_f1": f1_score(y_test, preds, average="macro", zero_division=0),
        "test_acc": accuracy_score(y_test, preds),
        "test_preds": preds,
        "test_labels": y_test,
    }


def eval_bfs_baseline(test_data) -> dict:
    """Evaluate BloodHound-style BFS path verification baseline."""
    bfs = BloodHoundBFSBaseline()
    preds = bfs.predict(test_data)
    y_test = [CLASS_TO_IDX[ec] for _, ec, _ in test_data]

    return {
        "test_f1": f1_score(y_test, preds, average="macro", zero_division=0),
        "test_acc": accuracy_score(y_test, preds),
        "test_preds": preds,
        "test_labels": y_test,
    }


# ─────────────────────────────────────────────────────────────────────
# Main
# ─────────────────────────────────────────────────────────────────────

def main():
    os.makedirs(RESULTS_DIR, exist_ok=True)
    os.makedirs(CHECKPOINT_DIR, exist_ok=True)

    print("=" * 70)
    print("CertGraph — Multi-ESC Vulnerability Classification (Fair Benchmarks)")
    print("=" * 70)

    # 1. Dataset Generation
    t0 = time.time()
    print(f"\n[1/4] Generating {NUM_ENVS} synthetic AD environments...")
    dataset = generate_dataset(num_envs=NUM_ENVS, balanced=True, seed=42)
    print(f"      Generated in {time.time() - t0:.1f}s")

    # Add custom attributes for PyG DataLoader batching
    for data, esc_class, target_idx in dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)

    # Extract labels for stratification
    labels = [CLASS_TO_IDX[esc_class] for _, esc_class, _ in dataset]
    indices = np.arange(len(dataset))

    # 2. 5-fold CV
    print(f"\n[2/4] Running {N_FOLDS}-fold cross-validation...")
    skf = StratifiedKFold(n_splits=N_FOLDS, shuffle=True, random_state=42)

    models_to_eval = [
        "CertGraph",
        "MLP",
        "Rule-Based",
        "Random Forest",
        "Graph-Augmented MLP",
        "Graph-Augmented RF",
        "BloodHound BFS",
    ]

    results = {m: defaultdict(list) for m in models_to_eval}
    results_preds = {m: [] for m in models_to_eval}
    results_labels = {m: [] for m in models_to_eval}
    all_histories = []
    best_model = None
    best_f1 = 0

    for fold, (train_idx, test_idx) in enumerate(skf.split(indices, labels)):
        print(f"\n  ── Fold {fold+1}/{N_FOLDS} (train={len(train_idx)}, test={len(test_idx)}) ──")

        train_data = [dataset[i] for i in train_idx]
        test_data = [dataset[i] for i in test_idx]

        # 1. CertGraph
        print(f"  [CertGraph]")
        cg_results = train_certgraph_fold(train_data, test_data, fold)
        results["CertGraph"]["f1"].append(cg_results["test_f1"])
        results["CertGraph"]["acc"].append(cg_results["test_acc"])
        results_preds["CertGraph"].extend(cg_results["test_preds"])
        results_labels["CertGraph"].extend(cg_results["test_labels"])
        all_histories.append(cg_results["history"])
        if cg_results["test_f1"] > best_f1:
            best_f1 = cg_results["test_f1"]
            best_model = cg_results["model"]
        print(f"    → F1: {cg_results['test_f1']:.4f} | Acc: {cg_results['test_acc']:.4f}")

        # 2. MLP (features only)
        mlp_res = train_mlp_fold(train_data, test_data)
        results["MLP"]["f1"].append(mlp_res["test_f1"])
        results["MLP"]["acc"].append(mlp_res["test_acc"])
        results_preds["MLP"].extend(mlp_res["test_preds"])
        results_labels["MLP"].extend(mlp_res["test_labels"])
        print(f"  [MLP (features)]         → F1: {mlp_res['test_f1']:.4f} | Acc: {mlp_res['test_acc']:.4f}")

        # 3. Rule-based
        rule_res = eval_rule_baseline(test_data)
        results["Rule-Based"]["f1"].append(rule_res["test_f1"])
        results["Rule-Based"]["acc"].append(rule_res["test_acc"])
        results_preds["Rule-Based"].extend(rule_res["test_preds"])
        results_labels["Rule-Based"].extend(rule_res["test_labels"])
        print(f"  [Rule-Based]             → F1: {rule_res['test_f1']:.4f} | Acc: {rule_res['test_acc']:.4f}")

        # 4. Random Forest (features only)
        rf_res = train_rf_fold(train_data, test_data)
        results["Random Forest"]["f1"].append(rf_res["test_f1"])
        results["Random Forest"]["acc"].append(rf_res["test_acc"])
        results_preds["Random Forest"].extend(rf_res["test_preds"])
        results_labels["Random Forest"].extend(rf_res["test_labels"])
        print(f"  [RF (features)]          → F1: {rf_res['test_f1']:.4f} | Acc: {rf_res['test_acc']:.4f}")

        # 5. Graph-Augmented MLP
        aug_mlp_res = train_augmented_mlp_fold(train_data, test_data)
        results["Graph-Augmented MLP"]["f1"].append(aug_mlp_res["test_f1"])
        results["Graph-Augmented MLP"]["acc"].append(aug_mlp_res["test_acc"])
        results_preds["Graph-Augmented MLP"].extend(aug_mlp_res["test_preds"])
        results_labels["Graph-Augmented MLP"].extend(aug_mlp_res["test_labels"])
        print(f"  [Graph-Augmented MLP]    → F1: {aug_mlp_res['test_f1']:.4f} | Acc: {aug_mlp_res['test_acc']:.4f}")

        # 6. Graph-Augmented RF
        aug_rf_res = train_augmented_rf_fold(train_data, test_data)
        results["Graph-Augmented RF"]["f1"].append(aug_rf_res["test_f1"])
        results["Graph-Augmented RF"]["acc"].append(aug_rf_res["test_acc"])
        results_preds["Graph-Augmented RF"].extend(aug_rf_res["test_preds"])
        results_labels["Graph-Augmented RF"].extend(aug_rf_res["test_labels"])
        print(f"  [Graph-Augmented RF]     → F1: {aug_rf_res['test_f1']:.4f} | Acc: {aug_rf_res['test_acc']:.4f}")

        # 7. BloodHound BFS
        bfs_res = eval_bfs_baseline(test_data)
        results["BloodHound BFS"]["f1"].append(bfs_res["test_f1"])
        results["BloodHound BFS"]["acc"].append(bfs_res["test_acc"])
        results_preds["BloodHound BFS"].extend(bfs_res["test_preds"])
        results_labels["BloodHound BFS"].extend(bfs_res["test_labels"])
        print(f"  [BloodHound BFS]         → F1: {bfs_res['test_f1']:.4f} | Acc: {bfs_res['test_acc']:.4f}")

    # 3. Aggregate results & Statistical Significance
    from scipy.stats import ttest_rel

    cg_f1s = results["CertGraph"]["f1"]
    p_values = {}
    for model_name in models_to_eval:
        if model_name == "CertGraph":
            continue
        base_f1s = results[model_name]["f1"]
        _, p_val = ttest_rel(cg_f1s, base_f1s)
        if np.isnan(p_val):
            p_val = 1.0
        p_values[model_name] = p_val

    print(f"\n\n{'=' * 95}")
    print(f"RESULTS SUMMARY — {N_FOLDS}-fold Cross-Validation (With Fair Graph-Augmented Baselines)")
    print(f"{'=' * 95}")
    print(f"{'Model':<25} {'Macro-F1':>15} {'Accuracy':>15} {'p-value (vs CG)':>22}")
    print("-" * 85)
    for model_name, metrics in results.items():
        f1_mean = np.mean(metrics["f1"])
        f1_std = np.std(metrics["f1"])
        acc_mean = np.mean(metrics["acc"])
        acc_std = np.std(metrics["acc"])
        p_str = f"{p_values[model_name]:.4e}" if model_name in p_values else "N/A (Reference)"
        print(f"{model_name:<25} {f1_mean:.4f}±{f1_std:.4f} {acc_mean:.4f}±{acc_std:.4f} {p_str:>22}")

    # Detailed Per-class Report for CertGraph
    print(f"\n\n{'=' * 85}")
    print("DETAILED PER-CLASS CLASSIFICATION REPORT FOR CERTGRAPH (AGGREGATED OVER ALL FOLDS)")
    print(f"{'=' * 85}")
    report = classification_report(
        results_labels["CertGraph"], results_preds["CertGraph"],
        target_names=ESC_CLASSES, zero_division=0
    )
    print(report)
    print(f"{'=' * 85}")

    # 4. Save results
    print(f"\n[3/4] Saving results...")

    ckpt_path = os.path.join(CHECKPOINT_DIR, "certgraph_best.pt")
    torch.save({
        "model_state_dict": best_model.state_dict() if best_model else None,
        "results": {k: {mk: mv for mk, mv in v.items()} for k, v in results.items()},
        "histories": all_histories,
        "config": {
            "num_envs": NUM_ENVS,
            "hidden_dim": HIDDEN_DIM,
            "out_dim": OUT_DIM,
            "num_heads": NUM_HEADS,
            "dropout": DROPOUT,
            "lr": LR,
            "epochs": EPOCHS,
            "n_folds": N_FOLDS,
        },
    }, ckpt_path)
    print(f"      Checkpoint: {ckpt_path}")

    # Save results JSON
    results_json = {}
    for model_name, metrics in results.items():
        agg_report = classification_report(
            results_labels[model_name], results_preds[model_name],
            target_names=ESC_CLASSES, output_dict=True, zero_division=0
        )
        results_json[model_name] = {
            "f1_mean": float(np.mean(metrics["f1"])),
            "f1_std": float(np.std(metrics["f1"])),
            "acc_mean": float(np.mean(metrics["acc"])),
            "acc_std": float(np.std(metrics["acc"])),
            "f1_per_fold": [float(x) for x in metrics["f1"]],
            "acc_per_fold": [float(x) for x in metrics["acc"]],
            "p_value_vs_certgraph": float(p_values[model_name]) if model_name in p_values else None,
            "detailed_report": agg_report,
        }
    json_path = os.path.join(RESULTS_DIR, "cv_results.json")
    with open(json_path, "w") as f:
        json.dump(results_json, f, indent=2)
    print(f"      Results JSON: {json_path}")

    if best_model:
        params = sum(p.numel() for p in best_model.parameters())
        print(f"\n[4/4] CertGraph parameters: {params:,}")

    print(f"\n[✓] Cross-validation and baseline comparison complete!")
    return results, all_histories


if __name__ == "__main__":
    main()
