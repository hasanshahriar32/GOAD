"""
adsynth_adapter.py — Microsoft Tiered AD Topology Generator
==========================================================
Generates enterprise-realistic Active Directory topologies following Microsoft's
three-tier administrative model (Tier 0, Tier 1, Tier 2) as described in the ADSynth
research. Simulates realistic nested group memberships and administrative boundary control.
"""

import random
import numpy as np
import torch
from torch_geometric.data import HeteroData

from generator import (
    TEMPLATE_GENERATORS, template_to_features, CLASS_TO_IDX,
    USER_FEATURE_DIM, GROUP_FEATURE_DIM, COMPUTER_FEATURE_DIM, CA_FEATURE_DIM
)

def generate_adsynth_environment(
    esc_class: str,
    num_users: int = 150,
    num_groups: int = 40,
    num_computers: int = 50,
    num_extra_templates: int = 3,
    seed: int | None = None
) -> tuple[HeteroData, int]:
    """
    Generate an AD environment structured by Microsoft's Tiered administration model:
    - Tier 0: Domain Controllers, Domain Admins, T0 Admins, Enterprise Admins.
    - Tier 1: Application Servers, Application Admins, Database Servers.
    - Tier 2: Workstations, Users, Helpdesk.
    """
    if seed is not None:
        random.seed(seed)
        np.random.seed(seed)

    data = HeteroData()

    # 1. Tier Assignments for Nodes
    # Split users, groups, and computers across Tiers (T0, T1, T2)
    # T0 is small (~10%), T1 is medium (~30%), T2 is large (~60%)
    
    # 1a. Users
    t0_users = max(2, int(num_users * 0.08))
    t1_users = max(5, int(num_users * 0.25))
    t2_users = num_users - t0_users - t1_users

    user_feats = []
    user_tiers = []
    
    # Tier 0 Users (Admins)
    for _ in range(t0_users):
        user_feats.append([1.0, 1.0, 1.0, 0.0, 1.0, 1.0]) # admincount, sensitive, is_admin
        user_tiers.append(0)
    # Tier 1 Users (Server Operators)
    for _ in range(t1_users):
        is_del = 1.0 if random.random() < 0.2 else 0.0
        user_feats.append([1.0, 0.0, 0.0, 0.0, is_del, 0.0])
        user_tiers.append(1)
    # Tier 2 Users (Standard Users)
    for _ in range(t2_users):
        dontreq = 1.0 if random.random() < 0.05 else 0.0
        user_feats.append([1.0, 0.0, 0.0, dontreq, 0.0, 0.0])
        user_tiers.append(2)

    data["User"].x = torch.tensor(user_feats, dtype=torch.float)

    # 1b. Groups
    t0_groups = max(2, int(num_groups * 0.15))
    t1_groups = max(4, int(num_groups * 0.30))
    t2_groups = num_groups - t0_groups - t1_groups

    group_feats = []
    group_tiers = []
    
    # Tier 0 Groups (e.g. Domain Admins, Schema Admins)
    for _ in range(t0_groups):
        group_feats.append([1.0, 1.0]) # highvalue, admincount
        group_tiers.append(0)
    # Tier 1 Groups (e.g. Server Admins, Database Admins)
    for _ in range(t1_groups):
        group_feats.append([0.0, 0.0])
        group_tiers.append(1)
    # Tier 2 Groups (e.g. Helpdesk, Department Groups)
    for _ in range(t2_groups):
        group_feats.append([0.0, 0.0])
        group_tiers.append(2)

    data["Group"].x = torch.tensor(group_feats, dtype=torch.float)

    # 1c. Computers
    t0_comps = max(1, int(num_computers * 0.06)) # DCs
    t1_comps = max(3, int(num_computers * 0.25)) # Servers
    t2_comps = num_computers - t0_comps - t1_comps # Workstations

    comp_feats = []
    comp_tiers = []

    # Tier 0 Computers (DCs)
    for _ in range(t0_comps):
        comp_feats.append([1.0, 1.0, 1.0]) # dc flag / highvalue / unconstrained delegation
        comp_tiers.append(0)
    # Tier 1 Computers (Application/DB Servers)
    for _ in range(t1_comps):
        comp_feats.append([1.0, 0.0, 0.0])
        comp_tiers.append(1)
    # Tier 2 Computers (Workstations)
    for _ in range(t2_comps):
        comp_feats.append([1.0, 0.0, 0.0])
        comp_tiers.append(2)

    data["Computer"].x = torch.tensor(comp_feats, dtype=torch.float)

    # 1d. CAs (Always Tier 0)
    data["CA"].x = torch.tensor([[1.0, 1.0, 1.0]], dtype=torch.float)

    # 2. Administrative & Membership Relationships (Edges)
    # Rules:
    # - Users are members of groups in their tier.
    # - Groups can be nested (member_of other groups) within their tier.
    # - Higher tier groups control lower tier targets (e.g. T0 manages T1 groups).
    # - Cross-tier misconfigurations: very rare, but present to test path reasoning.
    
    user_group_edges = []
    group_group_edges = []
    comp_group_edges = []
    group_group_ace_edges = []

    # 2a. User-Group Memberships
    # Direct memberships
    for u_idx in range(num_users):
        u_tier = user_tiers[u_idx]
        # Find groups of the same tier
        same_tier_groups = [g for g in range(num_groups) if group_tiers[g] == u_tier]
        if same_tier_groups:
            # Join 1-2 groups of the same tier
            g_choice = random.choice(same_tier_groups)
            user_group_edges.append([u_idx, g_choice])
            if random.random() < 0.4 and len(same_tier_groups) > 1:
                g_choice2 = random.choice(same_tier_groups)
                if g_choice2 != g_choice:
                    user_group_edges.append([u_idx, g_choice2])
        
        # Add rare cross-tier misconfiguration (T2 user in T0 group)
        if u_tier == 2 and random.random() < 0.005:
            t0_g = [g for g in range(num_groups) if group_tiers[g] == 0]
            if t0_g:
                user_group_edges.append([u_idx, random.choice(t0_g)])

    # 2b. Nested Group Memberships
    # Group nesting within the same tier
    for tier in [0, 1, 2]:
        tier_groups = [g for g in range(num_groups) if group_tiers[g] == tier]
        if len(tier_groups) > 1:
            for g_child in tier_groups[1:]:
                # Child group can be member of a parent group in the same tier
                if random.random() < 0.2:
                    g_parent = random.choice(tier_groups)
                    if g_parent != g_child:
                        group_group_edges.append([g_child, g_parent])

    # 2c. Computer Memberships
    # Computers belong to groups of their same tier
    for c_idx in range(num_computers):
        c_tier = comp_tiers[c_idx]
        same_tier_groups = [g for g in range(num_groups) if group_tiers[g] == c_tier]
        if same_tier_groups:
            comp_group_edges.append([c_idx, random.choice(same_tier_groups)])

    # 2d. Group-to-Group generic_all ACEs
    # Higher tier groups control lower tier groups: T0 has generic_all over T1 & T2 groups
    t0_groups_list = [g for g in range(num_groups) if group_tiers[g] == 0]
    t1_groups_list = [g for g in range(num_groups) if group_tiers[g] == 1]
    t2_groups_list = [g for g in range(num_groups) if group_tiers[g] == 2]

    # T0 controls T1 & T2
    if t0_groups_list:
        for dst_g in t1_groups_list + t2_groups_list:
            if random.random() < 0.15:
                src_g = random.choice(t0_groups_list)
                group_group_ace_edges.append([src_g, dst_g])
    
    # T1 controls T2
    if t1_groups_list:
        for dst_g in t2_groups_list:
            if random.random() < 0.10:
                src_g = random.choice(t1_groups_list)
                group_group_ace_edges.append([src_g, dst_g])

    # Assign base edges
    if user_group_edges:
        data["User", "member_of", "Group"].edge_index = (
            torch.tensor(user_group_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "member_of", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    if group_group_edges:
        data["Group", "member_of", "Group"].edge_index = (
            torch.tensor(group_group_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Group", "member_of", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    if comp_group_edges:
        data["Computer", "member_of", "Group"].edge_index = (
            torch.tensor(comp_group_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Computer", "member_of", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    if group_group_ace_edges:
        data["Group", "generic_all", "Group"].edge_index = (
            torch.tensor(group_group_ace_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Group", "generic_all", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # 3. Layer ADCS Certificate Templates & Authority
    # Generate templates
    target_tmpl = TEMPLATE_GENERATORS[esc_class]()
    templates = [target_tmpl]
    
    for _ in range(num_extra_templates):
        extra_class = random.choice(["Safe", "Safe", "Safe", esc_class])
        templates.append(TEMPLATE_GENERATORS[extra_class]())

    template_feats = [template_to_features(t) for t in templates]
    data["Template"].x = torch.tensor(template_feats, dtype=torch.float)

    # Assign labels
    labels = torch.full((len(templates),), CLASS_TO_IDX["Safe"], dtype=torch.long)
    labels[0] = CLASS_TO_IDX[esc_class]
    data["Template"].y = labels

    # Connect CA
    issued_edges = [[t, 0] for t in range(len(templates))]
    data["Template", "issued_by", "CA"].edge_index = (
        torch.tensor(issued_edges, dtype=torch.long).t().contiguous()
    )

    # Identify user groups by privilege
    # Admins are T0 users
    admin_users = [u for u in range(num_users) if user_tiers[u] == 0]
    # Low privilege are T2 users
    low_priv_users = [u for u in range(num_users) if user_tiers[u] == 2]

    # Find T0 group for policy OID links
    da_group_choice = t0_groups_list[0] if t0_groups_list else 0

    enroll_edges = []
    tmpl_acl_edges = []
    policy_edges = []

    for t_idx, tmpl in enumerate(templates):
        is_target = (t_idx == 0)
        is_hn_esc1 = tmpl.get("hard_negative_type") == "ESC1"
        is_hn_esc4 = tmpl.get("hard_negative_type") == "ESC4"
        is_hn_esc13 = tmpl.get("hard_negative_type") == "ESC13"

        # Enrollment:
        if is_target and esc_class == "ESC1":
            # Real ESC1: T2 user can enroll
            for u in low_priv_users[:4]:
                enroll_edges.append([u, t_idx])
        elif is_target and is_hn_esc1:
            # HN ESC1: Only T0 user can enroll
            for u in admin_users[:4]:
                enroll_edges.append([u, t_idx])
        else:
            # Safe/Default enrollment
            for u in low_priv_users[:2]:
                enroll_edges.append([u, t_idx])
            for u in admin_users[:2]:
                enroll_edges.append([u, t_idx])

        # Write ACL:
        if is_target and esc_class == "ESC4":
            # Real ESC4: Writable by T2 users
            for u in low_priv_users[:2]:
                tmpl_acl_edges.append([u, t_idx])
        elif is_target and is_hn_esc4:
            # HN ESC4: Writable only by T0 users
            for u in admin_users[:2]:
                tmpl_acl_edges.append([u, t_idx])
        elif tmpl.get("has_vulnerable_acl"):
            for u in admin_users[:1]:
                tmpl_acl_edges.append([u, t_idx])

        # Issuance Policy OID:
        if is_target and esc_class == "ESC13":
            policy_edges.append([t_idx, da_group_choice])
        elif is_target and is_hn_esc13:
            # Link to Tier 2 group (safe group)
            if t2_groups_list:
                policy_edges.append([t_idx, random.choice(t2_groups_list)])

    # Assign template edges
    if enroll_edges:
        data["User", "enrolls", "Template"].edge_index = (
            torch.tensor(enroll_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "enrolls", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    if tmpl_acl_edges:
        data["User", "write_dacl", "Template"].edge_index = (
            torch.tensor(tmpl_acl_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "write_dacl", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    if policy_edges:
        data["Template", "linked_to", "Group"].edge_index = (
            torch.tensor(policy_edges, dtype=torch.long).t().contiguous()
        )
        # Reverse edge: Group → links_policy → Template (for GNN message passing)
        reverse_policy = [[g, t] for t, g in policy_edges]
        data["Group", "links_policy", "Template"].edge_index = (
            torch.tensor(reverse_policy, dtype=torch.long).t().contiguous()
        )
    else:
        data["Template", "linked_to", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)
        data["Group", "links_policy", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    return data, 0

def generate_adsynth_dataset(
    num_envs: int = 500,
    balanced: bool = True,
    seed: int = 42
) -> list[tuple[HeteroData, str, int]]:
    """Generate a balanced/unbalanced ADSynth-structured dataset."""
    random.seed(seed)
    np.random.seed(seed)

    dataset = []
    classes = ["ESC1", "ESC2", "ESC3", "ESC4", "ESC9", "ESC13", "Safe"]
    num_classes = len(classes)
    
    if balanced:
        per_class = num_envs // num_classes
        remainder = num_envs % num_classes
        class_counts = {c: per_class for c in classes}
        for i, c in enumerate(classes):
            if i < remainder:
                class_counts[c] += 1
    else:
        class_counts = {c: num_envs // num_classes for c in classes}

    env_id = 0
    for esc_class, count in class_counts.items():
        for _ in range(count):
            data, target_idx = generate_adsynth_environment(
                esc_class=esc_class,
                seed=seed + env_id
            )
            dataset.append((data, esc_class, target_idx))
            env_id += 1

    random.shuffle(dataset)
    return dataset
