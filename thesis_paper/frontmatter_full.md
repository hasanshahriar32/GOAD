# CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense {.unnumbered .text-center}

**Course Code: ECE 452 &emsp; Course Title: Project and Thesis**

**Submitted By—**

**Student ID: 2002126** &emsp;&emsp; Level: 4, Semester: II

**Student ID: 2002138** &emsp;&emsp; Level: 4, Semester: II

**Student ID: 2102151** &emsp;&emsp; Level: 4, Semester: II

![](figures/hstu_logo.png){width=1.0in}

**Submitted To—**

**Department of Electronics and Communication Engineering**

in partial fulfillment of the requirements for the degree of

**Bachelor of Science in Electronics and Communication Engineering**

**Hajee Mohammad Danesh Science and Technology University (HSTU)**

Dinajpur-5200, Bangladesh

**October, 2026**

# Certificate {.unnumbered .text-center}

This is to certify that the thesis work entitled **“CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense”** is carried by the following ID numbers: **2002126, 2002138, 2102151**. To the fullest extent of our knowledge, we assert that this undertaking is an authentic and original contribution to the field. We certify that this thesis has not been previously submitted for the award of any other degree or diploma at this or any other institution.

**Signed by the Final Examining committee:**

| | |
|:-------------------------------------------|:-------------------------------------------|
| ............................ | ............................ |
| **Chairman** | **Supervisor** |
| Examination Committee | Department of ECE, HSTU |
| | |
| ............................ | ............................ |
| **External Member** | **Co-Supervisor** |
| Examination Committee | Department of ECE, HSTU |
| | |
| ............................ | |
| **Internal Member** | |
| Examination Committee | |

# Candidate's Declaration {.unnumbered .text-center}

We hereby declare that the research work presented in this thesis entitled **“CertGraph: Heterogeneous Graph Attention Networks for Active Directory Certificate Services Vulnerability Detection and Autonomous Defense”** is the outcome of an original investigation conducted by us under the supervision of the Department of Electronics and Communication Engineering, Hajee Mohammad Danesh Science and Technology University (HSTU), Dinajpur-5200, Bangladesh.

We further solemnly declare that:

1. This work, or any part thereof, has not been submitted previously to any university or institution for the award of any degree, diploma, or other academic qualification.
2. All material, concepts, and algorithms taken from the published or unpublished work of others have been fully and properly acknowledged and cited in accordance with standard academic referencing protocols.
3. All synthetic datasets, forensic auditing scripts, empirical benchmark routines, and graph learning models described herein were constructed with rigorous adherence to ethical scientific standards and academic integrity.

| | |
|:-------------------------------------------|:-------------------------------------------|
| **Date:** October, 2026 | ............................ |
| **Place:** HSTU, Dinajpur | **Student ID: 2002126** <br> Level: 4, Semester: II |
| | ............................ |
| | **Student ID: 2002138** <br> Level: 4, Semester: II |
| | ............................ |
| | **Student ID: 2102151** <br> Level: 4, Semester: II |
| | Department of ECE, HSTU |

# Dedication {.unnumbered .text-center}

<br>
<br>

*This thesis is dedicated to our beloved parents,*
*whose endless sacrifices, prayers, and unconditional love*
*have been the guiding light of our lives.*

<br>

*And to all our teachers and mentors,*
*who inspired our passion for computer science, cybersecurity, and scientific discovery.*

# Acknowledgements {.unnumbered .text-center}

First and foremost, all praises are due to Almighty Allah, the Most Merciful and Most Beneficent, who bestowed upon us the health, strength, patience, and intellect required to complete this project and thesis research successfully.

We express our profound gratitude, respect, and deepest indebtedness to our respected thesis supervisor and co-supervisor in the Department of Electronics and Communication Engineering, Hajee Mohammad Danesh Science and Technology University (HSTU), Dinajpur. Their exemplary guidance, insightful suggestions, constant encouragement, and critical academic reviews were invaluable throughout the formulation, mathematical derivation, experimental validation, and manuscript preparation of this research.

We are deeply thankful to the Chairman and all distinguished faculty members of the Department of Electronics and Communication Engineering, HSTU, for providing a vibrant academic environment, high-quality computational facilities, and continuous moral support during our undergraduate curriculum.

Our sincere gratitude goes to the global open-source cybersecurity and machine learning research communities. In particular, we acknowledge the pioneering work of Will Schroeder and Lee Christensen (SpecterOps) for uncovering the ADCS attack surface; the creators of BloodHound, SharpHound, and Certipy for their foundational offensive graph tools; the developers of the Game of Active Directory (GOAD) laboratory; and the core contributors of PyTorch Geometric and NetworkX.

Finally, we owe an immeasurable debt of gratitude to our parents and families for their unending sacrifices, patience, and blessings throughout our university education. We also express warm appreciation to our batchmates, lab peers, and friends whose intellectual discussions, camaraderie, and encouragement enriched every stage of this thesis journey.

| | |
|:-------------------------------------------|:-------------------------------------------|
| **HSTU, Dinajpur** | **Student ID: 2002126** |
| **October, 2026** | **Student ID: 2002138** |
| | **Student ID: 2102151** |
| | Department of ECE, HSTU |

# Abstract {.unnumbered .text-center}

Microsoft Active Directory (AD) is deployed across more than 90% of Fortune 1000 enterprises as the central identity fabric, with Active Directory Certificate Services (ADCS) widely integrated to manage Public Key Infrastructure (PKI) credentials for authentication and encryption. However, complex configuration parameters across certificate templates, Access Control Lists (ACLs), and issuance policies introduce systemic privilege escalation vectors (documented across ESC1 through ESC15+), allowing unprivileged accounts to compromise entire Active Directory domains. Existing auditing utilities (such as Certipy, BloodHound, and PSPKIAudit) rely primarily on rule-based heuristics and path traversal: they evaluate template configuration flags without continuous contextual risk scoring, or suffer high traversal overhead when analyzing dense multi-forest environments.

In this thesis, we present **CertGraph**, a heterogeneous Graph Neural Network architecture designed for structural vulnerability detection across Active Directory Certificate Services attack graphs. While the full ADCS threat taxonomy spans ESC1 through ESC15+, empirical modeling and formal evaluations focus on the core structural escalation vectors: ESC1, ESC2, ESC3, ESC4, ESC9, and ESC13. We formalize enterprise identity infrastructure as a typed, directed, heterogeneous multigraph $G = (V, E, \mathcal{T}_V, \mathcal{T}_E)$ and employ a Heterogeneous Graph Attention Network (Hetero-GAT) equipped with relation-specific message passing to perform inductive node-level classification over certificate templates.

Grounding our work in a methodological audit following the security machine learning principles of Arp et al. (USENIX Security 2022), we identify and resolve experimental pitfalls in synthetic identity generation: positional index leakage, baseline information asymmetry, and rule saturation where simple tabular models match complex neural architectures. We establish that residual skip connections are theoretically and empirically essential to preserve raw configuration attributes and maintain non-vanishing gradient bounds with respect to input features; omitting them triggers severe representation decay, reducing Macro-F1 from $0.9986$ to $0.4768$.

On a sanitized benchmark of 700 enterprise environments evaluated under 5-fold cross-validation, CertGraph achieves a Macro-F1 score of **0.9986 ± 0.0029**, outperforming isolated signature heuristics ($0.7791 \pm 0.0247$) and flat feature-only classifiers ($0.8600 \pm 0.0130$). To examine out-of-distribution generalization, we design an adversarial **Zero-Shot Hard Negative** benchmark where models trained on standard topologies are evaluated against non-exploitable templates bearing dangerous flags ($n = 63$). Under this distribution shift, pure neural models succumb to shortcut learning, achieving $1.59\%$ accuracy (95% Wilson CI: $0.3\%$--$8.5\%$) by relying on template flag correlations rather than path reachability. Conversely, symbolic graph traversal achieves $84.13\%$ accuracy (95% Wilson CI: $73.1\%$--$91.2\%$).

These findings motivate a **Two-Tier Neuro-Symbolic Architecture** that pairs fast relational GNN screening for candidate prioritization with targeted symbolic graph verification for deterministic exploitability proofs. Finally, we formulate the enterprise identity access interdiction problem within a Stackelberg game-theoretic framework and prove its NP-hardness via reduction to Directed Multiterminal Cut.

<br>

**Keywords:** Active Directory Certificate Services (ADCS), Graph Attention Networks, Heterogeneous Graphs, Identity and Access Management, Neuro-Symbolic Security, Shortcut Learning, Autonomous Cyber Defense.

# Table of Contents {.unnumbered}
