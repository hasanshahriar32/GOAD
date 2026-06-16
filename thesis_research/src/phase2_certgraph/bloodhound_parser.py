"""
bloodhound_parser.py — Parse real BloodHound JSON dumps into PyG HeteroData graphs.
=================================================================================
Parses users, groups, and computers from BloodHound JSON files (SharpHound v5 format)
and builds a PyTorch Geometric HeteroData graph matching the CertGraph schema.
Supports injecting ADCS template nodes and edges to simulate ESC attacks on real topologies.
"""

import os
import glob
import json
import random
import torch
from torch_geometric.data import HeteroData
from generator import (
    TEMPLATE_GENERATORS, template_to_features, CLASS_TO_IDX,
    USER_FEATURE_DIM, GROUP_FEATURE_DIM, COMPUTER_FEATURE_DIM, CA_FEATURE_DIM
)

def find_bloodhound_files(data_dir: str) -> dict[str, str]:
    """Find the latest user, group, and computer JSON files in data_dir."""
    patterns = {
        "users": "*_users.json",
        "groups": "*_groups.json",
        "computers": "*_computers.json"
    }
    files = {}
    for key, pat in patterns.items():
        matched = glob.glob(os.path.join(data_dir, pat))
        if not matched:
            raise FileNotFoundError(f"Could not find any files matching {pat} in {data_dir}")
        # Sort to get the latest by name (which usually starts with timestamp)
        matched.sort()
        files[key] = matched[-1]
    return files

def parse_bloodhound_dir(data_dir: str) -> HeteroData:
    """
    Parse BloodHound JSON files from a directory and return a PyG HeteroData object.
    Resolves SIDs and constructs User, Group, Computer nodes and member_of / generic_all edges.
    """
    files = find_bloodhound_files(data_dir)
    
    # Load JSON files
    with open(files["users"], "r") as f:
        users_data = json.load(f)["data"]
    with open(files["groups"], "r") as f:
        groups_data = json.load(f)["data"]
    with open(files["computers"], "r") as f:
        computers_data = json.load(f)["data"]

    # Initialize HeteroData
    data = HeteroData()

    # 1. Build SID registries and map properties to indices
    user_sids = {}
    group_sids = {}
    comp_sids = {}

    # Helper: get property safely
    def get_prop(node, prop, default=False):
        return node.get("Properties", {}).get(prop, default)

    # 1a. Parse Users
    user_feats = []
    user_names = []
    for idx, u in enumerate(users_data):
        sid = u["ObjectIdentifier"]
        user_sids[sid] = idx
        user_names.append(get_prop(u, "name", "UNKNOWN"))
        
        # User feature vector (6 dims):
        # [constant 1.0, admincount, sensitive, dontreqpreauth, unconstraineddelegation, is_admin]
        admincount = 1.0 if get_prop(u, "admincount") else 0.0
        sensitive = 1.0 if get_prop(u, "sensitive") else 0.0
        dontreqpreauth = 1.0 if get_prop(u, "dontreqpreauth") else 0.0
        unconstraineddelegation = 1.0 if get_prop(u, "unconstraineddelegation") else 0.0
        # is_admin will be resolved post-membership mapping, default to admincount for now
        user_feats.append([1.0, admincount, sensitive, dontreqpreauth, unconstraineddelegation, admincount])
    
    # 1b. Parse Groups
    group_feats = []
    group_names = []
    for idx, g in enumerate(groups_data):
        sid = g["ObjectIdentifier"]
        group_sids[sid] = idx
        group_names.append(get_prop(g, "name", "UNKNOWN"))
        
        # Group feature vector (2 dims):
        # [highvalue, admincount]
        highvalue = 1.0 if get_prop(g, "highvalue") else 0.0
        admincount = 1.0 if get_prop(g, "admincount") else 0.0
        group_feats.append([highvalue, admincount])

    # 1c. Parse Computers
    comp_feats = []
    comp_names = []
    for idx, c in enumerate(computers_data):
        sid = c["ObjectIdentifier"]
        comp_sids[sid] = idx
        comp_names.append(get_prop(c, "name", "UNKNOWN"))
        
        # Computer feature vector (3 dims):
        # [constant 1.0, unconstraineddelegation, highvalue]
        unconstraineddelegation = 1.0 if get_prop(c, "unconstraineddelegation") else 0.0
        highvalue = 1.0 if get_prop(c, "highvalue") else 0.0
        comp_feats.append([1.0, unconstraineddelegation, highvalue])

    # 2. Extract edges from membership relations
    user_group_edges = []
    group_group_edges = []
    comp_group_edges = []

    for g_idx, g in enumerate(groups_data):
        for member in g.get("Members", []):
            m_sid = member["ObjectIdentifier"]
            m_type = member["ObjectType"]
            
            if m_type == "User" and m_sid in user_sids:
                user_group_edges.append([user_sids[m_sid], g_idx])
            elif m_type == "Group" and m_sid in group_sids:
                group_group_edges.append([group_sids[m_sid], g_idx])
            elif m_type == "Computer" and m_sid in comp_sids:
                comp_group_edges.append([comp_sids[m_sid], g_idx])

    # Resolve "is_admin" feature based on membership in "DOMAIN ADMINS" or similar group
    admin_group_indices = set()
    for sid, idx in group_sids.items():
        name = group_names[idx].upper()
        if "DOMAIN ADMINS" in name or "ADMINISTRATORS" in name or "ENTERPRISE ADMINS" in name:
            admin_group_indices.add(idx)

    # Simple transitive membership lookup for users
    def get_transitive_groups(u_idx):
        visited = set()
        # Direct groups
        queue = [g for u, g in user_group_edges if u == u_idx]
        while queue:
            g = queue.pop(0)
            if g not in visited:
                visited.add(g)
                # Nesting groups
                parents = [parent for child, parent in group_group_edges if child == g]
                queue.extend(parents)
        return visited

    for u_idx in range(len(user_feats)):
        member_groups = get_transitive_groups(u_idx)
        if member_groups.intersection(admin_group_indices):
            user_feats[u_idx][5] = 1.0  # is_admin = True

    # Assign node features to PyG tensors
    data["User"].x = torch.tensor(user_feats, dtype=torch.float)
    data["Group"].x = torch.tensor(group_feats, dtype=torch.float)
    data["Computer"].x = torch.tensor(comp_feats, dtype=torch.float)

    # Assign member_of edge indexes
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

    # 3. Extract Group-to-Group generic_all edges from ACEs
    group_group_ace_edges = []
    ace_privileges = {"GenericAll", "GenericWrite", "WriteDacl", "WriteOwner", "Owns"}
    for g_idx, g in enumerate(groups_data):
        for ace in g.get("Aces", []):
            p_sid = ace["PrincipalSID"]
            p_type = ace["PrincipalType"]
            right = ace["RightName"]
            
            if right in ace_privileges and p_type == "Group" and p_sid in group_sids:
                group_group_ace_edges.append([group_sids[p_sid], g_idx])

    if group_group_ace_edges:
        data["Group", "generic_all", "Group"].edge_index = (
            torch.tensor(group_group_ace_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Group", "generic_all", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)

    # Save meta for debugging
    data.user_names = user_names
    data.group_names = group_names
    data.comp_names = comp_names
    data.user_sids = user_sids
    data.group_sids = group_sids

    return data

def inject_adcs_vulnerability(
    data: HeteroData,
    esc_class: str,
    target_template_idx: int = 0
) -> tuple[HeteroData, int]:
    """
    Injects ADCS certificate templates and CAs with specific configurations to test CertGraph.
    Connects enrollment and ACL modification permissions based on real topology nodes.
    
    Returns:
        Modified HeteroData object
        Index of the injected target template
    """
    num_users = data["User"].x.shape[0]
    num_groups = data["Group"].x.shape[0]

    # 1. Inject CA Node
    # CA feature vector (3 dims): [highvalue, is_enterprise, enabled]
    ca_feats = [[1.0, 1.0, 1.0]]
    data["CA"].x = torch.tensor(ca_feats, dtype=torch.float)

    # 2. Inject target template & some extra safe templates
    target_tmpl = TEMPLATE_GENERATORS[esc_class]()
    templates = [target_tmpl]
    
    # Generate 2 extra safe templates
    templates.append(TEMPLATE_GENERATORS["Safe"]())
    templates.append(TEMPLATE_GENERATORS["Safe"]())

    template_feats = [template_to_features(t) for t in templates]
    data["Template"].x = torch.tensor(template_feats, dtype=torch.float)

    # Assign labels
    labels = torch.full((len(templates),), CLASS_TO_IDX["Safe"], dtype=torch.long)
    labels[target_template_idx] = CLASS_TO_IDX[esc_class]
    data["Template"].y = labels

    # 3. Connect ("Template", "issued_by", "CA") edges
    issued_edges = [[t, 0] for t in range(len(templates))]
    data["Template", "issued_by", "CA"].edge_index = (
        torch.tensor(issued_edges, dtype=torch.long).t().contiguous()
    )

    # Identify low-privileged and high-privileged users/groups in real topology
    # Low-priv: not admin, not highvalue
    low_priv_users = []
    admin_users = []
    for u_idx in range(num_users):
        is_admin = data["User"].x[u_idx, 5].item() > 0.5
        if is_admin:
            admin_users.append(u_idx)
        else:
            low_priv_users.append(u_idx)

    # If no low-priv or admin users, fallback to random indices
    if not low_priv_users:
        low_priv_users = [0]
    if not admin_users:
        admin_users = [0]

    # Find a high-value group to link policy OID for ESC13
    da_idx = 0
    for g_idx in range(num_groups):
        name = data.group_names[g_idx].upper()
        if "DOMAIN ADMINS" in name or "ADMINISTRATORS" in name:
            da_idx = g_idx
            break

    # Connect Edges:
    enroll_edges = []
    tmpl_acl_edges = []
    policy_edges = []

    # Inject edges for templates
    for t_idx, tmpl in enumerate(templates):
        is_target = (t_idx == target_template_idx)
        is_hn_esc1 = tmpl.get("hard_negative_type") == "ESC1"
        is_hn_esc4 = tmpl.get("hard_negative_type") == "ESC4"
        is_hn_esc13 = tmpl.get("hard_negative_type") == "ESC13"

        # Enrollment edges:
        if is_target and esc_class == "ESC1":
            # Real ESC1: Low-priv users can enroll
            for u in low_priv_users[:3]:
                enroll_edges.append([u, t_idx])
        elif is_target and is_hn_esc1:
            # HN ESC1: Only admins can enroll
            for u in admin_users:
                enroll_edges.append([u, t_idx])
        else:
            # Default enrollment
            for u in low_priv_users[:2]:
                enroll_edges.append([u, t_idx])
            for u in admin_users[:1]:
                enroll_edges.append([u, t_idx])

        # Write ACL edges (WriteDacl/WriteOwner/GenericAll):
        if is_target and esc_class == "ESC4":
            # Real ESC4: Writable by low-priv users
            for u in low_priv_users[:2]:
                tmpl_acl_edges.append([u, t_idx])
        elif is_target and is_hn_esc4:
            # HN ESC4: Writable only by admin users
            for u in admin_users:
                tmpl_acl_edges.append([u, t_idx])
        elif tmpl.get("has_vulnerable_acl"):
            # Safe/Other templates with ACL flag set
            for u in admin_users[:1]:
                tmpl_acl_edges.append([u, t_idx])

        # Issuance Policy edges:
        if is_target and esc_class == "ESC13":
            # Real ESC13: Policy linked to domain admin group
            policy_edges.append([t_idx, da_idx])
        elif is_target and is_hn_esc13:
            # HN ESC13: Linked to random safe group instead of high-value
            policy_edges.append([t_idx, num_groups - 1])

    # Assign edges to PyG data
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
        rev_edges = [[g, t] for t, g in policy_edges]
        data["Group", "links_policy", "Template"].edge_index = (
            torch.tensor(rev_edges, dtype=torch.long).t().contiguous()
        )
    else:
        data["Template", "linked_to", "Group"].edge_index = torch.empty((2, 0), dtype=torch.long)
        data["Group", "links_policy", "Template"].edge_index = torch.empty((2, 0), dtype=torch.long)

    return data, target_template_idx
