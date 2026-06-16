"""
transfer_eval.py — Domain Generalization & Transfer Learning Evaluation
======================================================================
Trains CertGraph on standard synthetic data and tests on realistic tiered ADSynth data,
and vice versa. Evaluates the model's structural generalization across distinct AD topologies.
"""

import os
import json
import time
import numpy as np
import torch
import torch.nn.functional as F
from sklearn.metrics import f1_score, accuracy_score, classification_report
from torch_geometric.loader import DataLoader

from generator import generate_dataset, CLASS_TO_IDX, NUM_CLASSES, ESC_CLASSES
from adsynth_adapter import generate_adsynth_dataset
from model import CertGraph

# Configs matching training
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2
LR = 0.005
EPOCHS = 80
BATCH_SIZE = 64
NUM_ENVS = 350 # smaller dataset for faster transfer run in tests, standard is 350-700

def train_and_evaluate(train_dataset, test_dataset, verbose=True):
    # Prepare loaders
    for data, esc_class, target_idx in train_dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)
    for data, esc_class, target_idx in test_dataset:
        data.target_idx = torch.tensor([target_idx], dtype=torch.long)
        data.y_class = torch.tensor([CLASS_TO_IDX[esc_class]], dtype=torch.long)

    train_list = [d for d, _, _ in train_dataset]
    test_list = [d for d, _, _ in test_dataset]

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
    
    optimizer = torch.optim.Adam(model.parameters(), lr=LR, weight_decay=1e-4)

    # Training loop
    for epoch in range(1, EPOCHS + 1):
        model.train()
        total_loss = 0.0
        for batch in train_loader:
            optimizer.zero_grad()
            logits = model(batch.x_dict, batch.edge_index_dict)
            ptr = batch['Template'].ptr
            target_indices = ptr[:-1] + batch.target_idx
            target_logits = logits[target_indices]
            loss = F.cross_entropy(target_logits, batch.y_class)
            loss.backward()
            optimizer.step()
            total_loss += loss.item() * batch.num_graphs

    # Evaluation
    model.eval()
    test_preds = []
    test_labels = []

    with torch.no_grad():
        for batch in test_loader:
            logits = model(batch.x_dict, batch.edge_index_dict)
            ptr = batch['Template'].ptr
            target_indices = ptr[:-1] + batch.target_idx
            target_logits = logits[target_indices]
            test_preds.extend(target_logits.argmax(dim=1).cpu().tolist())
            test_labels.extend(batch.y_class.cpu().tolist())

    f1 = f1_score(test_labels, test_preds, average="macro", zero_division=0)
    acc = accuracy_score(test_labels, test_preds)
    report = classification_report(test_labels, test_preds, target_names=ESC_CLASSES, output_dict=True, zero_division=0)

    return f1, acc, report

def main():
    research_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    results_dir = os.path.join(research_root, "results", "phase2")
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 75)
    print("DOMAIN GENERALIZATION / TRANSFER EVALUATION")
    print("=" * 75)

    # 1. Generate datasets
    print(f"[*] Generating datasets ({NUM_ENVS} environments each)...")
    t0 = time.time()
    synthetic_dataset = generate_dataset(num_envs=NUM_ENVS, balanced=True, seed=42)
    adsynth_dataset = generate_adsynth_dataset(num_envs=NUM_ENVS, balanced=True, seed=42)
    print(f"    Generated in {time.time() - t0:.1f}s")

    # 2. Experiment 1: Train Synthetic -> Test ADSynth
    print("\n[*] Running Experiment 1: Train Synthetic → Test ADSynth...")
    syn_to_ad_f1, syn_to_ad_acc, syn_to_ad_rep = train_and_evaluate(synthetic_dataset, adsynth_dataset)
    print(f"    Results: F1 = {syn_to_ad_f1:.4f} | Acc = {syn_to_ad_acc:.4f}")

    # 3. Experiment 2: Train ADSynth -> Test Synthetic
    print("\n[*] Running Experiment 2: Train ADSynth → Test Synthetic...")
    ad_to_syn_f1, ad_to_syn_acc, ad_to_syn_rep = train_and_evaluate(adsynth_dataset, synthetic_dataset)
    print(f"    Results: F1 = {ad_to_syn_f1:.4f} | Acc = {ad_to_syn_acc:.4f}")

    # 4. Experiment 3: 5-Fold Cross-Validation on ADSynth alone (Realistic topology baseline)
    print("\n[*] Running Experiment 3: 5-Fold CV on ADSynth (Realistic Topology Baseline)...")
    from sklearn.model_selection import StratifiedKFold
    labels = [CLASS_TO_IDX[esc_class] for _, esc_class, _ in adsynth_dataset]
    indices = np.arange(len(adsynth_dataset))
    skf = StratifiedKFold(n_splits=5, shuffle=True, random_state=42)
    
    cv_f1s = []
    cv_accs = []
    
    for fold, (train_idx, test_idx) in enumerate(skf.split(indices, labels)):
        train_sub = [adsynth_dataset[i] for i in train_idx]
        test_sub = [adsynth_dataset[i] for i in test_idx]
        f1, acc, _ = train_and_evaluate(train_sub, test_sub, verbose=False)
        cv_f1s.append(f1)
        cv_accs.append(acc)
        print(f"    Fold {fold+1}/5 - F1: {f1:.4f} | Acc: {acc:.4f}")

    cv_f1_mean = np.mean(cv_f1s)
    cv_f1_std = np.std(cv_f1s)
    cv_acc_mean = np.mean(cv_accs)
    cv_acc_std = np.std(cv_accs)
    print(f"    5-Fold CV Results: F1 = {cv_f1_mean:.4f}±{cv_f1_std:.4f} | Acc = {cv_acc_mean:.4f}±{cv_acc_std:.4f}")

    # Save results to JSON
    transfer_results = {
        "synthetic_to_adsynth": {
            "f1": syn_to_ad_f1,
            "accuracy": syn_to_ad_acc,
            "report": syn_to_ad_rep
        },
        "adsynth_to_synthetic": {
            "f1": ad_to_syn_f1,
            "accuracy": ad_to_syn_acc,
            "report": ad_to_syn_rep
        },
        "adsynth_5fold_cv": {
            "f1_mean": cv_f1_mean,
            "f1_std": cv_f1_std,
            "acc_mean": cv_acc_mean,
            "acc_std": cv_acc_std,
            "f1s": cv_f1s,
            "accs": cv_accs
        }
    }

    results_json_path = os.path.join(results_dir, "transfer_results.json")
    with open(results_json_path, "w") as f:
        json.dump(transfer_results, f, indent=2)
    print(f"\n[✓] Saved transfer evaluation results to: {results_json_path}")

if __name__ == "__main__":
    main()
