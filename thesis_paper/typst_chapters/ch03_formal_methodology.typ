= Formal Methodology and CertGraph Architecture <ch:methodology>


== Mathematical Formalization of Enterprise Identity Multigraphs

To rigorously model the complex, relational authorization topology of Active Directory (AD) and Active Directory Certificate Services (ADCS), we formalize the enterprise environment as a typed, directed, heterogeneous multigraph. Unlike flat tabular databases or homogeneous network graphs that treat all entities and connections identically, a heterogeneous multigraph explicitly preserves the distinct semantic properties of different directory objects and authorization relationships.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Definition Active Directory Heterogeneous Multigraph.* \
    An Active Directory enterprise environment is formally defined as a 6-tuple:
$ G = (V, E, cal(T)_V, cal(T)_E, phi_V, psi_E) $

where:

+ $V = union.big_(tau in cal(T)_V) V_tau$ is the finite set of all directory entities (vertices), partitioned into disjoint subsets by entity type, such that $V_(tau_1) sect V_(tau_2) = emptyset$ for all $tau_1 != tau_2$.
+ $E subset.eq V times cal(T)_E times V$ is the multiset of directed authorization, administrative, and enrollment relationships (edges). An edge $e = (u, r, v) in E$ indicates a directed relationship of relation type $r$ from source entity $u$ to target entity $v$.
+ $cal(T)_V = {"User", "Computer", "Group", "Template", "EnterpriseCA"}$ represents the discrete set of node entity types ($|cal(T)_V| = 5$).
+ $cal(T)_E = {"MemberOf"$, $"Enroll"$, $"GenericAll"$, $"WriteDacl"$, $"WriteOwner"$, $"PublishedTo"$, $"ManageCA"$, $"LinksPolicy"}$ represents the discrete set of canonical directed relation types ($|cal(T)_E| = 8$).
+ $phi_V: V arrow.r cal(T)_V$ is an ontological type-mapping function assigning each vertex $v in V$ its unique structural entity type $tau(v) in cal(T)_V$.
+ $psi_E: E arrow.r cal(T)_E$ is a relation-mapping function assigning each directed edge $e = (u, r, v) in E$ its canonical relation type $r in cal(T)_E$.


  ]
  ],
  caption: none,
  kind: "definition",
  supplement: [Definition],
)



#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Definition Network Schema and Canonical Metapaths.* \
    The network schema of the enterprise identity multigraph is a directed meta-graph $cal(S)_G = (cal(T)_V, cal(T)_E)$, specifying allowable directed relations between node types. A metapath $cal(P)$ of length $l$ is a sequence of entity types and relation types:
$ cal(P) = tau_0 limits(arrow.r)^(r_1) tau_1 limits(arrow.r)^(r_2) tau_2 limits(arrow.r)^(r_3) dots limits(arrow.r)^(r_l) tau_l $

In Active Directory Certificate Services, privilege escalation is formalized as the existence of a valid composite metapath connecting an unprivileged security principal $s in V_("User") union V_("Computer")$ to an administrative certificate issuance template $t in V_("Template")$, followed by an authentication exchange terminating at a Tier-0 asset.
  ]
  ],
  caption: none,
  kind: "definition",
  supplement: [Definition],
)


== Node Feature Vector Spaces and Semantic Encodings

Each vertex $v in V$ is assigned an initial feature vector $x_v in bb(R)^(d_(tau(v)))$ encoding intrinsic local attributes extracted directly from LDAP directory queries and Active Directory security descriptors. Because different entity types possess distinct configuration schemas, feature spaces are typed and heterogeneous.

=== Certificate Template Feature Representation

Certificate templates are the primary targets of ADCS audits. A template vertex $t in V_("Template")$ is assigned a 10-dimensional binary feature vector $x_("Template") in bb(R)^(10)$:
$ x_("Template") = [ & f_("supplies_subject"), f_("client_auth"), f_("any_purpose"), f_("agent_eku"), f_("no_security_ext"), 

& f_("schema_v1"), f_("requires_approval"), f_("has_policy_link"), f_("has_dangerous_dacl"), f_("is_published") ]^T $

The individual binary dimensions are defined and extracted as follows:

+ $f_("supplies_subject") in {0, 1}$: Extracted from the LDAP integer attribute `msPKI-Certificate-Name-Flag`. Evaluates to $1$ if the bitwise flag `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` (`0x00000001`) is set, indicating that the enroller can specify an arbitrary Subject Alternative Name (SAN).
+ $f_("client_auth") in {0, 1}$: Extracted from the multi-valued string attribute `pKIExtendedKeyUsage`. Evaluates to $1$ if the template includes the Client Authentication Object Identifier (OID `1.3.6.1.5.5.7.3.2`) or Smart Card Logon (OID `1.3.6.1.4.1.311.20.2.2`).
+ $f_("any_purpose") in {0, 1}$: Evaluates to $1$ if `pKIExtendedKeyUsage` contains the Any Purpose OID (`2.5.29.37.0`) or if the attribute is empty/null, which Windows CryptoAPI interprets as valid for all cryptographic applications.
+ $f_("agent_eku") in {0, 1}$: Evaluates to $1$ if `pKIExtendedKeyUsage` contains the Certificate Request Agent OID (`1.3.6.1.4.1.311.20.2.1`), permitting on-behalf-of enrollment.
+ $f_("no_security_ext") in {0, 1}$: Extracted from `msPKI-Enrollment-Flag`. Evaluates to $1$ if the flag `CT_FLAG_NO_SECURITY_EXTENSION` (`0x00080000`) is enabled, instructing the CA to omit the security extension embedding the requestor's SID.
+ $f_("schema_v1") in {0, 1}$: Extracted from the integer attribute `msPKI-Template-Schema-Version`. Evaluates to $1$ if the schema version equals $1$, signifying a legacy Windows 2000 template susceptible to CVE-2024-49019 (EKUwu).
+ $f_("requires_approval") in {0, 1}$: Extracted from `msPKI-Enrollment-Flag`. Evaluates to $1$ if `CT_FLAG_PEND_ALL_REQUESTS` (`0x00000002`) is set, mandating CA certificate manager intervention prior to certificate issuance.
+ $f_("has_policy_link") in {0, 1}$: Extracted from `msPKI-Certificate-Policy`. Evaluates to $1$ if the template references one or more Issuance Policy OIDs.
+ $f_("has_dangerous_dacl") in {0, 1}$: Extracted by evaluating the Discretionary Access Control List (DACL) in `nTSecurityDescriptor`. Evaluates to $1$ if any low-privileged security principal holds `GenericAll`, `GenericWrite`, `WriteDacl`, or `WriteOwner` access rights on the template object.
+ $f_("is_published") in {0, 1}$: Evaluates to $1$ if the template name is actively listed in the `certificateTemplates` attribute of at least one operational Enterprise CA object within the Active Directory configuration partition.



=== Security Principal Feature Representations

The security principals capable of initiating or forwarding access control operations are represented by typed feature vectors capturing administrative tiering, protocol configuration, and account state:


+ *User Nodes ($x_("User") in bb(R)^6$):* $ x_("User") = [ & f_("is_enabled"), f_("is_sensitive"), f_("dont_req_preauth"), & f_("trusted_for_delegation"), f_("has_spn"), f_("is_admin") ]^T $ where $f_("is_enabled")$ indicates whether `ACCOUNTDISABLE` is absent from `userAccountControl`; $f_("is_sensitive")$ indicates `NOT_DELEGATED`; $f_("dont_req_preauth")$ identifies accounts vulnerable to AS-REP roasting; $f_("trusted_for_delegation")$ flags unconstrained Kerberos delegation; $f_("has_spn")$ flags accounts susceptible to Kerberoasting; and $f_("is_admin") in {0, 1}$ indicates membership in a Tier-0 administrative role (`adminCount` = 1).
+ *Computer Nodes ($x_("Computer") in bb(R)^6$):* $ x_("Computer") = [ & f_("is_enabled"), f_("is_dc"), f_("unconstrained"), & f_("constrained"), f_("rbcd"), f_("is_admin") ]^T $ where $f_("is_dc")$ indicates a primary Domain Controller; $f_("unconstrained")$ and $f_("constrained")$ capture Kerberos delegation settings; and $f_("rbcd")$ flags resource-based constrained delegation configurations.
+ *Security Group Nodes ($x_("Group") in bb(R)^2$):* $ x_("Group") = [f_("is_tier0"), f_("is_builtin")]^T $ where $f_("is_tier0") = 1$ denotes high-value administrative groups (e.g., `Domain Admins`, `Enterprise Admins`, `Schema Admins`, `Administrators`, `Account Operators`); and $f_("is_builtin") = 1$ indicates standard well-known Windows security groups.
+ *Enterprise Certificate Authority Nodes ($x_("CA") in bb(R)^3$):* $ x_("CA") = [f_("is_root_ca"), f_("allows_user_spec"), f_("enforces_encryption")]^T $ where $f_("is_root_ca")$ identifies root CAs; $f_("allows_user_spec")$ flags the presence of the dangerous registry setting `EDITF_ATTRIBUTESUBJECTALTNAME2`; and $f_("enforces_encryption")$ identifies whether RPC interface encryption is mandated on the CA endpoint (relevant to ESC11).



=== Relational Adjacency and Canonical Reverse Relations

For each relation type $r = (tau_s, "rel", tau_t) in cal(T)_E$, the directed adjacency matrix $A_r in {0, 1}^(|V_(tau_s)| times |V_(tau_t)|)$ satisfies:
$ A_r[u, v] = 1 <=> (u, r, v) in E $


A fundamental challenge in graph representation learning on directed identity graphs is that access control permissions flow from principals to resources (e.g., $"User" limits(arrow.r)^("Enroll)" "Template"$), whereas vulnerability reasoning requires evaluating the reverse query: _"Which unprivileged principals possess an inbound access path to this template?"_

To facilitate bidirectional information exchange across the message-passing layers, we introduce formal reverse canonical relations for every directed edge type:
$ forall r = (tau_s, "rel", tau_t) in cal(T)_E => r^(-1) = (tau_t, "rel"^(-1), tau_s) in cal(T)_E^(-1) $

The adjacency matrix for the reverse relation is the exact transpose of the forward adjacency:
$ A_(r^(-1)) = A_r^T $

The augmented relational set $tilde(cal(T))_E = cal(T)_E union cal(T)_E^(-1)$ contains 16 directed relations, ensuring that certificate templates can gather structural context from prospective enrollers and administrative controllers during forward message passing.

== The CertGraph Hetero-GAT Architecture

CertGraph implements an inductive Heterogeneous Graph Attention Network (Hetero-GAT). Unlike homogeneous GNNs that collapse entity distinctions into a single latent space, CertGraph maintains type-specific linear projections and relation-specific multi-head attention mechanisms.

#figure(
  image("figures/certgraph_architecture_diagram.png", width: 90%),
  caption: [CertGraph end-to-end Hetero-GAT pipeline, detailing input feature encoding, multi-head relational attention layers, additive residual skip-connections, and the multi-class template classification head.],
) <fig:certgraph_arch>


=== Relation-Specific Linear Feature Projections

Let $h_u^((l-1)) in bb(R)^(d_(tau(u))^((l-1)))$ denote the hidden representation of node $u$ at layer $l-1$, where $h_u^((0)) = x_u$. For each canonical relation $r = (tau(u), "rel", tau(v)) in tilde(cal(T))_E$ terminating at target node $v$, source and target node representations are projected into a common relational metric space $bb(R)^(d_("out")^((l)))$:
$ z_u^((l, r)) = W_("src")^((l, r)) h_u^((l-1)),   z_v^((l, r)) = W_("dst")^((l, r)) h_v^((l-1)) $

where $W_("src")^((l, r)) in bb(R)^(d_("out")^((l)) times d_(tau(u))^((l-1)))$ and $W_("dst")^((l, r)) in bb(R)^(d_("out")^((l)) times d_(tau(v))^((l-1)))$ are learnable projection matrices. In our implementation, hidden dimensions are set to $d_("hidden") = 64$ across all layers.

=== Multi-Head Relational Graph Attention

To capture multi-faceted topological dependencies (e.g., distinguishing between direct group membership and delegated write permissions), CertGraph deploys $K$ independent attention heads per relation.

For attention head $k in {1, dots, K}$, the unnormalized attention coefficient $e_(v u)^((k, l, r))$ quantifying the importance of incoming source node $u$ to target node $v$ across relation $r$ is computed as:
$ e_(v u)^((k, l, r)) = op("LeakyReLU") ( bold(a)_k^((l, r) T) [ z_v^((k, l, r))  ||  z_u^((k, l, r)) ] ) $

where $bold(a)_k^((l, r)) in bb(R)^(2 d_("head"))$ is a learnable relation-specific attention vector, $||$ denotes vector concatenation, and the LeakyReLU non-linearity employs a negative slope parameter of $alpha_("leaky") = 0.2$. The head dimension satisfies $d_("head") = d_("out")^((l)) / K$.

To ensure comparability across nodes with varying in-degrees, attention coefficients are normalized across the set of incoming relation neighbors $cal(N)_r(v) = \{u in V_(tau_s) | (u, r, v) in E}$ using the relational softmax function:
$ alpha_(v u)^((k, l, r)) = (exp ( e_(v u)^((k, l, r)) ))/(sum_(w in cal(N)_r(v)) exp ( e_(v w)^((k, l, r)) )) $

The aggregated message for node $v$ under relation $r$ across all $K$ attention heads is obtained via concatenation:
$ mu_(v, r)^((l)) = product_(k=1)^K ( sum_(u in cal(N)_r(v)) alpha_(v u)^((k, l, r)) z_u^((k, l, r)) ) $

where $||$ denotes concatenation along the channel dimension, resulting in $mu_(v, r)^((l)) in bb(R)^(d_("out")^((l)))$.

=== Semantic-Level Aggregation and Residual Skip-Connections

Because a target entity $v$ may receive incoming messages from multiple distinct relation types $cal(R)_("in")(tau(v)) = \{r in tilde(cal(T))_E | "target"(r) = tau(v)}$, CertGraph performs semantic-level aggregation via vector summation:
$ h_(v, "agg")^((l)) = sum_(r in cal(R)_("in")(tau(v))) mu_(v, r)^((l)) $


*Additive Residual Skip-Connections:*
As established theoretically in @sec:theorem1_discussion, pure neighborhood aggregation in directed acyclic or source-dominated subgraphs suffers from catastrophic representation collapse. To preserve node-specific identity features and maintain stable gradient flow, CertGraph incorporates parameterized additive residual skip-connections:
$ tilde(h)_v^((l)) = h_(v, "agg")^((l)) + W_("skip")^((l, tau(v))) h_v^((l-1)) $

where $W_("skip")^((l, tau(v))) in bb(R)^(d_("out")^((l)) times d_(tau(v))^((l-1)))$ is a type-specific linear projection matrix.

The pre-activation state is transformed via the Exponential Linear Unit (ELU) activation function, followed by Layer Normalization and Dropout:
$ macron(h)_v^((l)) &= op("ELU") ( tilde(h)_v^((l)) ) 

h_v^((l)) &= op("Dropout") ( op("LayerNorm") ( macron(h)_v^((l)) ), p = 0.2 ) $


=== Multi-Class Vulnerability Classification Head

CertGraph stacks $L = 2$ heterogeneous graph attention layers. A 2-hop receptive field over the materialized graph is mathematically sufficient to resolve all canonical ADCS escalation paths:

+ $"User" limits(arrow.r)^("MemberOf)" "Group" limits(arrow.r)^("Enroll)" "Template"$ (2 hops).
+ $"User" limits(arrow.r)^("Enroll)" "Template" limits(arrow.r)^("LinksPolicy)" "Group"$ (2 hops).
+ $"User" limits(arrow.r)^("WriteDacl)" "Template" limits(arrow.r)^("PublishedTo)" "CA"$ (2 hops).



*Transitive Closure of Group Nesting Hierarchy:*
A critical architectural consideration in Active Directory security graphs is the handling of deeply nested group hierarchies ($"User" limits(arrow.r)^("MemberOf)" "Group"_1 limits(arrow.r)^("MemberOf)" dots limits(arrow.r)^("MemberOf)" "Group"_k$). If group relationships were maintained purely as local 1-hop edges, an $L = 2$ layer GNN would be strictly limited to evaluating 2-hop paths, failing to detect privilege escalation for users whose enrollment rights derive from groups nested at depth $k > 1$. 

To address this without increasing network depth (which would induce severe over-smoothing and gradient attenuation across sparse security graphs), CertGraph pre-expands all nested group memberships via *transitive closure materialization* during graph extraction. Following the operational semantics of the Windows Security subsystem (specifically, the Local Security Authority's evaluation of the `tokenGroups` attribute) and production graph auditing tools (such as BloodHound), our ingestion pipeline computes the reflexive transitive closure of all `MemberOf` relations prior to model ingestion:
$ E_("MemberOf")^* = {(u, "MemberOf", g) | exists " path " u limits(arrow.r)^("MemberOf)^+" g " in " G} $

By replacing raw nested edges with their transitive closure $E_("MemberOf")^*$, every effective group membership is collapsed into a direct 1-hop relation between the user and all ancestor groups. Consequently, $L = 2$ layers provide a comprehensive receptive field: Hop 1 resolves effective principal permissions and transitive group memberships, while Hop 2 captures template enrollment, issuance policy mapping, and CA publication edges. If transitive closure is omitted, path detection is strictly bounded by the network depth $L = 2$.

Following the second message-passing layer, we isolate the final latent representation of the target certificate template $h_t^((L)) in bb(R)^(64)$. This embedding is forwarded to a two-layer Multi-Layer Perceptron (MLP) classification head:
$ z_t &= op("ReLU") ( W_1 h_t^((L)) + b_1 ),   W_1 in bb(R)^(32 times 64),   b_1 in bb(R)^(32) 

hat(y)_t &= op("Softmax") ( W_2 z_t + b_2 ),   W_2 in bb(R)^(7 times 32),   b_2 in bb(R)^(7) $

where $hat(y)_t in Delta^6$ represents the predicted probability distribution over the 7 target vulnerability classes:
$ cal(C) = {"Safe", "ESC1", "ESC2", "ESC3", "ESC4", "ESC9", "ESC13"} $


=== Objective Function with Class Imbalance Regularization

In enterprise Active Directory environments, vulnerable certificate templates are rare relative to benign configurations. To counter class imbalance and prevent overfitting, the network is trained end-to-end by minimizing the Weighted Cross-Entropy Loss with $L_2$ weight regularization:
$ cal(L)(Theta) = - sum_(i=1)^N sum_(c=1)^(|cal(C)|) omega_c   y_(i, c) log hat(y)_(i, c) + lambda_("reg") sum_(theta in Theta) \|theta||_2^2 $

where $N$ is the batch size; $y_(i, c) in {0, 1}$ is the one-hot encoded ground truth; $omega_c = (N)/(|cal(C)| dot N_c)$ is the inverse class frequency weight; $lambda_("reg") = 10^(-4)$ is the weight decay coefficient; and $Theta$ denotes all learnable parameters ($W_("src"), W_("dst"), bold(a)_k, W_("skip"), W_1, W_2$). Parameter optimization is performed using AdamW with an initial learning rate of $eta = 10^(-3)$ and a cosine annealing learning rate schedule.

== Formal Algorithmic Specifications

To ensure complete scientific reproducibility, we formalize the core execution routines of CertGraph into algorithmic specifications.

=== End-to-End Layer Forward Pass

@alg:certgraph_layer formalizes the computation of a single CertGraph heterogeneous attention layer with residual skip-connections and relational softmax.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: 1pt + rgb("#cbd5e1"), width: 100%)[
#align(left)[
#h(0.0em) *Require:* Heterogeneous Multigraph $G = (V, E, tilde(cal(T))_E)$; Input hidden states $\{h_v^((l-1))}_(v in V)$; Projection matrices $\{W_("src")^((l, r)), W_("dst")^((l, r))}$; Attention vectors $\{bold(a)_k^((l, r))}$; Skip projections $\{W_("skip")^((l, tau))}$. \
#h(0.0em) *Ensure:* Updated hidden representations $\{h_v^((l))}_(v in V)$. \
#h(0.0em) *for* each canonical relation $r = (tau_s, "rel", tau_t) in tilde(cal(T))_E$: \
#h(1.5em) Compute projected representations: \
#h(1.5em)   $z_u^((l, r)) arrow.l W_("src")^((l, r)) h_u^((l-1))$ for all $u in V_(tau_s)$ \
#h(1.5em)   $z_v^((l, r)) arrow.l W_("dst")^((l, r)) h_v^((l-1))$ for all $v in V_(tau_t)$ \
#h(1.5em) *for* each attention head $k in {1, dots, K}$: \
#h(3.0em) *for* each edge $(u, r, v) in E_r$: \
#h(4.5em) $e_(v u)^((k, l, r)) arrow.l op("LeakyReLU") ( bold(a)_k^((l, r) T) [z_v^((k, l, r))  ||  z_u^((k, l, r))] )$ \
#h(3.0em) *for* each target node $v in V_(tau_t)$: \
#h(4.5em) Normalize: $alpha_(v u)^((k, l, r)) arrow.l (exp(e_(v u)^((k, l, r))))/(sum_(w in cal(N)_r(v)) exp(e_(v w)^((k, l, r))))$ \
#h(1.5em) *for* each target node $v in V_(tau_t)$: \
#h(3.0em) Compute head concatenation: $mu_(v, r)^((l)) arrow.l product_(k=1)^K ( sum_(u in cal(N)_r(v)) alpha_(v u)^((k, l, r)) z_u^((k, l, r)) )$ \
#h(0.0em) *for* each entity $v in V$: \
#h(1.5em) Semantic aggregation: $h_(v, "agg")^((l)) arrow.l sum_(r in cal(R)_("in")(tau(v))) mu_(v, r)^((l))$ \
#h(1.5em) Additive residual skip: $tilde(h)_v^((l)) arrow.l h_(v, "agg")^((l)) + W_("skip")^((l, tau(v))) h_v^((l-1))$ \
#h(1.5em) Non-linear activation: $macron(h)_v^((l)) arrow.l op("ELU")(tilde(h)_v^((l)))$ \
#h(1.5em) Normalization & Regularization: $h_v^((l)) arrow.l op("Dropout")(op("LayerNorm")(macron(h)_v^((l))), p = 0.2)$ \
#h(0.0em) *return* $\{h_v^((l))}_(v in V)$
]
  ],
  caption: [CertGraph Heterogeneous Attention Layer Forward Pass],
  kind: "algorithm",
  supplement: [Algorithm],
) <alg:certgraph_layer>


=== Vulnerability Inference and Calibrated Risk Scoring

@alg:certgraph_infer details the inference pipeline that ingests raw enterprise graphs, executes message passing, and generates calibrated risk rankings for security teams.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: 1pt + rgb("#cbd5e1"), width: 100%)[
#align(left)[
#h(0.0em) *Require:* Enterprise Active Directory Graph $G = (V, E)$; Trained CertGraph model $cal(M)_Theta$; Risk threshold $tau_("risk") in [0, 1]$. \
#h(0.0em) *Ensure:* Prioritized list of high-risk certificate templates $cal(R)_("alerts")$. \
#h(0.0em) Extract node feature tensors $\{x_v}_(v in V)$ from LDAP and DACL attributes \
#h(0.0em) Construct reverse relations $r^(-1)$ for all $r in cal(T)_E$ to form augmented graph $tilde(G)$ \
#h(0.0em) Initialize $h_v^((0)) arrow.l x_v$ for all $v in V$ \
#h(0.0em) *for* layer $l = 1$ to $L=2$: \
#h(1.5em) $\{h_v^((l))}_(v in V) arrow.l op("CertGraphLayerForward")(tilde(G), \{h_v^((l-1))}_(v in V), Theta^((l)))$ \
#h(0.0em) Initialize empty alert queue $cal(R)_("alerts") arrow.l []$ \
#h(0.0em) *for* each published template $t in V_("Template")$: \
#h(1.5em) Forward embedding $h_t^((L))$ to classification head: $hat(y)_t arrow.l op("Softmax")(W_2 op("ReLU")(W_1 h_t^((L)) + b_1) + b_2)$ \
#h(1.5em) Compute composite risk score: $S_("risk")(t) arrow.l 1.0 - hat(y)_t["Safe"]$ \
#h(1.5em) Determine predicted vector: $c_("pred") arrow.l op("argmax")_(c) hat(y)_t[c]$ \
#h(1.5em) *if* $S_("risk")(t) >= tau_("risk")$ and $c_("pred") != "Safe"$: \
#h(3.0em) Append $(t, c_("pred"), S_("risk")(t), hat(y)_t)$ to $cal(R)_("alerts")$ \
#h(0.0em) Sort $cal(R)_("alerts")$ in descending order of risk score $S_("risk")(t)$ \
#h(0.0em) *return* $cal(R)_("alerts")$
]
  ],
  caption: [CertGraph Enterprise Vulnerability Screening and Risk Prioritization],
  kind: "algorithm",
  supplement: [Algorithm],
) <alg:certgraph_infer>


== Theoretical Analysis: Intrinsic Attribute Preservation and Gradient Bounds <sec:theorem1_discussion>

A foundational theoretical contribution of this thesis is the formal proof that parameterized residual skip-connections are mathematically indispensable in heterogeneous security graph neural networks to prevent intrinsic attribute erasure and representation decay.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Theorem Intrinsic Attribute Preservation and Gradient Lower Bounds.* \
    Let $G = (V, E, cal(T)_V, cal(T)_E)$ be a directed heterogeneous multigraph. Consider an $L$-layer heterogeneous message-passing neural network where layer $l in {1, dots, L}$ computes hidden representations:

+ *Intrinsic Feature Erasure without Skip Connections:* Under pure relational aggregation without skip connections: $ h_v^((l)) = sigma ( sum_(r in cal(R)_("in")(tau(v))) plus.circle.big_(u in cal(N)_r(v)) alpha_(v u)^((l)) W_r^((l)) h_u^((l-1)) ) $ the hidden representation $h_v^((1))$ is a function exclusively of adjacent incoming neighbor states. Consequently, for any node $v$ (including certificate templates $t in V_("Template")$), the gradient of the immediate hidden state with respect to its own initial configuration vector $x_v$ vanishes: $ (diff h_v^((1)))/(diff x_v) = bold(0) in bb(R)^(d_1 times d_0) $ causing complete erasure of intrinsic configuration attributes from the primary state representation. For source-only nodes where $d_("in")(v) = 0$, $h_v^((l)) = bold(0)$ for all $l >= 1$.
+ *Guaranteed Gradient Lower Bound via Residual Skips:* Introducing parameterized residual skip connections $tilde(h)_v^((l)) = h_v^((l)) + W_("skip")^((l)) tilde(h)_v^((l-1))$ guarantees that the Jacobian of the representation with respect to the initial input features satisfies: $ || (diff tilde(h)_v^((L)))/(diff x_v) || >= product_(k=1)^L sigma_(min)(W_("skip")^((k))) > 0 $ where $sigma_(min)(W_("skip")^((k))) > 0$ is the minimum singular value of $W_("skip")^((k))$, establishing a strictly positive lower bound that prevents attribute decay across message-passing hops.


  ]
  ],
  caption: none,
  kind: "theorem",
  supplement: [Theorem],
) <thm:representation_preservation>


_Proof Outline._ The full mathematical derivation is provided in Appendix @proof:theorem1. Without skip connections or self-loops, $h_v^((1))$ aggregates only incoming messages from external neighbors $cal(N)(v)$, discarding the node's own feature tensor $x_v$. In certificate templates, this erases the 10 binary configuration flags governing PKI issuance. With residual skip projections following the GCNII framework (Chen et al., 2020) @chen2020simple, the direct linear skip path guarantees full-rank propagation of $x_v$ to the final classification head.


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Corollary Security Attribute Preservation Corollary.* \
    In Active Directory Certificate Services, a certificate template's exploitability depends fundamentally on its intrinsic configuration attributes (such as `ENROLLEE_SUPPLIES_SUBJECT` and Client Authentication EKUs). Omitting residual skip connections isolates these flags from the node's immediate layer representations, leading to severe representation decay and empirical performance collapse.
  ]
  ],
  caption: none,
  kind: "corollary",
  supplement: [Corollary],
)


== Computational Complexity and Scalability Analysis

To understand why CertGraph can screen enterprise networks in milliseconds while graph traversal tools encounter combinatorial slowdowns, we analyze its asymptotic time and space complexity:


#figure(
  block(fill: rgb("#f8fafc"), inset: 1.2em, radius: 4pt, stroke: (left: 3pt + rgb("#1e3a8a")), width: 100%)[
#align(left)[
    *Proposition Computational Complexity of CertGraph Inference.* \
    Let $G = (V, E)$ denote an enterprise identity multigraph with $|V|$ vertices, $|E|$ edges, hidden dimension $d$, and $L$ convolutional layers. The computational time complexity of a CertGraph forward pass is:
$ cal(O) ( L dot ( |E| dot d + |V| dot d^2 ) ) $

and its auxiliary space complexity is $cal(O)(|V| dot d + |E|)$.
  ]
  ],
  caption: none,
  kind: "proposition",
  supplement: [Proposition],
)



_Proof._ For each layer $l in {1, dots, L}$:

+ *Node Feature Projections:* Projecting all $|V|$ nodes across incoming relations requires $|V| dot d^2$ multiply-accumulate operations.
+ *Attention Logit Computation:* Computing unnormalized attention coefficients $e_(v u)^((k, l, r))$ requires evaluating the dot product $bold(a)_k^T [z_v || z_u]$ for every directed edge in $E$. This evaluates in $cal(O)(|E| dot d)$ operations.
+ *Relational Softmax and Aggregation:* Normalizing attention coefficients and taking the weighted sum over neighbor feature vectors evaluates in $cal(O)(|E| dot d)$ operations using sparse segment reduction primitives.
+ *Skip Connection and Non-Linearity:* Adding the residual projection and evaluating ELU and LayerNorm requires $cal(O)(|V| dot d)$ operations.


Summing these stages across $L$ layers yields $cal(O)(L (|E| d + |V| d^2))$. Because $L = 2$ and $d = 64$ are fixed constants, the complexity scales strictly linearly with graph volume:
$ cal(O)(|V| + |E|) $

Memory space is dominated by the node state tensors $bb(R)^(|V| times d)$ and the edge index tensor $bb(Z)^(2 times |E|)$, bounded by $cal(O)(|V| d + |E|)$. #h(1fr) $square$


In contrast, deterministic graph traversal (e.g., Breadth-First Search or Cypher shortest-path queries) across all published templates exhibits worst-case computational complexity of $cal(O)(|V_("Template")| dot (|V| + |E|))$. In densely connected enterprise forests where $|E| >> |V|$, recursive path-finding encounters exponential path explosion along cyclic group delegation chains, whereas CertGraph executes as a sequence of highly parallelized, constant-depth GPU tensor operations.
