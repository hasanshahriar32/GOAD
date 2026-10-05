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
| **Date:** October, 2026 | **Student ID: 2002126** |
| **Place:** HSTU, Dinajpur | **Student ID: 2002138** |
| | **Student ID: 2102151** |
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

Active Directory Certificate Services (ADCS) forms the cryptographic backbone of enterprise identity, issuing credentials for domain authentication and single sign-on. Misconfigured certificate templates, access control lists (ACLs), and issuance policies introduce systemic privilege escalation vectors (ESC1--ESC15+) that enable unprivileged accounts to compromise entire Active Directory domains. Signature-based scanners (e.g., Certipy, BloodHound) evaluate flags in isolation and incur high traversal overhead on large topologies. In this thesis, we present **CertGraph**, a heterogeneous Graph Attention Network (Hetero-GAT) that models enterprise identity as a typed multigraph $G = (V, E, \mathcal{T}_V, \mathcal{T}_E)$ to detect structural escalation paths across core vectors (ESC1, ESC2, ESC3, ESC4, ESC9, and ESC13).

Grounding our evaluation in the security machine learning framework of Arp et al. (USENIX Security 2022), we identify and resolve three systemic pitfalls in synthetic identity datasets: positional index leakage, baseline feature asymmetry, and rule saturation. We prove mathematically (Theorem 1) that residual skip-connections are indispensable for preventing representation collapse on identity graphs; omitting them makes template representations independent of input flags, reducing classification Macro-F1 from 0.9986 to 0.4768. On an audited 700-environment enterprise benchmark evaluated under 5-fold cross-validation with Nadeau-Bengio corrected variance, CertGraph achieves a Macro-F1 of 0.9986, substantially outperforming flat classifiers (0.8600) and signature heuristics (0.7791).

However, when evaluated against an adversarial Zero-Shot Hard Negative suite ($n = 63$) containing benign templates with dangerous flags, pure neural models collapse to 1.59% accuracy due to shortcut learning on isolated attributes, whereas symbolic graph traversal achieves 84.13%. To resolve this dichotomy, we formulate a Two-Tier Neuro-Symbolic architecture pairing rapid GNN candidate screening (filtering >89% of benign templates) with a localized symbolic verification oracle to eliminate false positives by construction. Finally, we model identity privilege revocation as a Stackelberg security game, prove its NP-hardness via reduction from Directed Multiway Cut, and demonstrate a greedy capacity-disruption heuristic that severs up to 68.6% of compromise paths under bounded operational budgets ($p < 10^{-8}$).

<br>

**Keywords:** Active Directory Certificate Services (ADCS), Graph Attention Networks, Heterogeneous Graphs, Identity and Access Management, Neuro-Symbolic Security, Autonomous Cyber Defense.

# Table of Contents {.unnumbered}
