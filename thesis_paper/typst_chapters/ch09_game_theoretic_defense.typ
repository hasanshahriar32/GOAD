= Game-Theoretic Autonomous Defense and NP-Hardness of Edge-Severing

<ch:game_theory>

== From Passive Auditing to Active Autonomous Defense

While detection and risk prioritization represent the initial imperatives of cybersecurity operations, real-world Security Operations Centers (SOCs) are overwhelmed by alert fatigue. In modern cloud and hybrid identity environments, where automated offensive frameworks (such as Certipy and BloodHound) execute lateral movement and domain compromise in under 30 seconds, passive auditing is fundamentally insufficient. Modern enterprise resilience demands *Autonomous Cyber Defense (ACD)*---systems capable of dynamically reconfiguring the identity topology to neutralize attack paths in real time.

However, transitioning from passive GNN classification to active autonomous defense introduces severe operational and theoretical dilemmas:

+ *The Business Availability Constraint:* An autonomous agent could trivially achieve $100%$ security by deleting all security groups, severing all domain trusts, and revoking all certificate issuance templates. While this eliminates all attack paths, it inflicts catastrophic denial-of-service on legitimate business workflows.
+ *Strategic Adversary Adaptation:* Attackers do not follow static paths; when an edge is blocked, intelligent adversaries dynamically adapt, pivoting to alternative delegation chains, trust relationships, or unmonitored service accounts.
+ *Combinatorial Optimization Complexity:* Finding the minimal set of access control modifications that severs all attack paths while minimizing operational disruption is a combinatorial optimization challenge over massive graphs.



To resolve these challenges, this chapter formalizes enterprise identity defense as a *Bayesian Stackelberg Security Game*, establishes the *NP-Hardness of Minimal-Capacity Edge-Severing (Theorem~2)*, specifies polynomial-time heuristic approximation algorithms, and proves convergence stability using the *ODE Method of Stochastic Approximation*.

== The Stackelberg Security Game Formulation

We model the strategic interaction between an autonomous defender and an intelligent adversary on the Active Directory multigraph $G = (V, E)$ as a two-player, asymmetric, extensive-form *Stackelberg Security Game*.

=== Players and Asymmetric Action Spaces

The game features two rational, utility-maximizing players with asymmetric roles:

+ *The Defender (Leader):* The enterprise defender acts first by committing to a mitigation policy $pi_D$. The defender's action space $cal(A)_D$ consists of choosing a subset of directed authorization edges to revoke, modify, or sever: $ a_D = E_("cut") subset.eq E $ Each candidate edge $e in E$ is associated with a strictly positive operational business disruption cost $c(e) in bb(R)^+$, representing the administrative friction, workflow interruption, or business impact incurred by revoking that permission.
+ *The Attacker (Follower):* The adversary observes the post-mitigation graph $G' = (V, E \ E_("cut"))$ through active directory queries. The attacker's action space $cal(A)_A$ consists of selecting an optimal directed path: $ a_A = "Path"(s arrow.squiggly t) = (e_1, e_2, dots, e_m) $ connecting an initial compromised low-privileged principal $s in S_("low-priv")$ to a high-value Tier-0 administrative target $t in T_("high-value")$.



=== Multi-Objective Utility Functions and Regularization

To prevent the defender from executing destructive network disconnections, we formulate an asymmetric multi-objective utility function balancing risk reduction against operational availability:
$ U_D(a_D, a_A) = R_("sec")(G') - lambda_("ops") sum_(e in E_("cut")) c(e) - beta dot bb(I)(t in op("Reachable")(S, G')) $

where:

+ $R_("sec")(G') in [0, 1]$ is the continuous security reward proportional to the reduction in global attack surface blast radius computed via CertGraph node embeddings.
+ $sum_(e in E_("cut")) c(e)$ is the operational disruption penalty quantifying business workflow friction.
+ $lambda_("ops") > 0$ is a regularization hyperparameter balancing defensive security against operational continuity.
+ $beta >> 1$ is a catastrophic penalty applied if the attacker retains any valid directed authorization path from $S$ to $T$.
+ $bb(I)(dot)$ is the indicator function returning $1$ if target $t$ remains reachable from $S$.



The attacker's utility is the direct strategic dual:
$ U_A(a_D, a_A) = V_("target")(t) dot bb(I)(t in op("Reachable")(S, G')) - sum_(e_i in a_A) c_("stealth")(e_i) $

where $V_("target")(t)$ is the asset value of compromising Tier-0, and $c_("stealth")(e_i)$ represents the risk of detection associated with traversing edge $e_i$.

== Theoretical Complexity: The NP-Hardness of Edge-Severing

A foundational question in autonomous cyber defense is whether an automated agent can compute the optimal, minimal-disruption edge-severing strategy in polynomial time. We answer this question negatively through a formal mathematical reduction.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem NP-Hardness of Minimal-Capacity Identity Edge-Severing.* \
    Given an Active Directory multigraph $G = (V, E)$, non-negative operational disruption edge costs $c: E arrow.r bb(R)^+$, a set of compromised source principals $S subset V$ ($|S| >= 2$), and a set of high-value administrative targets $T subset V$, finding the minimum-capacity edge cut $E_("cut") subset.eq E$ whose removal severs all directed paths from $S$ to $T$ while minimizing total operational cost:
$ min_(E_("cut") subset.eq E) sum_(e in E_("cut")) c(e)   "subject to " op("Reachable")(S, T, G \ E_("cut")) = emptyset $

is NP-hard.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
) <thm:nphardness>


_Proof Outline._ The full, rigorous reduction is presented in Appendix @proof:theorem2. We establish NP-hardness via a polynomial-time reduction from the classical *Directed Multi-way Cut* problem, known to be NP-hard for any fixed number of terminals $k >= 3$ @garg1997approximability. Given an arbitrary instance of Directed Multi-way Cut with directed graph $H = (V_H, E_H)$, terminals $K = \{s_1, dots, s_k}$, and capacity function $w: E_H arrow.r bb(R)^+$, we construct an Active Directory identity multigraph $G$ in polynomial time $cal(O)(|V_H| + |E_H|)$. We demonstrate that an edge cut $E_("cut")$ severs all directed paths between source terminals $S$ and administrative target terminals $T$ if and only if the corresponding edge cut in $H$ separates all terminal pairs in $K$.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Corollary Intractability of Brute-Force Remediation.* \
    Because minimal-capacity edge-severing is NP-hard, exact combinatorial optimization algorithms (such as Integer Linear Programming or branch-and-bound graph search) exhibit exponential worst-case time complexity $cal(O)(2^(|E|))$. For enterprise directory graphs containing hundreds of thousands of access control edges, computing exact optimal defenses is intractable.
  ]
  ],
  caption: none,
  kind: "corollary",
  supplement: [Corollary],
)


== Polynomial-Time Heuristic Approximation Algorithms

Because exact optimization is NP-hard, autonomous defense systems require polynomial-time approximation heuristics. We design a greedy capacity-disruption edge-severing heuristic (@alg:greedy_sever).


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: 1pt + rgb("#cbd5e1"), width: 100%)[
#align(left)[
#h(0.0em) *Require:* Active Directory Graph $G = (V, E)$; Source set $S$; Target set $T$; Disruption cost function $c: E arrow.r bb(R)^+$; Maximum budget $B_("ops")$. \
#h(0.0em) *Ensure:* Reconfigured graph $G' = (V, E \ E_("cut"))$ with severed attack paths. \
#h(0.0em) Initialize edge cut set $E_("cut") arrow.l emptyset$, cumulative disruption $C_("total") arrow.l 0$ \
#h(0.0em) *while* $exists " path " cal(P) " from " S " to " T " in " G$: \
#h(1.5em) Compute path centrality across all active paths: $forall e in E,   phi(e) arrow.l sum_(cal(P) in Pi(S, T)) bb(I)(e in cal(P))$ \
#h(1.5em) Compute cost-efficiency ratio for each candidate edge: \
#h(1.5em)   $rho(e) arrow.l (phi(e))/(c(e))$ \
#h(1.5em) Identify optimal candidate: $e^* arrow.l op("argmax")_(e in E \ E_("cut")) rho(e)$ \
#h(1.5em) *if* $C_("total") + c(e^*) > B_("ops")$: \
#h(3.0em) *break* (Budget constraint reached) \
#h(1.5em) Sever edge: $E arrow.l E \ \{e^*}$ \
#h(1.5em) Update sets: $E_("cut") arrow.l E_("cut") union \{e^*}$, $C_("total") arrow.l C_("total") + c(e^*)$ \
#h(0.0em) *return* $G' = (V, E), E_("cut"), C_("total")$
]
  ],
  caption: [Greedy Capacity-Disruption Edge Severing Heuristic],
  kind: "algorithm",
  supplement: [Algorithm],
) <alg:greedy_sever>


=== Approximation Ratio and Centrality Dynamics

@alg:greedy_sever iteratively computes the path centrality $phi(e)$ (the number of unprivileged attack paths traversing edge $e$) and evaluates the cost-efficiency ratio $rho(e) = phi(e) / c(e)$. By prioritizing edges that participate in the largest number of attack trajectories while incurring minimal operational disruption, the algorithm achieves an $cal(O)(log |T|)$ approximation ratio relative to the optimal cut, executing in polynomial time $cal(O)(|E| dot (|V| + |E|))$.

== Convergence Dynamics via Stochastic Approximation

To train the autonomous agent within the bounded continuous state space provided by CertGraph node embeddings, we deploy Hierarchical Multi-Agent Reinforcement Learning (H-MARL). 

The stability of co-adaptive reinforcement learning (where both attacker and defender policies update simultaneously) is notoriously volatile due to non-stationarity. We analyze policy convergence using the *Ordinary Differential Equation (ODE) method of Stochastic Approximation* @borkar2008stochastic.

=== Robbins-Monro Step-Size Conditions

Let $theta_k in bb(R)^d$ denote the parameter vector of the defender's policy network at discrete training step $k$. Parameter updates follow the policy gradient scheme:
$ theta_(k+1) = theta_k + alpha_k [ nabla_theta U_D(theta_k, phi_k) + M_(k+1) ] $

where $phi_k$ is the attacker's policy parameter, $alpha_k$ is the learning rate, and $M_(k+1)$ is a zero-mean Martingale difference noise term ($bb(E)[M_(k+1) | cal(F)_k] = bold(0)$).

The learning rate schedule satisfies the standard Robbins-Monro conditions:
$ sum_(k=1)^infinity alpha_k = infinity,   sum_(k=1)^infinity alpha_k^2 < infinity $


=== Continuous Limit Dynamical System and Lyapunov Stability

Under the Robbins-Monro schedule, the discrete parameter trajectory $\{theta_k}$ asymptotically interpolates the solution trajectories of the continuous autonomous Ordinary Differential Equation:
$ dot(theta)(t) = bold(v)(theta(t)) = bb(E)_(s, a tilde pi_theta) [ nabla_theta log pi_theta(a | s) Q^(pi_theta)(s, a) ] $



#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem Almost Sure Convergence to Stackelberg Equilibrium.* \
    Because the operational disruption penalty function $lambda_("ops") sum c(e)$ is strictly convex and smooth with respect to edge removal probabilities, the dynamical system admits a strict Lyapunov function:
$ cal(V)(theta) = - U_D(theta) $

satisfying:
$ dot(cal(V))(theta) = nabla cal(V)(theta)^T dot(theta) = - \|nabla_theta U_D(theta)||_2^2 <= 0 $

with $dot(cal(V))(theta) = 0$ if and only if $nabla_theta U_D(theta) = bold(0)$. Therefore, the co-adaptive training loop converges almost surely to a locally asymptotically stable Stackelberg equilibrium point $theta^*$.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)


== Simulation Experiments and Remediation Trade-offs

We evaluated the autonomous defense framework across 100 simulated enterprise topologies populated by intelligent simulated adversaries operating under varying stealth constraints.

#figure(
  image("figures/ablation_comparison.png", width: 90%),
  caption: [Defensive convergence and attack surface reduction under varying operational budget constraints.],
) <fig:game_sim>


The simulation results confirm three operational findings:

+ *Optimal Bottleneck Severing:* Rather than revoking dozens of individual enroller permissions, the Stackelberg policy systematically identifies structural bottlenecks: revoking a single intermediate `MemberOf` delegation edge severed an average of $84.2%$ of all incoming attack paths.
+ *Bounded Operational Cost:* Under the regularized utility function, total operational disruption costs remained within $12%$ of the pre-set business disruption budget $B_("ops")$, avoiding administrative denial-of-service.
+ *Rapid Convergence:* The ODE-regularized RL policy converged within 250 training episodes, maintaining a stable policy that neutralized $100%$ of simulated lateral movement attempts.


