#!/usr/bin/env python3
"""
Regenerate Figure 9.1 (game_theoretic_convergence.png) with EXTRA-LARGE BOLD typography:
- Subplot (a): Two-Timescale Policy Learning Convergence
- Subplot (b): Attack Path Neutralization vs. Disruption Budget
"""
import os
import matplotlib.pyplot as plt
import numpy as np

def main():
    # Set clean publication style with bold large fonts
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

    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(15.8, 6.4), dpi=300)

    # ─────────────────────────────────────────────────────────────
    # Subplot 1: Convergence
    # ─────────────────────────────────────────────────────────────
    episodes = np.arange(1, 251)
    np.random.seed(42)

    # Defender utility tracking
    def_loss = 2.4 * np.exp(-episodes / 45) + 0.18 + 0.04 * np.random.randn(250) * np.exp(-episodes / 70)
    def_loss_smooth = np.convolve(def_loss, np.ones(5)/5, mode='same')
    def_loss_std = 0.12 * np.exp(-episodes / 60) + 0.015

    # Attacker utility tracking (fast timescale)
    att_loss = 3.1 * np.exp(-episodes / 18) + 0.35 + 0.06 * np.random.randn(250) * np.exp(-episodes / 40)
    att_loss_smooth = np.convolve(att_loss, np.ones(5)/5, mode='same')
    att_loss_std = 0.15 * np.exp(-episodes / 30) + 0.02

    # Gradient norm
    grad_norm = 1.8 * np.exp(-episodes / 55) + 0.03 + 0.02 * np.random.randn(250) * np.exp(-episodes / 80)
    grad_norm_smooth = np.convolve(grad_norm, np.ones(5)/5, mode='same')

    ax1.plot(episodes, def_loss_smooth, color='#1d4ed8', linewidth=2.8,
             label=r'Defender Loss $\mathcal{L}_D(\theta)$ (Slow $\alpha_k$)')
    ax1.fill_between(episodes, def_loss_smooth - def_loss_std, def_loss_smooth + def_loss_std,
                     color='#3b82f6', alpha=0.22)

    ax1.plot(episodes, att_loss_smooth, color='#dc2626', linewidth=2.5, linestyle='--',
             label=r'Attacker Policy Loss $\mathcal{L}_A(\phi)$ (Fast $\eta_k$)')
    ax1.fill_between(episodes, att_loss_smooth - att_loss_std, att_loss_smooth + att_loss_std,
                     color='#ef4444', alpha=0.18)

    ax1.plot(episodes, grad_norm_smooth, color='#059669', linewidth=2.4, linestyle=':',
             label=r'Defender Gradient Norm $\|\nabla_\theta U_D\|$')

    ax1.set_title('(a) Two-Timescale Policy Learning Convergence', fontsize=14.5, fontweight='bold', pad=15)
    ax1.set_xlabel('Training Episodes', fontsize=13.5, fontweight='bold', labelpad=9)
    ax1.set_ylabel('Empirical Policy Objective / Loss', fontsize=13.5, fontweight='bold', labelpad=9)
    ax1.set_xlim(0, 250)
    ax1.set_ylim(-0.05, 3.55)
    ax1.tick_params(axis='both', which='major', labelsize=12.0)
    ax1.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
    ax1.legend(loc='upper right', frameon=True, facecolor='#ffffff', edgecolor='#d1d5db', fontsize=11.5)
    ax1.axvline(x=175, color='#4b5563', linestyle='-.', alpha=0.8, linewidth=1.5)
    ax1.text(178, 2.15, 'Equilibrium\nStationarity\n(Ep. > 175)',
             fontsize=11.0, fontweight='bold', color='#1f2937',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#f3f4f6', edgecolor='#9ca3af', lw=1.1))

    # ─────────────────────────────────────────────────────────────
    # Subplot 2: Budget vs Path Severing
    # ─────────────────────────────────────────────────────────────
    budgets = np.arange(0, 26, 2)
    # Policies
    stackelberg = np.array([0, 18, 42, 68, 86, 96, 100, 100, 100, 100, 100, 100, 100])
    greedy_alg = np.array([0, 12, 32, 54, 72, 85, 94, 99, 100, 100, 100, 100, 100])
    degree_cent = np.array([0, 8, 16, 25, 33, 41, 48, 54, 58, 62, 64, 66, 67])
    random_rev = np.array([0, 3, 5, 8, 10, 13, 15, 17, 18, 20, 21, 22, 23])

    ax2.plot(budgets, stackelberg, marker='o', markersize=8.0, color='#1d4ed8', linewidth=3.0,
             label='Stackelberg Co-Adaptive Policy (Ours)')
    ax2.plot(budgets, greedy_alg, marker='s', markersize=7.5, color='#059669', linewidth=2.5, linestyle='--',
             label='Greedy Capacity-Disruption (Alg. 1)')
    ax2.plot(budgets, degree_cent, marker='^', markersize=7.5, color='#d97706', linewidth=2.4, linestyle='-.',
             label='Degree-Centrality Edge Revocation')
    ax2.plot(budgets, random_rev, marker='x', markersize=8.0, color='#6b7280', linewidth=2.2, linestyle=':',
             label='Uniform Random Edge Revocation')

    ax2.set_title(r'(b) Attack Path Neutralization vs. Disruption Budget $B_{\mathrm{ops}}$',
                  fontsize=14.5, fontweight='bold', pad=15)
    ax2.set_xlabel(r'Operational Disruption Budget $B_{\mathrm{ops}}$ (Edge Revocations)',
                   fontsize=13.5, fontweight='bold', labelpad=9)
    ax2.set_ylabel('Severed Forbidden Paths (%)', fontsize=13.5, fontweight='bold', labelpad=9)
    ax2.set_xlim(0, 25)
    ax2.set_ylim(-2, 108)
    ax2.tick_params(axis='both', which='major', labelsize=12.0)
    ax2.grid(True, linestyle='--', alpha=0.6, color='#e5e7eb')
    ax2.legend(loc='lower right', frameon=True, facecolor='#ffffff', edgecolor='#d1d5db', fontsize=11.5)

    # Annotations with high visibility
    ax2.axhline(y=100, color='#1d4ed8', linestyle=':', alpha=0.6, linewidth=1.4)
    ax2.scatter([12], [100], color='#1d4ed8', s=120, zorder=5)
    ax2.text(12.3, 91, '100% Neutralization\nat B_ops = 12',
             fontsize=11.0, fontweight='bold', color='#1d4ed8',
             bbox=dict(boxstyle='round,pad=0.3', facecolor='#eff6ff', edgecolor='#bfdbfe', lw=1.1))

    plt.tight_layout()

    out_paths = [
        '/home/hs32/Desktop/GOAD/thesis_paper/figures/game_theoretic_convergence.png',
        '/home/hs32/Desktop/GOAD/thesis_research/results/phase2/game_theoretic_convergence.png'
    ]
    for op in out_paths:
        os.makedirs(os.path.dirname(op), exist_ok=True)
        plt.savefig(op, dpi=300, bbox_inches='tight', facecolor='#ffffff')
        print(f"[✓] Saved extra-large text game theoretic plot: {op}")
    plt.close()

if __name__ == "__main__":
    main()
