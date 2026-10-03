= Domain Generalization, Robustness, and Scalability <ch:robustness>


== Enterprise Operational Demands on Security Graph Learning

To successfully transition from an academic prototype to an enterprise-grade defense utility, a security machine learning model must satisfy four demanding operational criteria:

+ *Out-of-Distribution Domain Generalization:* The model must generalize across distinct enterprise architectures, organizational unit hierarchies, and administrative tiering models without requiring expensive per-customer retraining.
+ *Resilience to Incomplete Telemetry:* In operational environments, Active Directory collections are rarely complete. Endpoint firewalls, offline workstations, network timeouts, and partial SharpHound executions regularly drop $10-30%$ of directory relationships. The model must degrade gracefully under missing topological data.
+ *Robustness to Attribute Noise and Adversarial Evasion:* The model must maintain stable risk classifications even when directory attributes are noisy, corrupted, or deliberately manipulated by adversaries seeking to evade detection.
+ *Sub-Second Computational Scalability on Commodity Hardware:* Enterprise Security Operations Centers (SOCs) cannot deploy multi-hour graph analytics that exhaust server RAM. Security auditing tools must execute inference in milliseconds on commodity analyst hardware while maintaining a bounded memory footprint.



This chapter systematically evaluates CertGraph against each of these operational imperatives through transfer learning on realistic tiered enterprise graphs, extensive perturbation stress-testing, sample complexity profiling, and hardware scalability benchmarks up to 10,000 nodes.

== Domain Generalization: Transfer Learning on ADSynth Tiered Networks

To determine whether CertGraph overfits to synthetic graph topologies or generalizes to realistic identity structures, we evaluated domain adaptation against networks generated via *ADSynth* @adsynth2024dsn. 

=== The Enterprise Administrative Tiering Model and ADCS Augmentation

ADSynth implements Microsoft's official *Enterprise Access Model* (formerly the Red Forest Tiered Administrative Architecture). This architecture strictly segregates enterprise identity assets into three isolated security planes:

+ *Tier 0 (Control Plane):* Highly secured systems governing identity authentication, including Domain Controllers, Enterprise Root CAs, Active Directory Federation Services (ADFS), and Tier-0 administrative groups (`Enterprise Admins`, `Domain Admins`).
+ *Tier 1 (Management Plane):* Enterprise servers, business-critical databases, line-of-business applications, and cloud proxy hosts.
+ *Tier 2 (Workstation Plane):* User endpoints, commodity laptops, and standard non-administrative domain user accounts.



Under strict tiering, credentials and administrative privileges must never cross boundaries downward: Tier-0 administrators are prohibited from logging onto Tier-2 workstations, preventing credential harvesting. ADSynth enforces these topological constraints, generating identity multigraphs with realistic clustering coefficients, path lengths, and group nesting depths.

*Methodology for Augmenting ADCS PKI Structures.*
Because native ADSynth synthesizes identity skeletons (users, computers, groups, sessions, OUs, and administrative delegations) without Active Directory Certificate Services objects, we developed an augmentation procedure to superimpose ADCS PKI components onto the ADSynth graph skeleton. Following Microsoft's PKI design guidelines:

+ *Enterprise CAs* were assigned strictly to Tier 0, linking to root Domain Controllers via RPC enrollment endpoints.
+ *Certificate Templates* were instantiated with varying configuration profiles (ESC1, ESC2, ESC3, ESC4, ESC9, ESC13, and hardened benign baselines).
+ *Enrollment and Write DACLs* were mapped across the tiered identity hierarchy: administrative templates restricted enrollment to Tier-0 principals, while general-purpose and vulnerable templates permitted enrollment from Tier-1 servers or Tier-2 domain users, creating multi-tier privilege escalation paths.



#figure(
  image("../figures/tool_comparison_f1.png", width: 90%),
  caption: [Comparative performance (CertGraph vs BloodHound vs Certipy) across synthetic and ADSynth realistic tiered enterprise topologies.],
) <fig:tool_comp>


=== Bidirectional Domain Transfer Evaluation

We conducted bidirectional domain adaptation experiments between our synthetic benchmark dataset and ADSynth tiered enterprise graphs across 200 held-out environments:

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr, 2fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 5 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Training Source*], [*Evaluation Target*], [*Macro-F1*], [*Accuracy*], [*Generalization Assessment*]),
    [*Synthetic*], [*ADSynth (Zero-Shot)*], [$bold(1.0000)$], [$bold(1.0000)$], [*High Zero-Shot Transfer*],
    [ADSynth], [Synthetic (Zero-Shot)], [$0.9347$], [$0.9400$], [Robust Transfer ($Delta = -0.06$)],
    [ADSynth], [ADSynth (5-Fold CV)], [$1.0000 plus.minus 0.0000$], [$1.0000 plus.minus 0.0000$], [Baseline Reference],
    [Synthetic], [Synthetic (5-Fold CV)], [$0.9986 plus.minus 0.0029$], [$0.9986 plus.minus 0.0029$], [Baseline Reference],
  )
],
  caption: [Bidirectional Domain Generalization Matrix Between Synthetic and ADSynth Topologies.],
) <tab:transfer_matrix>


*Discussion of Transfer Dynamics:*
As reported in @tab:transfer_matrix, CertGraph trained exclusively on synthetic topologies and evaluated zero-shot on ADSynth tiered topologies achieved a Macro-F1 of $bold(1.0000)$ and Accuracy of $bold(1.0000)$. In the reverse direction, training on ADSynth and testing on synthetic topologies achieved a Macro-F1 of $0.9347$.

This bidirectional transfer confirms that CertGraph does not overfit to specific node counts or uniform group densities. However, as analyzed in Chapters @ch:audit and @ch:evaluation, this transfer performance must be interpreted in light of the model's reliance on intrinsic template flags ($x_("Template")$): because the template configuration schema remains identical across synthetic and ADSynth graphs, the GNN's preserved template features allow it to maintain high classification fidelity across diverse background identity topologies.

== Systematic Sensitivity and Robustness Analysis

In real-world security operations, Active Directory telemetry is frequently degraded by collection timeouts, network packet loss, and missing access control entries. Grounding our evaluation in the principled empirical framework of GNN structural and attribute robustness under perturbations formalized by Wu et al. (2025) @wu2025understanding, we subjected CertGraph to systematic perturbation stress tests evaluating topological edge deletions, configuration feature noise, and sample efficiency scaling.

#figure(
  image("../figures/robustness_analysis.png", width: 90%),
  caption: [GNN robustness evaluation under systematic edge deletions (collection gaps), configuration feature noise (attribute corruption), and training data efficiency scaling.],
) <fig:robustness_fig>


=== Topological Edge Deletions (Collection Gaps)

To simulate incomplete BloodHound telemetry resulting from network collection drops, we randomly deleted directed authorization edges from evaluation graphs at perturbation ratios of $5%, 10%, 20%, 30%, " and " 50%$.

#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr, 2fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 7 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Edge Deletion*], [*Macro-F1*], [*Accuracy*], [*Retention*], [*Impact on Defense*]),
    [$0%$ (Complete Graph)], [$1.0000$], [$1.0000$], [$100.0%$], [Pristine Baseline],
    [$5%$ Edge Deletion], [$0.9941$], [$0.9950$], [$99.4%$], [Negligible Impact],
    [$10%$ Edge Deletion], [$0.9882$], [$0.9900$], [$98.8%$], [High Retention],
    [$20%$ Edge Deletion], [$0.9754$], [$0.9775$], [$97.5%$], [Moderate Retention],
    [$30%$ Edge Deletion], [$0.9637$], [$0.9650$], [$96.4%$], [Minor Degradation],
    [$50%$ Edge Deletion], [$0.9120$], [$0.9150$], [$91.2%$], [Retains $>91%$ F1],
  )
],
  caption: [Model Performance Degradation under Systematic Topological Edge Deletions.],
) <tab:edge_perturbation>


As documented in @tab:edge_perturbation and @fig:robustness_fig, CertGraph demonstrates notable resilience to missing edges:

+ When $10%$ of edges are dropped, Macro-F1 remains high at $0.9882$.
+ When nearly a third ($30%$) of all authorization relationships are missing, CertGraph maintains over $96.3%$ Macro-F1.
+ Even under $50%$ edge removal, CertGraph retains $91.2%$ classification performance.



=== Configuration Feature Noise Perturbation

Conversely, we evaluated model sensitivity to attribute corruption by randomly flipping binary template configuration flags at rates of $5%, 10%, 20%, " and " 30%$:

+ $0%$ noise: Macro-F1 = $bold(1.0000)$
+ $5%$ bit flip: Macro-F1 = $bold(0.8412)$ ($-15.9%$)
+ $10%$ bit flip: Macro-F1 = $bold(0.7105)$ ($-28.9%$)
+ $20%$ bit flip: Macro-F1 = $bold(0.5899)$ ($-41.0%$)
+ $30%$ bit flip: Macro-F1 = $bold(0.4210)$ ($-57.9%$)



*Critical Analysis of Perturbation Asymmetry:*
The stark contrast between topological resilience (dropping $50%$ of edges causes only an $8.8%$ drop in F1) and attribute sensitivity (flipping just $5%$ of template flags causes a $15.9%$ drop in F1) provides crucial empirical corroboration of the shortcut learning phenomenon identified in @ch:audit:

+ Because synthetic benchmark distributions under-specified negative templates with dangerous configuration flags, the neural network learned to place heavy predictive weight on intrinsic template features $x_("Template")$.
+ When graph edges are deleted, @thm:representation_preservation's non-vanishing gradient bounds ensure that the template's intrinsic configuration representation remains preserved through Layer~1 skip connections, allowing the model to classify templates based on their flags even with degraded graph topology.
+ However, when configuration flags are flipped, this primary decision pathway is corrupted, resulting in rapid performance degradation. This empirical finding reinforces the necessity of the neuro-symbolic hybrid architecture presented in @ch:neuro_symbolic, which combines neural feature learning with strict symbolic path verification.



=== Sample Efficiency and Learning Convergence

We evaluated how rapidly CertGraph converges as a function of the number of training enterprise environments:

+ 20 domains: Macro-F1 = $bold(0.8415)$
+ 40 domains: Macro-F1 = $bold(0.9274)$
+ 80 domains: Macro-F1 = $bold(0.9847)$
+ 160 domains: Macro-F1 = $bold(0.9899)$
+ 320 domains: Macro-F1 = $bold(1.0000)$


The model crosses the $0.98$ F1 threshold with approximately 80 training domains, demonstrating favorable sample efficiency. This establishes the practical viability of deploying CertGraph in enterprise environments without requiring millions of labeled training graphs.

== Computational Complexity and Scalability Benchmarking

To verify that CertGraph can operate within operational enterprise constraints (standard analysts' workstations with limited memory allocations), we benchmarked model inference latency, throughput, and memory consumption across enterprise graph scales ranging from 100 to 10,000 nodes ($approx 765,000$ directed edges).

#figure(
  image("../figures/scalability_metrics.png", width: 90%),
  caption: [Scalability benchmarks showing empirical inference latency scaling near-linearly with edge volume, displaying a moderate hardware cache-boundary inflection at 10,000 nodes, while Resident Set Size (RSS) memory remains bounded.],
) <fig:scalability_fig>


#figure(
  text(size: 9.5pt)[
  #table(
    columns: (1.5fr, 1fr, 1fr, 1fr, 2fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 6 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Graph Scale ($|V|$)*], [*Edge Count*], [*Latency (ms)*], [*RSS Memory*], [*Throughput (Graphs/s)*]),
    [100 nodes], [7,650], [$7.83$ ms], [$894.64$ MB], [$127.7$],
    [500 nodes], [38,250], [$12.45$ ms], [$894.64$ MB], [$80.3$],
    [1,000 nodes], [76,500], [$20.00$ ms], [$894.64$ MB], [$50.0$],
    [5,000 nodes], [382,500], [$112.50$ ms], [$894.64$ MB], [$8.9$],
    [10,000 nodes], [765,000], [$342.99$ ms], [$894.64$ MB], [$2.9$],
  )
],
  caption: [Inference Latency, Memory Footprint, and Throughput Across Enterprise Graph Scales.],
) <tab:scalability_table>


=== Scalability Insights and Empirical Runtime Profiling

*Scaling Analysis and Hardware Cache Inflection:*
As reported in @tab:scalability_table, CertGraph executes fast forward inference across enterprise graphs. From 100 to 5,000 nodes, inference time tracks edge volume closely: 7.83~ms at 7,650 edges, 20.00~ms at 76,500 edges ($2.55times$ runtime for $10times$ edges), and 112.50~ms at 382,500 edges ($5.62times$ runtime for $5times$ edges). 

Between 5,000 nodes (382,500 edges, 112.50~ms) and 10,000 nodes (765,000 edges, 342.99~ms), latency exhibits a $3.05times$ increase for a $2.0times$ edge increase. A strictly linear projection would predict approximately 225~ms. This modest super-linear inflection is caused by hardware memory hierarchy boundaries: at 765,000 directed edges, materializing intermediate multi-head attention logits across 4 attention heads and 64-dimensional feature projections requires over 48~MB of working tensor buffers per layer. This working set exceeds the host CPU's 32~MB L3 cache, causing sparse gather-scatter operations to transition from on-chip cache lines to DRAM memory bus transfers. Despite this cache-line spillover, total inference latency remains strictly sub-second at *342.99~ms* (0.34 seconds), orders of magnitude faster than full-graph recursive BFS queries that frequently require tens of seconds.

*Process Memory Baseline:*
Throughout the scaling benchmark, process Resident Set Size (RSS) memory remained constant at *894.64 MB*. This figure reflects the baseline memory allocation of the Python runtime, PyTorch core libraries, and CUDA driver initialization. Because PyTorch Geometric's sparse message-passing kernels evaluate edge reductions without materializing dense adjacency tensors, intermediate message allocations are accommodated within this initialized buffer without triggering additional heap allocations. This confirms that CertGraph can execute within background monitoring daemons on commodity security appliances.

=== Large-Scale Multi-Forest Partitioning Strategies

For multi-national enterprise conglomerates containing over 100,000 users and computers, monolithic graph loading into GPU memory can exceed VRAM limits. For such large-scale directories, CertGraph integrates with standard graph sampling techniques:

+ *Target-Centric Subgraph Extraction:* Rather than loading the entire corporate directory, the system extracts the $k$-hop directed backward authorization subgraphs rooted at each published certificate template ($k=2$). Because template subgraphs average fewer than 500 nodes, inference can be distributed across parallel CPU threads.
+ *GraphSAINT / Cluster-GCN Partitioning:* For forest-wide link analysis, directory objects can be partitioned into tightly connected administrative clusters using METIS partitioning, allowing mini-batch training and inference across distributed cluster nodes with bounded memory consumption.


