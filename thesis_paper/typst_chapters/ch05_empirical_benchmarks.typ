= Empirical Evaluation and Benchmarks <ch:evaluation>


== Experimental Configuration and Benchmarking Setup

To rigorously evaluate CertGraph and establish reproducible empirical benchmarks, all experiments were conducted on a dedicated security machine learning workstation running Linux 6.x. The software stack was built on Python 3.11, PyTorch 2.3.0, PyTorch Geometric 2.5.3, and Scikit-learn 1.4.2, accelerated via an NVIDIA GeForce RTX GPU with CUDA 12.2.

=== Benchmark Dataset Characteristics

The primary evaluation dataset consists of 700 independently synthesized, fully sanitized enterprise Active Directory environments generated via our overhauled `generator.py` pipeline. Each environment models an independent corporate domain comprising an average of 30 nodes and 120 directed authorization edges, capturing the structural complexity of realistic mid-sized enterprise networks.

The dataset enforces a balanced class distribution across the seven target classification classes, with exactly 100 enterprise environments per class:

+ `Safe`: Completely secure certificate templates or published templates lacking unprivileged attack paths.
+ `ESC1`: Templates with `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` enabled alongside Client Authentication EKUs, enrollable by unprivileged accounts.
+ `ESC2`: Templates configured with Any Purpose EKU or lacking EKUs, enrollable by unprivileged accounts.
+ `ESC3`: Templates specifying Certificate Request Agent EKU, enrollable by unprivileged principals.
+ `ESC4`: Templates possessing insecure Access Control Entries in their security descriptor (`GenericAll`, `WriteDacl`, `WriteOwner`) allowing low-privileged users to alter configuration flags.
+ `ESC9`: Templates lacking security extension flags (`CT_FLAG_NO_SECURITY_EXTENSION`) in environments susceptible to strong certificate mapping bypasses.
+ `ESC13`: Templates referencing Issuance Policy OIDs that map directly to high-value Tier-0 administrative security groups.



To guarantee absolute scientific reproducibility, global random seeds were deterministically fixed to 42 across Python `random`, NumPy `random.seed`, and PyTorch `torch.manual_seed` runtimes.

=== Hyperparameter Specifications

@tab:hyperparams summarizes the standardized hyperparameter configuration employed across all neural and tabular model trainings.

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 10 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Hyperparameter*], [*Value*], [*Architectural Description / Rationale*]),
    [Hidden Feature Dimension ($d$)], [$64$], [Optimal capacity balancing expressiveness and over-fitting],
    [Attention Heads ($K$)], [$4$], [Multi-head projection ($d_("head") = 16$ per head)],
    [Convolutional Layers ($L$)], [$2$], [Receptive field sufficient to capture 2-hop delegation chains],
    [Learning Rate ($eta$)], [$10^(-3)$], [Initial learning rate for AdamW optimizer],
    [Learning Rate Schedule], [Cosine], [Smooth annealing with $T_("max") = 100$ epochs],
    [Weight Decay ($lambda_("reg")$)], [$10^(-4)$], [$L_2$ weight regularization on projection tensors],
    [Dropout Rate ($p$)], [$0.2$], [Applied following LayerNorm in each GAT layer],
    [Batch Size], [$32$], [Mini-batch graph collation via PyG `DataLoader`],
    [Training Epochs], [$100$], [Early stopping invoked if validation loss plateaus for 15 epochs],
  )
],
  caption: [Hyperparameter Specifications for Model Training and Optimization.],
) <tab:hyperparams>


== In-Distribution 5-Fold Cross-Validation

We benchmarked CertGraph against six baseline classifiers across stratified 5-fold cross-validation on the 700 enterprise environments. When conducting $K$-fold cross-validation, the training sets across folds overlap significantly (each pair of training sets shares $(K-2)/(K-1)$ of the data), violating the independent sample assumption of the standard Student's $t$-test. As proved by Nadeau and Bengio (2003) @nadeau2003inference, this training-set overlap causes the standard $t$-test to underestimate variance, yielding inflated Type-I error rates. To provide rigorous statistical hypothesis testing, we report both standard paired $t$-test $p$-values ($p_("std")$) and corrected repeated cross-validation statistics ($p_("corr")$) based on the Nadeau-Bengio variance estimator:
$ hat(sigma)^2_("corr") = ( (1)/(K) + (n_2)/(n_1) ) hat(S)^2 $

where $n_2$ denotes the test fold size and $n_1$ denotes the training fold size. Under our 5-fold cross-validation scheme ($K=5$, $n_2/n_1 = 0.20/0.80 = 0.25$), the standard error is scaled by $sqrt(1/K + n_2/n_1) / sqrt(1/K) = sqrt(0.45 / 0.20) = sqrt(2.25) = 1.50$, yielding the conservative corrected test statistic:
$ t_("corr") = (t_("std"))/(1.50),   "with " nu = K - 1 = 4 " degrees of freedom." $


#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 8 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Model Architecture*], [*Macro-F1*], [*Accuracy*], [*Std $p$-val*], [*Corr $p$-val*], [*Significance*]),
    [*CertGraph (Hetero-GAT)*], [$bold(0.9986 plus.minus 0.0029)$], [$bold(0.9986 plus.minus 0.0029)$], [---], [---], [_Reference_],
    [Graph-Augmented MLP], [$0.9971 plus.minus 0.0035$], [$0.9971 plus.minus 0.0035$], [$0.6213$], [$0.7396$], [Not Sig.],
    [Graph-Augmented RF], [$0.9871 plus.minus 0.0084$], [$0.9871 plus.minus 0.0084$], [$0.0780$], [$0.1913$], [Not Sig.],
    [BloodHound BFS (Symbolic)], [$0.9082 plus.minus 0.0229$], [$0.9100 plus.minus 0.0215$], [$1.64 times 10^(-3)$], [$7.28 times 10^(-3)$], [$p < 0.01$],
    [Flat MLP (Features Only)], [$0.8600 plus.minus 0.0130$], [$0.8643 plus.minus 0.0118$], [$2.62 times 10^(-5)$], [$1.30 times 10^(-4)$], [$p < 10^(-3)$],
    [Flat RF (Features Only)], [$0.8384 plus.minus 0.0057$], [$0.8443 plus.minus 0.0051$], [$1.32 times 10^(-6)$], [$6.66 times 10^(-6)$], [$p < 10^(-5)$],
    [Rule-Based (Certipy Heuristic)], [$0.7791 plus.minus 0.0247$], [$0.8143 plus.minus 0.0205$], [$6.33 times 10^(-5)$], [$3.12 times 10^(-4)$], [$p < 10^(-3)$],
  )
],
  caption: [5-Fold Cross-Validation Performance Across 7 Evaluated Models on 700 Enterprise Domains (Reporting Standard and Nadeau-Bengio Corrected $p$-values vs CertGraph).],
) <tab:cv_results>


#figure(
  image("figures/confusion_matrix.png", width: 90%),
  caption: [CertGraph 7-Class Confusion Matrix.],
) <fig:conf_matrix>


=== Per-Class Performance Dissection

@tab:per_class reports the detailed per-class precision, recall, and F1 scores achieved by CertGraph across all 7 evaluation classes under 5-fold cross-validation:

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr, 2fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 9 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Class Label*], [*Precision*], [*Recall*], [*F1-Score*], [*Support (Domains)*]),
    [`Safe`], [$1.0000$], [$1.0000$], [$1.0000$], [$100$],
    [`ESC1`], [$1.0000$], [$1.0000$], [$1.0000$], [$100$],
    [`ESC2`], [$0.9901$], [$1.0000$], [$0.9950$], [$100$],
    [`ESC3`], [$1.0000$], [$1.0000$], [$1.0000$], [$100$],
    [`ESC4`], [$1.0000$], [$0.9900$], [$0.9950$], [$100$],
    [`ESC9`], [$1.0000$], [$1.0000$], [$1.0000$], [$100$],
    [`ESC13`], [$1.0000$], [$1.0000$], [$1.0000$], [$100$],
    [*Macro Average*], [$bold(0.9986)$], [$bold(0.9986)$], [$bold(0.9986)$], [$bold(700)$],
  )
],
  caption: [CertGraph Per-Class Precision, Recall, and F1 Scores under 5-Fold Cross-Validation.],
) <tab:per_class>


*Critical Analysis of In-Distribution Findings:*

+ *Decisive Superiority Over Static Signatures and Flat ML:* CertGraph outperforms industry signature heuristics (Certipy) by $+28.2%$ in Macro-F1 ($0.9986$ vs $0.7791$) and flat ML by $+16.1%$ ($0.9986$ vs $0.8600$). The signature tool suffers because it inspects template flags in isolation without evaluating authorization path connectivity, generating frequent false positives.
+ *Statistical Equivalence to Graph-Augmented MLP and Benchmark Saturation:* The comparison between CertGraph and Graph-Augmented MLP yields standard $p = 0.6213$ and Nadeau-Bengio corrected $p = 0.7396$, confirming that on in-distribution synthetic data, there is no statistically significant difference between a multi-layer GNN and a flat MLP provided with four topological summary counts. Furthermore, the headline score of $0.9986 plus.minus 0.0029$ corresponds to exactly one misclassified template out of 700 ($699/700 = 0.99857$). A 7-node decision tree recovers $0.9928$ (representing approximately 5 errors out of 700), and the single-head attention ablation achieves $1.0000$. Because ground-truth labels in synthetic generators are generated from access-control rules, in-distribution cross-validation primarily evaluates rule recovery on synthesized data rather than generalized security reasoning, necessitating the out-of-distribution hard-negative evaluation in @sec:hard_negatives.
+ *High Precision Across Core Attack Vectors:* Out of 700 evaluation domains, CertGraph incurred only a single false positive (misclassifying a subtle ESC4 DACL-delegation variant as ESC2) and a single false negative, maintaining $>0.99$ precision and recall across all evaluated classes.
+ *Architectural Justification: Why GNNs Over CART Trees and Graph-Augmented MLPs:* While a 7-node CART decision tree ($0.9928$ F1) and a Graph-Augmented MLP ($0.9971$ F1) achieve competitive scores on synthetic rule recovery, the heterogeneous GNN architecture is indispensable for real-world enterprise deployment for four fundamental reasons: 





=== Evaluation Under Realistic Class Imbalance and Enterprise Base Rates <sec:class_imbalance>

In production corporate directories, certificate template distributions are heavily right-skewed: the vast majority of active templates (> 95%) are configured safely, while true privilege escalation vulnerabilities represent rare anomalies. Evaluating models purely under balanced cross-validation can mask calibration errors and inflated false-alarm rates.

To rigorously benchmark CertGraph under realistic operational conditions, we synthesized an enterprise-scale *Class-Imbalanced Evaluation Benchmark* comprising $N = 2{,}000$ evaluated templates across 200 directory forests, structured with an extreme *96.0% Safe Base Rate*:

+ *Safe Templates:* $1{,}920$ benign templates ($96.0%$).
+ *Vulnerable Templates:* $80$ vulnerable templates ($4.0%$), distributed evenly across the 6 attack classes ($approx 13"--"14$ templates each for ESC1, ESC2, ESC3, ESC4, ESC9, and ESC13).



Under heavy class imbalance, traditional Accuracy is dominated by the majority class and becomes uninformative. We therefore report Precision-Recall Area Under the Curve (*PR-AUC*), Macro-F1, Precision, Recall, *Expected Calibration Error (ECE)* across 10 probability bins, and the *Brier Score* ($(1)/(N) sum_(i=1)^N sum_(c=1)^C (p_(ic) - y_(ic))^2$):

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 8 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Model Architecture*], [*PR-AUC*], [*Macro-F1*], [*Precision*], [*Recall*], [*ECE*], [*Brier Score*]),
    [*CertGraph (Hetero-GAT)*], [$bold(0.9982)$], [$bold(0.9941)$], [$bold(0.9925)$], [$bold(0.9958)$], [$bold(0.0142)$], [$bold(0.0031)$],
    [Graph-Augmented MLP], [$0.9854$], [$0.9782$], [$0.9680$], [$0.9887$], [$0.0385$], [$0.0118$],
    [Graph-Augmented RF], [$0.9610$], [$0.9520$], [$0.9412$], [$0.9630$], [$0.0512$], [$0.0195$],
    [BloodHound BFS (Symbolic)], [$0.9125$], [$0.8984$], [$0.8870$], [$0.9100$], [---], [$0.0754$],
    [Flat MLP (Features Only)], [$0.8240$], [$0.8125$], [$0.7950$], [$0.8310$], [$0.0915$], [$0.0620$],
    [Flat RF (Features Only)], [$0.7985$], [$0.7850$], [$0.7620$], [$0.8100$], [$0.1140$], [$0.0785$],
    [Rule-Based (Certipy Heuristic)], [$0.7250$], [$0.7180$], [$0.6840$], [$0.7560$], [---], [$0.1120$],
  )
],
  caption: [Model Performance and Calibration Under Realistic Enterprise Class Imbalance (96.0% Safe Base Rate, $N = 2{,}000$ Templates).],
) <tab:imbalanced_results>


As shown in @tab:imbalanced_results, CertGraph maintains remarkable stability under extreme base-rate skew, achieving $"PR-AUC" = 0.9982$ and $"Macro-F1" = 0.9941$. Crucially, CertGraph achieves an Expected Calibration Error of only $bold(0.0142)$ and a Brier Score of $bold(0.0031)$, confirming that the predicted Softmax probabilities correspond directly to true empirical exploitability likelihoods. In sharp contrast, flat feature models suffer significant calibration degradation ($"ECE" > 0.09$, Precision dropping to $0.7950$), generating frequent false alarms that overwhelm security operations teams when benign samples heavily dominate the prior.

== Systematic Architectural Ablation Studies <sec:ablation_results>

To isolate the contribution of each architectural component within CertGraph, we executed controlled ablation experiments across four variants under identical 5-fold cross-validation splits.

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 5 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Architecture Variant*], [*Macro-F1*], [*$Delta$ vs Full*], [*Std $p$-val*], [*Corr $p$-val*], [*Significance*]),
    [*Full CertGraph (Hetero-GAT)*], [$bold(0.9986 plus.minus 0.0029)$], [---], [---], [---], [_Reference_],
    [Single-Head Attention ($K = 1$)], [$1.0000 plus.minus 0.0000$], [$+0.0014$], [$0.3739$], [$0.5415$], [Not Sig.],
    [No Graph Context (Features Only)], [$0.8600 plus.minus 0.0130$], [$-0.1386$], [$2.62 times 10^(-5)$], [$1.30 times 10^(-4)$], [$p < 10^(-3)$],
    [*No Skip Connections ($W_("skip") = 0$)*], [$bold(0.4768 plus.minus 0.0532)$], [$bold(-0.5218)$], [$bold(1.31 times 10^(-6))$], [$bold(6.61 times 10^(-6))$], [$bold(p < 10^(-5))$],
  )
],
  caption: [Systematic Architectural Ablation Study of CertGraph Components (Reporting Standard and Nadeau-Bengio Corrected $p$-values vs Full CertGraph).],
) <tab:ablation_results>


#figure(
  image("figures/ablation_comparison.png", width: 90%),
  caption: [Ablation study comparison highlighting the performance collapse when residual skip connections are disabled.],
) <fig:ablation_fig>


*Empirical Confirmation of Theorem 1:*
The most striking result of the ablation suite is the consequence of removing residual skip connections ($W_("skip") = 0$). In standard undirected graph benchmarks (e.g., Cora, Citeseer), omitting skip connections typically causes a minor degradation of $2-5%$. In sharp contrast, on Active Directory identity graphs, removing skip connections triggers a *severe collapse in Macro-F1 from $0.9986$ to $0.4768$* (standard $p = 1.31 times 10^(-6)$, Nadeau-Bengio corrected $p = 6.61 times 10^(-6)$, representing a $>52%$ absolute drop).

This empirical collapse directly confirms @thm:representation_preservation: without residual skip connections, a certificate template node aggregates messages exclusively from its incoming neighbors during Layer 1, completely discarding its own initial 10-dimensional configuration feature vector $x_("Template")$ ($diff h_t^((1)) / diff x_t = bold(0)$). Furthermore, low-in-degree principals suffer representation decay across successive message-passing hops. The network loses direct sensitivity to critical configuration flags (such as `ENROLLEE_SUPPLIES_SUBJECT` and Client Authentication EKUs), destroying its ability to differentiate dangerous templates from secure ones. Parameterized skip connections preserve initial attributes and maintain non-vanishing gradient bounds, preventing representation collapse.

== The Zero-Shot Adversarial Hard Negative Benchmark <sec:hard_negatives>

While in-distribution cross-validation demonstrated near-perfect metrics for both CertGraph and Graph-Augmented MLP, the critical scientific question remained: _Did the neural models learn to reason about topological graph reachability, or did they merely exploit feature-level statistical shortcuts?_

To answer this question, we established an out-of-distribution *Zero-Shot Adversarial Hard Negative Benchmark*:

+ *Training Environment:* 1,400 clean enterprise domains containing zero hard negative samples. Every template bearing vulnerable configuration flags possessed a valid, unprivileged authorization path.
+ *Adversarial Test Suite:* 63 out-of-distribution enterprise domains containing "Hard Negative" templates. Each hard negative template had dangerous configuration flags active (e.g., `ENROLLEE_SUPPLIES_SUBJECT` or policy links enabled), but all incoming `Enroll` and DACL permissions were strictly restricted to administrative Tier-0 accounts. The ground-truth security label was strictly `Safe`.



#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr, 2fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 8 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Model Architecture*], [*Safe Count*], [*Accuracy*], [*95% Wilson CI*], [*Observed Failure Mode*]),
    [*BloodHound BFS (Symbolic)*], [$bold(53 / 63)$], [$bold(84.13%)$], [$[73.1%, 91.2%]$], [*Verifies path absence via search*],
    [Graph-Augmented MLP], [$18 / 63$], [$28.57%$], [$[18.8%, 40.8%]$], [Weak topological count conditioning],
    [*CertGraph (Hetero-GAT)*], [$bold(1 / 63)$], [$bold(1.59%)$], [$[0.3%, 8.5%]$], [*Shortcut Collapse on Template Flags*],
    [Flat MLP (Features Only)], [$0 / 63$], [$0.00%$], [$[0.0%, 5.7%]$], [Fooled by template flags],
    [Flat RF (Features Only)], [$0 / 63$], [$0.00%$], [$[0.0%, 5.7%]$], [Fooled by template flags],
    [Graph-Augmented RF], [$0 / 63$], [$0.00%$], [$[0.0%, 5.7%]$], [Tree split prioritized local flags],
    [Rule-Based (Certipy Heuristic)], [$0 / 63$], [$0.00%$], [$[0.0%, 5.7%]$], [Static signature false positive],
  )
],
  caption: [Zero-Shot Adversarial Hard Negative Benchmark Results ($n = 63$ Test Environments).],
) <tab:hn_results>


#figure(
  image("figures/hard_negatives_comparison.png", width: 90%),
  caption: [Zero-shot adversarial evaluation demonstrating the collapse of pure neural models due to shortcut learning compared to symbolic BFS path traversal.],
) <fig:hn_fig>


=== Theoretical Post-Mortem: Under-Specification and Shortcut Collapse

The empirical results in @tab:hn_results establish crucial insights into the limits of pure deep learning on security graphs:

+ *Failure of Pure Neural Models on Hard Negatives:* Despite achieving $0.9986$ F1 in-distribution, CertGraph correctly classified only *1 out of 63* adversarial hard negatives, collapsing to *1.59% accuracy* (95% Wilson score interval: $[0.3%, 8.5%]$). All flat feature models collapsed to *0.00% accuracy* ($[0.0%, 5.7%]$).
+ *Performance and Limitations of the Symbolic Graph Baseline:* In contrast, the symbolic baseline (BloodHound BFS) correctly resolved *84.13%* ($53/63$, 95% Wilson CI: $[73.1%, 91.2%]$) of the adversarial environments. While exact path-reachability would achieve 100% if labels depended solely on reachability, the simplified BFS baseline evaluated primary containment and enrollment edges without evaluating fine-grained Discretionary Access Control List (DACL) permission masks (e.g., `GenericAll` vs write rights on parent containers vs explicit deny ACEs), leading to 10 discrepancies where full access evaluation is required.
+ *Under-Specification and Shortcut Convergence:* The underlying driver of neural collapse is the well-known machine learning challenge of *under-specification* and spurious shortcut learning (Arp et al., 2022 @arp2022dos; Geirhos et al., 2020 @geirhos2020shortcut; Ye et al., 2026 @ye2026cleverhans; Bell and Wang, 2024 @bell2024pragmatic). In the standard training set of 1,400 environments, templates configured with dangerous flags possessed a valid authorization path 100% of the time. Consequently, the two decision rules---flags $=>$ vulnerable" and path $=>$ vulnerable"---fit the training loss with equal empirical precision. Because inspecting local template flags ($x_("Template")$) requires a simple single-layer linear projection, whereas verifying multi-hop reachability requires coordinating high-order message-passing convolutions, gradient descent naturally converges to the simpler flag-based shortcut.
+ *Reconciliation with Enterprise Testbeds:* This failure underscores that pure neural models cannot guarantee soundness when evaluated on out-of-distribution counterfactual topologies. As demonstrated in @ch:case_study and formalized in @ch:neuro_symbolic, enterprise false-positive suppression on hardened templates is achieved by deploying CertGraph within the *Two-Tier Neuro-Symbolic Hybrid Architecture*, where fast neural screening is verified by targeted symbolic path deduction.



== Attention Weight Explainability and Graph Attribution

To analyze what CertGraph learns internally, we inspected the learned multi-head attention weights $alpha_(v u)^((k, r))$ across the 2-hop computational subgraph of evaluated templates.

#figure(
  image("figures/attention_explainability.png", width: 90%),
  caption: [Localized 2-hop attention weight attribution for an ESC13 template, showing concentrated attention along the valid enrollment and issuance policy path.],
) <fig:attention_exp>


As illustrated in @fig:attention_exp, for a genuinely exploitable ESC13 template, CertGraph concentrates its attention weights ($alpha > 0.85$) along the authentic privilege escalation path:

+ High attention is assigned to the incoming `Enroll` edge originating from the compromised low-privileged group.
+ High attention is assigned to the outgoing `LinksPolicy` edge terminating at the Tier-0 administrative security group.
+ Spurious or unprivileged peripheral edges receive negligible attention coefficients ($alpha < 0.05$).



This localized attribution provides Security Operations Center (SOC) analysts with interpretable evidence of why an alert was triggered, highlighting the exact authorization hops that must be severed to remediate the vulnerability.
