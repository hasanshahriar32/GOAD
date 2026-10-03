= Formal Mathematical Proofs <app:proofs>

== Proof of Theorem 1: Intrinsic Attribute Preservation and Non-Vanishing Gradient Bounds <proof:theorem1>

#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem Intrinsic Attribute Preservation and Gradient Lower Bounds.* \
    Let $G = (V, E, cal(T)_V, cal(T)_E)$ be a directed heterogeneous multigraph with node type mapping $tau: V arrow.r cal(T)_V$. Let each node $v in V$ have an initial feature vector $x_v = h_v^((0)) in bb(R)^(d_0)$. Consider an $L$-layer heterogeneous message-passing neural network where layer $l in {1, dots, L}$ computes hidden representations:

+ *Intrinsic Feature Erasure in Relational Neighborhood Aggregation:* Under pure relational neighborhood aggregation without self-loops or skip connections: $ h_v^((l)) = sigma ( sum_(r in cal(R)_("in")(tau(v))) plus.circle.big_(u in cal(N)_r(v)) alpha_(v u)^((l)) W_r^((l)) h_u^((l-1)) ) $ where $cal(N)_r(v) = \{u in V | (u, r, v) in E}$ denotes incoming neighbors under relation $r$, the layer-1 hidden state $h_v^((1))$ is conditionally independent of $x_v$ given $cal(N)(v)$. Consequently: $ (diff h_v^((1)))/(diff x_v) = bold(0) in bb(R)^(d_1 times d_0) $ Moreover, for any source-only node $v$ satisfying $cal(N)_("in")(v) = emptyset$, $h_v^((l)) = bold(0)$ for all $l >= 1$.
+ *Guaranteed Gradient Lower Bound via Parameterized Residual Skips:* When parameterized residual skip connections are introduced: $ tilde(h)_v^((l)) = h_v^((l)) + W_("skip")^((l)) tilde(h)_v^((l-1)) $ where $W_("skip")^((l)) in bb(R)^(d_l times d_(l-1))$ has minimum singular value $sigma_(min)(W_("skip")^((l))) > 0$, the Jacobian of the representation with respect to the initial input features satisfies: $ sigma_(min) ( (diff tilde(h)_v^((L)))/(diff x_v) ) >= product_(k=1)^L sigma_(min)(W_("skip")^((k))) - \|cal(J)_("graph")(v)|| $ where $\|cal(J)_("graph")(v)|| <= L_sigma^L alpha_(max) product_(l=1)^L \|W^((l))||$ bounds the cyclical feedback gradient. When $G$ contains no self-directed cycles of length $<= L$ involving $v$, $cal(J)_("graph")(v) = bold(0)$, yielding the exact lower bound $product_(k=1)^L sigma_(min)(W_("skip")^((k))) > 0$. Under the spectral condition $product_(k=1)^L sigma_(min)(W_("skip")^((k))) > \|cal(J)_("graph")(v)||$, input feature sensitivity is strictly preserved: $ || (diff tilde(h)_v^((L)))/(diff x_v) || >= product_(k=1)^L sigma_(min)(W_("skip")^((k))) - \|cal(J)_("graph")(v)|| > 0 $ guaranteeing that input feature sensitivity does not vanish across message-passing layers.


  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)



_Proof._ We establish the proof in three parts: intrinsic feature erasure, gradient lower bounds under residual skip connections, and the specific application to identity multigraphs.

*Part 1: Intrinsic Feature Erasure under Pure Neighborhood Aggregation.*
Let $v in V$ be an arbitrary node in $G$ with initial feature vector $x_v = h_v^((0)) in bb(R)^(d_0)$. Under the standard heterogeneous relational convolution layer:
$ h_v^((1)) = sigma ( sum_(r in cal(R)_("in")(tau(v))) plus.circle.big_(u in cal(N)_r(v)) alpha_(v u)^((1)) W_r^((1)) h_u^((0)) ) $

Observe that the argument of $sigma(dot)$ is a linear combination of neighbor states $\{h_u^((0)) | u in cal(N)_r(v), r in cal(R)_("in")(tau(v))}$. In an access control multigraph lacking explicit self-loop relations on template nodes:
$ v not in cal(N)_r(v),   forall r in cal(R)_("in")(tau(v)) $

Differentiating $h_v^((1))$ with respect to $x_v = h_v^((0))$:
$ (diff h_v^((1)))/(diff x_v) = sigma'(dot) dot sum_(r in cal(R)_("in")(tau(v))) sum_(u in cal(N)_r(v)) alpha_(v u)^((1)) W_r^((1)) (diff h_u^((0)))/(diff h_v^((0))) $

Because distinct nodes have disjoint representations ($diff h_u^((0)) / diff h_v^((0)) = bold(0)$ for all $u != v$), every term in the summation evaluates to zero:
$ (diff h_v^((1)))/(diff x_v) = bold(0) in bb(R)^(d_1 times d_0) $

Thus, at layer 1, the node's updated embedding $h_v^((1))$ is completely independent of its initial feature vector $x_v$. In certificate templates ($t in V_("Template")$), this means that the 10 binary configuration flags $x_("Template")$ (which govern whether the template allows enrollee-supplied SANs, requires manager approval, or specifies client authentication EKUs) are completely discarded from $h_t^((1))$. 

Furthermore, if $v$ is a source-only entity satisfying $d_("in")(v) = 0$ (such as user accounts possessing outgoing enrollment rights but no incoming delegations), then $cal(N)_r(v) = emptyset$ for all $r$. By the identity of aggregation over an empty set ($plus.circle.big(emptyset) = bold(0)$) and $sigma(bold(0)) = bold(0)$, we obtain $h_v^((l)) = bold(0)$ for all $l >= 1$.

*Part 2: Gradient Lower Bounds via Parameterized Residual Skips.*
Now consider the layer formulation equipped with parameterized additive residual skip connections:
$ tilde(h)_v^((l)) = h_v^((l)) + W_("skip")^((l)) tilde(h)_v^((l-1)) $

where $tilde(h)_v^((0)) = x_v$ and $W_("skip")^((l)) in bb(R)^(d_l times d_(l-1))$. Unrolling the recurrence from layer $L$ to layer $0$:
$ tilde(h)_v^((L)) = ( product_(k=1)^L W_("skip")^((k)) ) x_v + sum_(l=1)^L ( product_(k=l+1)^L W_("skip")^((k)) ) h_v^((l)) $

where by convention $product_(k=L+1)^L W_("skip")^((k)) = I_(d_L)$. 

Taking the Jacobian of $tilde(h)_v^((L))$ with respect to $x_v$:
$ (diff tilde(h)_v^((L)))/(diff x_v) = product_(k=1)^L W_("skip")^((k)) + cal(J)_("graph")(v) $

where $cal(J)_("graph")(v) = sum_(l=1)^L ( product_(k=l+1)^L W_("skip")^((k)) ) (diff h_v^((l)))/(diff x_v)$ represents the indirect gradient flowing through cyclical graph paths (e.g., $v arrow.r u arrow.r v$).

By Weyl's perturbation inequality for singular values (Horn & Johnson, 2012):
$ sigma_(min) ( (diff tilde(h)_v^((L)))/(diff x_v) ) >= sigma_(min) ( product_(k=1)^L W_("skip")^((k)) ) - \|cal(J)_("graph")(v)|| $

Applying the sub-multiplicative property of singular values:
$ sigma_(min) ( product_(k=1)^L W_("skip")^((k)) ) >= product_(k=1)^L sigma_(min)(W_("skip")^((k))) $


Now, we explicitly bound the operator norm $\|cal(J)_("graph")(v)||$. At layer 1, since there are no self-loops ($v not in cal(N)(v)$), $(diff h_v^((1)))/(diff x_v) = bold(0)$. For $L = 2$, applying the chain rule to the second aggregation layer yields:
$ (diff h_v^((2)))/(diff x_v) = sum_(r in cal(R)_("in")) sum_(u in cal(N)_r(v)) alpha_(v u)^((2)) sigma'(z_v^((2))) W_r^((2)) (diff tilde(h)_u^((1)))/(diff x_v) $

Expanding $(diff tilde(h)_u^((1)))/(diff x_v) = (diff h_u^((1)))/(diff x_v) + W_("skip")^((1)) (diff x_u)/(diff x_v)$: since $u != v$, $(diff x_u)/(diff x_v) = bold(0)$, and $(diff h_u^((1)))/(diff x_v) = sum_(r' in cal(R)_("in")) sum_(w in cal(N)_(r')(u)) alpha_(uw)^((1)) sigma'(z_u^((1))) W_(r')^((1)) (diff x_w)/(diff x_v)$. The term $(diff x_w)/(diff x_v)$ is non-zero ($I_(d_0)$) if and only if $w = v$, corresponding to a 2-hop directed cycle $v arrow.r u arrow.r v$.

We therefore distinguish two topological regimes:

+ *Acyclic Receptive Field ($\nexists 2$-cycle $v arrow.squiggly u arrow.squiggly v$):* In standard Active Directory permission DAGs (where user accounts possess forward enrollment rights into templates, but certificate templates do not hold outgoing access-control rights over users), no 2-hop cycles terminate back at $v$. Consequently, $(diff h_u^((1)))/(diff x_v) = bold(0)$ for all $u in cal(N)(v)$, establishing: $ cal(J)_("graph")(v) = bold(0) => || (diff tilde(h)_v^((L)))/(diff x_v) || >= product_(k=1)^L sigma_(min)(W_("skip")^((k))) > 0 $ The lower bound holds with exact equality.
+ *Cyclical Graphs ($exists 2$-cycle $v arrow.r u arrow.r v$):* By the sub-multiplicativity of induced operator norms and the Lipschitz continuity of the activation function ($\|sigma'|| <= L_sigma = 1$ for ELU/ReLU): $ \|cal(J)_("graph")(v)|| &<= L_sigma^2 sum_(u in cal(N)(v)) alpha_(v u)^((2)) alpha_(u v)^((1)) \|W^((2))|| \|W^((1))|| &<= L_sigma^2 ( max_(u in cal(N)(v)) alpha_(u v)^((1)) ) \|W^((2))|| \|W^((1))|| sum_(u in cal(N)(v)) alpha_(v u)^((2)) &= alpha_(max)^((1)) \|W^((2))|| \|W^((1))|| $ where $alpha_(max)^((1)) = max_(u in cal(N)(v)) alpha_(u v)^((1)) <= 1$. Under standard spectral scaling or weight regularization where the skip connection singular values satisfy $product_(k=1)^L sigma_(min)(W_("skip")^((k))) > alpha_(max)^((1)) product_(l=1)^L \|W^((l))||$, we strictly establish: $ || (diff tilde(h)_v^((L)))/(diff x_v) || >= sigma_(min) ( (diff tilde(h)_v^((L)))/(diff x_v) ) >= product_(k=1)^L sigma_(min)(W_("skip")^((k))) - \|cal(J)_("graph")(v)|| > 0 $



*Part 3: Implication for Active Directory Certificate Template Classification.*
In Active Directory Certificate Services, certificate template classification is a joint decision requiring both:

+ Intrinsic configuration flags $x_t in bb(R)^(10)$ (e.g., whether `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` and Client Authentication EKUs are enabled).
+ Topological reachability from unprivileged principals ($exists u in V_("low-priv") arrow.squiggly t$).


Without residual skip connections ($W_("skip") = 0$), $h_t^((1))$ completely erases $x_t$. While $x_t$ can theoretically influence $h_t^((2))$ through 2-hop cycles ($t arrow.r u arrow.r t$), this signal is severely diluted by attention normalization across all adjacent principals and relations. Consequently, the network loses direct access to the template's configuration flags, explaining the empirical collapse from Macro-F1 = $0.9986$ to $0.4768$ observed in @sec:ablation_results. Parameterized residual skip connections guarantee that the 10 binary flags are directly retained in the final node embedding, preserving classification efficacy. #h(1fr) $square$



#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Corollary Necessity in Active Directory Identity Graphs.* \
    In enterprise identity graphs, where certificate templates rely heavily on intrinsic configuration attributes and user principals frequently act as low in-degree sources in administrative authorization subgraphs, parameterized residual skip connections are mathematically required to prevent feature decay and gradient vanishing across multi-hop relational convolutions.
  ]
  ],
  caption: none,
  kind: "corollary",
  supplement: [Corollary],
)

#pagebreak()

== Proof of Theorem 2: NP-Hardness of Multi-Principal Access Interdiction in Enterprise Identity Graphs <proof:theorem2>

#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem NP-Hardness of Multi-Principal Access Interdiction.* \
    Let $G = (V, E)$ be a directed multigraph representing an Active Directory domain, where $V$ represents security principals and directory objects, and $E$ represents directed authorization, delegation, and administrative permissions. Let $c: E arrow.r bb(R)^+$ assign operational disruption costs to edges, representing the business friction of revoking a specific privilege.

Let $cal(P)_("forbidden") = {(s_1, t_1), (s_2, t_2), dots, (s_k, t_k)}$ denote a set of $k >= 3$ forbidden source-target compromise pairs (e.g., specific unprivileged footholds and their respective target administrative assets across distinct trust or tier boundaries) that must be severed.

The *Multi-Principal Access Interdiction (MPAI)* problem asks: given an operational disruption budget $K in bb(R)^+$, does there exist an edge interdiction subset $E_("cut") subset.eq E$ such that:

+ Total operational revocation cost is bounded: $ sum_(e in E_("cut")) c(e) <= K $
+ All forbidden directed compromise paths are severed: $ forall (s_i, t_i) in cal(P)_("forbidden"), "Path"(s_i arrow.squiggly t_i) " does not exist in " G' = (V, E \ E_("cut")) $


The MPAI problem is NP-complete for $k >= 3$. Consequently, finding the optimal edge-severing defense strategy that minimizes operational disruption while neutralizing multiple independent lateral compromise paths is NP-hard.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)



_Proof._ We prove NP-completeness by establishing:

+ $"MPAI" in "NP"$, and
+ A polynomial-time reduction from the classical NP-complete *Directed Multiway Cut* problem @garg1994multiway to MPAI: $ "Directed Multiway Cut" <=_p "MPAI" $



*Part 1: Membership in NP.*
Given a candidate edge subset $E_("cut") subset.eq E$:

+ We compute the total operational revocation cost $sum_(e in E_("cut")) c(e)$ in $cal(O)(|E_("cut")|)$ time and verify whether $sum_(e in E_("cut")) c(e) <= K$.
+ We construct the residual graph $G' = (V, E \ E_("cut"))$ in $cal(O)(|V| + |E|)$ time.
+ For each of the $k$ forbidden pairs $(s_i, t_i) in cal(P)_("forbidden")$, we execute Breadth-First Search (BFS) starting from $s_i$ in $G'$ to verify that $t_i$ is unreachable. This requires $cal(O)(k dot (|V| + |E|))$ time.


Because all verification steps complete in deterministic polynomial time with respect to the graph size, $"MPAI" in "NP"$.

*Part 2: Polynomial-Time Reduction from Directed Multiway Cut.*
While the classical Multiterminal Cut problem on undirected graphs was proven NP-complete for $k >= 3$ by Dahlhaus et al. (1994) @dahlstrm2000multiway (and polynomial-time solvable for $k=2$ via standard min-cut algorithms), enterprise identity attack graphs are directed and asymmetric. We emphasize that while finding an edge cut severing all paths from a single source to a single target is polynomial-time solvable via standard $(S, T)$ min-cut, and prior Active Directory interdiction literature (Guo et al., 2022, 2023) @guo2022practical @guo2023scalable established the W[1]-hardness of single-target _shortest-path_ interdiction, @thm:nphardness proves that complete reachability interdiction across multiple forbidden terminal pairs is NP-hard. We base our reduction on the *Directed Multiway Cut* problem, which was proven NP-complete even for $k >= 2$ by Garg, Vazirani, and Yannakakis (1994) @garg1994multiway:
\begin{quote}
*Directed Multiway Cut:* Given a directed graph $H = (V_H, E_H)$ with positive edge weights $w: E_H arrow.r bb(R)^+$, a subset of $k >= 3$ distinct terminal vertices $X = \{x_1, x_2, dots, x_k} subset.eq V_H$, and a cost threshold $W$, does there exist an edge subset $C subset.eq E_H$ with $sum_(e in C) w(e) <= W$ such that no directed path connects any terminal $x_i$ to any other terminal $x_j$ ($i != j$) in the residual graph $H' = (V_H, E_H \ C)$?
\end{quote}

Given an arbitrary instance $angle.l H = (V_H, E_H), w, X = \{x_1, dots, x_k}, W angle.r$ of the Directed Multiway Cut problem ($k >= 3$), we construct an instance $angle.l G = (V, E), c, cal(P)_("forbidden"), K angle.r$ of MPAI in polynomial time:


+ *Vertex Construction:* For each terminal $x_i in X$, create two distinct nodes in $G$: an attacker source principal $s_i$ and a high-value target asset $t_i$. For all non-terminal vertices $v in V_H \ X$, include $v in V$. Thus: $ V = (V_H \ X) union \{s_1, dots, s_k} union \{t_1, dots, t_k} $
+ *Edge and Cost Construction:*
  + For every original edge $(u, v) in E_H$:
  + If $u not in X$ and $v not in X$, add $(u, v) in E$ with cost $c(u, v) = w(u, v)$.
  + If $u = x_i in X$ and $v not in X$, add $(s_i, v) in E$ with cost $c(s_i, v) = w(x_i, v)$.
  + If $u not in X$ and $v = x_j in X$, add $(u, t_j) in E$ with cost $c(u, t_j) = w(u, x_j)$.
  + If $u = x_i in X$ and $v = x_j in X$ ($i != j$), add $(s_i, t_j) in E$ with cost $c(s_i, t_j) = w(x_i, x_j)$.
  + For each terminal index $i in {1, dots, k}$, add a directed continuation edge $(t_i, s_i)$ with infinite capacity $c(t_i, s_i) = infinity$ (or $W + 1$). This enforces that reaching target $t_i$ allows traversing any path leaving source $s_i$, preserving the full reachability topology of vertex $x_i$ in $H$.
+ *Forbidden Pair Definition:* Set the forbidden compromise pair set to all distinct terminal combinations: $ cal(P)_("forbidden") = {(s_i, t_j) | 1 <= i, j <= k, i != j} $ Here $|cal(P)_("forbidden")| = k(k-1) >= 6$ for $k >= 3$.
+ *Disruption Budget:* Set $K = W$.



The reduction generates $|V| = |V_H| + k$ vertices and $|E| = |E_H| + k$ edges, requiring $cal(O)(|V_H| + |E_H|)$ time.

*Equivalence of Solutions:*

+ $(=>)$ Suppose there exists a valid Directed Multiway Cut $C subset.eq E_H$ in $H$ with $sum_(e in C) w(e) <= W$ that disconnects all pairs $x_i arrow.squiggly x_j$ for $i != j$. Let $E_("cut") subset.eq E$ be the identical set of edges in $G$. Since $C$ contains no infinite-cost edges, $sum_(e in E_("cut")) c(e) = sum_(e in C) w(e) <= W = K$. Furthermore, because no path connects $x_i$ to $x_j$ in $H \ C$, no path can connect $s_i$ to $t_j$ in $G \ E_("cut")$. Hence, all pairs in $cal(P)_("forbidden")$ are severed.
+ $(arrow.l.double)$ Conversely, suppose there exists an edge cut $E_("cut") subset.eq E$ in $G$ with cost $sum_(e in E_("cut")) c(e) <= K = W$ severing all paths for every pair $(s_i, t_j) in cal(P)_("forbidden")$ ($i != j$). Because $K < infinity$, $E_("cut")$ cannot contain any infinite-capacity continuation edge $(t_i, s_i)$. Thus, $E_("cut")$ corresponds directly to a valid edge subset $C subset.eq E_H$ in $H$. If there existed a directed path from $x_i$ to $x_j$ ($i != j$) in $H \ C$, the identical sequence of edges would form a directed path from $s_i$ to $t_j$ in $G \ E_("cut")$, contradicting the assumption that $(s_i, t_j)$ is severed. Therefore, $C$ separates all terminal pairs in $H$ with cost $<= W$.



This establishes that MPAI is NP-complete for $k >= 3$. The optimization problem of finding the minimal-disruption edge-severing set is therefore NP-hard. #h(1fr) $square$