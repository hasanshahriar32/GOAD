"""
certgraph_generator.py — Synthetic AD Environment Generator for CertGraph
==========================================================================
Generates labeled synthetic Active Directory environments with varying
ESC vulnerability configurations for training the CertGraph classifier.

Each environment contains:
  - Users, Groups, Computers (with realistic AD properties)
  - Certificate Templates (labeled ESC1/ESC2/ESC3/ESC4/ESC9/ESC13/Safe)
  - Certificate Authority node
  - Membership, ACE, and enrollment edges

ESC Classification Rules (from SpecterOps/Certipy research):
  ESC1:  ENROLLEE_SUPPLIES_SUBJECT (flag & 0x1) + Client Auth EKU + no manager approval + no RA sig
  ESC2:  Any Purpose EKU (2.5.29.37.0) or no EKU + no manager approval
  ESC3:  Certificate Request Agent EKU (1.3.6.1.4.1.311.20.2.1) + RA signature required on dependent
  ESC4:  Template has vulnerable write ACEs (WriteDacl/WriteOwner/GenericAll by low-priv principal)
  ESC9:  No security extension (CT_FLAG_NO_SECURITY_EXTENSION=0x80000) + Client Auth
  ESC13: Issuance policy OID linked to group + Client Auth + no enrollee-supplies-subject
  Safe:  None of the above conditions met
"""

import json
import os
import random
import numpy as np
import torch
from torch_geometric.data import HeteroData

# ── EKU OIDs ──
EKU_CLIENT_AUTH = "1.3.6.1.5.5.7.3.2"
EKU_ANY_PURPOSE = "2.5.29.37.0"
EKU_CERT_REQUEST_AGENT = "1.3.6.1.4.1.311.20.2.1"
EKU_CODE_SIGNING = "1.3.6.1.5.5.7.3.3"
EKU_EMAIL_PROTECTION = "1.3.6.1.5.5.7.3.4"
EKU_EFS = "1.3.6.1.4.1.311.10.3.4"
EKU_SERVER_AUTH = "1.3.6.1.5.5.7.3.1"

# ── Flag constants ──
CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT = 0x1
CT_FLAG_NO_SECURITY_EXTENSION = 0x80000

ESC_CLASSES = ["ESC1", "ESC2", "ESC3", "ESC4", "ESC9", "ESC13", "Safe"]
NUM_CLASSES = len(ESC_CLASSES)
CLASS_TO_IDX = {c: i for i, c in enumerate(ESC_CLASSES)}


# ─────────────────────────────────────────────────────────────────────
# Template generators — one per ESC class
# ─────────────────────────────────────────────────────────────────────

def _gen_esc1_template() -> dict:
    """ESC1: Enrollee supplies subject + Client Auth + no approval + no RA sig."""
    return {
        "name_flag": CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT,
        "enrollment_flag": 0,
        "ra_signature": 0,
        "ekus": [EKU_CLIENT_AUTH],
        "has_issuance_policy_oid": False,
        "has_vulnerable_acl": False,
        "schema_version": 2,
        "hard_negative_type": None,
    }


def _gen_esc2_template() -> dict:
    """ESC2: Any Purpose EKU or SubCA + no manager approval."""
    return {
        "name_flag": random.choice([0, 0x2000000]),
        "enrollment_flag": random.choice([0, 32]),
        "ra_signature": 0,
        "ekus": [EKU_ANY_PURPOSE],
        "has_issuance_policy_oid": False,
        "has_vulnerable_acl": False,
        "schema_version": 2,
        "hard_negative_type": None,
    }


def _gen_esc3_template() -> dict:
    """ESC3: Certificate Request Agent EKU + RA sig on dependent template."""
    return {
        "name_flag": random.choice([0, 0x2000000]),
        "enrollment_flag": random.choice([0, 32]),
        "ra_signature": 1,
        "ekus": [EKU_CERT_REQUEST_AGENT] if random.random() < 0.5 else [EKU_CLIENT_AUTH],
        "has_issuance_policy_oid": False,
        "has_vulnerable_acl": False,
        "schema_version": 2,
        "hard_negative_type": None,
    }


def _gen_esc4_template() -> dict:
    """ESC4: Template has writable ACEs by low-priv principals."""
    return {
        "name_flag": random.choice([0, 0x2000000]),
        "enrollment_flag": random.choice([0, 32, 43]),
        "ra_signature": random.choice([0, 1]),
        "ekus": [random.choice([EKU_CODE_SIGNING, EKU_CLIENT_AUTH, EKU_SERVER_AUTH])],
        "has_issuance_policy_oid": False,
        "has_vulnerable_acl": True,
        "schema_version": 2,
        "hard_negative_type": None,
    }


def _gen_esc9_template() -> dict:
    """ESC9: No security extension flag + Client Auth."""
    return {
        "name_flag": 0x2000000,
        "enrollment_flag": CT_FLAG_NO_SECURITY_EXTENSION | random.choice([0, 9]),
        "ra_signature": 0,
        "ekus": [EKU_CLIENT_AUTH] + random.sample([EKU_EFS, EKU_EMAIL_PROTECTION], k=random.randint(0, 2)),
        "has_issuance_policy_oid": False,
        "has_vulnerable_acl": False,
        "schema_version": 2,
        "hard_negative_type": None,
    }


def _gen_esc13_template() -> dict:
    """ESC13: Issuance policy OID linked to group + Client Auth."""
    return {
        "name_flag": 0x2000000,
        "enrollment_flag": 0,
        "ra_signature": 0,
        "ekus": [EKU_CLIENT_AUTH],
        "has_issuance_policy_oid": True,
        "has_vulnerable_acl": False,
        "schema_version": 2,
        "hard_negative_type": None,
    }


def _gen_safe_template(include_hard_negatives: bool = True) -> dict:
    """
    Safe: Non-vulnerable template.
    Adversarial Modification: Safe templates can include 'Hard Negatives'
    that look like vulnerabilities based on configuration flags, but lack the critical
    graph permissions (edges) required for exploitation.
    """
    if not include_hard_negatives:
        mode = "Normal"
    else:
        mode = random.choice(["Normal", "HN_ESC1", "HN_ESC4", "HN_ESC13"])

    if mode == "Normal":
        return {
            "name_flag": 0x2000000,  # no enrollee-supplies-subject
            "enrollment_flag": random.choice([0, 2, 32]),  # may require approval
            "ra_signature": random.choice([0, 1]),
            "ekus": [random.choice([EKU_CODE_SIGNING, EKU_SERVER_AUTH, EKU_EMAIL_PROTECTION])],
            "has_issuance_policy_oid": False,
            "has_vulnerable_acl": False,
            "schema_version": random.choice([1, 2, 4]),
            "hard_negative_type": None,
            "hn_variant": None,
        }
    elif mode == "HN_ESC1":
        # Features match ESC1, but we block enrollment edges for low-priv users
        return {
            "name_flag": CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT,
            "enrollment_flag": 0,
            "ra_signature": 0,
            "ekus": [EKU_CLIENT_AUTH],
            "has_issuance_policy_oid": False,
            "has_vulnerable_acl": False,
            "schema_version": 2,
            "hard_negative_type": "ESC1",
            "hn_variant": None,
        }
    elif mode == "HN_ESC4":
        # Features match ESC4, but vulnerable write access is restricted to admins
        return {
            "name_flag": random.choice([0, 0x2000000]),
            "enrollment_flag": random.choice([0, 32, 43]),
            "ra_signature": random.choice([0, 1]),
            "ekus": [random.choice([EKU_CODE_SIGNING, EKU_CLIENT_AUTH, EKU_SERVER_AUTH])],
            "has_issuance_policy_oid": False,
            "has_vulnerable_acl": True,
            "schema_version": 2,
            "hard_negative_type": "ESC4",
            "hn_variant": None,
        }
    else:  # HN_ESC13
        # Features match ESC13, but policy link points to low-value group or enrollment is blocked
        return {
            "name_flag": 0x2000000,
            "enrollment_flag": 0,
            "ra_signature": 0,
            "ekus": [EKU_CLIENT_AUTH],
            "has_issuance_policy_oid": True,
            "has_vulnerable_acl": False,
            "schema_version": 2,
            "hard_negative_type": "ESC13",
            "hn_variant": random.choice(["low_value_group", "admin_only_enroll"]),
        }


TEMPLATE_GENERATORS = {
    "ESC1": _gen_esc1_template,
    "ESC2": _gen_esc2_template,
    "ESC3": _gen_esc3_template,
    "ESC4": _gen_esc4_template,
    "ESC9": _gen_esc9_template,
    "ESC13": _gen_esc13_template,
    "Safe": _gen_safe_template,
}


# ─────────────────────────────────────────────────────────────────────
# Feature extraction (matches CertGraph schema)
# ─────────────────────────────────────────────────────────────────────

def template_to_features(tmpl: dict) -> list[float]:
    """Convert template config to 10-dim feature vector."""
    nf = tmpl["name_flag"]
    ef = tmpl["enrollment_flag"]
    ekus = set(tmpl["ekus"])

    return [
        1.0 if (nf & CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT) else 0.0,
        0.0 if (ef & 0x02) else 1.0,  # manager approval NOT required
        1.0 if (ef & CT_FLAG_NO_SECURITY_EXTENSION) else 0.0,
        1.0 if EKU_CLIENT_AUTH in ekus else 0.0,
        1.0 if EKU_ANY_PURPOSE in ekus else 0.0,
        1.0 if EKU_CERT_REQUEST_AGENT in ekus else 0.0,
        float(tmpl["ra_signature"]),
        1.0 if tmpl["has_issuance_policy_oid"] else 0.0,
        1.0 if tmpl["has_vulnerable_acl"] else 0.0,
        tmpl["schema_version"] / 4.0,
    ]


TEMPLATE_FEATURE_DIM = 10
TEMPLATE_FEATURE_NAMES = [
    "enrollee_supplies_subject", "no_manager_approval", "no_security_extension",
    "has_client_auth", "has_any_purpose", "has_cert_req_agent",
    "ra_signature_required", "has_issuance_policy_oid", "has_vulnerable_acl",
    "schema_version_norm",
]

USER_FEATURE_DIM = 6
GROUP_FEATURE_DIM = 2
COMPUTER_FEATURE_DIM = 3
CA_FEATURE_DIM = 3


# ─────────────────────────────────────────────────────────────────────
# Full environment generator
# ─────────────────────────────────────────────────────────────────────

def generate_environment(
    esc_class: str,
    num_users: int | None = None,
    num_groups: int | None = None,
    num_computers: int | None = None,
    num_extra_templates: int | None = None,
    seed: int | None = None,
    include_hard_negatives: bool = True,
) -> tuple[HeteroData, int]:
    """Generate a single synthetic AD environment with one target template."""
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    num_users = num_users or random.randint(10, 80)
    num_groups = num_groups or random.randint(5, 30)
    num_computers = num_computers or random.randint(1, 5)
    num_extra_templates = num_extra_templates if num_extra_templates is not None else random.randint(0, 3)

    data = HeteroData()

    # ── User features ──
    # Assign admin users randomly across indices (decoupling privilege from index)
    num_admins = max(1, num_users // 10)
    admin_indices = set(random.sample(range(num_users), num_admins))
    lowpriv_indices = set(range(num_users)) - admin_indices

    user_feats = []
    for i in range(num_users):
        is_admin = i in admin_indices
        user_feats.append([
            1.0,
            1.0 if is_admin and random.random() < 0.3 else 0.0,
            1.0 if random.random() < 0.1 else 0.0,
            1.0 if random.random() < 0.05 else 0.0,
            1.0 if random.random() < 0.15 else 0.0,
            1.0 if is_admin else 0.0,
        ])
    data["User"].x = torch.tensor(user_feats, dtype=torch.float)

    # ── Group features ──
    # Assign high-value groups randomly across indices (no fixed group 0 artifact)
    num_hv_groups = max(1, num_groups // 5)
    highvalue_indices = set(random.sample(range(num_groups), num_hv_groups))
    lowvalue_indices = set(range(num_groups)) - highvalue_indices

    group_feats = []
    for i in range(num_groups):
        is_hv = i in highvalue_indices
        group_feats.append([
            1.0 if is_hv else 0.0,
            1.0 if is_hv else 0.0,
        ])
    data["Group"].x = torch.tensor(group_feats, dtype=torch.float)

    # ── Computer features ──
    comp_feats = []
    for i in range(num_computers):
        comp_feats.append([
            1.0,
            1.0 if random.random() < 0.2 else 0.0,
            1.0 if random.random() < 0.3 else 0.0,
        ])
    data["Computer"].x = torch.tensor(comp_feats, dtype=torch.float)

    # ── CA features ──
    ca_feats = [[
        1.0 if random.random() < 0.7 else 0.0,
        1.0 if random.random() < 0.3 else 0.0,
        1.0 if random.random() < 0.5 else 0.0,
    ]]
    data["CA"].x = torch.tensor(ca_feats, dtype=torch.float)

    # ── Template features ──
    # Place target_tmpl at a randomized index target_idx
    target_tmpl = (
        TEMPLATE_GENERATORS[esc_class](include_hard_negatives=include_hard_negatives)
        if esc_class == "Safe"
        else TEMPLATE_GENERATORS[esc_class]()
    )

    templates = []
    target_idx = random.randint(0, num_extra_templates)
    for t_idx in range(num_extra_templates + 1):
        if t_idx == target_idx:
            templates.append(target_tmpl)
        else:
            extra_class = random.choice(["Safe", "Safe", "Safe", esc_class])
            extra_tmpl = (
                TEMPLATE_GENERATORS[extra_class](include_hard_negatives=include_hard_negatives)
                if extra_class == "Safe"
                else TEMPLATE_GENERATORS[extra_class]()
            )
            templates.append(extra_tmpl)

    template_feats = [template_to_features(t) for t in templates]
    data["Template"].x = torch.tensor(template_feats, dtype=torch.float)
    num_templates = len(templates)

    # Template labels
    labels = torch.full((num_templates,), CLASS_TO_IDX["Safe"], dtype=torch.long)
    labels[target_idx] = CLASS_TO_IDX[esc_class]
    data["Template"].y = labels

    # ── User → member_of → Group ──
    user_group_edges = []
    for u in admin_indices:
        for g in highvalue_indices:
            if random.random() < 0.6:
                user_group_edges.append([u, g])
    for u in range(num_users):
        num_memberships = random.randint(1, min(4, num_groups))
        for g in random.sample(range(num_groups), num_memberships):
            user_group_edges.append([u, g])

    if user_group_edges:
        data["User", "member_of", "Group"].edge_index = (
            torch.tensor(user_group_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "member_of", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # ── Group → member_of → Group ──
    group_group_edges = []
    all_groups = list(range(num_groups))
    for g in all_groups:
        if random.random() < 0.25:
            other_groups = [og for og in all_groups if og != g]
            if other_groups:
                parent = random.choice(other_groups)
                group_group_edges.append([g, parent])
    if group_group_edges:
        data["Group", "member_of", "Group"].edge_index = (
            torch.tensor(group_group_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Group", "member_of", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # ── Group → generic_all → Group ──
    ace_edges_gg = []
    for g_src in highvalue_indices:
        for g_dst in range(num_groups):
            if g_src != g_dst and random.random() < 0.15:
                ace_edges_gg.append([g_src, g_dst])
    if ace_edges_gg:
        data["Group", "generic_all", "Group"].edge_index = (
            torch.tensor(ace_edges_gg, dtype=torch.long).t().contiguous()
        )
    else:
        data["Group", "generic_all", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # ── User → write_dacl → Template (ESC4 vs HN_ESC4) ──
    tmpl_acl_edges = []
    for t in range(num_templates):
        tmpl = templates[t]
        if tmpl["has_vulnerable_acl"]:
            is_hn_esc4 = tmpl.get("hard_negative_type") == "ESC4"
            if not is_hn_esc4:
                # Real ESC4: low-privileged users have write DACL
                for u in lowpriv_indices:
                    if random.random() < 0.3:
                        tmpl_acl_edges.append([u, t])
                for u in admin_indices:
                    if random.random() < 0.2:
                        tmpl_acl_edges.append([u, t])
            else:
                # HN_ESC4: ONLY admin users have write DACL
                for u in admin_indices:
                    if random.random() < 0.5:
                        tmpl_acl_edges.append([u, t])
    if tmpl_acl_edges:
        data["User", "write_dacl", "Template"].edge_index = (
            torch.tensor(tmpl_acl_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "write_dacl", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # ── User → enrolls → Template (ESC1 / General Enrollment) ──
    enroll_edges = []
    for t in range(num_templates):
        tmpl = templates[t]
        is_hn_esc1 = tmpl.get("hard_negative_type") == "ESC1"
        is_hn_esc13_admin_only = (
            tmpl.get("hard_negative_type") == "ESC13"
            and tmpl.get("hn_variant") == "admin_only_enroll"
        )

        if is_hn_esc1 or is_hn_esc13_admin_only:
            # Low-priv users blocked; only admins can enroll
            for u in admin_indices:
                if random.random() < 0.4:
                    enroll_edges.append([u, t])
        else:
            # Low-priv users can enroll
            for u in lowpriv_indices:
                if random.random() < 0.4:
                    enroll_edges.append([u, t])
            for u in admin_indices:
                if random.random() < 0.2:
                    enroll_edges.append([u, t])

    if enroll_edges:
        data["User", "enrolls", "Template"].edge_index = (
            torch.tensor(enroll_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "enrolls", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # ── Template → issued_by → CA ──
    issued_edges = [[t, 0] for t in range(num_templates)]
    data["Template", "issued_by", "CA"].edge_index = (
        torch.tensor(issued_edges, dtype=torch.long).t().contiguous()
    )

    # ── Template → linked_to → Group (ESC13 vs HN_ESC13) ──
    policy_edges = []
    for t in range(num_templates):
        tmpl = templates[t]
        if tmpl["has_issuance_policy_oid"]:
            is_hn_esc13 = tmpl.get("hard_negative_type") == "ESC13"
            if not is_hn_esc13:
                # Real ESC13: links to a random HIGH-VALUE group
                target_g = random.choice(list(highvalue_indices))
                policy_edges.append([t, target_g])
            else:
                hn_var = tmpl.get("hn_variant")
                if hn_var == "low_value_group":
                    # Links to a LOW-VALUE group
                    target_g = random.choice(list(lowvalue_indices)) if lowvalue_indices else random.choice(list(highvalue_indices))
                    policy_edges.append([t, target_g])
                else:
                    # Links to a high-value group, but low-priv enrollment is blocked
                    target_g = random.choice(list(highvalue_indices))
                    policy_edges.append([t, target_g])

    if policy_edges:
        data["Template", "linked_to", "Group"].edge_index = (
            torch.tensor(policy_edges, dtype=torch.long).t().contiguous()
        )
        rev_edges = [[g, t] for t, g in policy_edges]
        data["Group", "links_policy", "Template"].edge_index = (
            torch.tensor(rev_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Template", "linked_to", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)
        data["Group", "links_policy", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # ── Computer → member_of → Group ──
    comp_group_edges = [[c, random.randint(0, num_groups - 1)] for c in range(num_computers)]
    data["Computer", "member_of", "Group"].edge_index = (
        torch.tensor(comp_group_edges, dtype=torch.long).t().contiguous()
    )

    return data, target_idx


def generate_dataset(
    num_envs: int = 500,
    balanced: bool = True,
    seed: int = 42,
    include_hard_negatives: bool = True,
) -> list[tuple[HeteroData, str, int]]:
    """Generate a full labeled dataset of synthetic AD environments."""
    random.seed(seed)
    np.random.seed(seed)

    dataset = []
    if balanced:
        per_class = num_envs // NUM_CLASSES
        remainder = num_envs % NUM_CLASSES
        class_counts = {c: per_class for c in ESC_CLASSES}
        for i, c in enumerate(ESC_CLASSES):
            if i < remainder:
                class_counts[c] += 1
    else:
        class_counts = {c: num_envs // NUM_CLASSES for c in ESC_CLASSES}

    env_id = 0
    for esc_class, count in class_counts.items():
        for _ in range(count):
            data, target_idx = generate_environment(
                esc_class=esc_class,
                seed=seed + env_id,
                include_hard_negatives=include_hard_negatives,
            )
            dataset.append((data, esc_class, target_idx))
            env_id += 1

    random.shuffle(dataset)
    return dataset


if __name__ == "__main__":
    print("Dataset generator initialized with robust feature-based logic and hard negatives.")
