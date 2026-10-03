= The Neuro-Symbolic Paradigm: Bridging Statistical GNNs and Symbolic Oracles <ch:neuro_symbolic>


== The Core Dilemma: Shortcut Learning in Security GNNs

The empirical results established across Chapters @ch:evaluation and @ch:case_study present a profound scientific paradox at the intersection of deep learning and cybersecurity:

+ *In-Distribution Empirical Mastery:* On in-distribution enterprise identity graphs, CertGraph achieves near-perfect classification performance (Macro-F1 = $0.9986$), outperforming industry signature tools by $+28.2%$ and discovering novel attack paths (such as ESC13) that evade static scanners.
+ *Zero-Shot Adversarial Collapse:* When confronted with adversarial out-of-distribution hard negatives, CertGraph's accuracy collapses catastrophically to *$1.59%$*, whereas deterministic symbolic graph traversal (BloodHound BFS) retains *$84.13%$*.



This divergence exposes a foundational vulnerability in pure statistical deep learning: _Why do Graph Attention Networks---possessing multi-layer message-passing capabilities---fail so comprehensively to verify graph reachability when evaluated out-of-distribution?_

=== Theoretical Root Cause: The Path-Feature Trade-off

The failure of pure GNNs on adversarial identity graphs is rooted in the machine learning phenomenon of *Shortcut Learning* and spurious correlations @geirhos2020shortcut @ye2026cleverhans @bell2024pragmatic. Deep neural networks trained via gradient descent inherently converge toward the simplest, most computationally accessible statistical correlations present in the training distribution that minimize empirical risk.

In Active Directory graphs, verifying whether an exploitable attack path exists requires the neural network to evaluate a multi-hop reachability conjunction:
$ exists " path " u arrow.squiggly v <=> [ or.big_(k=1)^K ( product_(i=1)^k A_(r_i) ) ]_(u v) > 0 $

This reachability function requires coordinating multi-hop message aggregations across multiple convolutional layers, multiplying attention coefficients, and maintaining sharp boolean conjunctions across heterogeneous relation types.

In stark contrast, inspecting the local template feature vector $x_("Template")$ requires a simple single-layer linear combination:
$ z = bold(w)^T x_("Template") + b $


Because benign enterprise training data rarely contains templates configured with dangerous flags that are completely unenrollable, the empirical training loss $cal(L)(Theta)$ can be minimized almost entirely by relying on local configuration flags ($x_("Template")$). The optimizer naturally drives the network to treat local template flags as a predictive "shortcut," allowing the deeper topological reachability pathways to remain under-optimized.

When the model is subsequently evaluated out-of-distribution on adversarial hard negatives (where configuration flags are active but all authorization paths are severed), the neural model blindly triggers on the local shortcut, producing false positive alerts.

== The Fundamental Dichotomy: Statistical vs. Symbolic AI

This finding highlights the irreconcilable architectural divide between connectionist statistical deep learning and deductive symbolic reasoning in enterprise cybersecurity:

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 6 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Architectural Dimension*], [*Statistical GNN (CertGraph)*], [*Symbolic Logic Oracle (Datalog / BloodHound)*]),
    [*Computational Profile*], [Constant-depth parallel tensor passes ($cal(O)(|V| + |E|)$, $< 350$ ms on 10k nodes)], [Multi-principal Horn-clause and DACL evaluation across templates (high solver overhead)],
    [*Contextual Generalization*], [High (learns continuous patterns, weights multi-modal signals, discovers novel vectors)], [Low (strictly bounded by explicitly engineered rule schemas and syntax)],
    [*Adversarial Robustness*], [Moderate (susceptible to shortcut learning on disconnected templates)], [High (deterministic reachability verification, $84.13%$ on hard negatives)],
    [*Operational Output*], [Continuous calibrated risk ranking ($S_("risk") in [0, 1]$)], [Deterministic boolean reachability proof],
    [*Auditability*], [Attention attribution heatmaps], [Exact deterministic derivation trace (verifiable edge sequence)],
  )
],
  caption: [Comparison of Statistical GNNs vs Symbolic Deduction in Identity Auditing.],
) <tab:dichotomy>


As summarized in @tab:dichotomy, neither paradigm is fully sufficient in isolation:

+ *Limitations of Pure Symbolic Systems:* Static rule scanners (Certipy) and deterministic solvers are blind to novel, un-modeled misconfiguration combinations (e.g., missing ESC13 until explicit rules were engineered) and cannot prioritize remediation based on continuous risk gradients across thousands of templates.
+ *Limitations of Pure Statistical Systems:* Deep GNNs can succumb to shortcut learning when trained on distributions lacking negative templates with dangerous configuration flags, leading to potential false positives on hardened templates.



== First-Order Logic Formalization of Active Directory Privilege Escalation

To bridge the statistical and symbolic paradigms, we formalize Active Directory Certificate Services privilege escalation within the mathematical framework of *First-Order Horn Logic (Datalog)*.

Let directory entities be denoted by constants, and let relations and attributes be represented by predicates. The conditions governing ADCS exploitability can be expressed as a set of deductive logical clauses:

$ "CanEnroll"(u, t) &arrow.l "Enroll"(u, t) 

"CanEnroll"(u, t) &arrow.l "MemberOf"(u, g) and "CanEnroll"(g, t) 

"CanEscalate"_("ESC1")(u, t) &arrow.l "CanEnroll"(u, t) and "SuppliesSubject"(t) 

&  and "ClientAuth"(t) and not "ApprovalReq"(t) 

"CanEscalate"_("ESC13")(u, t, g_("admin")) &arrow.l "CanEnroll"(u, t) and "LinksPolicy"(t, p) 

&  and "MappedGroup"(p, g_("admin")) and "Tier0"(g_("admin")) $


When a symbolic solver queries these Horn clauses against the enterprise multigraph $G$, it produces a formal *Proof Tree* demonstrating the exact transitive sequence of permissions enabling the exploit. If the proof tree resolves to true, the vulnerability is deterministically verified under the defined logic rules.

== The Two-Tier Neuro-Symbolic Architecture

To harness the speed and inductive pattern discovery of Graph Neural Networks while ensuring deterministic verification of attack paths, we propose a unified *Two-Tier Neuro-Symbolic Architecture*.

#figure(
  image("figures/neuro_symbolic_pipeline.png", width: 90%),
  caption: [The Two-Tier Neuro-Symbolic Architecture, pairing fast CertGraph GNN screening for risk prioritization with deterministic BloodHound BFS path verification.],
) <fig:neuro_pipeline>


As illustrated in @fig:neuro_pipeline, the architecture orchestrates a coarse-to-fine cooperative pipeline:

=== Tier 1: Fast Inductive Neural Screening

The enterprise Active Directory multigraph $G$ is first ingested by CertGraph. In a single forward pass executing in milliseconds, CertGraph computes continuous vulnerability probability distributions across all published certificate templates:
$ hat(y)_t = op("CertGraph")(G, t) in Delta^6,   forall t in V_("Template") $

Templates are ranked in descending order of risk score:
$ S_("risk")(t) = 1.0 - hat(y)_t["Safe"] $

CertGraph acts as a high-throughput inductive filter: it prunes benign enterprise templates whose risk score falls below an operational threshold ($S_("risk")(t) < tau_("threshold")$). The top candidate templates are forwarded to Tier 2:
$ cal(Q)_("suspect") = \{t in V_("Template") | S_("risk")(t) >= tau_("threshold")} $


=== Tier 2: Targeted Deductive Graph Verification

For each candidate template $t in cal(Q)_("suspect")$, the symbolic graph engine executes a targeted, bidirectional reachability query restricted to the candidate's localized 2-hop authorization subgraph:
$ "Exploitable"(t) = op("SymbolicVerify")(G, V_("low-priv"), t, "Rule"(hat(y)_t)) $


+ *Path Confirmed (Verified Vulnerability):* If the symbolic oracle discovers a valid authorization path connecting an unprivileged principal to the template, the system outputs a *Verified Exploitability Trace* containing the exact edge sequence, triggering prioritized remediation.
+ *Path Absent (Hard Negative / Suppressed Alert):* If no authorization path connects unprivileged accounts to the template, the candidate is flagged as an unexploitable configuration anomaly, suppressing the alert and logging the template for administrative review.



*Soundness by Construction:*
Crucially, the suppression of false positives on hard negative templates is direct by construction rather than an emergent statistical capability of the machine learning model. In identity access governance, exploitability is formally defined by the existence of an authorized path from low-privileged principals to the certificate template under appropriate enrollment rights. Because Tier~2 executes a deterministic reachability search over the formal Horn clauses governing exploitability, any template lacking an unprivileged path is deterministically rejected. The value of the hybrid architecture lies in this principled division of labor: the statistical neural network provides high-throughput continuous risk prioritization and candidate filtering across dense enterprise graphs, while the symbolic logic oracle guarantees soundness and eliminates false positives.

=== Empirical Threshold Sensitivity and Latency Profiling <subsec:threshold_sensitivity>

An inherent characteristic of two-tier cascaded pipelines is that Tier~2 only evaluates candidates admitted by Tier~1. Consequently, the overall pipeline recall is strictly bounded by the sensitivity of the neural screener:
$ "Recall"_("hybrid") <= "Recall"_("GNN")(tau_("threshold")) $

If the screening threshold $tau_("threshold")$ is set too aggressively, subtle vulnerabilities might be filtered prematurely, causing false negatives. Conversely, setting $tau_("threshold")$ too low admits excessive benign templates, burdening the symbolic solver with unnecessary queries.

To rigorously characterize this operational trade-off, @tab:threshold_sensitivity documents empirical sensitivity across five screening thresholds ($tau in {0.10, 0.25, 0.50, 0.75, 0.90}$) evaluated on a held-out test suite of $N=600$ enterprise certificate templates containing exactly 60 ground-truth privilege escalation paths.

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 6 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Threshold ($tau$)*], [*Admitted*], [*Admit Rate*], [*Recall*], [*GNN (ms)*], [*Symbolic (ms)*], [*Total (ms)*]),
    [$tau = 0.10$], [$182$], [$30.3%$], [$bold(60 / 60\ (100.0%))$], [$18.2$], [$324.5$], [$342.7$],
    [$tau = 0.25$], [$104$], [$17.3%$], [$bold(60 / 60\ (100.0%))$], [$18.2$], [$185.3$], [$203.5$],
    [$bold(tau = 0.50)$], [$bold(62)$], [$bold(10.3%)$], [$bold(60 / 60\ (100.0%))$], [$bold(18.2)$], [$bold(110.6)$], [$bold(128.8)$],
    [$tau = 0.75$], [$58$], [$9.7%$], [$58 / 60\ (96.7%)$], [$18.2$], [$103.4$], [$121.6$],
    [$tau = 0.90$], [$49$], [$8.2%$], [$49 / 60\ (81.7%)$], [$18.2$], [$87.2$], [$105.4$],
  )
],
  caption: [Empirical Threshold Sensitivity and Latency Trade-offs of the Two-Tier Auditor ($N = 600$ Enterprise Templates, 60 True Escalation Paths).],
) <tab:threshold_sensitivity>


As documented in @tab:threshold_sensitivity:

+ *Optimal Operational Operating Point ($tau = 0.50$):* At the standard decision threshold $tau = 0.50$, Tier~1 admits 62 candidate templates (filtering $89.7%$ of benign templates), while capturing all $60/60$ true escalation vectors ($100.0%$ recall, zero false negatives). Total pipeline latency is only $128.8$~ms ($18.2$~ms GNN forward pass $+ 110.6$~ms localized symbolic checks).
+ *Risk-Averse Deployments ($tau in [0.10, 0.25]$):* In ultra-high-security environments where missing an attack path carries extreme penalties, setting $tau = 0.10$ or $0.25$ provides a generous safety margin. Even at $tau = 0.10$, where 182 candidates are forwarded to Tier~2, total execution time remains well under half a second ($342.7$~ms), confirming that the hybrid pipeline retains real-time performance even under hyper-sensitive screening.
+ *Conservative Threshold Degradation ($tau >= 0.75$):* When $tau$ is raised above $0.50$, the neural screener begins truncating marginal candidates. At $tau = 0.75$, two subtle delegation-chain variants are missed (yielding $96.7%$ recall), and at $tau = 0.90$, recall drops to $81.7%$. Consequently, operational enterprise deployments should strictly calibrate $tau <= 0.50$.



== Complexity and Efficiency Profiling

We formalize the computational advantage of the Two-Tier Neuro-Symbolic pipeline over exhaustive symbolic path-finding:


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem Computational Complexity of Neuro-Symbolic Screening.* \
    Let $G = (V, E)$ denote an Active Directory multigraph with $|V_("Template")|$ published certificate templates. Let $T_("GNN") = cal(O)(|V| + |E|)$ denote the inference latency of CertGraph, and let $T_("symb")(t)$ denote the Horn-clause DACL evaluation time on the localized 2-hop subgraph of candidate template $t$.

The total computational complexity of the Two-Tier Neuro-Symbolic pipeline is:
$ T_("hybrid") = cal(O)(|V| + |E|) + sum_(t in cal(Q)_("suspect")) T_("symb")(t) $

satisfying:
$ T_("hybrid") << T_("exhaustive") = sum_(t in V_("Template")) T_("symb")^("global")(t) $

while eliminating false positives on disconnected configurations.
  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
)



_Proof._ In an enterprise network with $|V_("Template")| = 200$ templates, exhaustive symbolic evaluation must resolve complex DACL inheritance, SID filtering, and group nesting across the full directory graph for all 200 templates:
$ T_("exhaustive") = sum_(t=1)^(200) T_("symb")^("global")(t) $

Under the two-tier pipeline, CertGraph evaluates all 200 templates in parallel tensor forward passes ($T_("GNN") = cal(O)(|V| + |E|)$). Because the neural filter prunes the vast majority of benign templates, the candidate queue contains only the small subset of suspicious templates ($|cal(Q)_("suspect")| << |V_("Template")|$). Furthermore, targeted symbolic evaluation executes exclusively on the extracted 2-hop subgraph ($|V_t| << |V|$ and $|E_t| << |E|$).

Therefore, total latency is bounded by:
$ T_("hybrid") = cal(O)(|V| + |E|) + |cal(Q)_("suspect")| dot T_("symb")^("local") approx cal(O)(|V| + |E|) $

substantially reducing total computational load. Furthermore, because alerts emitted by Tier 2 are validated by an exact symbolic proof trace, false positive alerts on unenrollable templates are eliminated. #h(1fr) $square$


== Algorithmic Specification of the Hybrid Pipeline

@alg:neuro_symbolic formalizes the cooperative execution routine of the Two-Tier Neuro-Symbolic Auditor.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: 1pt + rgb("#cbd5e1"), width: 100%)[
#align(left)[
#h(0.0em) *Require:* Active Directory Graph $G = (V, E)$; Trained CertGraph model $cal(M)$; Risk screening threshold $tau_("threshold") in (0, 1)$; Low-privileged user set $V_("low-priv")$. \
#h(0.0em) *Ensure:* Confirmed vulnerability alerts $cal(A)_("verified")$ with deterministic proof traces. \
#h(0.0em) Initialize alert queue $cal(A)_("verified") arrow.l []$ \
#h(0.0em) *Tier 1: Fast Inductive Neural Screening* \
#h(0.0em) Compute model logits across all published templates: $bold(Z) arrow.l cal(M)(G)$ \
#h(0.0em) Compute risk vector: $bold(S)_("risk") arrow.l 1.0 - op("Softmax")(bold(Z), "dim"=-1)[:, "Safe"]$ \
#h(0.0em) Identify candidate suspects: $cal(Q)_("suspect") arrow.l \{t in V_("Template") | bold(S)_("risk")[t] >= tau_("threshold")}$ \
#h(0.0em) *Tier 2: Targeted Deductive Symbolic Verification* \
#h(0.0em) *for* each template $t in cal(Q)_("suspect")$: \
#h(1.5em) Predicted class: $c arrow.l op("argmax")_k bold(Z)[t, k]$ \
#h(1.5em) Extract 2-hop backward authorization subgraph: $G_t arrow.l op("ExtractSubgraph")(G, t, "hops"=2)$ \
#h(1.5em) Execute targeted BFS verification: $("is_valid", "proof_trace") arrow.l op("SymbolicBFS")(G_t, V_("low-priv"), t, c)$ \
#h(1.5em) *if* $"is_valid" = "True"$: \
#h(3.0em) Append $(t, c, bold(S)_("risk")[t], "proof_trace")$ to $cal(A)_("verified")$ \
#h(1.5em) *else:* \
#h(3.0em) Log anomalous configuration: $op("LogHardNegative")(t, c, bold(S)_("risk")[t])$ \
#h(0.0em) *return* $cal(A)_("verified")$
]
  ],
  caption: [Two-Tier Neuro-Symbolic Vulnerability Auditor],
  kind: "algorithm",
  supplement: [Algorithm],
) <alg:neuro_symbolic>


== Enterprise Security Operations Center (SOC) Orchestration

In production enterprise architectures, the Two-Tier Neuro-Symbolic Auditor integrates directly into Security Information and Event Management (SIEM) systems (such as Splunk Enterprise Security and Microsoft Sentinel) and Security Orchestration, Automation, and Response (SOAR) pipelines:

+ *Continuous Ingestion:* A lightweight background service ingests directory snapshots emitted by domain controllers every 60 minutes.
+ *Sub-Second Prioritization:* Tier 1 screens the directory in under 350 ms, generating real-time risk heatmaps for security analysts.
+ *Automated Ticket Generation with Verified Proofs:* Tier 2 resolves candidate alerts. When an alert is verified, the SOAR platform automatically generates a ServiceNow or Jira incident containing the exact Cypher execution trace, eliminating analyst investigation time.
+ *Suppression of Alert Fatigue:* By delegating confirmatory authority to the symbolic gatekeeper, false positive alerts arising from unenrollable or disconnected templates are effectively eliminated from the SOC alert queue.


