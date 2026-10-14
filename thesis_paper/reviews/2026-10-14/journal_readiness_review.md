CertGraph — independent journal-readiness review

Review date: 14 October 2026. Repository commit reviewed: aa4aa8b. This is a research assessment, not a journal acceptance prediction.

**Verdict**

Do not submit the current manuscript to a high-end security journal yet. The repository contains substantial implementation and useful exploratory results, but the evidence does not substantiate its main claims of architectural necessity, superiority to established tools, independently validated enterprise detection, or a completed neuro-symbolic autonomous defense system. Several problems require new experiments or a change in research question; rewriting alone will not resolve them.

Publication remains possible, particularly through a rigorous ADCS benchmark and generalization study, or a measured study of learned screening combined with symbolic checking. Neither contribution is established to high-end journal standards by the current artifacts. A lower-ranked journal would not make unsupported results or invalid proofs acceptable.

**Review scope and limits**

I inspected the journal source, thesis chapters and proofs, research source modules, saved JSON results, evaluation data provenance, and the conversation history. I checked relevant primary literature and current tool documentation. I independently executed bounded generator, rule-baseline, exact graph-overlap, and attention-derivative diagnostics. I did not retrain the neural models, deploy or attack a lab, rerun the entire defense benchmark, independently reproduce the saved neural scores, or perform an exhaustive systematic literature review.

The accompanying diagnostic_checks.py and diagnostic_results.json record the new checks. They preserve original research files and results. The diagnostic rule set was constructed after inspecting this generator; it measures benchmark simplicity, not independent real-world security correctness. Saved results are distinguished from newly reproduced checks below. Missing evidence means not found in this workspace, not proof that an experiment was never performed elsewhere.

**What the work currently implements**

Phase 1 builds an HGAT link-prediction prototype around ESC13. Phase 2 uses two relation-specific graph-attention layers, type-specific residual projections, and a template classification head. It predicts ESC1, ESC2, ESC3, ESC4, ESC9, ESC13, or Safe in generated environments. Other modules implement tabular and graph baselines, controlled injection into BloodHound-derived topology, perturbation studies, inference timing, and static greedy edge removal.

This is primarily a study of template classification on constructed graphs. Detecting a template class, identifying a principal-specific exploitable path, observing an actual attack, and safely remediating a running directory are different tasks. The manuscript frequently treats them as interchangeable.

**What the results actually support**

| Evidence | Recorded result | Defensible interpretation |
|---|---:|---|
| CertGraph cross-validation | Macro-F1 0.99857 ± 0.00286 | Fits this synthetic distribution extremely well |
| Graph-augmented MLP | 0.99714 ± 0.00350; ordinary paired p=0.6213 | No demonstrated GNN advantage over this information-matched baseline; non-significance is not proof of equivalence |
| Graph-augmented RF | 0.98712 ± 0.00836; p=0.0780 | Also competitive; no conventional significance at .05 in this test |
| Hetero-SAGE comparison | 1.0000 ± 0.0000 | Attention is not established as necessary for this task |
| No-skip ablation | 0.47677 ± 0.02394 | Removing this implementation's local feature route hurts this configuration; not a universal theorem |
| Zero-shot hard negatives | CertGraph 1/63; augmented MLP 18/63; custom symbolic baseline 53/63 | Poor specificity under this deliberately changed training/test protocol |
| Greedy defense, budget 24 | 68.64% initially reachable source–target pairs disconnected | A useful static heuristic experiment on 30 small synthetic graphs |
| Largest saved timing | 421.10 ± 70.74 ms, 10,002 nodes, 779,226 edges | Sub-second forward computation in this microbenchmark |

Sources: thesis_research/results/phase2/{cv_results,gnn_baselines_results,ablation_results,hard_negatives_results,defense_results,scalability_results}.json.

The zero-shot models are separately trained without hard-negative exposure (hard_negatives.py:174), whereas regular CV uses generator defaults that include hard negatives (train.py:376; generator.py:514). It is misleading to imply that the very same CV/deployment checkpoint was necessarily the model obtaining 1/63. This controlled experiment is informative, but the protocol difference must be explicit.

All 63 selected hard negatives are Safe. Accuracy there is specificity on that subset; an always-Safe classifier obtains 63/63 while providing no useful attack detection. Joint positive/negative evaluation is necessary before claiming robustness. Failure alone also does not conclusively establish the causal mechanism of shortcut learning; counterfactual and attribution interventions would strengthen that explanation.

**Submission blocker 1: benchmark saturation and weak symbolic baseline**

I regenerated the 700-case CV corpus with the current code and seed 42. The target templates contain only 24 unique 10-dimensional feature vectors. ESC1, ESC2, ESC9, and ESC13 each use one target vector; ESC3 uses two. There are many graphs, but little variation in the certificate configurations central to the target task.

The current custom symbolic baseline makes 64 errors: 44 ESC4 cases and 20 Safe cases classified as ESC3. Its `(cra or ras) and nma` branch executes before its vulnerable-ACL branch (bfs_baseline.py:85). Merely requiring an authorized signature is treated too broadly as evidence for ESC3.

A short diagnostic rule set, checking ACL cases first and narrowing that ESC3 predicate, obtains 700/700 on the CV corpus and 63/63 on the regenerated hard-negative subset. Predictions inspect only supplied features and direct edges; they do not read the class label. This is a post-hoc generator-matching diagnostic, not a new held-out benchmark or certified ADCS oracle. Nevertheless, it defeats the inference that these datasets demonstrate an indispensable benefit from deep graph learning. It also shows that the symbolic baseline's reported shortfall need not be a limitation of symbolic reasoning.

The generator does not supply an independent execution-based oracle for actual exploitation. It chooses a label, constructs corresponding attributes and relationships, and tests whether models recover that construction. A credible benchmark should include multiple independent ways of instantiating the same exploit and benign cases that differ in exactly one relevant precondition. Real exploitability must include CA publication, authorization, group closure, trust, policy and patch-dependent prerequisites as applicable.

The positional-index argument also needs revision. A standard message-passing GNN without node-ID features is permutation equivariant. Fixed indices may harm generation or a hand-written evaluator, but their existence alone does not prove that this GNN learned array indices. Test consistent node relabeling before attributing model behavior to positional leakage.

**Submission blocker 2: external evaluation and tool claims exceed the implementation**

bloodhound_parser.py:208 explicitly injects templates and CAs. At :229 it calls the same TEMPLATE_GENERATORS used by the synthetic training pipeline, and at :239 it assigns the requested labels. case_study.py, community_eval.py, and fresh_data_eval.py use this mechanism. These evaluations are controlled injections into collected AD topology, not independent detection of collected real ADCS configurations. Repeated dates and related GOAD domains do not establish independent organizational replication. The community sample README also identifies a GOAD origin.

adsynth_adapter.py:1 describes a locally implemented tiered generator inspired by ADSynth. It imports the same template generators at :14. This is not evidence of independent replication on the original ADSynth implementation or a new source of ADCS labels. Call it a tiered synthetic topology experiment unless actual ADSynth provenance is supplied.

In tool_comparison.py:163-170, the names Certipy and BloodHound refer to a local RuleBaseline and a custom query engine. The CV class called BloodHoundBFSBaseline inspects direct edges; it does not run BloodHound. Surrogate baselines may be useful if labeled honestly, but their scores cannot establish real product superiority.

Current primary documentation directly contradicts the claim that Certipy is blind to ESC13: its v5 release adds ESC13 support, and its introduction distinguishes template identification from downstream group-privilege analysis. BloodHound already represents ADCS objects and combines relations into attack edges. Sources: [Certipy v5 announcement](https://github.com/ly4k/Certipy/discussions/270), [Certipy introduction](https://github.com/ly4k/Certipy/wiki/01-%E2%80%90-Introduction), [SpecterOps ADCS graph implementation](https://specterops.io/blog/2024/01/24/adcs-attack-paths-in-bloodhound-part-1/).

Ordinary visited-node BFS reachability is O(V+E), not inherently exponential. Enumerating every path can be exponential, and complicated query workloads can be expensive, but those are different problems. The manuscript's generic exponential-BFS rationale and 12.4× BloodHound speedup require replacement by measured, equivalent-task comparisons.

**Submission blocker 3: central system metrics have no traceable implementation/results**

The journal reports 18.2 ms neural screening, 110.6 ms verification, 128.8 ms total, a threshold study on 600 templates, zero false positives/negatives, and continuous LDAP USN synchronization (manuscript.tex:435-457). I found no corresponding hybrid evaluation implementation, USN synchronization implementation, or saved result artifact in the research source/results/notebooks searched.

Similarly, the 96% benign/0.9941 macro-F1/0.9982 PR-AUC study, R-GCN 0.9240, homogeneous GAT 0.8912, and no-reverse-relations 0.9412 rows are not traceable to the inspected research code and saved outputs. The actual GNN results contain homogeneous GCN, Hetero-GCN, and Hetero-SAGE. These are different architectures. The journal also gives standard deviations that disagree with saved artifacts and sometimes copies macro-F1 values into the accuracy column.

Every such result needs its dataset, exact experiment, predictions, timing procedure, configuration, and artifact. If unavailable, remove it or clearly identify it as a proposed design. A table, slide, thesis paragraph, or earlier assistant statement does not establish that an experiment occurred.

There is also an arithmetic issue: 62 candidates from 600 means 89.7% of all templates are excluded. With 60 true positives retained and 540 actual safe templates, excluding 538 safe templates would be 99.6% of safe templates, not 89.7%. These denominators must be explicit.

**Submission blocker 4: both journal theorems need substantive repair**

Theorem 1 (manuscript.tex:253-275) claims that removing skips makes target-feature derivatives zero, and adding skips guarantees a strictly positive Jacobian lower bound.

The first statement ignores attention coefficients that depend on target features. The diagnostic computes a valid scalar no-self-loop attention example with derivative approximately 0.28463, not zero. The second statement ignores cancellation between graph and residual derivatives. For h(x)=F(x)+x with F(x)=-x, the derivative is zero despite an identity skip. Rectangular projection products may also vanish despite each factor having nonzero reported singular values. Activations add further conditions. The empirical ablation remains useful but cannot prove these universal statements.

Theorem 2 in the journal (manuscript.tex:462-470) states that separating every source in S from every target in T by minimum-cost edge deletion is NP-hard. For the stated complete-separation problem with a cost budget, add a super-source connected to S and a super-sink connected from T by uncuttable edges, then compute a standard minimum cut and compare its cost with the budget. The reduction incorrectly equates selected forbidden pairs with all Cartesian S×T pairs. A graph containing only s1→t2 already refutes that equivalence when the specified pairs are (s1,t1) and (s2,t2).

The thesis appendix uses a different, pair-specific formulation, which must not be conflated with the journal statement. Pair-specific directed multicut and maximizing disrupted pairs under a limited budget are separate problems. State the actual operational objective precisely and prove only the relevant theorem. Renaming a known cut problem is not, by itself, a strong novelty claim. For the standard cut computation see [NetworkX minimum-cut documentation](https://networkx.org/documentation/stable/reference/algorithms/generated/networkx.algorithms.flow.minimum_cut.html).

**Submission blocker 5: defense evidence is static and operationally simplified**

The measured defense compares random, degree-based, and greedy strategies on 30 synthetic graphs averaging about 80.8 nodes and 200 edges. The 68.64% value measures disconnected source–target pairs, not the fraction of all distinct attack paths, actual compromises prevented, or business disruption avoided (defense_eval.py:68).

The graph conversion assigns cost 1 to every edge and includes all modeled relations (defense_eval.py:37-53), including computational reverse relations. These are not automatically valid independently revocable AD permissions. A DiGraph also collapses parallel relations between the same endpoints. The heuristic counts one current shortest path per active pair, not every attack path (:137-143). A production interpretation requires preserving relationship semantics, restricting allowable actions, measuring business effects, and checking alternate routes after each action.

The MARL metrics are explicitly labeled notional_theoretical_simulation and entered as constants (:236-243). The policy-loss curves are generated from analytic exponentials and noise (:374-382). They are illustrations, not training evidence. Their explicit labels are good, but they cannot support a completed co-adaptive defense claim. Keep them out of empirical comparisons.

**Other reproducibility issues**

1. My hash check found that 45 of the 200 graphs regenerated by tool_comparison.py exactly overlap the 700-case CV corpus. generate_dataset uses seed+env_id, so changing the base seed does not guarantee independent sets. The selected checkpoint may have trained on overlapping graphs. This is a current-source finding, not proof of the precise provenance of older JSON results; freeze split manifests and identify the selected training split.
2. train.py selects the saved checkpoint by best test-fold F1 (:423). Do not use a test-selected model as the basis for claims of untouched external evaluation. Select through validation and freeze the final test set.
3. The primary CV code uses one five-fold split and ordinary paired t-tests (:477). The thesis separately discusses corrected values; retain explicit computation and do not mix corrected and uncorrected p-values in the journal. Prefer independent environment-level repeated experiments, paired confidence intervals, and a predeclared evaluation protocol. p=.62 means insufficient evidence for a difference, not statistical equivalence.
4. The current timing artifact is 421 ms at 779,226 edges, not 343 ms at 765,000 edges. scale_test.py times a randomly initialized architecture, which can support a forward-cost microbenchmark but not detection accuracy at that scale. Memory is measured before inference using cumulative process peak RSS on CPU; a flat value does not establish constant memory consumption.
5. Perturbation experiments should distinguish missing observations from actual security changes. If the graph is truly remediated, ground truth may change; if collection misses an edge, the hidden true graph stays fixed. Randomly dropping forward and reverse edges independently can leak evidence through the retained counterpart. Compare equally informed baselines under the same observation model.
6. Phase 1 injects the positive impersonation edge (dataset.py:435), includes it in the encoder graph, and computes AUC on training predictions (train.py:84,130,153). Its AUC=1 is not a held-out link-prediction result.
7. The manuscript describes ELU/LayerNorm and a 64→32→7 head. The current implementation uses ReLU and a 16→16→7 head, with a 32×4 first layer (model.py:43-104; train.py:48). Results must be attached to the architecture actually evaluated.
8. The current review environment has torch 2.12.0+cpu and torch_geometric 2.8.0, whereas the README describes older versions and requirements are unpinned. Record an environment lock, checkpoint/data hashes, source commit, and command for every final experiment.

**Novelty assessment against prior work**

| Proposed contribution | Assessment |
|---|---|
| ADCS-specific heterogeneous classification | Potentially useful domain adaptation; a narrow first-use claim is not established by this targeted search and is insufficient alone |
| Graph attention / residuals | Established building blocks; no new learning operator is implemented here |
| Typed ADCS graph and multi-hop paths | Existing tools already model typed ADCS relationships; novelty must identify the additional semantics or capability |
| Stronger accuracy than flat baselines | Mostly an information-access comparison; graph-augmented MLP and Hetero-SAGE undermine the necessity claim |
| Hard-negative failure analysis | The most promising present observation, but needs realistic counterfactuals, mixed-label tests, multiple models/seeds, and independent validation |
| Neuro-symbolic screening | Plausible system direction; must demonstrate a benefit over full symbolic checking and cheap non-neural prefilters |
| Autonomous interdiction | Well-populated prior-art area; current static greedy experiment is incremental and lacks operationally valid actions |
| Formal theory | Current journal statements are invalid; repaired statements need meaningful novelty and correspondence to the implemented model |

Relevant primary work includes [Graph Attention Networks](https://arxiv.org/abs/1710.10903), [GCNII residual/identity methods](https://proceedings.mlr.press/v119/chen20v.html), [ADSynth, DSN 2024](https://ieeexplore.ieee.org/document/10647035/), [Guo et al., AAAI 2023 edge blocking](https://ojs.aaai.org/index.php/AAAI/article/view/25701), [Goel et al., dynamic AD defense](https://arxiv.org/abs/2406.19596), and [Goel et al., GNN-approximated co-evolutionary defense preprint](https://arxiv.org/abs/2505.11710). The latter already combines GNNs, attacker–defender modeling, and evolutionary defense; distinguish the preprint's status from peer-reviewed work. Earlier [Heat-ray](https://www.microsoft.com/en-us/research/publication/heat-ray-combating-identity-snowball-attacks-using-machine-learning-combinatorial-optimization-and-attack-graphs/) also combines machine learning and attack-graph optimization. Merely combining those categories is not new.

A rigorous negative-results/benchmark paper is possible in principle, but documenting errors in one's own generator is not enough by itself. The study needs a generalizable insight, externally meaningful cases, and reusable evaluation methods. [Arp et al., USENIX Security 2022](https://www.usenix.org/conference/usenixsecurity22/presentation/arp) already establishes broad security-ML evaluation pitfalls; identify what is newly learned about ADCS specifically.

The CertGraph name also already appears in an unrelated [2024 cloud-security certification knowledge-graph paper](https://pinzger.github.io/papers/Schoeberl2024-certgraph.pdf) and a [certificate OSINT tool](https://github.com/lanrat/certgraph). This is a discoverability/naming concern, not evidence that they preempt the ADCS-specific research.

**Recommended route to a credible paper**

Focus the paper on one question: Under what conditions does learned screening improve the cost, prioritization, or robustness of sound ADCS auditing compared with direct symbolic analysis?

A possible working title is: “Learning versus Symbolic Verification for ADCS Misconfiguration Detection: A Counterfactual Benchmark.” If an implemented hybrid demonstrates a measurable advantage, revise the title around that actual advantage. Avoid promising autonomous defense unless it becomes a separate validated contribution.

Proceed in this order:

1. Create a claim-to-artifact ledger. Every number needs a reproducible command, exact inputs/split, configuration, predictions, and source commit. Remove unsupported claims and illustrations presented as measurements. Reconcile the journal with code before adding more sections.
2. Define the target: vulnerable configuration versus exploitable principal–template path versus active exploitation. Build an independent oracle and validate labels against controlled Windows/ADCS behavior. Include safe counterfactuals and overlapping ESC conditions; use multilabel outputs or explicitly justify precedence.
3. Replace the saturated generator with varied, independently labeled cases: nested groups, denied and inherited permissions, CA/template publication, trust and policy conditions, patch variations, and multiple independent lab configurations. Preserve disjoint organizations/topology families and counterfactual families across splits. Real enterprise access helps, but a well-designed independent lab benchmark can still be valuable if its limits are explicit.
4. Benchmark actual pinned Certipy and BloodHound versions, a correct symbolic implementation, simple prefilters, graph-augmented trees/MLPs, and appropriate GNNs on equivalent information and tasks. Measure the cost of feature extraction and preprocessing too. Do not add complexity merely to make the GNN win.
5. Implement the hybrid only if there is a demonstrated bottleneck. Measure end-to-end recall, false-positive rates, calibration, verification work, and runtime. Evaluate full symbolic verification, rule-prefilter+verification, tabular-prefilter+verification, and GNN-prefilter+verification at matched recall. For a sequential filter, overall recall cannot exceed the first-stage recall unless rejected cases have another recovery path.
6. Run repeated independent seeds and environment-level tests, preserve per-case predictions, estimate uncertainty, and report operational base rates. A test with zero errors does not establish a universal zero-error guarantee.
7. If retaining remediation, map actions to real permissions, use measured or defensible disruption costs, preserve benign workflow constraints, and compare against exact optima on small instances and strong published methods. Otherwise keep this component explicitly preliminary or move it to future work.

Success means a defensible new result, not a particular F1 threshold. Possible outcomes include a demonstrably faster high-recall auditor, a validated failure mode affecting several approaches, a useful public benchmark, or evidence that simple symbolic methods are preferable for the fully observed task. Any of these is more credible than retaining a broad superiority claim unsupported by the experiments.

**Journal choice**

Q1 is a year-, category-, and database-specific ranking, not an acceptance criterion. This review does not certify current quartiles. Check the exact index your university recognizes before choosing a venue.

IEEE TDSC is a plausible scope match for a mature, validated identity-security system; its [official scope](https://www.computer.org/digital-library/journals/tq/cfp-dependable-secure-computing) emphasizes foundations, mechanisms, and evaluation. IEEE TIFS is another possible scope match if a strong methodological security contribution and reproducible evidence emerge; its [official page](https://signalprocessingsociety.org/publications-resources/ieee-transactions-information-forensics-and-security/about-transactions) explicitly encourages reproducibility. The current manuscript does not meet the evidential standard I would recommend for either submission.

Do not follow the earlier generic suggestion of Computers & Security for this ML-centered paper without accounting for its current scope: the [Elsevier journal page](https://shop.elsevier.com/journals/computers-and-security/0167-4048) states a moratorium on submissions with significant AI/ML components. This is a concrete venue-fit obstacle regardless of manuscript quality.

My editorial assessment is “do not submit yet; substantial research revision required.” The work is worth developing, but the strongest next investment is independent ground truth, fair baselines, and one demonstrated contribution—not further cosmetic expansion of the current manuscript.
