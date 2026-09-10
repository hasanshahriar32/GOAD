"""
bfs_baseline.py — BloodHound-Style Graph Path Traversal Baseline
================================================================
Deterministic graph traversal baseline modeling BloodHound/Certipy Cypher path queries:
- Checks template configuration flags for candidate ESC vulnerabilities.
- For ESC1: Verifies whether any low-privileged user has an enrollment path to the template.
- For ESC4: Verifies whether any low-privileged user has write_dacl permissions on the template.
- For ESC13: Verifies whether the template links to a high-value group AND low-privileged users can enroll.
- For ESC2, ESC3, ESC9: Verifies template configuration flags.
- Otherwise: Classifies as Safe.
"""

import torch
from torch_geometric.data import HeteroData
from generator import CLASS_TO_IDX, ESC_CLASSES


class BloodHoundBFSBaseline:
    """BloodHound-style graph path verification baseline."""

    def __init__(self):
        pass

    def predict_sample(self, data: HeteroData, target_idx: int) -> int:
        """Classify a single template target_idx in environment data."""
        feat = data["Template"].x[target_idx].tolist()

        ess = feat[0] > 0.5   # enrollee_supplies_subject
        nma = feat[1] > 0.5   # no_manager_approval
        nse = feat[2] > 0.5   # no_security_extension
        ca  = feat[3] > 0.5   # has_client_auth
        ap  = feat[4] > 0.5   # has_any_purpose
        cra = feat[5] > 0.5   # has_cert_req_agent
        ras = feat[6] > 0.5   # ra_signature_required
        ipo = feat[7] > 0.5   # has_issuance_policy_oid
        vacl= feat[8] > 0.5   # has_vulnerable_acl

        # Extract user admin flags from User.x[:, 5]
        user_x = data["User"].x
        is_admin_user = (user_x[:, 5] > 0.5)

        # ── 1. Check enrollment access for low-privileged users ──
        has_lowpriv_enrollment = False
        if ("User", "enrolls", "Template") in data.edge_types:
            ei = data["User", "enrolls", "Template"].edge_index
            target_mask = (ei[1] == target_idx)
            enrollers = ei[0][target_mask]
            # Check if any enroller is low-privileged (not admin)
            if len(enrollers) > 0 and (~is_admin_user[enrollers]).any().item():
                has_lowpriv_enrollment = True

        # ── 2. Check write_dacl access for low-privileged users ──
        has_lowpriv_dacl = False
        if ("User", "write_dacl", "Template") in data.edge_types:
            ei = data["User", "write_dacl", "Template"].edge_index
            target_mask = (ei[1] == target_idx)
            writers = ei[0][target_mask]
            if len(writers) > 0 and (~is_admin_user[writers]).any().item():
                has_lowpriv_dacl = True

        # ── 3. Check issuance policy linking to high-value group ──
        links_to_highvalue_group = False
        if ("Template", "linked_to", "Group") in data.edge_types:
            ei = data["Template", "linked_to", "Group"].edge_index
            target_mask = (ei[0] == target_idx)
            linked_groups = ei[1][target_mask]
            if len(linked_groups) > 0:
                group_x = data["Group"].x
                # Feature 0 of Group is is_highvalue
                is_hv = (group_x[linked_groups, 0] > 0.5)
                if is_hv.any().item():
                    links_to_highvalue_group = True

        # ── Multi-ESC Classification Rules with Graph Path Verification ──
        if ess and ca and nma and not ras:
            # Candidate ESC1
            if has_lowpriv_enrollment:
                return CLASS_TO_IDX["ESC1"]
            else:
                return CLASS_TO_IDX["Safe"]  # Hard negative ESC1 (blocked enrollment)

        if ap and nma:
            return CLASS_TO_IDX["ESC2"]

        if (cra or ras) and nma:
            return CLASS_TO_IDX["ESC3"]

        if vacl:
            # Candidate ESC4
            if has_lowpriv_dacl:
                return CLASS_TO_IDX["ESC4"]
            else:
                return CLASS_TO_IDX["Safe"]  # Hard negative ESC4 (admin-only ACL)

        if nse and ca:
            return CLASS_TO_IDX["ESC9"]

        if ipo and ca:
            # Candidate ESC13
            if links_to_highvalue_group and has_lowpriv_enrollment:
                return CLASS_TO_IDX["ESC13"]
            else:
                return CLASS_TO_IDX["Safe"]  # Hard negative ESC13 (low-priv group or blocked enrollment)

        return CLASS_TO_IDX["Safe"]

    def predict(self, dataset: list) -> list[int]:
        """Predict for a list of (data, esc_class, target_idx) tuples."""
        return [self.predict_sample(d, ti) for d, _, ti in dataset]
