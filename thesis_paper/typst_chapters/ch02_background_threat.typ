= Literature Review and Domain Background <ch:background>


== Evolution of Identity-Based Lateral Movement in Enterprise Networks

Enterprise computing relies on centralized directory services to manage authentication, authorization, and cryptographic trust across distributed systems. In Windows enterprise networks, the core identity backbone is provided by Microsoft Active Directory Domain Services (AD DS) and its associated cryptographic public-key subsystem, Active Directory Certificate Services (ADCS). As modern organizations adopt Zero Trust principles and cloud-hybrid architectures, the primary operational focus of enterprise defense has shifted from perimeter firewall boundaries to the internal identity and access management fabric.

Once an adversary achieves initial code execution on any internal endpoint (e.g., through credential stuffing, phishing, or vulnerable edge services), enterprise defense shifts entirely to combating *Lateral Movement*---the techniques adversaries use to navigate across systems, accounts, and directory objects to compromise authoritative Tier-0 administrative assets.

=== Historical Precedents: Memory-Based Credential Abuse

Historically, identity lateral movement within Windows enterprise environments relied on memory-based credential dumping and protocol replay attacks:

+ *Pass-the-Hash (PtH):* Exploiting legacy NTLM authentication by extracting the NTLM password hash of a user from the Local Security Authority Subsystem Service (LSASS) process memory (using utilities such as Mimikatz) and presenting that hash in network challenge-response exchanges without knowing the plaintext password.
+ *Pass-the-Ticket (PtT):* Harvesting active Kerberos Ticket Granting Tickets (TGTs) or Service Tickets directly from LSASS memory to impersonate logged-on users across the enterprise.
+ *Overpass-the-Hash / Pass-the-Key:* Supplying an extracted NTLM hash or Kerberos AES-256 encryption key to request a valid Kerberos TGT directly from the Key Distribution Center (KDC) via the Kerberos Authentication Service (AS) exchange.
+ *Golden and Silver Tickets:* Forging cryptographically authentic Kerberos TGTs using the secret symmetric key of the domain's `KRBTGT` service account (Golden Ticket), or forging targeted service tickets using a specific server's machine account password hash (Silver Ticket), embedding arbitrary administrative group SIDs directly into the authorization token.



With the widespread deployment of Microsoft Credential Guard, Remote Credential Guard, Virtualization-Based Security (VBS), and Protected Process Light (PPL) in modern Windows operating systems, raw LSASS memory dumping has become substantially more difficult, triggering aggressive Endpoint Detection and Response (EDR) behavioral telemetry. Consequently, sophisticated adversaries have shifted their primary attack vectors from host memory exploitation to *architectural access-control abuse* and *Active Directory Certificate Services (ADCS)*.

== Graph-Theoretic Modeling of Active Directory Security

Active Directory Domain Services (AD DS) is fundamentally a massive, distributed, multi-relational graph database. In 2016, the release of *BloodHound* by Andy Robbins, Will Schroeder, and Rohan Vazarkar @robbins2017bloodhound transformed enterprise offensive and defensive security by formalizing Active Directory permissions as a directed identity attack graph.

=== Prior Attack Graph Literature

The concept of modeling security vulnerabilities as attack graphs dates back to foundational work by Phillips and Swiler (1998) @phillips1998graph and Sheyner et al. (2002) @sheyner2002automated, who represented computer network state transitions as directed graphs to analyze multi-step vulnerability chaining. Logic-based attack graph tools such as MulVAL (Ou et al., 2005) @ou2005mulval later automated attack path synthesis using Datalog rules to model multi-host vulnerability dependencies. However, early attack graph models suffered from severe combinatorial state explosion when applied to realistic enterprise networks, as they attempted to model low-level host vulnerabilities, network service versions, and system exploit states simultaneously.

BloodHound resolved this scalability dilemma by decoupling host-level software vulnerabilities from *identity authorization topology*. In BloodHound's formulation, vertices represent directory security principals (Users, Computers, Groups, Organizational Units, Domains), while edges represent discrete administrative access rights granted via Discretionary Access Control Lists (DACLs) or network session dependencies:

+ `MemberOf`: Direct or transitive security group containment.
+ `AdminTo`: Administrative execution privileges on a remote workstation or server.
+ `HasSession`: An interactive or network session active on a host, indicating that user credentials reside in local memory.
+ `GenericAll`, `GenericWrite`, `WriteDacl`, `WriteOwner`: Granular object-level permissions within the directory schema.



=== Capabilities and Limitations of Deterministic Graph Traversal

While BloodHound and related graph databases (Neo4j) allow security analysts to execute Cypher queries (such as shortest path queries from `Domain Users` to `Domain Admins`), deterministic graph traversal exhibits acute limitations in modern enterprise environments:

+ *Computational Intractability on Dense Enterprise Graphs:* Large multi-forest enterprises routinely contain over 100,000 security principals and tens of millions of access control entries. While single-source shortest path is polynomial $O(|V| + |E|)$, exhaustive multi-source path enumeration and all-pairs reachability queries suffer from exponential branching factors, causing path-finding queries to time out or exhaust server memory.
+ *Absence of Contextual Probabilistic Risk Scoring:* Deterministic graph traversal treats every valid edge as equally likely to be traversed. It cannot incorporate operational context, such as whether a workstation is actively monitored by an EDR agent, whether a service account has been dormant, or whether an attack step requires complex operational prerequisites.
+ *Heuristic Coverage and Schema Updates:* Traditional graph collectors require explicit rule definitions. While modern releases of BloodHound (v5.4.0+, 2024) natively support core ADCS attack edges (including ESC1, ESC3, ESC4, ESC6, ESC9, ESC10, and ESC13), and tools such as Certipy @alldritt2023certipy cover ESC1--ESC17, both utilities evaluate access rules via deterministic logic without inductive learning or continuous blast-radius ranking.



== Graph Representation Learning in Security

To overcome the brittleness and combinatorial limitations of deterministic graph search, researchers have increasingly investigated *Graph Representation Learning* and *Graph Neural Networks (GNNs)* for cybersecurity applications @goel2025coevolutionary @guo2023scalable.

=== The Message-Passing Neural Network (MPNN) Framework

Gilmer et al. @gilmer2017neural unified modern graph deep learning architectures under the Message-Passing Neural Network (MPNN) framework. For a graph $G = (V, E)$ with node feature vectors $x_v in bb(R)^d$, an MPNN layer computes updated node representations $h_v^((l))$ through three core computational phases:

+ *Message Computation:* For each directed edge $(u, v) in E$, a message vector is computed: $ m_(v u)^((l)) = M_l ( h_v^((l-1)), h_u^((l-1)), e_(v u) ) $ where $M_l$ is a parameterized message function, and $e_(v u)$ represents edge features.
+ *Message Aggregation:* Messages from all incoming neighbors in $cal(N)(v)$ are aggregated using a permutation-invariant aggregation operator $plus.circle.big$: $ macron(m)_v^((l)) = plus.circle.big_(u in cal(N)(v)) m_(v u)^((l)) $
+ *State Update:* The node's hidden representation is updated by combining its previous state with the aggregated message: $ h_v^((l)) = U_l ( h_v^((l-1)), macron(m)_v^((l)) ) $ where $U_l$ is a parameterized update function (e.g., a Multi-Layer Perceptron or gated recurrent unit).



=== Homogeneous vs. Heterogeneous GNNs

Early GNN architectures---including Graph Convolutional Networks (GCN) @kipf2017semi, GraphSAGE @hamilton2017inductive, and Graph Attention Networks (GAT) @velickovic2018graph --- were designed for homogeneous graphs where all nodes belong to a single entity type and all edges represent uniform relationships.

In contrast, enterprise identity graphs are profoundly *heterogeneous*. Modeling an Active Directory forest requires distinguishing between distinct node types (Users, Computers, Groups, Certificate Templates, Certificate Authorities) and distinct relational edge semantics (`MemberOf`, `Enroll`, `WriteDacl`, `LinksPolicy`). Applying homogeneous GNNs to identity graphs destroys the semantic boundaries between entities, leading to severe representation conflation.

To handle heterogeneous structures, specialized architectures have been proposed:

+ *Relational GCN (R-GCN):* Schlichtkrull et al. @schlichtkrull2018modeling introduced relation-specific transformation matrices $W_r$, parameterizing message passing per edge type.
+ *Heterogeneous Graph Attention Networks (HAN):* Wang et al. @wang2019heterogeneous introduced hierarchical attention, computing node-level attention followed by semantic-level meta-path attention.
+ *Heterogeneous Graph Transformer (HGT):* Hu et al. @hu2020heterogeneous parameterized self-attention using source-type, target-type, and relation-type matrices to model continuous web-scale graphs.



=== Game Theory and Machine Learning Pitfalls in Cybersecurity

Applying machine learning and game theory to enterprise cybersecurity introduces distinct structural and combinatorial constraints. In active defense, Stackelberg security games (Kiekintveld et al., 2009) @kiekintveld2009computing provide a principled foundation for allocating defensive countermeasures against worst-case adversaries. On enterprise attack graphs, Guo et al. (AAAI 2023) @guo2023scalable investigated scalable edge-blocking algorithms by exploiting graph treewidth and parameterizing non-splitting paths to minimize an attacker's reachability to Domain Admin under operational budget constraints. Expanding upon this game-theoretic interdiction formulation, Goel et al. (2025) @goel2025coevolutionary introduced a co-evolutionary defense framework pairing Graph Neural Network-approximated dynamic programming (GNNDP) with evolutionary diversity optimization over parameterized attack graphs, demonstrating that neural approximations can scale defensive search against adaptive multi-hop attackers.

Crucially, while these foundational studies address combinatorial edge interdiction and path reachability over generic host-compromise attack graphs, they do not model the cryptographic configuration semantics of Active Directory Certificate Services (ADCS), nor do they tackle inductive multi-class vulnerability detection or examine shortcut learning under distribution shifts. CertGraph addresses this unaddressed domain by formalizing enterprise PKI as a typed heterogeneous multigraph, jointly evaluating relational attention over certificate template configurations and multi-hop enrollment paths.

Concurrently, empirical security machine learning is subject to severe methodological pitfalls, as formalized by Arp et al. (USENIX Security 2022) @arp2022dos, Sommer & Paxson (IEEE S&P 2010) @sommer2010outside, and Pendlebury et al. (USENIX Security 2019) @pendlebury2019tesseract. These pitfalls include sampling bias, synthetic generator artifacts, lab-only evaluation lacking ecological validity, and inappropriate baseline comparisons. Moreover, as networks grow deeper, preserving raw node attributes requires residual skip connections (GCNII, Chen et al., ICML 2020) @chen2020simple to prevent over-smoothing and gradient decay.

In this thesis, we build upon the principles of Heterogeneous Graph Attention Networks to engineer *CertGraph*, introducing relation-specific multi-head attention alongside crucial additive residual skip-connections necessary to preserve configuration attributes across asymmetric enterprise identity topologies.

== Active Directory Architecture and Cryptographic Primitives

To establish the technical foundation for our attack graph formulation, we examine the core internal mechanisms of Active Directory.

=== Security Principals and Security Identifiers (SIDs)

Every security entity within Active Directory is termed a *Security Principal*. Each security principal is assigned a globally unique, immutable identifier called a *Security Identifier (SID)*:
$ "SID" = "S-"1"-"5"-"21"-"D_1"-"D_2"-"D_3"-"R $

where $D_1, D_2, D_3$ denote the unique domain sub-authority, and $R$ represents the Relative Identifier (RID). RIDs below 1000 are reserved for well-known administrative entities:

+ `RID 500`: Built-in `Administrator`.
+ `RID 502`: Built-in `KRBTGT` (Kerberos Key Distribution Center service account).
+ `RID 512`: `Domain Admins` security group.
+ `RID 519`: `Enterprise Admins` security group (Tier-0 forest root).


RIDs above 1000 designate dynamically created domain users, groups, and computer workstations.

=== Kerberos Authentication and Token Construction

Authentication in Active Directory is governed primarily by the Kerberos v5 protocol. The authentication workflow proceeds through the following sequential stages:

+ *Authentication Service (AS) Exchange:* The client encrypts a timestamp using their hashed password and transmits an `AS-REQ` to the Key Distribution Center (KDC) running on a Domain Controller. The KDC decrypts the timestamp to verify identity and issues an `AS-REP` containing a Ticket Granting Ticket (TGT).
+ *Privilege Attribute Certificate (PAC):* Crucially, the TGT embeds a cryptographically signed binary structure called the *Privilege Attribute Certificate (PAC)*. The PAC enumerates all security groups to which the user belongs (including transitive nested group memberships) and is signed using both the server secret and the KDC's private key.
+ *Ticket Granting Service (TGS) Exchange:* When the client desires access to a network service (e.g., an SMB share or LDAP directory), it presents its TGT to the KDC via a `TGS-REQ`. The KDC validates the PAC signature and issues a service ticket (`TGS-REP`) encrypted with the target service's long-term key.



=== PKINIT: Public Key Cryptography for Initial Authentication

When Public Key Cryptography for Initial Authentication (PKINIT) is enabled via ADCS (standardized in RFC 4556), a client can initiate the AS exchange by presenting an X.509 digital certificate rather than a password hash. The client signs the `PA-PK-AS-REQ` pre-authentication structure using its private key and includes its X.509 certificate.

Upon receipt, the KDC:

+ Validates that the certificate was signed by a trusted Enterprise Certificate Authority listed in the domain's NTAuth store (`CN=NTAuthCertificates,CN=Public Key Services,CN=Services,CN=Configuration,DC=domain,DC=local`).
+ Verifies that the certificate contains an authorized Extended Key Usage (EKU) permitting client authentication.
+ Extracts the user identity from the certificate's *Subject Alternative Name (SAN)* extension (matching User Principal Name or sAMAccountName) or `altSecurityIdentities` attribute.
+ Constructs a Kerberos TGT carrying a PAC populated with the privileges of the mapped account.



This mechanism allows any valid certificate carrying an administrative SAN to be exchanged directly for an administrative Kerberos TGT.

=== Access Control Lists (ACLs) and Security Descriptors

Every Active Directory object is protected by a *Security Descriptor* containing a Discretionary Access Control List (DACL). A DACL comprises an ordered sequence of Access Control Entries (ACEs) defining permissions granted or denied to specific SIDs. Key administrative ACEs include:

+ `GenericAll`: Full unrestricted control over the target object (enabling password resets, attribute modification, and object deletion).
+ `GenericWrite`: Permission to modify any non-confidential attribute of the object.
+ `WriteDacl`: Permission to modify the DACL itself, enabling an attacker to grant themselves `GenericAll`.
+ `WriteOwner`: Permission to assume ownership of the object and subsequently rewrite its security descriptor.
+ `ExtendedRight`: Special domain rights, including `Certificate-Enrollment` and `All-Extended-Rights`.



== Active Directory Certificate Services (ADCS) Mechanics

Active Directory Certificate Services (ADCS) is an integrated Windows role that allows an organization to construct an internal Public Key Infrastructure (PKI). ADCS comprises several core architectural components:

#figure(
  image("figures/adcs_attack_graph_schema.png", width: 90%),
  caption: [Heterogeneous Active Directory Certificate Services (ADCS) Graph Schema, illustrating relations between security principals (Users, Computers, Groups), Certificate Templates, and Enterprise Certificate Authorities.],
) <fig:adcs_schema>



+ *Enterprise Certificate Authority (CA):* A server hosting the ADCS role integrated with Active Directory. Enterprise CAs store their configuration, trust anchors, and published templates directly within the LDAP Configuration partition (`CN=Configuration,DC=domain,DC=local`).
+ *Certificate Templates:* LDAP objects (`class: pKICertificateTemplate`) defining the cryptographic and authorization parameters of certificates issued by the CA. Templates control key usage, validity periods, issuance requirements, and enrollment permissions.
+ *Extended Key Usages (EKUs):* Object Identifiers (OIDs) embedded in certificates designating their authorized operational functions. Critical security-relevant EKUs include:
  + *Client Authentication* (`1.3.6.1.5.5.7.3.2`): Authorizes the certificate for Kerberos PKINIT and TLS client authentication.
  + *Smart Card Logon* (`1.3.6.1.4.1.311.20.2.2`): Enables interactive smart card authentication to Windows domains.
  + *Any Purpose* (`2.5.29.37.0`): Wildcard EKU granting authorization for any cryptographic purpose.
  + *Certificate Request Agent* (`1.3.6.1.4.1.311.20.2.1`): Authorizes an enrollee to request enrollment on behalf of other users (enrollment agent).
+ *Enrollment Flags and Subject Specification:* The `mspki-certificate-name-flag` attribute governs how the certificate's subject identity is populated. If the flag `CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT` (`0x00000001`) is set, the certificate requestor explicitly defines the subject and SAN in their Certificate Signing Request (CSR).



== Exhaustive Taxonomy of ADCS Vulnerability Classes (ESC1--ESC15)

SpecterOps and subsequent security researchers categorized common ADCS misconfiguration patterns into numbered Escalation Vectors (ESC). @tab:esc_taxonomy presents a comprehensive comparative analysis of all 15 documented classes.

#figure(
  text(size: 8pt)[
  #table(
    columns: (1fr, 1fr, 1fr, 1fr),
    stroke: (x, y) => if y == 0 { (top: 1.2pt + luma(0), bottom: 0.8pt + luma(0)) } else if y == 1 { (bottom: 0.8pt + luma(0)) } else if y == 16 { (bottom: 1.2pt + luma(0)) } else { none },
    inset: (x: 4pt, y: 3.8pt),
    table.header([*Vector*], [*Vulnerability Name*], [*Key Configuration Prerequisites*], [*Exploitation Impact*]),
    [ESC1], [Enrollee Supplies SAN], [`ENROLLEE_SUPPLIES_SUBJECT` + Client Auth EKU + Unprivileged Enroll], [Direct domain admin impersonation via Kerberos PKINIT],
    [ESC2], [Any Purpose EKU], [Any Purpose EKU (`2.5.29.37.0`) or missing EKU + Unprivileged Enroll], [Arbitrary impersonation across all cryptographic protocols],
    [ESC3], [Enrollment Agent], [Certificate Request Agent EKU + 2-hop template enrollment path], [Co-signs CSR on behalf of arbitrary domain accounts],
    [ESC4], [Insecure Template DACL], [`GenericAll` / `WriteDacl` / `WriteOwner` on template object], [Rewrites template to ESC1, enrolls, reverts configuration],
    [ESC5], [Insecure PKI Object DACL], [Insecure ACLs on CA container / enrollment services object], [Takes ownership of PKI infrastructure and roots],
    [ESC6], [CA SAN Flag Active], [`EDITF_ATTRIBUTESUBJECTALTNAME2` enabled on CA server], [Injects arbitrary SAN into any template request],
    [ESC7], [Insecure CA Permissions], [`ManageCA` or `ManageCertificates` rights on CA object], [Overrides CA settings, approves unprivileged requests],
    [ESC8], [HTTP Enrollment Relay], [NTLM authentication enabled on Web Enrollment HTTP endpoints], [Coerced NTLM relay from DC to obtain DC certificate],
    [ESC9], [Missing Security Ext.], [`CT_FLAG_NO_SECURITY_EXTENSION` enabled on template], [UPN spoofing bypasses strong mapping without PAC check],
    [ESC10], [Weak Certificate Mapping], [Weak UPN/DNS mapping registry keys on Domain Controllers (pre-KB5014754)], [Account takeover via unverified X.509 mapping syntax],
    [ESC11], [Insecure RPC Interface], [RPC enrollment endpoint (MS-ICPR) lacking packet privacy (Heiniger 2023)], [Relays NTLM to RPC enrollment interface],
    [ESC12], [CA Interface Relay Abuse], [ICertPassage / RPC enrollment interface abuse (Knobloch 2023)], [Coerced NTLM relay to CA RPC interface yielding rogue certificate],
    [ESC13], [Issuance Policy Link], [`msPKI-Certificate-Policy` OID maps to Tier-0 security group], [Injects Tier-0 group SID into Kerberos PAC token],
    [ESC14], [altSecurityIdentities Hijack], [Insecure write permissions over user `altSecurityIdentities` attribute], [Links arbitrary victim certificates to attacker account],
    [ESC15], [EKUwu (CVE-2024-49019)], [Schema Version 1 template allows custom CSR application policy (Bollinger 2024)], [Injects Client Authentication EKU into non-auth templates],
  )
],
  caption: [Comprehensive Comparative Taxonomy of ADCS Privilege Escalation Vectors (ESC1--ESC15).],
) <tab:esc_taxonomy>


#figure(
  image("figures/esc13_attack_path_diagram.png", width: 90%),
  caption: [Two-hop ESC13 privilege escalation attack path, showing the chain from an unprivileged user through enrollment permissions and issuance policy OID linkage to high-value domain administrative group tokens.],
) <fig:esc13_path>


== Formal Threat Model

To establish rigorous scientific boundaries, we define our threat model following standard enterprise security conventions:

=== Attacker Model


+ *Assumed Breach Posture:* We operate under an assumed-breach model. The adversary has already acquired unprivileged execution capability inside the internal corporate network (e.g., standard workstation access with credentials of a regular `Domain Users` account).
+ *Telemetry and Capabilities:* The adversary has read access to the directory service via standard LDAP queries and can enumerate the active PKI infrastructure using unprivileged tools (e.g., Certipy or SharpHound).
+ *Objective:* The adversary seeks to achieve full domain dominance (_Domain Admin_ or _Enterprise Admin_ status) by identifying and exploiting an ADCS escalation path with minimal detection risk.



=== Defender Model


+ *Auditing Scope:* The defender possesses read-only administrative auditing telemetry over the Active Directory forest, capable of extracting object attributes and DACL relationships via automated collection pipelines.
+ *Remediation Constraints:* The defender must autonomously or semi-autonomously identify and neutralize exploitable attack paths. Crucially, the defender operates under a *business availability constraint*: defensive mitigations (such as revoking template enrollment rights or deleting groups) must not disrupt legitimate enterprise operations.
+ *Computational Budget:* The detection architecture must execute efficiently on commodity security operations infrastructure (e.g., standard analysts' workstations with bounded RAM budgets), precluding the deployment of cumbersome full-OS virtual machine simulations for static auditing.


