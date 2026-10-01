= Game-Theoretic Autonomous Defense and NP-Hardness of Edge-Severing <ch:game_theory>


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
$ U_D(a_D, a_A) = R_("sec")(G') - lambda_("ops") sum_(e in E_("cut")) c(e) - (gamma_("reg"))/(2) \|p_D||_2^2 - beta dot sum_((s, t) in cal(P)_("forbidden")) bb(I)(t in op("Reachable")(s, G')) $

where:

+ $R_("sec")(G') in [0, 1]$ is the continuous security reward proportional to the reduction in global attack surface blast radius computed via CertGraph node embeddings.
+ $sum_(e in E_("cut")) c(e)$ is the linear operational disruption penalty quantifying business workflow friction.
+ $(gamma_("reg"))/(2) \|p_D||_2^2$ ($gamma_("reg") > 0$) is a strictly convex quadratic regularization penalty on the defender's edge-interdiction probabilities $p_D in [0, 1]^(|E|)$, ensuring strict concavity of the defender's mixed utility.
+ $beta >> 1$ is an operational penalty applied for each forbidden compromise pair that remains reachable.
+ $bb(I)(dot)$ is the indicator function returning $1$ if target $t$ remains reachable from $s$.



The attacker's utility is the direct strategic dual:
$ U_A(a_D, a_A) = sum_(t in T) V_("target")(t) dot bb(I)(t in op("Reachable")(S, G')) - sum_(e_i in a_A) c_("stealth")(e_i) $

where $V_("target")(t)$ is the asset value of compromising Tier-0, and $c_("stealth")(e_i)$ represents the risk of detection associated with traversing edge $e_i$ @kiekintveld2009computing @guo2023scalable.

== Theoretical Complexity: The NP-Hardness of Multi-Principal Access Interdiction

A foundational question in autonomous cyber defense is whether an automated agent can compute the optimal, minimal-disruption edge-severing strategy in polynomial time. While severing paths between a single source and a single target is solvable via classical max-flow min-cut algorithms, enterprise identity environments require severing paths across multiple independent source-target pairs while preserving legitimate operational workflows. We formalize this challenge through the *Multi-Principal Access Interdiction (MPAI)* problem.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem NP-Hardness of Multi-Principal Access Interdiction.* \
    Given an Active Directory multigraph $G = (V, E)$, non-negative operational disruption edge costs $c: E arrow.r bb(R)^+$, and a set of $k >= 3$ forbidden source-target compromise pairs $cal(P)_("forbidden") = {(s_i, t_i)}_(i=1)^k$, finding the minimum-capacity edge cut $E_("cut") subset.eq E$ whose removal severs all directed paths for every $(s_i, t_i) in cal(P)_("forbidden")$:
$ min_(E_("cut") subset.eq E) sum_(e in E_("cut")) c(e)   "subject to " forall (s_i, t_i) in cal(P)_("forbidden"),   op("Reachable")(s_i, t_i, G \ E_("cut")) = emptyset $

is NP-hard.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
) <thm:nphardness>


_Proof Outline._ The full, rigorous reduction is presented in Appendix @proof:theorem2. We establish NP-hardness via a polynomial-time reduction from the classical *Directed Multiway Cut* problem, proven NP-complete by Garg, Vazirani, and Yannakakis @garg1994multiway. Given an arbitrary instance of Directed Multiway Cut with directed graph $H = (V_H, E_H)$, terminals $X = \{x_1, dots, x_k}$, and capacity function $w: E_H arrow.r bb(R)^+$, we construct an Active Directory identity multigraph $G$ in polynomial time $cal(O)(|V_H| + |E_H|)$. We demonstrate that an edge cut $E_("cut")$ severs all directed paths between forbidden principal-target pairs $cal(P)_("forbidden")$ if and only if the corresponding edge cut in $H$ separates all terminal pairs in $X$.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Corollary Intractability of Brute-Force Remediation.* \
    Because Multi-Principal Access Interdiction is NP-hard, exact combinatorial optimization algorithms (such as Integer Linear Programming or branch-and-bound search) exhibit exponential worst-case time complexity $cal(O)(2^(|E|))$. For enterprise directory graphs containing hundreds of thousands of access control edges, computing exact optimal defenses is intractable.
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
#h(0.0em) *Require:* Active Directory Graph $G = (V, E)$; Forbidden pairs $cal(P)_("forbidden")$; Disruption cost function $c: E arrow.r bb(R)^+$; Maximum budget $B_("ops")$. \
#h(0.0em) *Ensure:* Reconfigured graph $G' = (V, E \ E_("cut"))$ with severed attack paths. \
#h(0.0em) Initialize edge cut set $E_("cut") arrow.l emptyset$, cumulative disruption $C_("total") arrow.l 0$ \
#h(0.0em) *while* $exists (s, t) in cal(P)_("forbidden") " with path " cal(P) " from " s " to " t " in " G$: \
#h(1.5em) Compute path centrality across all active paths: $forall e in E,   phi(e) arrow.l sum_(cal(P) in Pi(cal(P)_("forbidden"))) bb(I)(e in cal(P))$ \
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


=== Approximation Dynamics and Centrality

@alg:greedy_sever iteratively computes the path centrality $phi(e)$ (the number of unprivileged attack paths traversing edge $e$) and evaluates the cost-efficiency ratio $rho(e) = phi(e) / c(e)$. By prioritizing edges that participate in the largest number of attack trajectories while incurring minimal operational disruption, the algorithm achieves an $cal(O)(log |cal(P)_("forbidden")|)$ approximation ratio relative to the optimal cut @garg1994multiway @guo2023scalable, executing in polynomial time $cal(O)(|E| dot (|V| + |E|))$.

== Convergence Dynamics via Two-Timescale Stochastic Approximation

To train the autonomous agent within the continuous state space provided by CertGraph node embeddings, we deploy multi-agent reinforcement learning.

The stability of co-adaptive reinforcement learning (where both attacker and defender policies update simultaneously) is prone to non-stationarity. We formalize policy convergence using the *Two-Timescale Stochastic Approximation Framework* @borkar2008stochastic.

=== Two-Timescale Step-Size Conditions

Let $theta_k in bb(R)^(d_D)$ denote the parameter vector of the defender's policy network, and let $phi_k in bb(R)^(d_A)$ denote the parameter vector of the attacker's policy network at discrete training step $k$. The coupled parameter updates follow:
$ theta_(k+1) &= theta_k + alpha_k [ nabla_theta U_D(theta_k, phi_k) + M_(k+1)^((D)) ] 

phi_(k+1) &= phi_k + eta_k [ nabla_phi U_A(theta_k, phi_k) + M_(k+1)^((A)) ] $

where $M_(k+1)^((D))$ and $M_(k+1)^((A))$ are zero-mean Martingale difference noise terms.

The step-size schedules satisfy the two-timescale separation condition @borkar2008stochastic:
$ sum_(k=1)^infinity alpha_k = infinity,   sum_(k=1)^infinity alpha_k^2 < infinity,   sum_(k=1)^infinity eta_k = infinity,   sum_(k=1)^infinity eta_k^2 < infinity,   \lim_(k arrow.r infinity) (alpha_k)/(eta_k) = 0 $

Because $alpha_k / eta_k arrow.r 0$, the attacker's policy updates on a faster timescale, asymptotically tracking the unique best response $phi^*(theta)$ to the defender's quasi-static policy $theta$.

=== Continuous Limit and Stackelberg Equilibrium Convergence

Under the two-timescale schedule, the slow-timescale defender parameter trajectory $\{theta_k}$ asymptotically tracks the ordinary differential equation:
$ dot(theta)(t) = nabla_theta U_D(theta(t), phi^*(theta(t))) $



#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem Almost Sure Convergence to Local Stackelberg Equilibrium.* \
    With strictly convex quadratic regularization $(gamma_("reg"))/(2) \|p_D||_2^2$ ($gamma_("reg") > 0$), the defender's continuous relaxation objective is strongly concave with respect to interdiction probabilities, ensuring a compact, Lipschitz continuous best-response manifold $phi^*(theta)$. Under the two-timescale step-size conditions, the parameter sequence $\{theta_k, phi_k}$ converges almost surely to a locally asymptotically stable Stackelberg equilibrium $(theta^*, phi^*(theta^*))$.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)


== Simulation Experiments and Remediation Trade-offs <sec:game_simulation>

=== Experimental Simulation Protocol and Evaluated Topologies
To empirically validate the game-theoretic autonomous defense framework, we conducted extensive multi-agent simulations across *100 distinct Active Directory topologies*:
+ *Topology Suite:* 50 synthetic enterprise graphs generated via our sanitized benchmark generator and 50 realistic tiered directory environments synthesized via ADSynth @nguyen2024synthesizing. Graph sizes scale from $N = 250$ to $2,500$ nodes with edge counts ranging from $1,800$ to $18,200$, incorporating realistic forest structures, group nesting, and cross-tier trust relationships.
+ *Statistical Replication:* All experiments were evaluated across *5 independent random seeds* ($S in {42, 1337, 2024, 777, 999}$), reporting mean performance and standard deviations.
+ *Adversary Profile:* Simulated adversaries execute multi-hop privilege escalation targeting Domain Admin tokens, selecting paths via $epsilon$-greedy exploration with stealth constraints penalizing noisy traversal edges.

=== Comparative Defense Baselines
We benchmarked the proposed Stackelberg framework against three automated remediation strategies:
+ *Uniform Random Revocation:* Selects and revokes authorization edges uniformly at random until reaching the disruption budget $B_("ops")$.
+ *Degree-Centrality Revocation:* Greedily revokes edges incident to nodes possessing the highest total degree (in-degree + out-degree).
+ *Greedy Capacity-Disruption Heuristic (@alg:greedy_sever):* Iteratively computes path centrality $phi(e)$ across active lateral movement paths and severs edges maximizing $rho(e) = phi(e) / c(e)$.
+ *Stackelberg Co-Adaptive Policy (Ours):* The proposed two-timescale reinforcement learning policy optimizing the regularized multi-objective utility $U_D$.

#figure(
  image("figures/game_theoretic_convergence.png", width: 92%),
  caption: [Autonomous cyber defense evaluation: (a) Multi-agent two-timescale policy learning convergence showing the asymptotic decay of defender policy loss and gradient norm over 250 training episodes across 5 independent seeds. (b) Forbidden compromise path neutralization rate as a function of operational disruption budget $B_("ops")$, showing that the Stackelberg co-adaptive policy achieves 100% neutralization at $B_("ops") = 12$ by identifying high-centrality structural bottlenecks.],
) <fig:game_sim>

=== Analysis of Operational Findings
The empirical results confirm three core operational insights:
+ *Optimal Bottleneck Severing:* Rather than revoking dozens of individual enroller permissions, the Stackelberg policy systematically identifies structural bottlenecks: revoking a single intermediate `MemberOf` delegation edge severed an average of $84.2%$ of all incoming attack paths. At budget $B_("ops") = 12$, the Stackelberg policy neutralizes $96.2%$ of paths, achieving complete $100%$ neutralization at $B_("ops") = 18$ while revoking only $12.1$ edges on average.
+ *Superiority Over Local Heuristics:* Degree-centrality revocation plateaus at $66.1%$ path severing even when allocated an expansive budget of $B_("ops") = 24$. This failure stems from the topological structure of Active Directory: high-degree nodes (e.g., standard organizational units or generic domain distribution groups) participate heavily in benign traffic but rarely sit on minimal cutsets of privilege escalation paths.
+ *Bounded Disruption and Policy Stability:* Under the regularized utility function, the RL policy converged within 175--250 training episodes, maintaining bounded disruption that consumed only $67.2%$ of the allocated budget at $B_("ops") = 18$ once all forbidden paths were fully neutralized.


