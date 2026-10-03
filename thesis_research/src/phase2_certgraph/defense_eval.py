#!/usr/bin/env python3
"""
defense_eval.py — Empirical Evaluation of Autonomous Edge-Interdiction Defenses
=============================================================================
Evaluates edge-interdiction strategies on Active Directory identity graphs:
1. Uniform Random Revocation
2. Degree-Centrality Revocation
3. Greedy Capacity-Disruption Heuristic (Algorithm 1, §9.3)

Evaluates across a suite of synthetic AD topologies under varying operational
disruption budgets (B_ops in {6, 12, 18, 24}). Outputs actual measured metrics
to thesis_research/results/phase2/defense_results.json and regenerates Figure 9.1.
"""

import os
import sys
import json
import time
import copy
import random
import numpy as np
import networkx as nx
import matplotlib.pyplot as plt
from scipy import stats

# Ensure local imports work
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from generator import generate_environment, ESC_CLASSES

RESEARCH_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
RESULTS_DIR = os.path.join(RESEARCH_ROOT, "results", "phase2")
PAPER_FIG_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", "..", "thesis_paper", "figures"))
os.makedirs(RESULTS_DIR, exist_ok=True)
os.makedirs(PAPER_FIG_DIR, exist_ok=True)


def hetero_to_networkx(data):
    """Convert PyG HeteroData into a directed NetworkX graph with edge costs."""
    G = nx.DiGraph()
    for ntype in ["User", "Group", "Computer", "Template", "CA"]:
        if ntype in data.node_types:
            num_nodes = data[ntype].num_nodes
            for i in range(num_nodes):
                G.add_node(f"{ntype}_{i}", ntype=ntype, idx=i)

    for edge_type in data.edge_types:
        src_type, rel, dst_type = edge_type
        edge_index = data[edge_type].edge_index
        for col in range(edge_index.size(1)):
            u = f"{src_type}_{edge_index[0, col].item()}"
            v = f"{dst_type}_{edge_index[1, col].item()}"
            # Standard operational revocation cost c(e) = 1.0
            G.add_edge(u, v, rel=rel, cost=1.0)
    return G


def get_forbidden_pairs(G, data, target_idx):
    """Identify all reachable (unprivileged_user, high_value_target) pairs."""
    user_x = data["User"].x
    lowpriv_users = [f"User_{i}" for i in range(data["User"].num_nodes) if user_x[i, 5] < 0.5]
    group_x = data["Group"].x
    admin_groups = [f"Group_{i}" for i in range(data["Group"].num_nodes) if group_x[i, 0] > 0.5]
    targets = admin_groups + [f"Template_{target_idx}"]
    pairs = [(u, t) for u in lowpriv_users for t in targets if nx.has_path(G, u, t)]
    return pairs


def evaluate_severed(G_cut, forbidden_pairs):
    """Compute the percentage of initial forbidden pairs that are severed."""
    if not forbidden_pairs:
        return 100.0
    active = sum(1 for (u, t) in forbidden_pairs if nx.has_path(G_cut, u, t))
    severed = len(forbidden_pairs) - active
    return (severed / len(forbidden_pairs)) * 100.0


def random_revocation(G, forbidden_pairs, budget, rng):
    """Uniform Random Revocation Baseline."""
    G_curr = G.copy()
    candidate_edges = list(G_curr.edges())
    rng.shuffle(candidate_edges)

    revoked = []
    cost = 0.0
    for u, v in candidate_edges:
        c = G_curr[u][v].get("cost", 1.0)
        if cost + c <= budget:
            G_curr.remove_edge(u, v)
            revoked.append((u, v))
            cost += c
        if cost >= budget:
            break

    pct = evaluate_severed(G_curr, forbidden_pairs)
    compliance = (cost / budget) * 100.0 if budget > 0 else 100.0
    return pct, len(revoked), compliance


def degree_centrality_revocation(G, forbidden_pairs, budget):
    """Degree-Centrality Revocation Baseline."""
    G_curr = G.copy()
    degrees = dict(G_curr.degree())
    edges = list(G_curr.edges())
    # Sort descending by sum of incident node degrees
    edges.sort(key=lambda e: (degrees[e[0]] + degrees[e[1]]), reverse=True)

    revoked = []
    cost = 0.0
    for u, v in edges:
        c = G_curr[u][v].get("cost", 1.0)
        if cost + c <= budget:
            G_curr.remove_edge(u, v)
            revoked.append((u, v))
            cost += c
        if cost >= budget:
            break

    pct = evaluate_severed(G_curr, forbidden_pairs)
    compliance = (cost / budget) * 100.0 if budget > 0 else 100.0
    return pct, len(revoked), compliance


def greedy_capacity_disruption(G, forbidden_pairs, budget):
    """
    Algorithm 1: Greedy Capacity-Disruption Edge Severing Heuristic (§9.3).
    Iteratively computes path centrality phi(e) and severs e* maximizing phi(e)/c(e).
    """
    G_curr = G.copy()
    E_cut = []
    C_total = 0.0

    while True:
        active_pairs = [(u, t) for (u, t) in forbidden_pairs if nx.has_path(G_curr, u, t)]
        if not active_pairs:
            break

        edge_phi = {}
        for u, t in active_pairs:
            try:
                path = nx.shortest_path(G_curr, u, t)
                for i in range(len(path) - 1):
                    e = (path[i], path[i + 1])
                    edge_phi[e] = edge_phi.get(e, 0) + 1
            except nx.NetworkXNoPath:
                continue

        if not edge_phi:
            break

        best_e = None
        best_rho = -1.0
        for e, phi in edge_phi.items():
            cost_e = G_curr[e[0]][e[1]].get("cost", 1.0)
            rho = phi / cost_e
            if rho > best_rho:
                best_rho = rho
                best_e = e

        if best_e is None:
            break

        cost_best = G_curr[best_e[0]][best_e[1]].get("cost", 1.0)
        if C_total + cost_best > budget:
            break

        G_curr.remove_edge(best_e[0], best_e[1])
        E_cut.append(best_e)
        C_total += cost_best

    pct = evaluate_severed(G_curr, forbidden_pairs)
    compliance = (C_total / budget) * 100.0 if budget > 0 else 100.0
    return pct, len(E_cut), compliance


def main():
    print("=" * 70)
    print("Empirical Evaluation of Autonomous Edge-Interdiction Defenses")
    print("=" * 70)

    # Suite parameters
    NUM_TOPOLOGIES = 30  # 5 topologies per ESC class (ESC1, ESC2, ESC3, ESC4, ESC9, ESC13)
    BUDGETS = [6, 12, 18, 24]
    RANDOM_REPS = 5  # repetitions for stochastic baseline
    BASE_SEED = 42

    print(f"Generating and evaluating {NUM_TOPOLOGIES} synthetic AD topologies...")
    topologies = []
    esc_classes = ["ESC1", "ESC2", "ESC3", "ESC4", "ESC9", "ESC13"]
    topo_idx = 0
    for esc_cls in esc_classes:
        for rep in range(NUM_TOPOLOGIES // len(esc_classes)):
            seed = BASE_SEED + topo_idx * 17
            data, target = generate_environment(
                esc_cls,
                num_users=random.Random(seed).randint(40, 60),
                num_groups=random.Random(seed).randint(12, 18),
                num_computers=random.Random(seed).randint(10, 15),
                seed=seed
            )
            G = hetero_to_networkx(data)
            pairs = get_forbidden_pairs(G, data, target)
            topologies.append({
                "id": topo_idx,
                "class": esc_cls,
                "nodes": G.number_of_nodes(),
                "edges": G.number_of_edges(),
                "forbidden_pairs": len(pairs),
                "graph": G,
                "pairs": pairs,
            })
            topo_idx += 1

    print(f"Successfully generated {len(topologies)} topologies.")
    avg_nodes = np.mean([t["nodes"] for t in topologies])
    avg_edges = np.mean([t["edges"] for t in topologies])
    avg_pairs = np.mean([t["forbidden_pairs"] for t in topologies])
    print(f"Average topology: {avg_nodes:.1f} nodes, {avg_edges:.1f} edges, {avg_pairs:.1f} reachable attack paths.")

    # Run evaluations
    results = {
        "metadata": {
            "num_topologies": NUM_TOPOLOGIES,
            "evaluated_budgets": BUDGETS,
            "random_replications": RANDOM_REPS,
            "avg_nodes": float(avg_nodes),
            "avg_edges": float(avg_edges),
            "avg_forbidden_paths": float(avg_pairs),
            "timestamp": time.strftime("%Y-%m-%d %H:%M:%S"),
        },
        "budgets": BUDGETS,
        "empirical_metrics": {
            "random_revocation": {},
            "degree_centrality": {},
            "greedy_capacity_disruption": {},
        },
        "notional_marl_model": {
            # Clearly labeled notional/illustrative reference curve for theoretical model
            "status": "notional_theoretical_simulation",
            "note": "Operational compliance omitted (None) as compliance was not a tracked quantity for the unrun theoretical model.",
            "6": {"paths_severed_mean": 68.3, "edges_revoked_mean": 5.8, "budget_compliance_mean": None},
            "12": {"paths_severed_mean": 96.2, "edges_revoked_mean": 11.4, "budget_compliance_mean": None},
            "18": {"paths_severed_mean": 100.0, "edges_revoked_mean": 12.1, "budget_compliance_mean": None},
            "24": {"paths_severed_mean": 100.0, "edges_revoked_mean": 12.1, "budget_compliance_mean": None},
        }
    }

    for b in BUDGETS:
        print(f"\n--- Evaluating Budget B_ops = {b} ---")
        rand_pcts, rand_edges, rand_comps = [], [], []
        deg_pcts, deg_edges, deg_comps = [], [], []
        grd_pcts, grd_edges, grd_comps = [], [], []

        for topo in topologies:
            G = topo["graph"]
            pairs = topo["pairs"]
            if not pairs:
                continue

            # Random baseline (average across RANDOM_REPS)
            r_p_list, r_e_list, r_c_list = [], [], []
            for r_seed in range(RANDOM_REPS):
                rng = random.Random(BASE_SEED + r_seed * 101 + topo["id"])
                p, e, c = random_revocation(G, pairs, b, rng)
                r_p_list.append(p)
                r_e_list.append(e)
                r_c_list.append(c)
            rand_pcts.append(np.mean(r_p_list))
            rand_edges.append(np.mean(r_e_list))
            rand_comps.append(np.mean(r_c_list))

            # Degree baseline
            dp, de, dc = degree_centrality_revocation(G, pairs, b)
            deg_pcts.append(dp)
            deg_edges.append(de)
            deg_comps.append(dc)

            # Greedy heuristic (Algorithm 1)
            gp, ge, gc = greedy_capacity_disruption(G, pairs, b)
            grd_pcts.append(gp)
            grd_edges.append(ge)
            grd_comps.append(gc)

        # Compute paired statistical significance: Algorithm 1 vs Degree Centrality
        t_stat, t_pval = stats.ttest_rel(grd_pcts, deg_pcts)
        try:
            w_stat, w_pval = stats.wilcoxon(grd_pcts, deg_pcts, zero_method='wilcox')
        except Exception:
            w_stat, w_pval = 0.0, 1.0

        # Record summary stats & per-topology distributions
        results["empirical_metrics"]["random_revocation"][str(b)] = {
            "paths_severed_mean": float(np.mean(rand_pcts)),
            "paths_severed_std": float(np.std(rand_pcts)),
            "paths_severed_per_topology": [float(x) for x in rand_pcts],
            "edges_revoked_mean": float(np.mean(rand_edges)),
            "edges_revoked_std": float(np.std(rand_edges)),
            "budget_compliance_mean": float(np.mean(rand_comps)),
        }
        results["empirical_metrics"]["degree_centrality"][str(b)] = {
            "paths_severed_mean": float(np.mean(deg_pcts)),
            "paths_severed_std": float(np.std(deg_pcts)),
            "paths_severed_per_topology": [float(x) for x in deg_pcts],
            "edges_revoked_mean": float(np.mean(deg_edges)),
            "edges_revoked_std": float(np.std(deg_edges)),
            "budget_compliance_mean": float(np.mean(deg_comps)),
        }
        results["empirical_metrics"]["greedy_capacity_disruption"][str(b)] = {
            "paths_severed_mean": float(np.mean(grd_pcts)),
            "paths_severed_std": float(np.std(grd_pcts)),
            "paths_severed_per_topology": [float(x) for x in grd_pcts],
            "edges_revoked_mean": float(np.mean(grd_edges)),
            "edges_revoked_std": float(np.std(grd_edges)),
            "budget_compliance_mean": float(np.mean(grd_comps)),
        }
        if "statistical_significance" not in results:
            results["statistical_significance"] = {}
        results["statistical_significance"][str(b)] = {
            "paired_ttest": {
                "t_statistic": float(t_stat),
                "p_value": float(t_pval),
                "significant_p05": bool(t_pval < 0.05),
                "significant_p01": bool(t_pval < 0.01),
                "significant_p001": bool(t_pval < 0.001),
            },
            "wilcoxon_signed_rank": {
                "w_statistic": float(w_stat),
                "p_value": float(w_pval),
                "significant_p05": bool(w_pval < 0.05),
                "significant_p01": bool(w_pval < 0.01),
            }
        }

        print(f"  Random Revocation:         {np.mean(rand_pcts):.1f} ± {np.std(rand_pcts):.1f}% severed, {np.mean(rand_edges):.1f} edges")
        print(f"  Degree Centrality:         {np.mean(deg_pcts):.1f} ± {np.std(deg_pcts):.1f}% severed, {np.mean(deg_edges):.1f} edges")
        print(f"  Greedy Disruption (Alg 1): {np.mean(grd_pcts):.1f} ± {np.std(grd_pcts):.1f}% severed, {np.mean(grd_edges):.1f} edges")
        print(f"  Significance (Alg 1 vs Deg): paired t = {t_stat:.3f}, p = {t_pval:.4e} | Wilcoxon W = {w_stat:.1f}, p = {w_pval:.4e}")

    # Save JSON results
    json_path = os.path.join(RESULTS_DIR, "defense_results.json")
    with open(json_path, "w") as f:
        json.dump(results, f, indent=2)
    print(f"\n[+] Saved empirical defense evaluation results to {json_path}")

    # ─────────────────────────────────────────────────────────────
    # Regenerate Figure 9.1 with REAL empirical data + labeled notional curve
    # ─────────────────────────────────────────────────────────────
    regenerate_figure(results)

def regenerate_figure(results):
    """Plot Figure 9.1 with 3 real empirical baseline curves + 1 labeled notional curve."""
    plt.style.use('default')
    plt.rcParams.update({
        'figure.facecolor': '#ffffff',
        'axes.facecolor': '#ffffff',
        'savefig.facecolor': '#ffffff',
        'text.color': '#111827',
        'axes.labelcolor': '#1f2937',
        'xtick.color': '#1f2937',
        'ytick.color': '#1f2937',
        'font.family': 'sans-serif',
        'font.size': 12.0,
        'axes.edgecolor': '#9ca3af',
        'axes.linewidth': 1.2,
    })

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16.0, 6.5), dpi=300)

    # ─────────────────────────────────────────────────────────────
    # Subplot (a): Two-Timescale Policy Learning Dynamics (Theoretical / Illustrative)
    # ─────────────────────────────────────────────────────────────
    episodes = np.arange(1, 251)
    np.random.seed(42)

    def_loss = 2.4 * np.exp(-episodes / 45) + 0.18 + 0.04 * np.random.randn(250) * np.exp(-episodes / 70)
    def_loss_smooth = np.convolve(def_loss, np.ones(5)/5, mode='same')
    def_loss_std = 0.12 * np.exp(-episodes / 60) + 0.015

    att_loss = 3.1 * np.exp(-episodes / 18) + 0.35 + 0.06 * np.random.randn(250) * np.exp(-episodes / 40)
    att_loss_smooth = np.convolve(att_loss, np.ones(5)/5, mode='same')
    att_loss_std = 0.15 * np.exp(-episodes / 30) + 0.02

    grad_norm = 1.8 * np.exp(-episodes / 55) + 0.03 + 0.02 * np.random.randn(250) * np.exp(-episodes / 80)
    grad_norm_smooth = np.convolve(grad_norm, np.ones(5)/5, mode='same')

    ax1.plot(episodes, def_loss_smooth, color='#1d4ed8', linewidth=2.8,
             label=r'Defender Objective $\mathcal{L}_D(\theta)$ (Slow $\alpha_k$)')
    ax1.fill_between(episodes, def_loss_smooth - def_loss_std, def_loss_smooth + def_loss_std,
                     color='#3b82f6', alpha=0.22)

    ax1.plot(episodes, att_loss_smooth, color='#dc2626', linewidth=2.5, linestyle='--',
             label=r'Attacker Policy Loss $\mathcal{L}_A(\phi)$ (Fast $\eta_k$)')
    ax1.fill_between(episodes, att_loss_smooth - att_loss_std, att_loss_smooth + att_loss_std,
                     color='#ef4444', alpha=0.18)

    ax1.plot(episodes, grad_norm_smooth, color='#059669', linewidth=2.4, linestyle=':',
             label=r'Defender Gradient Norm $\|\nabla_\theta U_D\|$')

    ax1.set_title('(a) Two-Timescale Policy Dynamics (Notional Simulation)', fontsize=13.5, fontweight='bold', pad=15)
    ax1.set_xlabel('Training Episodes', fontsize=12.5, fontweight='bold', labelpad=9)
    ax1.set_ylabel('Objective / Loss Value', fontsize=12.5, fontweight='bold', labelpad=9)
    ax1.set_xlim(0, 250)
    ax1.set_ylim(-0.05, 3.55)
    ax1.tick_params(axis='both', which='major', labelsize=11.5)
    ax1.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
    ax1.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#d1d5db', fontsize=10.5)
    ax1.axvline(x=175, color='#4b5563', linestyle='-.', alpha=0.8, linewidth=1.5)
    ax1.text(178, 2.15, 'Asymptotic\nStationarity\n(Ep. > 175)',
             fontsize=10.5, fontweight='bold', color='#1f2937',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#f3f4f6', edgecolor='#9ca3af', lw=1.1))

    # ─────────────────────────────────────────────────────────────
    # Subplot (b): Real Empirical Baselines + Labeled Notional MARL Model
    # ─────────────────────────────────────────────────────────────
    budgets = results["budgets"]
    emp = results["empirical_metrics"]

    grd_means = [0.0] + [emp["greedy_capacity_disruption"][str(b)]["paths_severed_mean"] for b in budgets]
    grd_stds  = [0.0] + [emp["greedy_capacity_disruption"][str(b)]["paths_severed_std"] for b in budgets]
    deg_means = [0.0] + [emp["degree_centrality"][str(b)]["paths_severed_mean"] for b in budgets]
    deg_stds  = [0.0] + [emp["degree_centrality"][str(b)]["paths_severed_std"] for b in budgets]
    rnd_means = [0.0] + [emp["random_revocation"][str(b)]["paths_severed_mean"] for b in budgets]
    rnd_stds  = [0.0] + [emp["random_revocation"][str(b)]["paths_severed_std"] for b in budgets]

    x_b = [0] + budgets

    # Plot 1: Algorithm 1 (Real Empirical)
    ax2.plot(x_b, grd_means, marker='s', markersize=8.0, color='#059669', linewidth=2.8,
             label='Greedy Capacity-Disruption [Alg. 1] (Measured)')
    ax2.fill_between(x_b, np.array(grd_means) - np.array(grd_stds), np.array(grd_means) + np.array(grd_stds),
                     color='#10b981', alpha=0.20)

    # Plot 2: Degree Centrality (Real Empirical)
    ax2.plot(x_b, deg_means, marker='^', markersize=7.5, color='#d97706', linewidth=2.4, linestyle='-.',
             label='Degree-Centrality Revocation (Measured)')
    ax2.fill_between(x_b, np.array(deg_means) - np.array(deg_stds), np.array(deg_means) + np.array(deg_stds),
                     color='#f59e0b', alpha=0.15)

    # Plot 3: Random Revocation (Real Empirical)
    ax2.plot(x_b, rnd_means, marker='x', markersize=8.0, color='#6b7280', linewidth=2.2, linestyle=':',
             label='Uniform Random Revocation (Measured)')
    ax2.fill_between(x_b, np.array(rnd_means) - np.array(rnd_stds), np.array(rnd_means) + np.array(rnd_stds),
                     color='#9ca3af', alpha=0.15)

    # Plot 4: Stackelberg Co-Adaptive Policy (Clearly Labeled Notional / Theoretical)
    notional_marl = [0.0, 68.3, 96.2, 100.0, 100.0]
    ax2.plot(x_b, notional_marl, marker='o', markersize=8.0, color='#1d4ed8', linewidth=2.8, linestyle='--',
             label='Stackelberg Co-Adaptive Policy (Notional / Model)')

    ax2.set_title(r'(b) Path Neutralization vs. Disruption Budget $B_{\mathrm{ops}}$',
                  fontsize=13.5, fontweight='bold', pad=15)
    ax2.set_xlabel(r'Operational Disruption Budget $B_{\mathrm{ops}}$ (Revoked Edges)',
                   fontsize=12.5, fontweight='bold', labelpad=9)
    ax2.set_ylabel('Severed Forbidden Paths (%)', fontsize=12.5, fontweight='bold', labelpad=9)
    ax2.set_xlim(0, 25)
    ax2.set_ylim(-2, 108)
    ax2.tick_params(axis='both', which='major', labelsize=11.5)
    ax2.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
    ax2.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#d1d5db', fontsize=10.0)

    plt.tight_layout()

    # Save to both destinations
    targets = [
        os.path.join(RESULTS_DIR, "game_theoretic_convergence.png"),
        os.path.join(PAPER_FIG_DIR, "game_theoretic_convergence.png"),
    ]
    for p in targets:
        plt.savefig(p, dpi=300, bbox_inches='tight', facecolor='#ffffff')
        print(f"[+] Saved updated convergence plot to: {p}")
    plt.close()

if __name__ == "__main__":
    main()
