"""Make standalone scientific figures from saved research results."""

import argparse
import hashlib
import json
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np


METHODS = ["legacy_or_keys", "issuer_serial", "conjunctive_window300", "conjunctive_point", "constraint_lineage"]
LABELS = ["OR identifiers", "Issuer + serial", "Conjunctive, 300 s", "Conjunctive, point time", "Constraint lineage"]


def build(directory):
    path = directory / "results.json"
    result = json.loads(path.read_text())
    data = result["by_family"]["randomized_mix"]
    figure_dir = directory / "figures"
    figure_dir.mkdir(exist_ok=True)
    fig, axes = plt.subplots(1, 2, figsize=(11, 4.3), constrained_layout=True)
    x = np.arange(len(METHODS))
    definite = [100 * data[m]["edge_recall"] for m in METHODS]
    possible = [100 * data[m]["possible_set_recall"] for m in METHODS]
    axes[0].barh(x + 0.16, definite, height=0.3, label="Definite output edges", color="#275d91")
    axes[0].barh(x - 0.16, possible, height=0.3, label="Includes possible candidates", color="#a9c8df")
    axes[0].set_yticks(x, LABELS)
    axes[0].set_xlim(0, 105)
    axes[0].set_xlabel("Observed true use edges covered (%)")
    axes[0].legend(frameon=False, fontsize=8, loc="lower right")
    axes[0].grid(axis="x", alpha=0.2)
    false = [data[m]["false_definite_exposure_edges"] for m in METHODS]
    axes[1].barh(x, false, color=["#a75f45"] * 4 + ["#275d91"])
    axes[1].set_yticks(x, LABELS)
    axes[1].set_xlabel("False definite mutation-attribution edges (count)")
    axes[1].grid(axis="x", alpha=0.2)
    for axis in axes:
        axis.invert_yaxis()
        axis.spines[["top", "right"]].set_visible(False)
    fig.suptitle("Synthetic randomized histories: 2,000 cases; results conditional on the simulator", fontsize=11)
    for suffix in ("pdf", "png", "svg"):
        fig.savefig(figure_dir / f"lineage_tradeoff.{suffix}", dpi=200)
    plt.close(fig)
    label_path = directory / "labels.jsonl"
    labels = [json.loads(line) for line in label_path.read_text().splitlines() if line.strip()]
    true_exposures = sum(r["true_exposure"] for r in labels if ":randomized_mix:" in r["case_id"])
    cost_ratios = np.linspace(0, 10, 201)
    utility = {}
    fig, axis = plt.subplots(figsize=(7, 4.5), constrained_layout=True)
    for method, label in zip(METHODS, LABELS):
        d = data[method]
        correct = d["definite_exposure_edges"] - d["false_definite_exposure_edges"]
        missed = true_exposures - correct
        false = d["false_definite_exposure_edges"]
        utility[method] = {"correct_definite_overlap_edges": correct, "missed_true_overlap_edges": missed,
                           "false_definite_overlap_edges": false}
        axis.plot(cost_ratios, missed + cost_ratios * false, label=label,
                  linewidth=2.3 if method == "constraint_lineage" else 1.3)
    axis.set_xlabel("Assumed cost of false definitive attribution / missed definitive overlap")
    axis.set_ylabel("Synthetic loss: missed + cost ratio × false")
    axis.set_title("A conditional cost model, not measured business disruption", fontsize=10)
    axis.legend(frameon=False, fontsize=8)
    axis.grid(alpha=0.2)
    axis.spines[["top", "right"]].set_visible(False)
    for suffix in ("pdf", "png", "svg"):
        fig.savefig(figure_dir / f"conditional_cost.{suffix}", dpi=200)
    plt.close(fig)
    full = utility["constraint_lineage"]
    point = utility["conjunctive_point"]
    utility["true_randomized_overlap_edges"] = true_exposures
    utility["full_vs_point_break_even_false_cost_ratio"] = (
        (full["missed_true_overlap_edges"] - point["missed_true_overlap_edges"])
        / (point["false_definite_overlap_edges"] - full["false_definite_overlap_edges"]))
    (figure_dir / "utility_analysis.json").write_text(json.dumps(utility, indent=2) + "\n")
    manifest = {"input_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                "labels_sha256": hashlib.sha256(label_path.read_bytes()).hexdigest(),
                "plot_source_sha256": hashlib.sha256(Path(__file__).read_bytes()).hexdigest()}
    (figure_dir / "manifest.json").write_text(json.dumps(manifest, indent=2) + "\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("directory", type=Path)
    build(parser.parse_args().directory)
