"""
fresh_data_eval.py — Evaluate CertGraph on Fresh GOAD BloodHound Collection
============================================================================
Validates the trained CertGraph model on freshly collected BloodHound data
from the running GOAD VMs (July 2026 collection). This provides temporal
separation from the original training/evaluation pipeline.
"""

import os
import sys
import json
import torch
import torch.nn.functional as F
from torch_geometric.data import HeteroData

sys.path.insert(0, os.path.dirname(__file__))
from bloodhound_parser import parse_bloodhound_dir, inject_adcs_vulnerability
from generator import ESC_CLASSES, CLASS_TO_IDX, NUM_CLASSES
from model import CertGraph, RuleBaseline

HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
DROPOUT = 0.2


def run_fresh_data_eval():
    research_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
    checkpoint_path = os.path.join(research_root, "results", "phase2", "certgraph_best.pt")
    fresh_data_dir = os.path.join(research_root, "data", "fresh_goad_collection")
    results_dir = os.path.join(research_root, "results", "phase2")
    os.makedirs(results_dir, exist_ok=True)

    print("=" * 75)
    print("FRESH GOAD COLLECTION VALIDATION (July 2026)")
    print("=" * 75)

    if not os.path.exists(checkpoint_path):
        raise FileNotFoundError(f"Checkpoint not found: {checkpoint_path}")

    # Split the fresh collection into per-domain directories
    # The files have timestamps as prefixes. Group by timestamp.
    import glob
    json_files = sorted(glob.glob(os.path.join(fresh_data_dir, "*.json")))
    
    # Group by timestamp prefix
    timestamps = sorted(set(
        os.path.basename(f).rsplit("_", 1)[0] for f in json_files
    ))
    
    domain_names = ["sevenkingdoms.local", "north.sevenkingdoms.local", "essos.local"]
    
    print(f"[*] Found {len(timestamps)} collections: {timestamps}")
    print(f"[*] Mapping to domains: {domain_names[:len(timestamps)]}")

    # Create temp directories per domain
    import tempfile, shutil
    temp_dirs = []
    for ts in timestamps:
        td = os.path.join(fresh_data_dir, f"domain_{ts}")
        os.makedirs(td, exist_ok=True)
        # Symlink or copy the domain's files
        for f in json_files:
            basename = os.path.basename(f)
            if basename.startswith(ts):
                dst = os.path.join(td, basename)
                if not os.path.exists(dst):
                    shutil.copy2(f, dst)
        temp_dirs.append(td)

    # Load model
    print("[*] Loading trained CertGraph model...")
    checkpoint = torch.load(checkpoint_path, weights_only=False)
    
    # Initialize with first domain
    base_graph = parse_bloodhound_dir(temp_dirs[0])
    sample_graph, _ = inject_adcs_vulnerability(base_graph.clone(), "Safe")
    
    model = CertGraph(
        metadata=sample_graph.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS,
        dropout=DROPOUT,
    )
    
    with torch.no_grad():
        model.eval()
        _ = model(sample_graph.x_dict, sample_graph.edge_index_dict)
    
    model.load_state_dict(checkpoint["model_state_dict"])
    model.eval()
    print("    Model loaded successfully.")

    rule_baseline = RuleBaseline()

    # Test cases
    test_cases = [
        ("ESC1", "ESC1"),
        ("ESC2", "ESC2"),
        ("ESC3", "ESC3"),
        ("ESC4", "ESC4"),
        ("ESC9", "ESC9"),
        ("ESC13", "ESC13"),
        ("Safe", "Safe"),
    ]

    all_results = {}
    overall_correct = 0
    overall_total = 0

    for domain_idx, (td, dname) in enumerate(zip(temp_dirs, domain_names[:len(temp_dirs)])):
        print(f"\n{'─' * 60}")
        print(f"  Domain: {dname}")
        print(f"{'─' * 60}")
        
        try:
            base = parse_bloodhound_dir(td)
        except Exception as e:
            print(f"    ⚠ Could not parse: {e}")
            continue
        
        print(f"    Nodes: {base['User'].x.shape[0]} Users, {base['Group'].x.shape[0]} Groups, {base['Computer'].x.shape[0]} Computers")
        
        domain_results = {}
        domain_correct = 0
        domain_total = 0

        for inject_type, expected_label in test_cases:
            graph, target_idx = inject_adcs_vulnerability(base.clone(), inject_type)
            
            with torch.no_grad():
                logits = model(graph.x_dict, graph.edge_index_dict)
                pred = logits[target_idx].argmax().item()
                pred_label = ESC_CLASSES[pred]
            
            correct = pred_label == expected_label
            domain_correct += int(correct)
            domain_total += 1
            overall_correct += int(correct)
            overall_total += 1
            
            status = "✓" if correct else "✗"
            domain_results[inject_type] = {
                "expected": expected_label,
                "predicted": pred_label,
                "correct": correct,
            }
            print(f"    [{status}] Inject: {inject_type:<12} → Predicted: {pred_label:<8} (Expected: {expected_label})")

        domain_acc = domain_correct / domain_total if domain_total > 0 else 0
        print(f"    Domain Accuracy: {domain_correct}/{domain_total} ({domain_acc:.1%})")
        
        all_results[dname] = {
            "tests": domain_results,
            "accuracy": domain_acc,
            "correct": domain_correct,
            "total": domain_total,
        }

    overall_acc = overall_correct / overall_total if overall_total > 0 else 0
    
    print(f"\n{'=' * 75}")
    print(f"OVERALL ACCURACY: {overall_correct}/{overall_total} ({overall_acc:.1%})")
    print(f"{'=' * 75}")

    # Save results
    summary = {
        "collection_date": "2026-07-02",
        "data_source": "Fresh BloodHound-python collection from running GOAD VMs",
        "domains": all_results,
        "overall_accuracy": overall_acc,
        "overall_correct": overall_correct,
        "overall_total": overall_total,
    }
    
    out_path = os.path.join(results_dir, "fresh_goad_eval_results.json")
    with open(out_path, "w") as f:
        json.dump(summary, f, indent=2)
    print(f"\n[✓] Results saved to: {out_path}")


if __name__ == "__main__":
    run_fresh_data_eval()
