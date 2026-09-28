= Forensic Audit: Unmasking Experimental Illusions in Security Machine Learning <ch:audit>


== The Methodological Crisis of Security Machine Learning

Applied machine learning in computer security is uniquely susceptible to methodological pitfalls and experimental artifacts. In conventional computer vision and natural language processing domains, models learn from human-perceptible patterns (such as textures, shapes, and syntax). In contrast, cybersecurity datasets---particularly those representing enterprise network graphs and identity topologies---consist of high-dimensional, abstract relational structures where human intuition cannot easily detect subtle distribution shifts or hidden correlations.

A pervasive pathology in modern security ML literature is the phenomenon of too good to be true" empirical results. When an experimental pipeline produces near-perfect classification metrics (e.g., Macro-F1 $= 1.0000$), researchers are confronted with a critical methodological dilemma:

+ *The Optimistic Hypothesis:* The deep neural network has discovered an omniscient, generalizable representation of the underlying security domain, solving the threat detection problem.
+ *The Adversarial Reality:* The experimental architecture has inadvertently leaked spurious, deterministic artifacts, allowing the neural network to achieve superficial perfection by exploiting statistical shortcuts that collapse in real-world deployments.



During the early development of CertGraph, initial iterations of our Hetero-GAT model achieved a flawless $1.0000$ Macro-F1 score across all seven evaluated ESC vulnerability classes on synthetic enterprise graphs. Rather than prematurely declaring victory, we adopted an *Adversarial Forensic Audit* doctrine: we treated our own data generators, feature encodings, and model baselines as potentially compromised systems requiring rigorous post-mortem dissection.

Our audit exposed four profound, compounding experimental illusions that had artificially inflated empirical performance. By systematically documenting how these illusions arose, how they were mathematically proven, and how our pipeline was re-engineered, this chapter provides a methodological blueprint for experimental hygiene in graph machine learning for cybersecurity.

== The Four Experimental Illusions


=== Illusion 1: Positional Index Leakage in Synthetic Topologies

In synthetic network generators, entities are typically instantiated sequentially within memory arrays or graph database buffers. In our initial generator implementation (`generator_v1.py`), directory entities were instantiated in fixed programmatic loops:

+ The Tier-0 administrative security group (`Domain Admins`) was consistently allocated at index $0$ of the `Group` entity tensor ($v_("group") = 0$).
+ Domain administrators were systematically allocated within the lowest numeric partition of the `User` tensor ($v_("user") in [0, \lfloor N_("users") / 10 \rfloor]$).
+ In ESC13 synthetic generation routines, the issuance policy OID was programmatically linked exclusively to group index $0$.



*Information-Theoretic Proof of Positional Leakage:*
Let $Y in cal(C)$ denote the random variable representing the true vulnerability class of a certificate template, and let $I_A in bb(N)$ denote the integer array index of the high-value target group or enroller principal. In a methodologically sound experimental benchmark, an entity's arbitrary memory buffer index must provide zero information regarding its security posture:
$ I(Y; I_A) = H(Y) - H(Y | I_A) = 0 $

where $H(Y)$ is the Shannon entropy of the class distribution, and $I(Y; I_A)$ is the mutual information.

However, because group index $0$ was deterministically reserved for `Domain Admins`, observing that a template's incoming or outgoing edge linked to index $0$ completely eliminated all uncertainty regarding the vulnerability class:
$ H(Y | I_A = 0) = 0 => I(Y; I_A = 0) = H(Y) = log_2(7) approx 2.807 " bits" $

The neural network was not learning relational access control semantics; it was functioning as an information-theoretic decoder of synthetic memory allocation offsets.

*The Deterministic Positional Oracle:*
To empirically verify whether deep graph convolutions were genuinely necessary or if the pipeline was merely exploiting index leakage, we constructed a trivial 6-line deterministic heuristic rule that performed zero neural computations:


#figure(
```python
def trivial_positional_oracle(hetero_graph, template_idx):
    # Check if any incoming enrollment edge originates from low-index users
    enrollers = hetero_graph[('User', 'enroll', 'Template')].edge_index[0]
    if any(u.item() < 3 for u in enrollers):
        return "ESC1"
    # Check if policy link terminates at group index 0 (Domain Admins)
    policy_targets = hetero_graph[('Template', 'links_policy', 'Group')].edge_index[1]
    if any(g.item() == 0 for g in policy_targets):
        return "ESC13"
    return "Safe"
```,
  caption: [Deterministic index-leakage oracle exploiting positional generator bias.],
)


When evaluated on the initial benchmark dataset, this trivial heuristic achieved an astonishing *100.0% classification accuracy* on ESC13 and ESC1. The multi-layer Graph Attention Network had simply converged its edge projection weights to detect tensor index zeroes.

=== Illusion 2: Baseline Information Asymmetry

In academic evaluations of Graph Neural Networks for security, standard practice involves benchmarking GNNs against flat, tabular machine learning classifiers (such as Multi-Layer Perceptrons and Random Forests). In published literature, these flat baselines routinely exhibit mediocre performance (F1 $approx 0.75 - 0.85$), leading authors to claim that "GNNs are fundamentally superior to tabular architectures for identity security."

Our forensic audit revealed that this apparent superiority stemmed from a fatal *Information Asymmetry*:

+ *Input Starvation of Flat Baselines:* Flat classifiers (MLP, Random Forest) were supplied exclusively with the 10-dimensional template configuration feature vector $x_("Template") in bb(R)^(10)$.
+ *Full Graph Visibility of GNNs:* CertGraph was supplied with both $x_("Template")$ and the entire heterogeneous authorization graph multiset $E$.



Because Active Directory vulnerability exploitability inherently depends on graph reachability (e.g., whether an unprivileged user has an `Enroll` path or whether write access is granted to an unprivileged SID), flat classifiers were structurally starved of the information necessary to resolve ambiguous templates. Their observed failure was not a failure of tabular learning architectures; it was an artifact of an unfair, asymmetrical benchmark protocol.

=== Illusion 3: The 7-Node Decision Tree Counterexample

To establish precisely how much graph topological information is required to classify ADCS vulnerabilities on in-distribution data, we engineered four elementary scalar graph topological count features extracted from the 1-hop and 2-hop local neighborhood:

+ $c_1 in bb(N)$: In-degree count of low-privileged users possessing direct `Enroll` permissions to the template ($c_1 = sum_(u in V_("low-priv")) A_("Enroll")[u, t]$).
+ $c_2 in bb(N)$: In-degree count of low-privileged principals possessing administrative write permissions ($c_2 = sum_(u in V_("low-priv")) (A_("GenericAll")[u, t] + A_("WriteDacl")[u, t])$).
+ $c_3 in {0, 1}$: Binary indicator of whether an outgoing `LinksPolicy` edge exists ($bb(I)("deg"_("out")(t, "LinksPolicy") > 0)$).
+ $c_4 in {0, 1}$: Binary indicator of whether the target group linked by `LinksPolicy` is a Tier-0 administrative group ($x_("Group")[0] > 0.5$).



Concatenating these 4 structural summary features with the 10 local template configuration flags yielded a 14-dimensional augmented feature vector:
$ x_("aug") = [x_("Template")  ||  c_1, c_2, c_3, c_4]^T in bb(R)^(14) $


#figure(
  image("figures/feature_heatmap.png", width: 90%),
  caption: [Correlation and separability heatmap of template configuration flags and augmented topological features across ESC vulnerability classes.],
) <fig:feature_heatmap>


We trained a standard, unconstrained CART Decision Tree classifier on $x_("aug")$ across 5-fold cross-validation on 700 enterprise environments. The resulting Decision Tree contained exactly *7 decision nodes* (depth 4), yet achieved a Macro-F1 score of:
$ "Macro-F1"_("Tree") = bold(0.9928 plus.minus 0.0057) $

@tab:dt_rules details the exact decision rules learned by this 7-node tree.

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 8 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Node ID*], [*Splitting Condition*], [*True Branch*], [*Predicted Class*]),
    [1], [$f_("is_published") <= 0.5$], [Template is not published to any active CA], [`Safe`],
    [2], [$f_("requires_approval") > 0.5$], [Manager approval blocks autonomous issuance], [`Safe`],
    [3], [$c_1 <= 0.5 " and " c_2 <= 0.5$], [No unprivileged enrollment or write access path], [`Safe`],
    [4], [$f_("supplies_subject") > 0.5 " and " f_("client_auth") > 0.5$], [Enrollee supplies SAN with Client Auth EKU], [`ESC1`],
    [5], [$f_("any_purpose") > 0.5$], [Any Purpose EKU allows full credential misuse], [`ESC2`],
    [6], [$f_("agent_eku") > 0.5$], [Enrollment Agent EKU allows on-behalf-of], [`ESC3`],
    [7], [$c_2 > 0.5 " and " f_("has_dangerous_dacl") > 0.5$], [Unprivileged write access allows DACL hijack], [`ESC4`],
  )
],
  caption: [Exact Decision Logic of the 7-Node Decision Tree Counterexample.],
) <tab:dt_rules>


This finding was a critical turning point in our investigation: consistent with the principles articulated by Arp et al. @arp2022dos regarding subtle dataset artifacts, it demonstrated that for in-distribution synthetic enterprise data, complex deep message-passing convolutions can be almost entirely matched by elementary tabular models if provided with basic topological summary counts.

=== Illusion 4: Hard Negative Memorization under In-Distribution Splits

To evaluate whether neural models could distinguish between genuinely exploitable templates and safe configurations bearing dangerous flags (referred to as *Hard Negatives*), earlier research protocols generated hard negative environments and included them directly in the training and validation sets with the ground-truth label `Safe`.

However, under conventional stratified 5-fold cross-validation, the test fold samples originated from the _identical statistical distribution_ as the training folds. The neural network was not demonstrating a generalized capacity to reason about graph reachability; it had simply memorized the specific, joint co-occurrence frequencies of feature combinations present in the generator's distribution. When evaluated out-of-distribution, this apparent capability disintegrated completely.

== Complete Generator Sanitization and Protocol Redesign

To eliminate these structural artifacts and establish a rigorous, leak-free empirical benchmark, we overhauled the data generation and evaluation pipeline in `generator.py`:


+ *Complete Positional Decoupling:* We broke all couplings between tensor indices and entity semantics. High-value target groups ($g_("target")$) and administrative accounts are selected via uniform random sampling across the entire node tensor ($g_("target") tilde cal(U){0, |V_("Group")|-1}$). Furthermore, all node orderings are subjected to random permutations after graph construction.
+ *Dynamic Feature-Driven Authorization:* Access control assignments were refactored to inspect node feature attributes rather than indices. An account is granted administrative access if and only if its attribute flag satisfies $f_("is_admin") = 1.0$.
+ *Fair Baseline Parity (Graph-Augmented Models):* Following the guidelines of Arp et al. @arp2022dos regarding baseline comparability, we established two fair baseline models: *Graph-Augmented MLP* and *Graph-Augmented Random Forest*. Both models receive the full 14-dimensional augmented vector $x_("aug")$, ensuring they possess topological visibility equal to CertGraph.
+ *Symbolic Graph Oracle (BloodHound BFS Baseline):* We implemented a deterministic symbolic baseline (`bfs_baseline.py`) that programmatically queries the multigraph for directed authorization paths from unprivileged principals to the target template, replicating the exact logic of BloodHound Cypher queries.
+ *Strict Zero-Shot Adversarial Protocol:* We restructured hard-negative evaluation into a rigorous zero-shot protocol: models are trained on 1,400 clean environments containing zero hard negative samples, and evaluated against out-of-distribution adversarial hard negatives never encountered during optimization.



== Statistical Verification of Generator Sanitization

To mathematically confirm that positional index leakage had been completely eliminated from the benchmark, we conducted an independent statistical audit across 700 freshly generated enterprise environments.

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 3 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Generator Version*], [*Admin at Index 0*], [*Theoretical Prob.*], [*Chi-Squared Goodness-of-Fit*]),
    [Flawed Generator (`v1.0`)], [$100.0%$ (700 / 700)], [$1.33%$ ($1/75$)], [$chi^2 = 51,800.0,   p < 10^(-100)$ (Severe Artifact)],
    [*Repaired Generator (`v2.0`)*], [$bold(1.29%)$ (9 / 700)], [$bold(1.33%)$ ($1/75$)], [$bold(chi^2 = 0.012  \  p = 0.913)$ (No Statistical Bias)],
  )
],
  caption: [Empirical Distribution of Administrative Group Allocation Across 700 Independent Environments.],
) <tab:leakage_audit>


As shown in @tab:leakage_audit, in the flawed generator, 100% of enterprise domains allocated the Tier-0 administrative group at index 0. In the repaired generator, the empirical frequency dropped to exactly $1.29%$ (9 out of 700 environments), closely matching the theoretical uniform expectation over 75 group nodes ($E = 700/75 approx 9.33$):
$ P(I_A = 0) = (1)/(|V_("Group")|) = (1)/(75) approx 1.33% $

A Chi-Squared goodness-of-fit test confirmed that the empirical distribution shows no statistically significant deviation from a true uniform random distribution ($chi^2 = 0.012, p = 0.913$). The positional artifact was conclusively eradicated.

== Methodological Guidelines for Security Graph Learning

Grounding our findings in the security machine learning principles of Arp et al. @arp2022dos, we formulate five methodological guidelines for researchers applying Graph Neural Networks to cybersecurity:


+ *Mandate Adversarial Trivial Baselines (Arp et al. Pitfall 3):* Before training deep neural networks, evaluate deterministic 1-line heuristics on raw tensor indices and local feature flags. If a trivial rule achieves high accuracy, the dataset contains an information-theoretic leak.
+ *Ensure Baseline Information Parity (Arp et al. Pitfall 7):* Never compare graph models against flat feature-only baselines unless the flat baselines are also provided with basic graph summary statistics (e.g., degree counts, path indicators).
+ *Enforce Zero-Shot Out-of-Distribution Stress Tests (Arp et al. Pitfall 6):* Evaluating models exclusively on random in-distribution splits masks shortcut learning. Benchmark security models on adversarial zero-shot edge distributions where features and topologies are intentionally decoupled.
+ *Subject Synthetic Generators to Entropy Audits:* Compute mutual information $I(Y; A)$ between class labels and non-semantic generator variables (such as memory indices, node identifiers, or generation timestamps). Any non-zero mutual information indicates synthetic bias.
+ *Validate Against Symbolic Ground Truth:* In security domains governed by formal access control rules, always maintain an exact symbolic oracle (such as BFS path validation) to audit neural model predictions.


