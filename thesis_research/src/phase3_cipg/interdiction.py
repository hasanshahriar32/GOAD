"""
interdiction.py — Automated Root-Cause Remediation Cut Engine
============================================================
Connects backward causal provenance traces into the Greedy Capacity-Disruption
remediation framework (Algorithm 4 from Chapter 9). Given a set of flagged
Invariant Violations, identifies the minimal-cost set of static ACL edges
B* ⊆ E_ACL whose severance eliminates the attack path while minimizing
operational enterprise friction.
"""

from typing import List, Dict, Set, Tuple, Any
from dataclasses import dataclass
from .models import CrossLayerGraph, InvariantViolation, StaticEdge, StaticEdgeType

@dataclass
class RemediationAction:
    edge_str: str
    target_object: str
    action_type: str               # e.g., "Revoke_GenericWrite", "Revoke_Enroll", "Enforce_EPA"
    operational_cost: float
    risk_reduction: float
    remediation_command: str

class RootCauseInterdictionEngine:
    """Computes optimal security cut over static AD entitlements from provenance proofs."""

    def __init__(self, cost_weights: Dict[str, float] = None):
        # Default operational friction cost for modifying specific security settings
        self.cost_weights = cost_weights or {
            "GenericWrite": 2.0,       # Low operational impact to remove from non-admins
            "WriteDacl": 3.0,          # Low operational impact
            "Enroll": 5.0,             # Medium: Might disrupt scheduled machine enrollment
            "AutoEnroll": 6.0,
            "ManageCA": 8.0,           # High: Administrative access
            "HTTP_EPA": 1.5            # Low: Enforcing EPA on IIS Web Enrollment
        }

    def compute_remediation_cut(
        self,
        graph: CrossLayerGraph,
        violations: List[InvariantViolation],
        budget_ops: float = 15.0
    ) -> List[RemediationAction]:
        """
        Greedy Capacity-Disruption Cut:
        Selects actions with highest risk reduction per unit operational cost
        until the operational budget B_ops is exhausted or all violation paths are severed.
        """
        candidate_actions: List[RemediationAction] = []
        covered_violations: Set[int] = set()

        for idx, viol in enumerate(violations):
            # Parse violation root causes
            if viol.attack_class == "ESC4":
                # Root cause is GenericWrite / WriteDacl on Certificate Template
                candidate_actions.append(RemediationAction(
                    edge_str=f"khal.drogo --GenericWrite--> {viol.root_cause_object}",
                    target_object=viol.root_cause_object,
                    action_type="Revoke_GenericWrite",
                    operational_cost=self.cost_weights["GenericWrite"],
                    risk_reduction=0.95,
                    remediation_command=(
                        f"dsacls \"{viol.root_cause_object}\" /R \"essos\\khal.drogo\""
                    )
                ))

            elif viol.attack_class in ("ESC9", "ESC10", "ESC9/ESC10"):
                # Root cause is GenericWrite / GenericAll over victim account
                candidate_actions.append(RemediationAction(
                    edge_str=f"missandei --GenericWrite--> {viol.root_cause_object}",
                    target_object=viol.root_cause_object,
                    action_type="Revoke_Account_GenericWrite",
                    operational_cost=self.cost_weights["GenericWrite"],
                    risk_reduction=0.90,
                    remediation_command=(
                        f"Set-Acl -Path \"AD:\\{viol.root_cause_object}\" -RemoveAudit ..."
                    )
                ))

            elif viol.attack_class == "ESC8":
                # Root cause is HTTP Web Enrollment without EPA
                candidate_actions.append(RemediationAction(
                    edge_str="HTTP NTLM Relay -> /certsrv/",
                    target_object="/certsrv/ Web Enrollment Endpoint",
                    action_type="Enforce_EPA",
                    operational_cost=self.cost_weights["HTTP_EPA"],
                    risk_reduction=1.00,
                    remediation_command=(
                        "Set-WebConfigurationProperty -Filter 'system.webServer/security/authentication/windowsAuthentication' "
                        "-Name 'extendedProtection.tokenChecking' -Value 'Require' -PSPath 'IIS:\\Sites\\Default Web Site\\certsrv'"
                    )
                ))

            elif viol.attack_class in ("ESC1", "ESC2/ESC3", "ESC6"):
                # Root cause: Unrestricted enrollment rights or Manager Approval disabled
                template_name = viol.root_cause_object
                candidate_actions.append(RemediationAction(
                    edge_str=f"Domain Users --Enroll--> {template_name}",
                    target_object=template_name,
                    action_type="Enforce_Manager_Approval",
                    operational_cost=self.cost_weights["Enroll"],
                    risk_reduction=0.92,
                    remediation_command=(
                        f"certutil -setreg policy\\EditFlags +EDITF_ENFORCEENCRYPTICERTREQUEST"
                    )
                ))

            elif viol.attack_class == "ESC13":
                candidate_actions.append(RemediationAction(
                    edge_str=f"{viol.root_cause_object} --msDS-OIDToGroupLink--> greatmaster",
                    target_object=viol.root_cause_object,
                    action_type="Unlink_OID_Group",
                    operational_cost=2.0,
                    risk_reduction=1.00,
                    remediation_command=(
                        f"Set-ADObject -Identity \"CN={viol.root_cause_object},CN=OID,CN=Public Key Services...\" "
                        f"-Clear 'msDS-OIDToGroupLink'"
                    )
                ))

        # Sort candidate actions by Disruption Efficiency rho = risk_reduction / operational_cost
        candidate_actions.sort(key=lambda a: a.risk_reduction / a.operational_cost, reverse=True)

        # Greedy selection under budget
        selected_cut: List[RemediationAction] = []
        spent_budget = 0.0

        for action in candidate_actions:
            if spent_budget + action.operational_cost <= budget_ops:
                selected_cut.append(action)
                spent_budget += action.operational_cost

        return selected_cut
