= Formal Mathematical Proofs <app:proofs>

== Proof of Theorem 1: Representation Collapse in Asymmetric Relational Message Passing <proof:theorem1>

#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem Representation Collapse in Directed Heterogeneous Convolutions.* \
    Let $G = (V, E, cal(T)_V, cal(T)_E)$ be a directed heterogeneous graph where $tau: V arrow.r cal(T)_V$ assigns node types. Let $cal(T)_("source") subset cal(T)_V$ denote the set of source-only node types satisfying:
$ forall v in V " such that " tau(v) in cal(T)_("source"),   cal(N)_("in")(v) = \{u in V | (u, v) in E} = emptyset $

Consider an $L$-layer heterogeneous message-passing neural network where layer $l in {1, dots, L}$ computes representations via relation-specific neighborhood aggregation without residual skip-connections:
$ h_v^((l)) = sigma ( sum_(r in cal(R)_("in")(tau(v))) plus.circle.big_(u in cal(N)_r(v)) alpha_(v u)^((l)) W_r^((l)) h_u^((l-1)) ) $

where $cal(R)_("in")(tau(v))$ is the set of relation types terminating at node type $tau(v)$, $plus.circle.big$ is a permutation-invariant aggregation operator with the empty-set identity $plus.circle.big(emptyset) = bold(0)$, $alpha_(v u)^((l))$ are attention weights, and $sigma$ is an activation function satisfying $sigma(bold(0)) = bold(0)$ (e.g., ReLU, LeakyReLU, ELU, Tanh).

Then:

+ For any source node $v in V$ with $tau(v) in cal(T)_("source")$ and any layer $l >= 1$: $ h_v^((l)) = bold(0) $
+ The gradient of the loss $cal(L)$ with respect to the input features $x_v = h_v^((0))$ vanishes identically: $ (diff cal(L))/(diff x_v) = bold(0) $
+ If additive residual skip connections of the form: $ tilde(h)_v^((l)) = h_v^((l)) + W_("skip")^((l)) tilde(h)_v^((l-1)) $ are introduced, where $W_("skip")^((l))$ is a parameterized projection matrix, then $h_v^((l))$ retains an injective transformation of the input features: $ tilde(h)_v^((l)) = ( product_(k=1)^l W_("skip")^((k)) ) x_v != bold(0) $ and the gradient $(diff cal(L))/(diff x_v)$ remains non-zero.


  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)



_Proof._ We prove each statement sequentially.

*Part 1: Collapse of Hidden Representations.*
Let $v in V$ be a node belonging to a source-only type $tau(v) in cal(T)_("source")$. By definition of source-only types in the directed graph $G$, the in-degree of $v$ is zero:
$ d_("in")(v) = |cal(N)_("in")(v)| = 0 $

Consequently, for every relation type $r = (s, "rel", tau(v)) in cal(T)_E$, the relation-specific incoming neighborhood is empty:
$ cal(N)_r(v) = \{u in V | (u, v) in E_r} = emptyset $

Now consider the layer update formula for $h_v^((1))$:
$ h_v^((1)) &= sigma ( sum_(r in cal(R)_("in")(tau(v))) plus.circle.big_(u in emptyset) alpha_(v u)^((1)) W_r^((1)) h_u^((0)) ) $

By the standard definition of graph aggregation operators (Sum, Mean, Max in PyTorch Geometric and DGL), aggregation over an empty set returns the zero vector identity:
$ plus.circle.big_(u in emptyset) (dot) = bold(0) in bb(R)^(d_("out")) $

Therefore, the finite sum of empty aggregations across all incoming relations is:
$ sum_(r in cal(R)_("in")(tau(v))) bold(0) = bold(0) $

Applying the activation function $sigma$ where $sigma(bold(0)) = bold(0)$:
$ h_v^((1)) = sigma(bold(0)) = bold(0) $

By mathematical induction, assume $h_v^((l-1)) = bold(0)$ for $l >= 2$. At layer $l$, the incoming neighborhood remains $cal(N)_r(v) = emptyset$. Hence:
$ h_v^((l)) = sigma ( sum_r plus.circle.big_(u in emptyset) (dot) ) = sigma(bold(0)) = bold(0) $

This establishes Part 1: every source-only node's embedding collapses to the zero vector at all hidden layers $l >= 1$.

*Part 2: Gradient Vanishing.*
Consider the scalar training loss $cal(L)(Y, hat(Y))$. By the multivariate chain rule, the gradient of $cal(L)$ with respect to the input feature vector $x_v = h_v^((0))$ is:
$ (diff cal(L))/(diff x_v) = sum_(w in V) (diff cal(L))/(diff h_w^((1))) (diff h_w^((1)))/(diff h_v^((0))) $

For any target node $w != v$, $h_w^((1))$ depends on $h_v^((0))$ if and only if $v in cal(N)_("in")(w)$. However, for $w = v$, we have established that $h_v^((1)) = bold(0)$ independently of $h_v^((0))$ because the mapping is constant zero. Therefore:
$ (diff h_v^((1)))/(diff h_v^((0))) = bold(0) in bb(R)^(d_1 times d_0) $

Furthermore, if a downstream node $w$ aggregates messages from $v$, the message is weighted by $W_r^((1)) h_v^((0))$. But in a directed graph where $v$ never updates its state, for any layer $l >= 2$:
$ (diff h_w^((l)))/(diff h_v^((l-1))) = (diff h_w^((l)))/(diff bold(0)) $

If the prediction head is placed directly on $v$ or on paths where $v$'s intermediate features are discarded, all sensitivity to $x_v$ is lost. Specifically, if $v$'s own identity or credentials determine path exploitability, the model cannot distinguish between a privileged administrative user and an unprivileged guest user because $h_("admin")^((l)) = h_("guest")^((l)) = bold(0)$.

*Part 3: Restoration via Residual Skip Connections.*
Now consider the update with additive residual skip connections:
$ tilde(h)_v^((l)) = h_v^((l)) + W_("skip")^((l)) tilde(h)_v^((l-1)) $

Substituting $h_v^((l)) = bold(0)$ for $v in cal(T)_("source")$:
$ tilde(h)_v^((1)) &= bold(0) + W_("skip")^((1)) x_v = W_("skip")^((1)) x_v 

tilde(h)_v^((2)) &= bold(0) + W_("skip")^((2)) tilde(h)_v^((1)) = W_("skip")^((2)) W_("skip")^((1)) x_v $

By induction, at layer $L$:
$ tilde(h)_v^((L)) = ( product_(k=1)^L W_("skip")^((k)) ) x_v $

Assuming full-rank initialization of $W_("skip")^((k))$, the product matrix $cal(M) = product_(k=1)^L W_("skip")^((k))$ satisfies $op("rank")(cal(M)) = min(d_L, d_0)$. Thus, $tilde(h)_v^((L)) != bold(0)$ for any non-zero input $x_v != bold(0)$. 

The gradient with respect to $x_v$ through the skip path is:
$ (diff tilde(h)_v^((L)))/(diff x_v) = product_(k=1)^L W_("skip")^((k)) != bold(0) $

which preserves gradient backpropagation throughout training. #h(1fr) $square$



#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Corollary Necessity in Active Directory Graphs.* \
    In Active Directory graphs $G_("AD")$, node types $"User"$ and $"Computer"$ frequently act as pure sources in the authorization subgraph (possessing outgoing edges such as $"MemberOf"$, $"Enroll"$, $"GenericAll"$, but zero incoming administrative delegation edges). Therefore, any GNN architecture omitting residual skip connections is mathematically guaranteed to destroy the identity feature embeddings of all low-privileged and administrative user accounts after layer 1.
  ]
  ],
  caption: none,
  kind: "corollary",
  supplement: [Corollary],
)

#pagebreak()

== Proof of Theorem 2: Computational Complexity of Optimal Active Directory Edge Blocking <proof:theorem2>

#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem NP-Hardness of Optimal Attack Path Severing.* \
    Let $G = (V, E)$ be a directed graph representing an Active Directory domain, where $V$ represents security principals and assets, and $E$ represents authorization and administrative edges. Let $c: E arrow.r bb(R)^+$ assign operational disruption costs (capacities) to edges, representing the cost of revoking an access right. 

Let $S subset V$ denote the set of compromised or low-privileged attacker source identities ($|S| >= 2$), and let $T subset V$ denote the set of high-value administrative terminal targets (e.g., Domain Admins, Enterprise Admins, Domain Controllers).

The *Active Directory Edge-Severing Defense Problem (ADESDP)* asks: given an operational disruption budget $K in bb(R)^+$, does there exist a subset of edges $E_("cut") subset.eq E$ such that:

+ Total operational cost is bounded: $ sum_(e in E_("cut")) c(e) <= K $
+ Every directed path from every source $s in S$ to every target $t in T$ is severed: $ forall s in S, forall t in T, "Path"(s arrow.squiggly t) " does not exist in " G' = (V, E \ E_("cut")) $


The ADESDP is NP-complete. Consequently, finding the optimal edge-severing defense strategy that minimizes operational business impact is NP-hard.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)



_Proof._ We prove NP-completeness by showing that:

+ $"ADESDP" in "NP"$, and
+ The known NP-complete problem *Directed Multi-way Cut* polynomially reduces to ADESDP: $ "Directed Multi-way Cut" <=_p "ADESDP" $



*Part 1: Membership in NP.*
Given a candidate edge set $E_("cut") subset.eq E$:

+ We compute the sum of edge costs $sum_(e in E_("cut")) c(e)$ in $O(|E_("cut")|)$ time and verify if it is $<= K$.
+ We construct the residual graph $G' = (V, E \ E_("cut"))$ in $O(|V| + |E|)$ time.
+ For each pair $(s, t) in S times T$, we run Breadth-First Search (BFS) or Depth-First Search (DFS) on $G'$ to verify that $t$ is unreachable from $s$. This requires $O(|S| dot (|V| + |E|))$ time.


Because all verification steps complete in deterministic polynomial time with respect to the input size, $"ADESDP" in "NP"$.

*Part 2: Polynomial-Time Reduction from Directed Multi-way Cut.*
Recall the definition of the *Directed Multi-way Cut* problem, proven NP-complete by Dahlhaus et al. @dahlstrm2000multiway:
\begin{quote}
*Directed Multi-way Cut:* Given a directed graph $H = (V_H, E_H)$ with edge weights $w: E_H arrow.r bb(R)^+$, a subset of terminal vertices $X = \{x_1, x_2, dots, x_k} subset.eq V_H$ ($k >= 3$), and a cost threshold $W$, does there exist an edge subset $C subset.eq E_H$ with $sum_(e in C) w(e) <= W$ such that no directed path connects any terminal $x_i$ to any other terminal $x_j$ ($i != j$) in $H' = (V_H, E_H \ C)$?
\end{quote}

Given an arbitrary instance $angle.l H, w, X, W angle.r$ of the Directed Multi-way Cut problem with $k >= 3$ terminals, we construct an instance $angle.l G = (V, E), c, S, T, K angle.r$ of ADESDP in polynomial time:


+ *Vertex Construction:* For each terminal $x_i in X$ ($i = 1, dots, k$), create two distinct nodes in $G$: a source node $s_i$ and a target node $t_i$. For all non-terminal vertices $v in V_H \ X$, include $v in V$. Thus: $ V = (V_H \ X) union \{s_1, dots, s_k} union \{t_1, dots, t_k} $ Set the attacker source set as $S = \{s_1, dots, s_k}$ and the administrative target set as $T = \{t_1, dots, t_k}$.
+ *Edge and Cost Construction:*
  + For every original directed edge $(u, v) in E_H$:
  + If $u not in X$ and $v not in X$, add $(u, v)$ to $E$ with cost $c(u, v) = w(u, v)$.
  + If $u = x_i in X$ and $v not in X$, add $(s_i, v)$ to $E$ with cost $c(s_i, v) = w(x_i, v)$.
  + If $u not in X$ and $v = x_j in X$, add $(u, t_j)$ to $E$ with cost $c(u, t_j) = w(u, x_j)$.
  + If $u = x_i in X$ and $v = x_j in X$ ($i != j$), add $(s_i, t_j)$ to $E$ with cost $c(s_i, t_j) = w(x_i, x_j)$.
  + For each $i in {1, dots, k}$, add a zero-cost directed enforcement edge $(t_i, s_i)$ with cost $c(t_i, s_i) = infinity$ (or $W + 1$). This ensures that reaching terminal $t_i$ allows reaching all outgoing paths from $s_i$, faithfully reproducing the transitivity of terminal $x_i$ in $H$.
  + Ensure that self-reachability $s_i arrow.squiggly t_i$ does not represent an inter-terminal path by adding an independent dummy terminal set if necessary, or simply setting the target requirement to: disconnect all pairs $(s_i, t_j)$ for $i != j$. By introducing an auxiliary collector vertex $T^*$ for each $s_i$ connected to all $t_j$ ($j != i$) with capacity $infinity$, we map this directly into the bipartite source-target formulation.
+ *Cost Threshold:* Set $K = W$.



The construction introduces at most $2|V_H|$ vertices and $|E_H| + k$ edges, which is computable in $O(|V_H| + |E_H|)$ time.

*Equivalence of Solutions:*

+ $(=>)$ Suppose there exists a cut $C subset.eq E_H$ in $H$ with $sum_(e in C) w(e) <= W$ that disconnects all terminal pairs $x_i arrow.squiggly x_j$ ($i != j$). Let $E_("cut")$ be the corresponding set of edges in $G$. Since no path existed between $x_i$ and $x_j$ in $H \ C$, no directed path can exist between $s_i$ and $t_j$ in $G \ E_("cut")$. The infinite-capacity edges $(t_i, s_i)$ are never cut, and $sum_(e in E_("cut")) c(e) = sum_(e in C) w(e) <= W = K$.
+ $(arrow.l.double)$ Conversely, suppose there exists an edge cut $E_("cut") subset.eq E$ in $G$ with cost $<= K = W$ severing all $s_i arrow.squiggly t_j$ paths ($i != j$). None of the infinite-cost edges $(t_i, s_i)$ can belong to $E_("cut")$ because $K < infinity$. Therefore, $E_("cut")$ corresponds strictly to a subset of original edges $C subset.eq E_H$ with $sum_(e in C) w(e) <= W$ that eliminates all paths between distinct terminals in $H$.



This proves that ADESDP is NP-complete. The optimization version---finding the minimal disruption edge set---is therefore NP-hard. #h(1fr) $square$