#set document(title: "CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense", author: ("2002126", "2002138", "2102151"))
#set page(paper: "a4", margin: (left: 3.0cm, right: 2.5cm, top: 2.5cm, bottom: 2.5cm))
#set text(font: "Times New Roman", size: 12pt, lang: "en")
#set par(justify: true, leading: 0.8em, first-line-indent: 1.5em)

// ─────────────────────────────────────────────────────────────
// 1. COVER PAGE (Exact replication of final(corrected).docx)
// ─────────────────────────────────────────────────────────────
#align(center)[
  #v(0.5fr)
  #text(size: 18pt, weight: "bold")[CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense]
  
  #v(0.8fr)
  #text(size: 11.5pt, weight: "bold")[Course Code: ECE 452 #h(0.8cm) Course Title: Project and Thesis]
  
  #v(0.8fr)
  #text(size: 11.5pt, weight: "bold")[Submitted By---] \
  #v(0.2cm)
  #align(center)[
    #table(
      columns: (auto, auto),
      stroke: none,
      inset: (x: 8pt, y: 3pt),
      align: (left, left),
      [*Student ID: 2002126*], [Level: 4, Semester: II],
      [*Student ID: 2002138*], [Level: 4, Semester: II],
      [*Student ID: 2102151*], [Level: 4, Semester: II],
    )
  ]
  
  #v(1.0fr)
  #image("figures/hstu_logo.png", width: 3.0cm)
  #v(1.0fr)
  
  #text(size: 11.5pt, weight: "bold")[Submitted To---] \
  #v(0.2cm)
  #text(size: 12.5pt, weight: "bold")[Department of Electronics and Communication Engineering] \
  #v(0.1cm)
  #text(size: 10.5pt)[in partial fulfillment of the requirements for the degree of] \
  #v(0.1cm)
  #text(size: 11.5pt, weight: "bold")[Bachelor of Science in Electronics and Communication Engineering]
  
  #v(0.9fr)
  #text(size: 12.5pt, weight: "bold")[Hajee Mohammad Danesh Science and Technology University (HSTU)] \
  #v(0.1cm)
  #text(size: 10.5pt)[Dinajpur-5200, Bangladesh] \
  #v(0.4cm)
  #text(size: 11.5pt, weight: "bold")[October, 2026]
  
  #v(0.5fr)
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
    *Date:* October, 2026 \
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
    *October, 2026*
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
Microsoft Active Directory (AD) is deployed across more than 90% of Fortune 1000 enterprises as the central identity fabric, with Active Directory Certificate Services (ADCS) widely integrated to manage Public Key Infrastructure (PKI) credentials for authentication and encryption. However, complex configuration parameters across certificate templates, Access Control Lists (ACLs), and issuance policies introduce systemic privilege escalation vectors (documented across ESC1 through ESC15+), allowing unprivileged accounts to compromise entire Active Directory domains. Existing auditing utilities (such as Certipy, BloodHound, and PSPKIAudit) rely primarily on rule-based heuristics and path traversal: they evaluate template configuration flags without continuous contextual risk scoring, or suffer high traversal overhead when analyzing dense multi-forest environments.

In this thesis, we present *CertGraph*, a heterogeneous Graph Neural Network architecture designed for structural vulnerability detection across Active Directory Certificate Services attack graphs. While the full ADCS threat taxonomy spans ESC1 through ESC15+, empirical modeling and formal evaluations focus on the core structural escalation vectors: ESC1, ESC2, ESC3, ESC4, ESC9, and ESC13. We formalize enterprise identity infrastructure as a typed, directed, heterogeneous multigraph $G = (V, E, cal(T)_V, cal(T)_E)$ and employ a Heterogeneous Graph Attention Network (Hetero-GAT) equipped with relation-specific message passing to perform inductive node-level classification over certificate templates.

Grounding our work in a methodological audit following the security machine learning principles of Arp et al. (USENIX Security 2022), we identify and resolve experimental pitfalls in synthetic identity generation: positional index leakage, baseline information asymmetry, and rule saturation where simple tabular models match complex neural architectures. We establish that residual skip connections are theoretically and empirically essential to preserve raw configuration attributes and maintain non-vanishing gradient bounds with respect to input features; omitting them triggers severe representation decay, reducing Macro-F1 from $0.9986$ to $0.4768$.

On a sanitized benchmark of 700 enterprise environments evaluated under 5-fold cross-validation, CertGraph achieves a Macro-F1 score of *0.9986 ± 0.0029*, outperforming isolated signature heuristics ($0.7791 plus.minus 0.0247$) and flat feature-only classifiers ($0.8600 plus.minus 0.0130$). To examine out-of-distribution generalization, we design an adversarial *Zero-Shot Hard Negative* benchmark where models trained on standard topologies are evaluated against non-exploitable templates bearing dangerous flags ($n = 63$). Under this distribution shift, pure neural models succumb to shortcut learning, achieving $1.59%$ accuracy (95% Wilson CI: $0.3%$–$8.5%$) by relying on template flag correlations rather than path reachability. Conversely, symbolic graph traversal achieves $84.13%$ accuracy (95% Wilson CI: $73.1%$–$91.2%$).

These findings motivate a *Two-Tier Neuro-Symbolic Architecture* that pairs fast relational GNN screening for candidate prioritization with targeted symbolic graph verification for deterministic exploitability proofs. Finally, we formulate the enterprise identity access interdiction problem within a Stackelberg game-theoretic framework and prove its NP-hardness via reduction to Directed Multiterminal Cut.

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
  [*BFS*], [Breadth-First Search],
  [*CA*], [Certificate Authority],
  [*CSR*], [Certificate Signing Request],
  [*CV*], [Cross-Validation],
  [*DACL*], [Discretionary Access Control List],
  [*DC*], [Domain Controller],
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

// HSTU Thesis Heading Specifications
// Chapter Title (Level 1): 16pt, Bold, Centered
#show heading.where(level: 1): it => block(width: 100%)[
  #set align(center)
  #set text(size: 16pt, weight: "bold")
  #v(0.8cm)
  #if it.numbering != none [
    Chapter #counter(heading).display() \
    #v(0.3cm)
  ]
  #it.body
  #v(0.6cm)
]

// Heading 1 / Main Section (Level 2): 14pt, Bold, Flush left
#show heading.where(level: 2): it => block(width: 100%)[
  #set align(left)
  #set text(size: 14pt, weight: "bold")
  #v(16pt)
  #if it.numbering != none [
    #counter(heading).display()
    #h(0.4em)
  ]
  #it.body
  #v(8pt)
]

// Heading 2 / Sub-heading (Level 3): 12pt, Bold, Flush left
#show heading.where(level: 3): it => block(width: 100%)[
  #set align(left)
  #set text(size: 12pt, weight: "bold")
  #v(12pt)
  #if it.numbering != none [
    #counter(heading).display()
    #h(0.4em)
  ]
  #it.body
  #v(6pt)
]

// Heading 3 / Sub-sub-heading (Level 4): 12pt, Italic, Flush left
#show heading.where(level: 4): it => block(width: 100%)[
  #set align(left)
  #set text(size: 12pt, weight: "regular", style: "italic")
  #v(10pt)
  #if it.numbering != none [
    #counter(heading).display()
    #h(0.4em)
  ]
  #it.body
  #v(4pt)
]

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

#counter(heading).update(0)
#set heading(numbering: "A.1")
#show heading.where(level: 1): it => block(width: 100%)[
  #set align(center)
  #set text(size: 16pt, weight: "bold")
  #v(0.8cm)
  #if it.numbering != none [
    Appendix #counter(heading).display() \
    #v(0.3cm)
  ]
  #it.body
  #v(0.6cm)
]

#include "typst_chapters/app_proofs.typ"
#pagebreak()

#bibliography("references.bib", style: "ieee")
