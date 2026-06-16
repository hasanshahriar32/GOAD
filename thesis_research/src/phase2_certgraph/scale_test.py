#!/usr/bin/env python3
"""
scale_test.py — Scalability Benchmarks for CertGraph GNN
======================================================
Measures graph generation time, model inference latency, and memory allocation
across different Active Directory graph sizes (from 100 to 10,000 nodes).
Demonstrates linear scalability suitable for large-scale enterprise ADs.
"""

import os
import time
import json
import numpy as np
import torch
import resource
import gc
import matplotlib.pyplot as plt
from generator import generate_environment
from model import CertGraph

# Config
SIZES = [100, 500, 1000, 5000, 10000]
NUM_RUNS = 20
HIDDEN_DIM = 32
OUT_DIM = 16
NUM_HEADS = 4
NUM_CLASSES = 7

RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
os.makedirs(RESULTS_DIR, exist_ok=True)


def get_params_for_scale(target_nodes: int) -> dict:
    """Calculate node counts to achieve the approximate target total node size."""
    # Ratio: Users (70%), Groups (20%), Computers (8%), Templates (2%)
    num_users = int(target_nodes * 0.70)
    num_groups = int(target_nodes * 0.20)
    num_computers = int(target_nodes * 0.08)
    num_extra_templates = int(target_nodes * 0.02)
    return {
        "num_users": max(10, num_users),
        "num_groups": max(5, num_groups),
        "num_computers": max(2, num_computers),
        "num_extra_templates": max(1, num_extra_templates)
    }


def main():
    print("=" * 70)
    print("CertGraph Scalability & Performance Benchmarks")
    print("=" * 70)
    
    results = []
    
    # Pre-initialize model on a small sample to get metadata structure
    sample_data, _ = generate_environment("Safe", num_users=10, num_groups=5, num_computers=2)
    model = CertGraph(
        metadata=sample_data.metadata(),
        hidden_channels=HIDDEN_DIM,
        out_channels=OUT_DIM,
        num_classes=NUM_CLASSES,
        num_heads=NUM_HEADS
    )
    model.eval()
    
    # Lazy initialize model weights
    with torch.no_grad():
        _ = model(sample_data.x_dict, sample_data.edge_index_dict)
        
    print(f"\nBenchmarking scales: {SIZES} nodes")
    
    for size in SIZES:
        params = get_params_for_scale(size)
        print(f"\n  ── Scale: ~{size} Nodes ──")
        print(f"     Config: Users={params['num_users']}, Groups={params['num_groups']}, Computers={params['num_computers']}, Templates={params['num_extra_templates']}")
        
        # 1. Measure Generation Time & Memory
        gc.collect()
        if torch.cuda.is_available():
            torch.cuda.reset_peak_memory_stats()
            torch.cuda.empty_cache()
            
        start_gen = time.perf_counter()
        data, _ = generate_environment(
            "ESC1",
            num_users=params["num_users"],
            num_groups=params["num_groups"],
            num_computers=params["num_computers"],
            num_extra_templates=params["num_extra_templates"],
            seed=42
        )
        end_gen = time.perf_counter()
        
        gen_time = (end_gen - start_gen) * 1000 # ms
        
        # Measure peak memory (GPU or RSS)
        if torch.cuda.is_available():
            mem_mb = torch.cuda.max_memory_allocated() / (1024.0 * 1024.0)
        else:
            mem_mb = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss / 1024.0
        
        # Count actual nodes and edges
        num_nodes = sum(x.shape[0] for x in data.x_dict.values())
        num_edges = sum(edge_idx.shape[1] for edge_idx in data.edge_index_dict.values())
        
        print(f"     Actual size: Nodes={num_nodes:,} | Edges={num_edges:,}")
        print(f"     Generation:  {gen_time:.2f} ms | Memory: {mem_mb:.3f} MB")
        
        # 2. Measure Inference Latency
        latencies = []
        with torch.no_grad():
            # Warmup
            for _ in range(5):
                _ = model(data.x_dict, data.edge_index_dict)
                
            for _ in range(NUM_RUNS):
                t0 = time.perf_counter()
                _ = model(data.x_dict, data.edge_index_dict)
                t1 = time.perf_counter()
                latencies.append((t1 - t0) * 1000) # ms
                
        avg_latency = float(np.mean(latencies))
        std_latency = float(np.std(latencies))
        print(f"     Inference:   {avg_latency:.2f} ms ± {std_latency:.2f} ms")
        
        results.append({
            "target_scale": size,
            "actual_nodes": num_nodes,
            "actual_edges": num_edges,
            "generation_time_ms": gen_time,
            "memory_usage_mb": mem_mb,
            "inference_latency_ms_mean": avg_latency,
            "inference_latency_ms_std": std_latency
        })
        
    # Save results JSON
    json_path = os.path.join(RESULTS_DIR, "scalability_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[✓] Benchmarks complete. Saved: {json_path}")
    
    # Plotting
    plt.rcParams.update({
        "figure.facecolor": "#1a1a2e", "axes.facecolor": "#16213e",
        "text.color": "white", "axes.labelcolor": "#aaa",
        "xtick.color": "#666", "ytick.color": "#666",
    })
    
    fig, axs = plt.subplots(1, 3, figsize=(18, 5))
    node_labels = [r["actual_nodes"] for r in results]
    
    # Subplot 1: Inference Latency
    axs[0].plot(node_labels, [r["inference_latency_ms_mean"] for r in results],
                marker="o", color="#FF6B6B", linewidth=2, label="Latency")
    axs[0].fill_between(node_labels,
                        [r["inference_latency_ms_mean"] - r["inference_latency_ms_std"] for r in results],
                        [r["inference_latency_ms_mean"] + r["inference_latency_ms_std"] for r in results],
                        color="#FF6B6B", alpha=0.15)
    axs[0].set_title("Model Inference Latency", fontsize=12, fontweight="bold")
    axs[0].set_xlabel("Number of Nodes", fontsize=10)
    axs[0].set_ylabel("Latency (ms)", fontsize=10)
    axs[0].grid(True, alpha=0.1, color="#555")
    
    # Subplot 2: Memory Consumption
    axs[1].plot(node_labels, [r["memory_usage_mb"] for r in results],
                marker="s", color="#4ECDC4", linewidth=2, label="Memory")
    axs[1].set_title("Graph Peak Memory footprint", fontsize=12, fontweight="bold")
    axs[1].set_xlabel("Number of Nodes", fontsize=10)
    axs[1].set_ylabel("Peak Memory (MB)", fontsize=10)
    axs[1].grid(True, alpha=0.1, color="#555")
    
    # Subplot 3: Generation Time
    axs[2].plot(node_labels, [r["generation_time_ms"] for r in results],
                marker="^", color="#FFA07A", linewidth=2, label="Gen Time")
    axs[2].set_title("Environment Generation Time", fontsize=12, fontweight="bold")
    axs[2].set_xlabel("Number of Nodes", fontsize=10)
    axs[2].set_ylabel("Time (ms)", fontsize=10)
    axs[2].grid(True, alpha=0.1, color="#555")
    
    for ax in axs:
        for s in ax.spines.values():
            s.set_color("#333")
            
    plot_path = os.path.join(RESULTS_DIR, "scalability_metrics.png")
    plt.tight_layout()
    plt.savefig(plot_path, dpi=300, facecolor=fig.get_facecolor())
    plt.close()
    print(f"      Scalability Plot: {plot_path}")


if __name__ == "__main__":
    main()
