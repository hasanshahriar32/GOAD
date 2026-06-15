"""
dataset.py — HGAT Data Pipeline for Active Directory Attack Path Detection
===========================================================================
Parses BloodHound JSON exports and GOAD ESC vulnerability templates into a
PyTorch Geometric HeteroData object with real AD features and relationships.

Node Types: User, Group, Computer, Template
Edge Types: member_of, generic_all, owns, write_dacl, enrolls, impersonates
"""

import json
import glob
import os
import torch
from torch_geometric.data import HeteroData


# Resolve paths relative to the GOAD project root
PROJECT_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
BLOODHOUND_DIR = os.path.join(PROJECT_ROOT, "Thesis_Data")
ESC_TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "ansible/roles/adcs_templates/files")
ESC13_FALLBACK = os.path.join(PROJECT_ROOT, "ad/GOAD/data/ESC13.json")


def _find_bh_file(pattern: str) -> str:
    """Locate a BloodHound JSON file by glob pattern."""
    matches = glob.glob(os.path.join(BLOODHOUND_DIR, pattern))
    if not matches:
        raise FileNotFoundError(
            f"No file matching '{pattern}' in {BLOODHOUND_DIR}/. "
            "Re-run BloodHound collection first."
        )
    return sorted(matches)[-1]  # latest timestamp


def _load_json(path: str) -> dict:
    """Load a JSON file, handling both UTF-8 and UTF-16 (PowerShell) encodings."""
    for encoding in ("utf-8", "utf-16"):
        try:
            with open(path, "r", encoding=encoding) as f:
                return json.load(f)
        except (UnicodeDecodeError, UnicodeError):
            continue
    raise ValueError(f"Cannot decode {path} with utf-8 or utf-16")


# ---------------------------------------------------------------------------
# Feature extractors — one per node type
# ---------------------------------------------------------------------------

def _user_features(user: dict) -> list[float]:
    """
    Extract 6-dim feature vector from a BloodHound user object.
    [enabled, sensitive, hasspn, dontreqpreauth, pwdneverexpires, admincount]
    """
    p = user.get("Properties", {})
    return [
        float(p.get("enabled", False)),
        float(p.get("sensitive", False)),
        float(p.get("hasspn", False)),
        float(p.get("dontreqpreauth", False)),
        float(p.get("pwdneverexpires", False)),
        float(p.get("admincount", False)),
    ]


def _group_features(group: dict) -> list[float]:
    """
    Extract 2-dim feature vector from a BloodHound group object.
    [highvalue, admincount]
    """
    p = group.get("Properties", {})
    return [
        float(p.get("highvalue", False)),
        float(p.get("admincount", False)),
    ]


def _computer_features(computer: dict) -> list[float]:
    """
    Extract 3-dim feature vector from a BloodHound computer object.
    [enabled, unconstraineddelegation, haslaps]
    """
    p = computer.get("Properties", {})
    return [
        float(p.get("enabled", False)),
        float(p.get("unconstraineddelegation", False)),
        float(p.get("haslaps", False)),
    ]


def _template_features(template: dict) -> list[float]:
    """
    Extract 3-dim feature vector from an ESC template JSON.
    [client_auth, no_manager_approval, enrollee_supplies_subject]
    """
    # Client Authentication EKU = 1.3.6.1.5.5.7.3.2
    ekus = template.get("pKIExtendedKeyUsage", [])
    app_policies = template.get("msPKI-Certificate-Application-Policy", [])
    all_ekus = set(ekus) | set(app_policies)
    client_auth = 1.0 if "1.3.6.1.5.5.7.3.2" in all_ekus else 0.0

    # Manager approval not required = enrollment flag bit 1 not set
    enrollment_flag = template.get("msPKI-Enrollment-Flag", 0)
    no_manager_approval = 0.0 if (enrollment_flag & 0x02) else 1.0

    # Enrollee supplies subject = name flag has CT_FLAG_ENROLLEE_SUPPLIES_SUBJECT (0x1)
    name_flag = template.get("msPKI-Certificate-Name-Flag", 0)
    enrollee_supplies_subject = 1.0 if (name_flag & 0x1) else 0.0

    return [client_auth, no_manager_approval, enrollee_supplies_subject]


# ---------------------------------------------------------------------------
# Edge extraction helpers
# ---------------------------------------------------------------------------

def _extract_membership_edges(
    members_list: list[dict],
    target_idx: int,
    user_map: dict[str, int],
    group_map: dict[str, int],
    comp_map: dict[str, int],
) -> dict[str, list[list[int]]]:
    """
    Parse a group's Members array into typed edge lists.
    Returns dict keyed by source type → list of [src_idx, dst_idx] pairs.
    """
    edges: dict[str, list[list[int]]] = {"User": [], "Group": [], "Computer": []}
    for member in members_list:
        sid = member.get("ObjectIdentifier", "")
        otype = member.get("ObjectType", "").lower()

        if otype == "user" and sid in user_map:
            edges["User"].append([user_map[sid], target_idx])
        elif otype == "group" and sid in group_map:
            edges["Group"].append([group_map[sid], target_idx])
        elif otype == "computer" and sid in comp_map:
            edges["Computer"].append([comp_map[sid], target_idx])
        elif otype == "foreignsecurityprincipal":
            # Foreign SIDs may match users/groups from trusted domains
            if sid in user_map:
                edges["User"].append([user_map[sid], target_idx])
            elif sid in group_map:
                edges["Group"].append([group_map[sid], target_idx])
    return edges


def _extract_ace_edges(
    aces: list[dict],
    target_sid: str,
    user_map: dict[str, int],
    group_map: dict[str, int],
    comp_map: dict[str, int],
    target_type: str,
) -> dict[str, list[tuple[str, int, str, int]]]:
    """
    Parse ACE entries into typed edges.
    Returns dict keyed by RightName → list of (src_type, src_idx, dst_type, dst_idx).
    """
    type_maps = {"User": user_map, "Group": group_map, "Computer": comp_map}
    target_map = type_maps.get(target_type, {})
    target_idx = target_map.get(target_sid)
    if target_idx is None:
        return {}

    edges: dict[str, list[tuple]] = {}
    for ace in aces:
        right = ace.get("RightName", "")
        if right not in ("GenericAll", "Owns", "WriteDacl", "WriteOwner",
                         "GenericWrite", "ForceChangePassword"):
            continue

        principal_sid = ace.get("PrincipalSID", "")
        principal_type = ace.get("PrincipalType", "").capitalize()
        src_map = type_maps.get(principal_type, {})
        if principal_sid not in src_map:
            continue

        src_idx = src_map[principal_sid]
        edges.setdefault(right, []).append(
            (principal_type, src_idx, target_type, target_idx)
        )
    return edges


# ---------------------------------------------------------------------------
# Main graph builder
# ---------------------------------------------------------------------------

def build_ad_graph(verbose: bool = True) -> HeteroData:
    """
    Build a PyTorch Geometric HeteroData object from BloodHound exports
    and ESC vulnerability templates.

    Returns:
        HeteroData with real AD features and relationship edges.
    """
    data = HeteroData()

    # ------------------------------------------------------------------
    # 1. Load BloodHound JSON files
    # ------------------------------------------------------------------
    users_raw = _load_json(_find_bh_file("*users.json")).get("data", [])
    groups_raw = _load_json(_find_bh_file("*groups.json")).get("data", [])
    computers_raw = _load_json(_find_bh_file("*computers.json")).get("data", [])

    if verbose:
        print(f"[+] Loaded BloodHound data: "
              f"{len(users_raw)} users, {len(groups_raw)} groups, "
              f"{len(computers_raw)} computers")

    # ------------------------------------------------------------------
    # 2. Build SID → index maps
    # ------------------------------------------------------------------
    user_sid_map = {u["ObjectIdentifier"]: i for i, u in enumerate(users_raw)}
    group_sid_map = {g["ObjectIdentifier"]: i for i, g in enumerate(groups_raw)}
    comp_sid_map = {c["ObjectIdentifier"]: i for i, c in enumerate(computers_raw)}

    # ------------------------------------------------------------------
    # 3. Load ESC templates
    # ------------------------------------------------------------------
    esc_files = sorted(glob.glob(os.path.join(ESC_TEMPLATES_DIR, "ESC*.json")))
    if not esc_files:
        # Fallback to the single copy
        esc_files = [ESC13_FALLBACK]

    templates_raw = []
    for ef in esc_files:
        templates_raw.append(_load_json(ef))

    template_name_map = {
        t.get("displayName", t.get("name", f"T{i}")): i
        for i, t in enumerate(templates_raw)
    }

    if verbose:
        names = list(template_name_map.keys())
        print(f"[+] Loaded {len(templates_raw)} ESC templates: {names}")

    # ------------------------------------------------------------------
    # 4. Build node feature tensors
    # ------------------------------------------------------------------
    data["User"].x = torch.tensor(
        [_user_features(u) for u in users_raw], dtype=torch.float
    )
    data["Group"].x = torch.tensor(
        [_group_features(g) for g in groups_raw], dtype=torch.float
    )
    data["Computer"].x = torch.tensor(
        [_computer_features(c) for c in computers_raw], dtype=torch.float
    )
    data["Template"].x = torch.tensor(
        [_template_features(t) for t in templates_raw], dtype=torch.float
    )

    # Store node names for interpretability
    data["User"].names = [
        u.get("Properties", {}).get("name", u["ObjectIdentifier"])
        for u in users_raw
    ]
    data["Group"].names = [
        g.get("Properties", {}).get("name", g["ObjectIdentifier"])
        for g in groups_raw
    ]
    data["Computer"].names = [
        c.get("Properties", {}).get("name", c["ObjectIdentifier"])
        for c in computers_raw
    ]
    data["Template"].names = list(template_name_map.keys())

    # ------------------------------------------------------------------
    # 5. Extract membership edges
    # ------------------------------------------------------------------
    user_memberof = []
    group_memberof = []
    comp_memberof = []

    for group in groups_raw:
        g_idx = group_sid_map[group["ObjectIdentifier"]]
        members = group.get("Members", [])
        typed = _extract_membership_edges(
            members, g_idx, user_sid_map, group_sid_map, comp_sid_map
        )
        user_memberof.extend(typed["User"])
        group_memberof.extend(typed["Group"])
        comp_memberof.extend(typed["Computer"])

    # Set membership edge_index tensors
    if user_memberof:
        data["User", "member_of", "Group"].edge_index = (
            torch.tensor(user_memberof, dtype=torch.long).t().contiguous()
        )
    else:
        data["User", "member_of", "Group"].edge_index = torch.empty(
            (2, 0), dtype=torch.long
        )

    if group_memberof:
        data["Group", "member_of", "Group"].edge_index = (
            torch.tensor(group_memberof, dtype=torch.long).t().contiguous()
        )
    else:
        data["Group", "member_of", "Group"].edge_index = torch.empty(
            (2, 0), dtype=torch.long
        )

    if comp_memberof:
        data["Computer", "member_of", "Group"].edge_index = (
            torch.tensor(comp_memberof, dtype=torch.long).t().contiguous()
        )
    else:
        data["Computer", "member_of", "Group"].edge_index = torch.empty(
            (2, 0), dtype=torch.long
        )

    if verbose:
        print(f"[+] Membership edges: "
              f"User→Group={len(user_memberof)}, "
              f"Group→Group={len(group_memberof)}, "
              f"Computer→Group={len(comp_memberof)}")

    # ------------------------------------------------------------------
    # 6. Extract ACE-based edges (GenericAll, Owns, WriteDacl)
    # ------------------------------------------------------------------
    ace_edges: dict[str, list[tuple]] = {}

    # Scan ACEs on Users
    for u in users_raw:
        u_sid = u["ObjectIdentifier"]
        for right, tuples in _extract_ace_edges(
            u.get("Aces", []), u_sid,
            user_sid_map, group_sid_map, comp_sid_map, "User"
        ).items():
            ace_edges.setdefault(right, []).extend(tuples)

    # Scan ACEs on Groups
    for g in groups_raw:
        g_sid = g["ObjectIdentifier"]
        for right, tuples in _extract_ace_edges(
            g.get("Aces", []), g_sid,
            user_sid_map, group_sid_map, comp_sid_map, "Group"
        ).items():
            ace_edges.setdefault(right, []).extend(tuples)

    # Scan ACEs on Computers
    for c in computers_raw:
        c_sid = c["ObjectIdentifier"]
        for right, tuples in _extract_ace_edges(
            c.get("Aces", []), c_sid,
            user_sid_map, group_sid_map, comp_sid_map, "Computer"
        ).items():
            ace_edges.setdefault(right, []).extend(tuples)

    # Convert ACE edges into HeteroData edge_index tensors
    # We normalize right names to lowercase for relation naming
    right_name_map = {
        "GenericAll": "generic_all",
        "Owns": "owns",
        "WriteDacl": "write_dacl",
        "WriteOwner": "write_owner",
        "GenericWrite": "generic_write",
        "ForceChangePassword": "force_change_password",
    }

    ace_summary = {}
    for right_name, edge_tuples in ace_edges.items():
        rel = right_name_map.get(right_name, right_name.lower())

        # Group by (src_type, dst_type) since HeteroData needs typed relations
        by_type: dict[tuple[str, str], list[list[int]]] = {}
        for src_type, src_idx, dst_type, dst_idx in edge_tuples:
            key = (src_type, dst_type)
            by_type.setdefault(key, []).append([src_idx, dst_idx])

        for (src_t, dst_t), pairs in by_type.items():
            edge_key = (src_t, rel, dst_t)
            tensor = torch.tensor(pairs, dtype=torch.long).t().contiguous()
            # Merge if edge type already exists
            if edge_key in data.edge_index_dict:
                existing = data[edge_key].edge_index
                data[edge_key].edge_index = torch.cat([existing, tensor], dim=1)
            else:
                data[src_t, rel, dst_t].edge_index = tensor
            ace_summary[edge_key] = ace_summary.get(edge_key, 0) + len(pairs)

    if verbose:
        total_ace = sum(ace_summary.values())
        print(f"[+] ACE edges: {total_ace} total across {len(ace_summary)} relation types")
        for k, v in sorted(ace_summary.items(), key=lambda x: -x[1])[:5]:
            print(f"    {k[0]}--{k[1]}-->{k[2]}: {v}")

    # ------------------------------------------------------------------
    # 7. ESC13 attack path edges (synthetic)
    # ------------------------------------------------------------------
    # ESC13 attack: A low-privilege user can ENROLL in a misconfigured
    # certificate template, then IMPERSONATE a high-privilege group.

    esc13_idx = template_name_map.get("ESC13", 0)

    # Find Domain Admins group
    da_idx = None
    for g in groups_raw:
        name = g.get("Properties", {}).get("name", "").upper()
        if "DOMAIN ADMINS" in name:
            da_idx = group_sid_map[g["ObjectIdentifier"]]
            break

    if da_idx is None:
        # Fallback: pick first high-value group
        for g in groups_raw:
            if g.get("Properties", {}).get("highvalue", False):
                da_idx = group_sid_map[g["ObjectIdentifier"]]
                break
        if da_idx is None:
            da_idx = 0  # absolute fallback

    # Enroll edges: all enabled, non-admin users can enroll in ESC13
    enroll_src = []
    for i, u in enumerate(users_raw):
        props = u.get("Properties", {})
        if props.get("enabled", False) and not props.get("admincount", False):
            enroll_src.append(i)

    if not enroll_src:
        # Fallback: at least one user
        enroll_src = [0]

    enroll_edges = torch.tensor(
        [[s, esc13_idx] for s in enroll_src], dtype=torch.long
    ).t().contiguous()
    data["User", "enrolls", "Template"].edge_index = enroll_edges

    # Impersonation edge: ESC13 template → Domain Admins
    data["Template", "impersonates", "Group"].edge_index = torch.tensor(
        [[esc13_idx], [da_idx]], dtype=torch.long
    )

    if verbose:
        da_name = groups_raw[da_idx].get("Properties", {}).get("name", "?")
        print(f"[+] ESC13 attack path: "
              f"{len(enroll_src)} users --enrolls--> Template[ESC13] "
              f"--impersonates--> Group[{da_name}]")

    # ------------------------------------------------------------------
    # 8. Summary
    # ------------------------------------------------------------------
    if verbose:
        print(f"\n{'='*60}")
        print(f"HeteroData Summary:")
        print(f"{'='*60}")
        for ntype in data.node_types:
            print(f"  {ntype}: {data[ntype].x.shape[0]} nodes, "
                  f"{data[ntype].x.shape[1]}-dim features")
        print()
        for etype in data.edge_types:
            ei = data[etype].edge_index
            print(f"  {etype[0]} --[{etype[1]}]--> {etype[2]}: {ei.shape[1]} edges")
        print(f"{'='*60}\n")

    return data


if __name__ == "__main__":
    graph = build_ad_graph(verbose=True)
    print("HeteroData object:")
    print(graph)
