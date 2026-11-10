def metadata_preserving_adaptive(G, forbidden_pairs, budget):
    """
    Policy 4 (Co-Adaptive Stackelberg Policy / Backward Causal DAG Minimal-Cut):
    Optimized via reverse BFS (nx.ancestors) per unique target.
    At each step of the bi-level leader-follower game, computes the follower's (attacker's)
    active best-response reachability subgraph G_BR subseteq G_curr from low-privilege
    entry nodes S to high-value targets T, evaluates candidate chokepoint cut edges via
    exact total-pair disconnection gain Delta Severed(e) / c(e) with sink-adjacent chokepoint
    weighting, and dynamically severs the optimal bottleneck edges within budget B_ops.
    """
    G_curr = G.copy()
    E_cut = []
    C_total = 0.0

    while True:
        unique_targets = set(t for _, t in forbidden_pairs)
        target_ancestors = {t: nx.ancestors(G_curr, t) for t in unique_targets}
        active_pairs = [(u, t) for (u, t) in forbidden_pairs if u in target_ancestors[t]]
        if not active_pairs:
            break

        # Compute active edges across all follower best-response shortest paths
        active_edges = {}
        for u, t in active_pairs:
            try:
                p = nx.shortest_path(G_curr, u, t)
                for i in range(len(p) - 1):
                    e = (p[i], p[i + 1])
                    active_edges[e] = active_edges.get(e, 0) + 1
            except nx.NetworkXNoPath:
                pass

        if not active_edges:
            break

        best_e = None
        best_gain = -1.0
        cur_active = len(active_pairs)

        for (u, v), phi in active_edges.items():
            if not G_curr[u][v].get("blockable", True):
                continue
            c = G_curr[u][v].get("cost", 1.0)
            if C_total + c > budget:
                continue

            # Evaluate exact marginal disconnection on residual graph via reverse BFS
            edge_attributes = dict(G_curr[u][v])
            G_curr.remove_edge(u, v)
            unique_tg = set(t for _, t in active_pairs)
            tg_anc = {t: nx.ancestors(G_curr, t) for t in unique_tg}
            rem = sum(1 for (src, tgt) in active_pairs if src in tg_anc[tgt])
            G_curr.add_edge(u, v, **edge_attributes)
            delta = cur_active - rem

            rel = G_curr[u][v].get("rel", "")
            is_choke = 2.0 if (rel in ("enrolls", "write_dacl", "escalates_to") or v.startswith("Template") or v.startswith("Group_0")) else 1.0
            gain = (delta * 10.0 * is_choke + phi * is_choke) / c
            if gain > best_gain:
                best_gain = gain
                best_e = (u, v)

        if best_e is None:
            # Fallback to candidate active edge fitting within budget
            for (u, v), phi in sorted(active_edges.items(), key=lambda x: x[1] / G_curr[x[0][0]][x[0][1]].get("cost", 1.0), reverse=True):
                if not G_curr[u][v].get("blockable", True):
                    continue
                c = G_curr[u][v].get("cost", 1.0)
                if C_total + c <= budget:
                    best_e = (u, v)
                    break

        if best_e is None:
            break

        c_best = G_curr[best_e[0]][best_e[1]].get("cost", 1.0)
        G_curr.remove_edge(best_e[0], best_e[1])
        E_cut.append(best_e)
        C_total += c_best

    pct = evaluate_severed(G_curr, forbidden_pairs)
    compliance = (C_total / budget) * 100.0 if budget > 0 else 100.0
    return {'pct': pct, 'cut': E_cut, 'cost': C_total, 'compliance': compliance}
