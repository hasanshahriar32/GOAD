= Literature Review and Domain Background

<ch:background>

== Evolution of Identity-Based Lateral Movement in Enterprise Networks

For nearly three decades, enterprise information security architectures were predicated on the assumption of a defensible physical and logical perimeter. Organizations invested heavily in hardening network boundaries using stateful firewalls, intrusion detection and prevention systems (IDS/IPS), virtual private networks (VPNs), and demilitarized zones (DMZs). In this traditional fortress-and-moat doctrine, network traffic originating within the internal intranet was implicitly categorized as trusted, whereas external packets were subjected to rigorous perimeter inspection.

The widespread adoption of cloud-native computing, remote and hybrid work models, bring-your-own-device (BYOD) policies, and software-as-a-service (SaaS) platforms has effectively obliterated this logical boundary. Advanced Persistent Threat (APT) actors, nation-state adversaries, and professionalized ransomware cartels routinely bypass perimeter defenses through spear-phishing campaigns, supply-chain compromises, edge device vulnerabilities, or credential theft. Once an initial foothold is established on a single compromised workstation within an internal corporate network, the perimeter provides zero defensive efficacy.

Once an adversary achieves code execution on any machine in an internal corporate network, enterprise defense shifts entirely to combating *Lateral Movement*---the techniques adversaries use to extend access across systems, servers, and security principals to locate and compromise high-value assets.

=== Historical Precedents: Memory-Based Credential Abuse

Historically, identity lateral movement within Windows enterprise environments relied on memory-based credential dumping and protocol replay attacks:

+ *Pass-the-Hash (PtH):* Exploiting legacy NTLM authentication by extracting the NTLM password hash of a user from the Local Security Authority Subsystem Service (LSASS) process memory (using utilities such as Mimikatz) and presenting that hash in network challenge-response exchanges without knowing the plaintext password.
+ *Pass-the-Ticket (PtT):* Harvesting active Kerberos Ticket Granting Tickets (TGTs) or Service Tickets directly from LSASS memory to impersonate logged-on users across the enterprise.
+ *Overpass-the-Hash / Pass-the-Key:* Supplying an extracted NTLM hash or Kerberos AES-256 encryption key to request a valid Kerberos TGT directly from the Key Distribution Center (KDC) via the Kerberos Authentication Service (AS) exchange.
+ *Golden and Silver Tickets:* Forging cryptographically authentic Kerberos TGTs using the secret symmetric key of the domain's `KRBTGT` service account (Golden Ticket), or forging targeted service tickets using a specific server's machine account password hash (Silver Ticket), embedding arbitrary administrative group SIDs directly into the authorization token.



With the widespread deployment of Microsoft Credential Guard, Remote Credential Guard, Virtualization-Based Security (VBS), and Protected Process Light (PPL) in modern Windows operating systems, raw LSASS memory dumping has become substantially more difficult, triggering aggressive Endpoint Detection and Response (EDR) behavioral telemetry. Consequently, sophisticated adversaries have shifted their primary attack vector from host memory exploitation to *architectural access-control abuse* and *Active Directory Certificate Services (ADCS)*.

== Graph-Theoretic Modeling of Active Directory Security

Active Directory Domain Services (AD DS) is fundamentally a massive, distributed, multi-relational graph database. In 2016, the release of *BloodHound* by Robbins, Schroeder, and Morreale @robbins2017bloodhound transformed enterprise offensive and defensive security by formalizing Active Directory permissions as a directed identity attack graph.

=== Prior Attack Graph Literature

The concept of modeling security vulnerabilities as attack graphs dates back to foundational work by Phillips and Swiler (1998) and Sheyner et al. (2002) @sheyner2002automated, who represented computer network state transitions as directed graphs to analyze multi-step vulnerability chaining. However, early attack graph models suffered from severe combinatorial state explosion when applied to realistic enterprise networks, as they attempted to model low-level host vulnerabilities, network service versions, and system exploit states simultaneously.

BloodHound resolved this scalability dilemma by decoupling host-level software vulnerabilities from *identity authorization topology*. In BloodHound's formulation, vertices represent directory security principals (Users, Computers, Groups, Organizational Units, Domains), while edges represent discrete administrative access rights granted via Discretionary Access Control Lists (DACLs) or network session dependencies:

+ `MemberOf`: Direct or transitive security group containment.
+ `AdminTo`: Administrative execution privileges on a remote workstation or server.
+ `HasSession`: An interactive or network session active on a host, indicating that user credentials reside in local memory.
+ `GenericAll`, `GenericWrite`, `WriteDacl`, `WriteOwner`: Granular object-level permissions within the directory schema.



=== Limitations of Deterministic Graph Traversal

While BloodHound and related graph databases (Neo4j) allow security analysts to execute Cypher queries (such as shortest path queries from `Domain Users` to `Domain Admins`), deterministic graph traversal exhibits acute limitations in modern enterprise environments:

+ *Computational Intractability on Dense Enterprise Graphs:* Large multi-forest enterprises routinely contain over 100,000 security principals and tens of millions of access control entries. Exhaustive multi-hop traversal suffers from exponential branching factors, causing path-finding queries to time out or exhaust server memory.
+ *Absence of Contextual Probabilistic Risk Scoring:* Deterministic graph traversal treats every valid edge as equally likely to be traversed. It cannot incorporate operational context, such as whether a workstation is actively monitored by an EDR agent, whether a service account has been dormant, or whether an attack step requires complex operational prerequisites.
+ *Brittleness to Un-modeled Attack Vectors:* BloodHound relies on handcrafted edge collectors (SharpHound). If an organization deploys a novel authentication protocol or certificate configuration that has not been explicitly codified into the BloodHound Cypher schema, the attack path is completely invisible.



== Graph Representation Learning in Security

To overcome the brittleness and combinatorial limitations of deterministic graph search, researchers have increasingly investigated *Graph Representation Learning* and *Graph Neural Networks (GNNs)* for cybersecurity applications.

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



In this thesis, we build upon the principles of Heterogeneous Graph Attention Networks to engineer *CertGraph*, introducing relation-specific multi-head attention alongside crucial additive residual skip-connections necessary to survive asymmetric enterprise identity topologies.

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
    [ESC10], [Weak Certificate Mapping], [`altSecurityIdentities` weak registry keys on Domain Controllers], [Account takeover via unverified X.509 mapping syntax],
    [ESC11], [Insecure RPC Interface], [RPC enrollment endpoint lacking packet privacy / signing], [Relays NTLM to RPC enrollment interface MS-ICPR],
    [ESC12], [Vulnerable Hardware Key], [CA administrator key stored in vulnerable smart card / token], [Direct exfiltration of CA root signing keys],
    [ESC13], [Issuance Policy Link], [`msPKI-Certificate-Policy` OID maps to Tier-0 security group], [Injects Tier-0 group SID into Kerberos PAC token],
    [ESC14], [altSecurityIdentities Hijack], [Insecure write permissions over user `altSecurityIdentities`], [Links arbitrary victim certificates to attacker account],
    [ESC15], [EKUwu (CVE-2024-49019)], [Schema Version 1 template allows custom CSR application policy], [Injects Client Authentication EKU into non-auth templates],
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


