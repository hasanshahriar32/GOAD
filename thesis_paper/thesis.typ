#set document(title: "CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense", author: ("2002126", "2002138", "2102151"))
#set page(paper: "a4", margin: (left: 3.0cm, right: 2.5cm, top: 2.5cm, bottom: 2.5cm))
#set text(font: ("Times New Roman", "Liberation Serif"), size: 12pt, lang: "en")
#set par(justify: true, leading: 0.8em, first-line-indent: 1.5em)

// ─────────────────────────────────────────────────────────────
// 1. COVER PAGE (Exact replication of final(corrected).docx)
// ─────────────────────────────────────────────────────────────
#align(center)[
  #v(0.2cm)
  #text(size: 17pt, weight: "bold")[CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense]
  
  #v(0.6cm)
  #text(size: 11pt, weight: "bold")[Course Code: ECE 452 #h(0.8cm) Course Title: Project and Thesis]
  
  #v(0.6cm)
  #text(size: 11pt, weight: "bold")[Submitted By---] \
  #v(0.15cm)
  #text(size: 10.5pt)[
    *Student ID: 2002126* #h(0.4cm) Level: 4, Semester: I \
    *Student ID: 2002138* #h(0.4cm) Level: 4, Semester: I \
    *Student ID: 2102151* #h(0.4cm) Level: 4, Semester: I \
  ]
  
  #v(0.6cm)
  #image("figures/hstu_logo.png", width: 2.6cm)
  #v(0.5cm)
  
  #text(size: 11pt, weight: "bold")[Submitted To---] \
  #v(0.15cm)
  #text(size: 12pt, weight: "bold")[Department of Electronics and Communication Engineering] \
  #text(size: 10pt)[in partial fulfillment of the requirements for the degree of] \
  #text(size: 11pt, weight: "bold")[Bachelor of Science in Electronics and Communication Engineering]
  
  #v(0.5cm)
  #text(size: 12pt, weight: "bold")[Hajee Mohammad Danesh Science and Technology University (HSTU)] \
  #text(size: 10pt)[Dinajpur-5200, Bangladesh]
  
  #v(0.8cm)
  #text(size: 11pt, weight: "bold")[October, 2026]
]

#pagebreak()

// Set Roman numeral page numbering for Front Matter
#set page(numbering: "i", number-align: center)
#counter(page).update(1)

// ─────────────────────────────────────────────────────────────
// 2. CERTIFICATE PAGE (Exact replication of final(corrected).docx)
// ─────────────────────────────────────────────────────────────
#align(center)[
  #v(0.5cm)
  #text(size: 16pt, weight: "bold")[Certificate]
]

#v(0.8cm)
This is to certify that the thesis work entitled *“CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense”* is carried by the following ID numbers: *2002126, 2002138, 2102151*. To the fullest extent of our knowledge, we assert that this undertaking is an authentic and original contribution to the field. We certify that this thesis has not been previously submitted for the award of any other degree or diploma at this or any other institution.

#v(1.8cm)
*Signed by the Final Examining committee:*

#v(1.2cm)
#grid(
  columns: (1fr, 1fr),
  row-gutter: 1.8cm,
  [
    .................................................... \
    *Chairman* \
    Examination Committee
  ],
  [
    .................................................... \
    *Supervisor* \
    Department of ECE, HSTU
  ],
  [
    .................................................... \
    *External Member* \
    Examination Committee
  ],
  [
    .................................................... \
    *Co-Supervisor* \
    Department of ECE, HSTU
  ],
  [
    .................................................... \
    *Internal Member* \
    Examination Committee
  ],
  []
)

#pagebreak()

// ─────────────────────────────────────────────────────────────
// 3. CANDIDATE'S DECLARATION
// ─────────────────────────────────────────────────────────────
#align(center)[
  #v(0.5cm)
  #text(size: 16pt, weight: "bold")[Candidate's Declaration]
]

#v(0.8cm)
We hereby declare that the research work presented in this thesis entitled *“CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense”* is the outcome of an original investigation conducted by us under the supervision of the Department of Electronics and Communication Engineering, Hajee Mohammad Danesh Science and Technology University (HSTU), Dinajpur-5200, Bangladesh.

#v(0.4cm)
We further solemnly declare that:
1. This work, or any part thereof, has not been submitted previously to any university or institution for the award of any degree, diploma, or other academic qualification.
2. All material, concepts, and algorithms taken from the published or unpublished work of others have been fully and properly acknowledged and cited in accordance with standard academic referencing protocols.
3. All synthetic datasets, forensic auditing scripts, empirical benchmark routines, and graph learning models described herein were constructed with rigorous adherence to ethical scientific standards and academic integrity.

#v(2.0cm)
#grid(
  columns: (1fr, 1fr),
  [
    *Date:* September, 2026 \
    *Place:* HSTU, Dinajpur
  ],
  [
    .................................................... \
    *Student ID: 2002126* \
    *Student ID: 2002138* \
    *Student ID: 2102151* \
    Department of ECE, HSTU
  ]
)

#pagebreak()

// ─────────────────────────────────────────────────────────────
// 4. DEDICATION & ACKNOWLEDGEMENTS
// ─────────────────────────────────────────────────────────────
#align(center + horizon)[
  #text(size: 15pt, weight: "bold")[Dedication] \
  #v(1.0cm)
  #text(size: 11pt, style: "italic")[
    This thesis is dedicated to our beloved parents, \
    whose endless sacrifices, prayers, and unconditional love \
    have been the guiding light of our lives. \
    \
    And to all our respected teachers and mentors, \
    who inspired our passion for engineering and scientific discovery.
  ]
]

#pagebreak()

#align(center)[
  #v(0.5cm)
  #text(size: 16pt, weight: "bold")[Acknowledgements]
]

#v(0.6cm)
First and foremost, all praises are due to Almighty Allah, the Most Merciful and Most Beneficent, who bestowed upon us the health, strength, patience, and intellect required to complete this project and thesis research successfully.

We express our profound gratitude, respect, and deepest indebtedness to our respected thesis supervisor and co-supervisor in the Department of Electronics and Communication Engineering, Hajee Mohammad Danesh Science and Technology University (HSTU), Dinajpur. Their exemplary guidance, insightful suggestions, constant encouragement, and critical academic reviews were invaluable throughout the formulation, mathematical derivation, experimental validation, and manuscript preparation of this research.

We are deeply thankful to the Chairman and all distinguished faculty members of the Department of Electronics and Communication Engineering, HSTU, for providing a vibrant academic environment, high-quality computational facilities, and continuous moral support during our undergraduate curriculum.

Our sincere gratitude goes to the global open-source cybersecurity and machine learning research communities. In particular, we acknowledge the pioneering work of Will Schroeder and Lee Christensen (SpecterOps) for uncovering the ADCS attack surface; the creators of BloodHound, SharpHound, and Certipy for their foundational offensive graph tools; the developers of the Game of Active Directory (GOAD) laboratory; and the core contributors of PyTorch Geometric and NetworkX.

Finally, we owe an immeasurable debt of gratitude to our parents and families for their unending sacrifices, patience, and blessings throughout our university education. We also express warm appreciation to our batchmates, lab peers, and friends whose intellectual discussions, camaraderie, and encouragement enriched every stage of this thesis journey.

#v(1.2cm)
#grid(
  columns: (1fr, 1fr),
  [
    *HSTU, Dinajpur* \
    *September, 2026*
  ],
  [
    *Student ID: 2002126* \
    *Student ID: 2002138* \
    *Student ID: 2102151* \
    Department of ECE, HSTU
  ]
)

#pagebreak()

// ─────────────────────────────────────────────────────────────
// 5. ABSTRACT
// ─────────────────────────────────────────────────────────────
#align(center)[
  #v(0.3cm)
  #text(size: 16pt, weight: "bold")[Abstract]
]

#v(0.4cm)
Active Directory Certificate Services (ADCS) is deployed across more than 90% of enterprise networks to administer Public Key Infrastructure (PKI) credentials for authentication and encryption. However, subtle architectural misconfigurations across certificate templates, Access Control Lists (ACLs), and issuance policies introduce catastrophic privilege escalation vectors (designated ESC1 through ESC15), enabling unprivileged actors to compromise entire Active Directory domains. Existing auditing utilities (Certipy, BloodHound, PSPKIAudit) are predominantly rule-based and signature-driven: they evaluate isolated template configuration flags via static heuristics without learning from global environment topology, reachability, or multi-hop delegation chains.

This thesis introduces *CertGraph*, the first heterogeneous Graph Neural Network architecture designed for structural vulnerability detection across Active Directory Certificate Services attack graphs. We formalize enterprise identity infrastructure as a typed, directed, heterogeneous multigraph $G = (V, E, cal(T)_V, cal(T)_E)$ and deploy a Heterogeneous Graph Attention Network (Hetero-GAT) equipped with relation-specific message passing and multi-head attention mechanisms to perform inductive node-level classification over certificate templates.

Crucially, our investigation was grounded in an end-to-end *Forensic Audit* of experimental methodology. We uncovered and eliminated critical structural illusions: synthetic positional index leakage (where administrative entities occupy predictable array offsets), baseline information asymmetry (where flat ML baselines are deprived of graph topological features), and test-set memorization under synthetic hard negatives. We mathematically prove that in directed heterogeneous identity graphs containing source-only entities (Users and Computers with zero in-degree), residual skip-connections are indispensable; without them, message-passing aggregation triggers catastrophic representation collapse ($h_v^((l+1)) = bold(0)$), causing Macro-F1 to collapse from $0.9986$ to $0.4768$ ($p = 1.31 times 10^(-6)$).

On a sanitized, leakage-free benchmark of 700 enterprise environments evaluated under 5-fold cross-validation, CertGraph achieves a Macro-F1 score of *0.9986 ± 0.0029*, substantially outperforming signature heuristics ($0.7791 plus.minus 0.0247, p < 10^(-4)$) and flat ML ($0.8600 plus.minus 0.0130, p < 10^(-4)$). To probe model reliability, we formulated a novel *Zero-Shot Adversarial Hard Negative* benchmark where models trained on benign environments are tested against non-exploitable templates bearing vulnerable flags. Under this shift, neural models—including GNNs—succumb to shortcut learning, collapsing to $1.59%$ accuracy by relying on template flags rather than verifying path reachability. Conversely, symbolic graph traversal (BloodHound BFS) retains $84.13%$ accuracy.

These findings provide the first empirical justification for a *Neuro-Symbolic Hybrid Architecture* in enterprise identity defense: leveraging fast relational GNNs for heuristic risk prioritization ($O(1)$ amortized screening) coupled with symbolic graph algorithms for deterministic exploitability proofs. Finally, we formulate the autonomous edge-severing defense problem as a Stackelberg security game and mathematically prove its NP-hardness via reduction to the Directed Multi-way Cut problem.

#v(0.4cm)
*Keywords:* Active Directory Certificate Services (ADCS), Graph Attention Networks, Heterogeneous Graphs, Identity and Access Management, Neuro-Symbolic Security, Shortcut Learning, Autonomous Cyber Defense.

#pagebreak()

// ─────────────────────────────────────────────────────────────
// 6. PRELIMINARY LISTS
// ─────────────────────────────────────────────────────────────
#outline(title: "Table of Contents", depth: 3, indent: auto)
#pagebreak()
#outline(title: "List of Figures", target: figure.where(kind: image))
#pagebreak()
#outline(title: "List of Tables", target: figure.where(kind: table))
#pagebreak()

#heading(numbering: none)[List of Acronyms]
#v(0.5cm)
#table(
  columns: (1fr, 3fr),
  align: (left, left),
  stroke: none,
  [*ACL*], [Access Control List],
  [*AD*], [Active Directory],
  [*ADCS*], [Active Directory Certificate Services],
  [*AWDP*], [Automated Windows Domain Penetration],
  [*BFS*], [Breadth-First Search],
  [*CA*], [Certificate Authority],
  [*CSR*], [Certificate Signing Request],
  [*CV*], [Cross-Validation],
  [*DACL*], [Discretionary Access Control List],
  [*DC*], [Domain Controller],
  [*DDQN*], [Dueling Double Deep Q-Network],
  [*ECE*], [Electronics and Communication Engineering],
  [*EKU*], [Extended Key Usage],
  [*ESC*], [Escalation Vector (ADCS Misconfiguration Primitive)],
  [*GAT*], [Graph Attention Network],
  [*GCN*], [Graph Convolutional Network],
  [*GNN*], [Graph Neural Network],
  [*GOAD*], [Game of Active Directory],
  [*Hetero-GAT*], [Heterogeneous Graph Attention Network],
  [*HSTU*], [Hajee Mohammad Danesh Science and Technology University],
  [*IAM*], [Identity and Access Management],
  [*KDC*], [Key Distribution Center],
  [*LDAP*], [Lightweight Directory Access Protocol],
  [*ML*], [Machine Learning],
  [*MLP*], [Multi-Layer Perceptron],
  [*NP*], [Nondeterministic Polynomial Time],
  [*ODE*], [Ordinary Differential Equation],
  [*OID*], [Object Identifier],
  [*PAC*], [Privilege Attribute Certificate],
  [*PKI*], [Public Key Infrastructure],
  [*RF*], [Random Forest],
  [*SAN*], [Subject Alternative Name],
  [*SID*], [Security Identifier],
  [*SOC*], [Security Operations Center],
  [*TGS*], [Ticket Granting Service],
  [*TGT*], [Ticket Granting Ticket],
  [*XAI*], [Explainable Artificial Intelligence],
)

#pagebreak()

// ─────────────────────────────────────────────────────────────
// MAIN CHAPTERS (Arabic page numbering)
// ─────────────────────────────────────────────────────────────
#set page(numbering: "1", number-align: center)
#counter(page).update(1)
#set heading(numbering: "1.1")


// ═════════════════════════════════════════════════════════════
// MAIN CHAPTERS
// ═════════════════════════════════════════════════════════════

#include "typst_chapters/ch01_introduction.typ"
#pagebreak()

#include "typst_chapters/ch02_background_threat.typ"
#pagebreak()

#include "typst_chapters/ch03_formal_methodology.typ"
#pagebreak()

#include "typst_chapters/ch04_forensic_audit.typ"
#pagebreak()

#include "typst_chapters/ch05_empirical_benchmarks.typ"
#pagebreak()

#include "typst_chapters/ch06_real_world_case_study.typ"
#pagebreak()

#include "typst_chapters/ch07_robustness_scalability.typ"
#pagebreak()

#include "typst_chapters/ch08_neuro_symbolic_hybrid.typ"
#pagebreak()

#include "typst_chapters/ch09_game_theoretic_defense.typ"
#pagebreak()

#include "typst_chapters/ch10_conclusion.typ"
#pagebreak()

// ═════════════════════════════════════════════════════════════
// APPENDICES & BIBLIOGRAPHY
// ═════════════════════════════════════════════════════════════

#include "typst_chapters/app_proofs.typ"
#pagebreak()

#bibliography("references.bib", style: "ieee")
