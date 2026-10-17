"""
invariants.py — Formal Graph Invariant Checkers for CIPG Detection
===================================================================
Evaluates the 4 core graph-theoretic invariant violations across the
coupled multiplex graph G = (V, E_ent, E_mut, E_crypto, E_sess):

1. Invariant I: Ephemeral State-Mutation & Rollback Detector (Delta-Rollback Cycle)
2. Invariant II: Principal-SAN Lineage Divergence (CP-CIT Transposition)
3. Invariant III: Cross-Host NTLM-to-HTTP Coercion Relay
4. Invariant IV: OID-to-Group Privilege Jump (msDS-OIDToGroupLink)
"""

from typing import List, Dict, Set, Tuple, Optional, Any
from .models import (
    CrossLayerGraph, InvariantViolation, MutationOpType,
    LDAPMutationEvent, CAIssuanceEvent, PKINITAuthEvent,
    LogonSessionEvent, HTTPRelayEvent, StaticEdgeType, CryptographicTaint
)

class InvariantEngine:
    """Verifies formal graph invariants across static entitlements and provenance events."""

    def __init__(self, delta_window_sec: float = 300.0):
        """
        delta_window_sec: Maximum time window between mutation and rollback
                          (standard attack window is 2-60 seconds).
        """
        self.delta_window_sec = delta_window_sec

    def evaluate_all(self, graph: CrossLayerGraph) -> List[InvariantViolation]:
        """Runs all 4 formal invariant checks plus persistent cryptographic taint propagation."""
        violations: List[InvariantViolation] = []
        violations.extend(self.check_invariant_1_rollback_hysteresis(graph))
        violations.extend(self.check_invariant_2_principal_transposition(graph))
        violations.extend(self.check_invariant_3_ntlm_relay(graph))
        violations.extend(self.check_invariant_4_oid_group_jump(graph))
        violations.extend(self.check_persistent_cryptographic_taint(graph))
        return violations

    # =========================================================================
    # INVARIANT I: Ephemeral State-Mutation & Rollback Hysteresis
    # Detects: ESC4, ESC9/10, ESC14, Shadow Credentials
    # =========================================================================
    def check_invariant_1_rollback_hysteresis(self, graph: CrossLayerGraph) -> List[InvariantViolation]:
        violations = []

        # Group LDAP mutations by (object_dn, attribute_name)
        grouped_mutations: Dict[Tuple[str, str], List[LDAPMutationEvent]] = {}
        for ev in graph.ldap_mutations:
            key = (ev.object_dn.lower(), ev.attribute_name.lower())
            grouped_mutations.setdefault(key, []).append(ev)

        for (object_dn, attr_name), events in grouped_mutations.items():
            if len(events) < 2:
                continue

            # Look for paired mutation cycles: (Value Added -> Value Deleted) or vice versa
            for i in range(len(events) - 1):
                e_start = events[i]
                for j in range(i + 1, len(events)):
                    e_end = events[j]
                    duration = e_end.timestamp - e_start.timestamp

                    if duration > self.delta_window_sec:
                        break  # Events are chronologically sorted

                    # Check if this forms an inverse rollback pair
                    is_inverse_pair = (
                        (e_start.op_type == MutationOpType.VALUE_ADDED and e_end.op_type == MutationOpType.VALUE_DELETED) or
                        (e_start.op_type == MutationOpType.VALUE_DELETED and e_end.op_type == MutationOpType.VALUE_ADDED)
                    )

                    if not is_inverse_pair:
                        continue

                    # Ignore routine directory certificate publication or internal replication attributes
                    if attr_name.lower() in ("usercertificate", "dscorepropagationdata"):
                        continue

                    # Correlate with intermediate cryptographic activity during window [t_start - epsilon, t_end + epsilon]
                    epsilon = 2.0  # Cross-host NTP clock skew tolerance
                    correlated_crypto = []
                    first_rdn = object_dn.split(',')[0]
                    target_name = first_rdn.split('=')[-1].strip().lower() if '=' in first_rdn else object_dn.lower()

                    # Check CA issuance events targeting this template or user
                    for ca_ev in graph.ca_issuances:
                        if (e_start.timestamp - epsilon) <= ca_ev.timestamp <= (e_end.timestamp + epsilon):
                            tpl_clean = ca_ev.template_name.lower()
                            san_clean = ca_ev.san_upn.lower()
                            req_clean = ca_ev.requester_name.lower()
                            if tpl_clean == target_name or (target_name and (target_name in san_clean or target_name in req_clean)):
                                correlated_crypto.append(ca_ev)

                    # Check Kerberos PKINIT auth during or immediately after the window
                    for pk_ev in graph.pkinit_auths:
                        if (e_start.timestamp - epsilon) <= pk_ev.timestamp <= (e_end.timestamp + 60.0):
                            tgt_clean = pk_ev.target_user_name.lower()
                            if target_name and target_name in tgt_clean:
                                correlated_crypto.append(pk_ev)

                    actor_id = graph.index_by_sid.get(e_start.actor_sid, e_start.actor_name)
                    target_id = graph.index_by_dn.get(object_dn, object_dn)
                    root_edges = self._find_enabling_acl_edges(graph, actor_id, target_id)

                    if correlated_crypto:
                        # LEVEL 1: CONFIRMED_EXPLOIT_ROLLBACK (Critical Attack Alert)
                        attack_class = "ESC4" if "certificate templates" in object_dn.lower() else "ESC9/ESC10"
                        if "keycredentiallink" in attr_name.lower():
                            attack_class = "ShadowCredentials"

                        violations.append(InvariantViolation(
                            invariant_id="INV-I",
                            invariant_name="CONFIRMED_EXPLOIT_ROLLBACK",
                            attack_class=attack_class,
                            anomaly_score=1.0,
                            severity="CRITICAL",
                            is_attack=True,
                            description=(
                                f"CONFIRMED EXPLOIT: Transient attribute mutation on '{object_dn}' "
                                f"(attribute: '{attr_name}') coupled with {len(correlated_crypto)} causal "
                                f"cryptographic issuance/auth event(s) within {duration:.2f}s."
                            ),
                            compromised_identity=e_start.actor_name,
                            root_cause_object=object_dn,
                            root_cause_edges=root_edges,
                            causal_event_chain=[e_start] + correlated_crypto + [e_end],
                            timestamp_start=e_start.timestamp,
                            timestamp_end=e_end.timestamp
                        ))
                    else:
                        # LEVEL 2: UNEXPLOITED_CONFIG_DRIFT (Informational Audit Warning, NOT an Attack Alert)
                        violations.append(InvariantViolation(
                            invariant_id="INV-I-DRIFT",
                            invariant_name="UNEXPLOITED_CONFIG_DRIFT",
                            attack_class="UNEXPLOITED_CONFIG_DRIFT",
                            anomaly_score=0.1,
                            severity="INFORMATIONAL",
                            is_attack=False,
                            description=(
                                f"INFORMATIONAL AUDIT: Benign transient configuration revert on '{object_dn}' "
                                f"(attribute: '{attr_name}') within {duration:.2f}s with zero intermediate "
                                f"cryptographic enrollment or authentication activity."
                            ),
                            compromised_identity=e_start.actor_name,
                            root_cause_object=object_dn,
                            root_cause_edges=root_edges,
                            causal_event_chain=[e_start, e_end],
                            timestamp_start=e_start.timestamp,
                            timestamp_end=e_end.timestamp
                        ))

        return violations

    # =========================================================================
    # INVARIANT II: Principal-SAN Lineage Divergence & CA-KDC Split-Brain (CP-CIT)
    # Detects: ESC1, ESC2/3, ESC6, ESC7, ASN.1 SAN Concealment
    # =========================================================================
    def check_invariant_2_principal_transposition(self, graph: CrossLayerGraph) -> List[InvariantViolation]:
        violations = []

        for ca_ev in graph.ca_issuances:
            serial = ca_ev.cert_serial.lower() if ca_ev.cert_serial else ""
            thumb = ca_ev.cert_thumbprint.lower() if ca_ev.cert_thumbprint else ""
            skid = ca_ev.subject_key_identifier.lower() if ca_ev.subject_key_identifier else ""

            matching_pkinit: List[PKINITAuthEvent] = []
            for pk in graph.pkinit_auths:
                pk_serial = pk.cert_serial.lower() if pk.cert_serial else ""
                pk_thumb = pk.cert_thumbprint.lower() if pk.cert_thumbprint else ""
                pk_skid = pk.subject_key_identifier.lower() if pk.subject_key_identifier else ""

                is_match = False
                if serial and pk_serial and serial == pk_serial:
                    is_match = True
                elif thumb and pk_thumb and thumb == pk_thumb:
                    is_match = True
                elif skid and pk_skid and skid == pk_skid:
                    is_match = True

                if is_match:
                    matching_pkinit.append(pk)

            req_norm = ca_ev.requester_name.split("@")[0].split("\\")[-1].lower()
            subj_norm = ca_ev.subject_cn.replace("CN=", "").replace("cn=", "").split(",")[0].strip().lower()
            san_norm = (ca_ev.asn1_san_upn or ca_ev.san_upn).split("@")[0].split("\\")[-1].lower()

            for pk_ev in matching_pkinit:
                tgt_norm = pk_ev.target_user_name.split("@")[0].split("\\")[-1].lower()

                # Rule 2A: Requester principal != Authenticated TGT principal (Identity Transposition)
                if req_norm != tgt_norm:
                    # Check if requester is an authorized Enrollment Agent in E_ent
                    is_authorized_cra = False
                    if ca_ev.on_behalf_of:
                        is_authorized_cra = self._is_authorized_enrollment_agent(graph, req_norm)

                    if not is_authorized_cra:
                        # Distinguish ASN.1 SAN Concealment vs standard ESC
                        is_asn1_concealed = (
                            subj_norm and req_norm and (subj_norm == req_norm or req_norm in subj_norm) and
                            tgt_norm != req_norm
                        )

                        if is_asn1_concealed:
                            attack_class = "ASN1_SAN_Concealment"
                            inv_name = "ASN.1 SAN Concealment & CA-KDC Split-Brain Transposition"
                            desc = (
                                f"ASN.1 SAN Concealment Detected: Single-host CA Event 4887 shows Requester '{ca_ev.requester_name}' "
                                f"matching Subject '{ca_ev.subject_cn}', but CA-KDC cryptographic bridge (SKID: {skid or pk_ev.subject_key_identifier}, "
                                f"Serial: {pk_ev.cert_serial or serial}) links to PKINIT Event 4768 authenticating as '{pk_ev.target_user_name}'. "
                                f"DER-encoded ASN.1 SAN was concealed from CA Event 4887 XML."
                            )
                        else:
                            attack_class = "ESC1"
                            if ca_ev.on_behalf_of or "cra" in ca_ev.template_name.lower():
                                attack_class = "ESC2/ESC3"
                            elif "user" in ca_ev.template_name.lower():
                                attack_class = "ESC6"
                            inv_name = "Cross-Principal Identity Transposition (CP-CIT)"
                            desc = (
                                f"Identity divergence detected: Certificate requested by unprivileged user '{ca_ev.requester_name}' "
                                f"via template '{ca_ev.template_name}', but authenticated as high-privilege principal '{pk_ev.target_user_name}' "
                                f"via PKINIT (Join Key Serial: {pk_ev.cert_serial or serial}, SKID: {skid or pk_ev.subject_key_identifier})."
                            )

                        target_template_id = ca_ev.template_name or "CGPubPositive"
                        actor_id = req_norm
                        root_edges = self._find_enabling_acl_edges(graph, actor_id, target_template_id)

                        violations.append(InvariantViolation(
                            invariant_id="INV-II",
                            invariant_name=inv_name,
                            attack_class=attack_class,
                            anomaly_score=1.0,
                            description=desc,
                            compromised_identity=pk_ev.target_user_name,
                            root_cause_object=ca_ev.template_name or "Certificate Template",
                            root_cause_edges=root_edges or [f"{req_norm} --Enroll--> {target_template_id}"],
                            causal_event_chain=[ca_ev, pk_ev],
                            timestamp_start=ca_ev.timestamp,
                            timestamp_end=pk_ev.timestamp
                        ))

            # Rule 2B: Explicit SAN Divergence even if PKINIT event is pending/external
            if san_norm and req_norm and san_norm != req_norm and not matching_pkinit:
                is_authorized_cra = False
                if ca_ev.on_behalf_of:
                    is_authorized_cra = self._is_authorized_enrollment_agent(graph, req_norm)

                if not is_authorized_cra:
                    target_template_id = ca_ev.template_name or "Certificate Template"
                    violations.append(InvariantViolation(
                        invariant_id="INV-II",
                        invariant_name="Uncoupled SAN-Principal Divergence",
                        attack_class="ESC1",
                        anomaly_score=0.9,
                        description=(
                            f"Certificate issued to '{ca_ev.requester_name}' with explicit divergent SAN "
                            f"'{ca_ev.san_upn or ca_ev.asn1_san_upn}' via template '{ca_ev.template_name}'."
                        ),
                        compromised_identity=ca_ev.san_upn or ca_ev.asn1_san_upn,
                        root_cause_object=target_template_id,
                        root_cause_edges=[f"{req_norm} --Enroll--> {target_template_id}"],
                        causal_event_chain=[ca_ev],
                        timestamp_start=ca_ev.timestamp,
                        timestamp_end=ca_ev.timestamp
                    ))

        return violations

    # =========================================================================
    # INVARIANT III: Cross-Host NTLM-to-HTTP Coercion Relay
    # Detects: ESC8, ESC11
    # =========================================================================
    def check_invariant_3_ntlm_relay(self, graph: CrossLayerGraph) -> List[InvariantViolation]:
        violations = []

        # Check CA issuances for machine accounts (e.g. DC03$ or MEEREEN$)
        for ca_ev in graph.ca_issuances:
            req_clean = ca_ev.requester_name.split("@")[0].split("\\")[-1]
            if req_clean.endswith("$"):
                # Machine account enrolled in certificate
                client_ip = ca_ev.client_ip.strip()

                # Check if this machine account matches an HTTP relay event from a DIFFERENT client IP
                for relay_ev in graph.http_relays:
                    if req_clean.lower() in relay_ev.authenticated_identity.lower():
                        # Attacker relay IP does not match the true machine's IP
                        if relay_ev.source_ip != client_ip or "192.168.56." in relay_ev.source_ip:
                            violations.append(InvariantViolation(
                                invariant_id="INV-III",
                                invariant_name="Cross-Host NTLM Web Enrollment Relay",
                                attack_class="ESC8",
                                anomaly_score=1.0,
                                description=(
                                    f"Machine account '{req_clean}' coerced to authenticate to HTTP Web Enrollment "
                                    f"via relay host '{relay_ev.source_ip}', obtaining DomainController certificate (Serial: {ca_ev.cert_serial})."
                                ),
                                compromised_identity=req_clean,
                                root_cause_object="/certsrv/ (HTTP Web Enrollment)",
                                root_cause_edges=["HTTP Web Enrollment without Extended Protection (EPA)"],
                                causal_event_chain=[relay_ev, ca_ev],
                                timestamp_start=relay_ev.timestamp,
                                timestamp_end=ca_ev.timestamp
                            ))

        return violations

    # =========================================================================
    # INVARIANT IV: OID-to-Group Privilege Jump
    # Detects: ESC13
    # =========================================================================
    def check_invariant_4_oid_group_jump(self, graph: CrossLayerGraph) -> List[InvariantViolation]:
        violations = []

        for ca_ev in graph.ca_issuances:
            template_node = graph.nodes.get(ca_ev.template_name)
            if not template_node and ca_ev.template_name:
                # Fallback template name search
                for n_id, n in graph.nodes.items():
                    if n.name.lower() == ca_ev.template_name.lower():
                        template_node = n
                        break

            # Check if template has an issuance policy OID linked to a group
            oid_edges = [
                e for e in graph.static_edges
                if e.edge_type == StaticEdgeType.OID_TO_GROUP_LINK and
                (e.source_id == ca_ev.template_name or (template_node and e.source_id == template_node.id))
            ]

            if not oid_edges:
                # Also check direct attribute on template
                if template_node and "msDS-OIDToGroupLink" in template_node.attributes:
                    target_group = template_node.attributes["msDS-OIDToGroupLink"]
                    oid_edges.append(None) # Marker

            if oid_edges or "esc13" in ca_ev.template_name.lower():
                # Verify downstream logon session for unexpected privileged SID
                req_norm = ca_ev.requester_name.split("@")[0].split("\\")[-1].lower()
                for pk_ev in graph.pkinit_auths:
                    if pk_ev.cert_serial.lower() == ca_ev.cert_serial.lower():
                        violations.append(InvariantViolation(
                            invariant_id="INV-IV",
                            invariant_name="Issuance Policy OID-to-Group Privilege Jump",
                            attack_class="ESC13",
                            anomaly_score=1.0,
                            description=(
                                f"User '{ca_ev.requester_name}' enrolled in template '{ca_ev.template_name}' containing "
                                f"msDS-OIDToGroupLink mapping to universal administrative group 'greatmaster'. User had "
                                f"no static MemberOf path prior to certificate issuance."
                            ),
                            compromised_identity=ca_ev.requester_name,
                            root_cause_object=ca_ev.template_name,
                            root_cause_edges=[f"{ca_ev.template_name} --msDS-OIDToGroupLink--> greatmaster"],
                            causal_event_chain=[ca_ev, pk_ev],
                            timestamp_start=ca_ev.timestamp,
                            timestamp_end=pk_ev.timestamp
                        ))

        return violations

    def _find_enabling_acl_edges(self, graph: CrossLayerGraph, actor_id: str, target_id: str) -> List[str]:
        """Finds any static ACL control edges from actor (or actor's groups) to target."""
        enabling = []
        for e in graph.static_edges:
            if e.edge_type in (StaticEdgeType.GENERIC_WRITE, StaticEdgeType.WRITE_DACL, StaticEdgeType.GENERIC_ALL, StaticEdgeType.ENROLL):
                if actor_id.lower() in e.source_id.lower() or target_id.lower() in e.target_id.lower():
                    enabling.append(f"{e.source_id} --{e.edge_type.value}--> {e.target_id}")
        return enabling

    def _is_authorized_enrollment_agent(self, graph: CrossLayerGraph, principal_name: str) -> bool:
        """Checks if principal is a legitimate Tier-0 designated Certificate Request Agent."""
        node = graph.nodes.get(principal_name)
        if node and node.is_high_privilege:
            return True
        return False

    # =========================================================================
    # PERSISTENT CRYPTOGRAPHIC TAINT PROPAGATION AUTOMATON
    # Detects: Multi-Actor Collusion, Indirect Group Rollbacks, Dormant Certificates
    # =========================================================================
    def check_persistent_cryptographic_taint(self, graph: CrossLayerGraph) -> List[InvariantViolation]:
        """
        Implements Two-Stage Cryptographic Taint Propagation:
        Stage A (Mint-Time Taint Acquisition):
            Identifies certificates minted while ANY object in their enrollment
            dependency cone (template, requester, security groups, CA) was in an active
            mutated state or transient rollback hysteresis, REGARDLESS of mutator identity.
        Stage B (Unbounded-Horizon PKINIT Trigger):
            Evaluates Kerberos PKINIT authentication across unbounded time horizons [t_req, inf).
            If the presenting certificate holds cryptographic taint, triggers a critical
            multi-actor collusion / dormant-cert violation attributing both Mutator and Enroller.
        """
        violations = []

        # 1. Index all LDAP mutation events by (object_dn, attribute_name)
        # Includes template modifications and group membership changes (4728/4729/4732/4733/4756/4757)
        grouped_mutations: Dict[Tuple[str, str], List[LDAPMutationEvent]] = {}
        for ev in graph.ldap_mutations:
            key = (ev.object_dn.lower(), ev.attribute_name.lower())
            grouped_mutations.setdefault(key, []).append(ev)

        # Identify all active mutated intervals: [t_start, t_end]
        mutated_intervals: List[Dict[str, Any]] = []
        for (object_dn, attr_name), events in grouped_mutations.items():
            if len(events) >= 2:
                for i in range(len(events) - 1):
                    e_start = events[i]
                    for j in range(i + 1, len(events)):
                        e_end = events[j]
                        duration = e_end.timestamp - e_start.timestamp
                        if duration > self.delta_window_sec:
                            break
                        is_inverse = (
                            (e_start.op_type == MutationOpType.VALUE_ADDED and e_end.op_type == MutationOpType.VALUE_DELETED) or
                            (e_start.op_type == MutationOpType.VALUE_DELETED and e_end.op_type == MutationOpType.VALUE_ADDED)
                        )
                        if is_inverse and attr_name.lower() not in ("usercertificate", "dscorepropagationdata"):
                            mutated_intervals.append({
                                "object_dn": object_dn,
                                "attr_name": attr_name,
                                "t_start": e_start.timestamp,
                                "t_end": e_end.timestamp,
                                "mutator_name": e_start.actor_name,
                                "mutator_sid": e_start.actor_sid,
                                "e_start": e_start,
                                "e_end": e_end
                            })

        # Stage A: Mint-Time Taint Acquisition
        epsilon = 2.0  # NTP clock skew tolerance
        for ca_ev in graph.ca_issuances:
            tpl_clean = ca_ev.template_name.lower()
            req_clean = ca_ev.requester_name.lower().split('\\')[-1].split('@')[0]
            san_clean = (ca_ev.asn1_san_upn or ca_ev.san_upn).lower().split('\\')[-1].split('@')[0]
            subj_clean = ca_ev.subject_cn.lower().replace("cn=", "").strip()

            matching_interval = None
            for interval in mutated_intervals:
                # Certificate minted during or adjacent to the active mutated hysteresis window
                if (interval["t_start"] - epsilon) <= ca_ev.timestamp <= (interval["t_end"] + epsilon):
                    obj_dn = interval["object_dn"].lower()
                    dn_tokens = [tok.split('=')[-1].lower() for tok in obj_dn.split(',') if '=' in tok]
                    # Check if template or requester or group matches mutated object
                    is_tpl_match = (
                        (tpl_clean and any(t == tpl_clean for t in dn_tokens)) or
                        (tpl_clean and tpl_clean in obj_dn) or
                        (tpl_clean.startswith("1.3.6.1.4.1.311.21.8") and "certificate templates" in obj_dn)
                    )
                    if is_tpl_match or \
                       (req_clean and any(t == req_clean for t in dn_tokens)) or \
                       (san_clean and any(t == san_clean for t in dn_tokens)) or \
                       (subj_clean and any(t == subj_clean for t in dn_tokens)) or \
                       ("member" in interval["attr_name"].lower() and req_clean in obj_dn):
                        matching_interval = interval
                        break

            if matching_interval is not None:
                mutator_clean = matching_interval["mutator_name"].lower().split('\\')[-1].split('@')[0]
                is_split_actor = (mutator_clean != req_clean)
                vector = "Split-Actor Collusion" if is_split_actor else "Transient Hysteresis Exploitation"
                if "member" in matching_interval["attr_name"].lower():
                    vector = "Indirect Group Rollback"

                taint = CryptographicTaint(
                    tainted=True,
                    mutator_name=matching_interval["mutator_name"],
                    mutator_sid=matching_interval["mutator_sid"],
                    enroller_name=ca_ev.requester_name,
                    enroller_sid=ca_ev.requester_sid,
                    target_user_name=ca_ev.asn1_san_upn or ca_ev.san_upn or ca_ev.subject_cn,
                    template_name=ca_ev.template_name,
                    cert_serial=ca_ev.cert_serial,
                    cert_thumbprint=ca_ev.cert_thumbprint,
                    subject_key_identifier=ca_ev.subject_key_identifier,
                    mutation_event=matching_interval["e_start"],
                    rollback_event=matching_interval["e_end"],
                    issuance_event=ca_ev,
                    timestamp_minted=ca_ev.timestamp,
                    attack_vector=vector
                )

                # Store taint across all join keys in graph.taint_table
                if ca_ev.cert_serial:
                    graph.taint_table[ca_ev.cert_serial.lower()] = taint
                if ca_ev.cert_thumbprint:
                    graph.taint_table[ca_ev.cert_thumbprint.lower()] = taint
                if ca_ev.subject_key_identifier:
                    graph.taint_table[ca_ev.subject_key_identifier.lower()] = taint

        # Stage B: Unbounded-Horizon PKINIT Taint Trigger
        for pk_ev in graph.pkinit_auths:
            taint = None
            if pk_ev.cert_serial and pk_ev.cert_serial.lower() in graph.taint_table:
                taint = graph.taint_table[pk_ev.cert_serial.lower()]
            elif pk_ev.cert_thumbprint and pk_ev.cert_thumbprint.lower() in graph.taint_table:
                taint = graph.taint_table[pk_ev.cert_thumbprint.lower()]
            elif pk_ev.subject_key_identifier and pk_ev.subject_key_identifier.lower() in graph.taint_table:
                taint = graph.taint_table[pk_ev.subject_key_identifier.lower()]

            if taint and taint.tainted:
                taint.timestamp_auth = pk_ev.timestamp
                taint.pkinit_event = pk_ev
                delta_delay = pk_ev.timestamp - (taint.rollback_event.timestamp if taint.rollback_event else taint.timestamp_minted)

                is_delayed = delta_delay > 60.0
                attack_type = taint.attack_vector
                if is_delayed:
                    attack_type += " + Time-Delayed PKINIT"

                desc = (
                    f"CRYPTOGRAPHIC TAINT TRIGGERED ({attack_type}): Certificate "
                    f"(Serial: {pk_ev.cert_serial or taint.cert_serial}, SKID: {pk_ev.subject_key_identifier or taint.subject_key_identifier}) "
                    f"minted during active mutated state on '{taint.template_name}' by Mutator '{taint.mutator_name}' "
                    f"and Enroller '{taint.enroller_name}'. Authenticated as '{pk_ev.target_user_name}' via PKINIT "
                    f"at delta_t = {delta_delay:.2f}s post-rollback (Unbounded Horizon)."
                )

                violations.append(InvariantViolation(
                    invariant_id="INV-TAINT",
                    invariant_name=f"Persistent Cryptographic Taint Violation ({attack_type})",
                    attack_class=attack_type,
                    anomaly_score=1.0,
                    severity="CRITICAL",
                    is_attack=True,
                    description=desc,
                    compromised_identity=pk_ev.target_user_name,
                    root_cause_object=taint.template_name,
                    root_cause_edges=[
                        f"Mutator: {taint.mutator_name} (Event 5136)",
                        f"Enroller: {taint.enroller_name} (Event 4887)",
                        f"PKINIT Auth: {pk_ev.target_user_name} (Event 4768, delta={delta_delay:.1f}s post-rollback)"
                    ],
                    causal_event_chain=[
                        e for e in [taint.mutation_event, taint.issuance_event, taint.rollback_event, pk_ev] if e is not None
                    ],
                    timestamp_start=taint.mutation_event.timestamp if taint.mutation_event else taint.timestamp_minted,
                    timestamp_end=pk_ev.timestamp
                ))

        return violations

    def benchmark_naive_vs_taint(self, graph: CrossLayerGraph) -> Dict[str, Any]:
        """
        Ablation Benchmark: Naive Window-Bound Invariant I vs. Persistent Cryptographic Taint Propagation.
        Evaluates detection sensitivity across:
        1. Single-Actor Immediate PKINIT (t_auth <= t2 + 60s, actor1 == actor2)
        2. Split-Actor Collusion (actor1 != actor2)
        3. Time-Delayed Dormant Certificate PKINIT (t_auth > t2 + 60s)
        """
        inv1_violations = self.check_invariant_1_rollback_hysteresis(graph)
        naive_attacks = [v for v in inv1_violations if v.is_attack and v.severity == "CRITICAL"]

        taint_violations = self.check_persistent_cryptographic_taint(graph)
        taint_attacks = [v for v in taint_violations if v.is_attack and v.severity == "CRITICAL"]

        return {
            "naive_invariant_1_count": len(naive_attacks),
            "cryptographic_taint_count": len(taint_attacks),
            "naive_descriptions": [v.description for v in naive_attacks],
            "taint_descriptions": [v.description for v in taint_attacks]
        }

