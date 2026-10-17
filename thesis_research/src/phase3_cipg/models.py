"""
models.py — Cross-Layer Identity & PKI Provenance Graph (CIPG) Core Models
========================================================================
Formulates the multiplex graph G = (V, E_ent, E_mut, E_crypto, E_sess)
fusing the static Active Directory entitlement plane with runtime
Windows CA, LDAP, and Kerberos provenance event streams.
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Set, Tuple, Any
import json
import time

class NodeType(str, Enum):
    USER = "User"
    GROUP = "Group"
    COMPUTER = "Computer"
    CA = "CertificateAuthority"
    TEMPLATE = "CertificateTemplate"
    OID = "IssuancePolicyOID"
    CERTIFICATE = "IssuedCertificate"
    TICKET_SESSION = "KerberosSession"

class StaticEdgeType(str, Enum):
    MEMBER_OF = "MemberOf"
    GENERIC_ALL = "GenericAll"
    GENERIC_WRITE = "GenericWrite"
    WRITE_DACL = "WriteDacl"
    WRITE_OWNER = "WriteOwner"
    ENROLL = "Enroll"
    AUTO_ENROLL = "AutoEnroll"
    MANAGE_CA = "ManageCA"
    MANAGE_CERTIFICATES = "ManageCertificates"
    OID_TO_GROUP_LINK = "msDS-OIDToGroupLink"
    DELEGATE_TO = "AllowedToDelegate"

class MutationOpType(str, Enum):
    VALUE_ADDED = "Value Added"        # Windows %%14674
    VALUE_DELETED = "Value Deleted"    # Windows %%14675

@dataclass
class StaticNode:
    id: str                        # Canonical identifier (DN or SID)
    node_type: NodeType
    name: str
    distinguished_name: str = ""
    sid: str = ""
    is_high_privilege: bool = False # Tier-0 / Domain Admin equivalent
    attributes: Dict[str, Any] = field(default_factory=dict)

@dataclass
class StaticEdge:
    source_id: str
    target_id: str
    edge_type: StaticEdgeType
    cost: float = 1.0              # Disruption/remediation cost in interdiction
    attributes: Dict[str, Any] = field(default_factory=dict)

# --- Dynamic Provenance Events ---

@dataclass
class LDAPMutationEvent:
    """Event ID 5136: Directory Service Object Modified."""
    event_id: int = 5136
    timestamp: float = 0.0          # Unix epoch seconds
    actor_name: str = ""
    actor_sid: str = ""
    object_dn: str = ""
    object_class: str = ""
    attribute_name: str = ""
    op_type: MutationOpType = MutationOpType.VALUE_ADDED
    attribute_value: str = ""
    correlation_id: str = ""

@dataclass
class CAIssuanceEvent:
    """Event ID 4886 (Request Received) & 4887 (Certificate Issued)."""
    event_id: int = 4887
    timestamp: float = 0.0
    request_id: int = 0
    requester_name: str = ""        # e.g. "khal.drogo@essos.local" or machine account
    requester_sid: str = ""
    template_name: str = ""
    san_upn: str = ""               # Subject Alternative Name (e.g. administrator@essos.local)
    cert_serial: str = ""           # Cryptographic Join Key
    cert_thumbprint: str = ""       # Cryptographic Join Key (SHA-1 thumbprint)
    subject_key_identifier: str = "" # CA/Event 4887 SubjectKeyIdentifier
    subject_cn: str = ""            # CommonName from Subject
    asn1_san_upn: str = ""          # DER-encoded ASN.1 2.5.29.17 UPN
    client_ip: str = ""
    on_behalf_of: str = ""          # ESC3 CRA co-sign agent identity
    ca_name: str = ""

@dataclass
class PKINITAuthEvent:
    """Event ID 4768: Kerberos TGT Requested via PKINIT (Pre-Auth 15/16)."""
    event_id: int = 4768
    timestamp: float = 0.0
    target_user_name: str = ""      # Authenticated identity inside TGT
    target_user_sid: str = ""
    cert_issuer: str = ""
    cert_serial: str = ""           # Cryptographic Join Key matching 4887
    cert_thumbprint: str = ""       # Cryptographic Join Key matching 4887
    pre_auth_type: int = 16         # 15 = PKINIT-OLD, 16 = PKINIT (RFC 4556)
    client_ip: str = ""
    service_name: str = "krbtgt"
    ticket_session_id: str = ""     # Links to downstream 4769/4624 events
    subject_key_identifier: str = "" # Enriched from CA DB Bridge matching 4887

@dataclass
class LogonSessionEvent:
    """Event ID 4624 (Logon) & 4672 (Special Privileges Assigned)."""
    event_id: int = 4624
    timestamp: float = 0.0
    user_name: str = ""
    user_sid: str = ""
    logon_id: str = ""
    logon_type: int = 3             # 3 = Network, 10 = RDP, 2 = Interactive
    client_ip: str = ""
    assigned_sids: List[str] = field(default_factory=list) # Includes OID-linked group SIDs
    elevated_token: bool = False

@dataclass
class HTTPRelayEvent:
    """IIS / Web Enrollment NTLM Relay Log Event."""
    timestamp: float = 0.0
    source_ip: str = ""             # Actual network client IP (Attacker)
    authenticated_identity: str = "" # Coerced identity (e.g. MEEREEN$)
    target_endpoint: str = "/certsrv/certfnsh.asp"
    http_method: str = "POST"
    user_agent: str = ""

@dataclass
class MetaLogonEdge:
    """Collapses repetitive benign host logons into a single weighted graph edge."""
    user_name: str
    client_ip: str
    logon_type: int
    event_count: int
    timestamp_start: float
    timestamp_end: float
    assigned_sids: List[str] = field(default_factory=list)

@dataclass
class InvariantViolation:
    invariant_id: str               # "INV-I", "INV-II", "INV-III", "INV-IV", "INV-I-DRIFT"
    invariant_name: str
    attack_class: str               # "ESC4", "ESC9", "ESC1", "ESC6", "ESC8", "ESC13", "UNEXPLOITED_CONFIG_DRIFT", etc.
    anomaly_score: float            # Normalized [0.0, 1.0]
    description: str
    compromised_identity: str
    root_cause_object: str
    root_cause_edges: List[str]     # Static ACL edges that permitted the attack
    causal_event_chain: List[Any]   # Sequence of provenance events forming the proof
    timestamp_start: float
    timestamp_end: float
    severity: str = "CRITICAL"      # "CRITICAL" (Attack alert) vs "INFORMATIONAL" (Audit warning)
    is_attack: bool = True          # False for benign unexploited config drift

@dataclass
class CryptographicTaint:
    """Persistent Cryptographic Taint assigned to certificate upon anomalous minting."""
    tainted: bool = False
    mutator_name: str = ""
    mutator_sid: str = ""
    enroller_name: str = ""
    enroller_sid: str = ""
    target_user_name: str = ""
    template_name: str = ""
    cert_serial: str = ""
    cert_thumbprint: str = ""
    subject_key_identifier: str = ""
    mutation_event: Optional[LDAPMutationEvent] = None
    rollback_event: Optional[LDAPMutationEvent] = None
    issuance_event: Optional[CAIssuanceEvent] = None
    pkinit_event: Optional[PKINITAuthEvent] = None
    timestamp_minted: float = 0.0
    timestamp_auth: float = 0.0
    attack_vector: str = ""  # "Split-Actor Collusion", "Indirect Group Rollback", "Delayed-PKINIT"

class CrossLayerGraph:
    """
    Multiplex Graph structure holding:
    - Layer 1: Static Entitlement Graph (V_ad, E_acl)
    - Layer 2: Temporal Provenance Streams (E_mut, E_crypto, E_sess)
    - Join Indexes: SerialNumber, Thumbprint, Principal SID, Target DN
    """
    def __init__(self):
        self.nodes: Dict[str, StaticNode] = {}
        self.static_edges: List[StaticEdge] = []
        self.adj_out: Dict[str, List[StaticEdge]] = {}
        self.adj_in: Dict[str, List[StaticEdge]] = {}

        # Temporal Event Lists (Sorted by timestamp)
        self.ldap_mutations: List[LDAPMutationEvent] = []
        self.ca_issuances: List[CAIssuanceEvent] = []
        self.pkinit_auths: List[PKINITAuthEvent] = []
        self.logon_sessions: List[LogonSessionEvent] = []
        self.http_relays: List[HTTPRelayEvent] = []
        self.meta_logon_edges: List[MetaLogonEdge] = []

        # High-Speed Query Indexes & Taint Table
        self.index_by_dn: Dict[str, str] = {}               # DN -> Node ID
        self.index_by_sid: Dict[str, str] = {}              # SID -> Node ID
        self.index_by_cert_serial: Dict[str, List[Any]] = {} # Serial -> [CAIssuance, PKINIT]
        self.index_by_object_mutations: Dict[str, List[LDAPMutationEvent]] = {} # DN -> mutations
        self.taint_table: Dict[str, CryptographicTaint] = {} # Key (serial/thumb/skid) -> Taint Record

    def add_node(self, node: StaticNode):
        self.nodes[node.id] = node
        if node.distinguished_name:
            self.index_by_dn[node.distinguished_name.lower()] = node.id
        if node.sid:
            self.index_by_sid[node.sid] = node.id
        if node.id not in self.adj_out:
            self.adj_out[node.id] = []
        if node.id not in self.adj_in:
            self.adj_in[node.id] = []

    def add_static_edge(self, edge: StaticEdge):
        self.static_edges.append(edge)
        self.adj_out.setdefault(edge.source_id, []).append(edge)
        self.adj_in.setdefault(edge.target_id, []).append(edge)

    def add_ldap_mutation(self, event: LDAPMutationEvent):
        self.ldap_mutations.append(event)
        dn_key = event.object_dn.lower()
        self.index_by_object_mutations.setdefault(dn_key, []).append(event)

    def add_ca_issuance(self, event: CAIssuanceEvent):
        self.ca_issuances.append(event)
        if event.cert_serial:
            self.index_by_cert_serial.setdefault(event.cert_serial.lower(), []).append(event)

    def add_pkinit_auth(self, event: PKINITAuthEvent):
        self.pkinit_auths.append(event)
        if event.cert_serial:
            self.index_by_cert_serial.setdefault(event.cert_serial.lower(), []).append(event)

    def add_logon_session(self, event: LogonSessionEvent):
        self.logon_sessions.append(event)

    def add_http_relay(self, event: HTTPRelayEvent):
        self.http_relays.append(event)

    def sort_all_events(self):
        """Ensure all temporal streams are strictly monotonically sorted by timestamp."""
        self.ldap_mutations.sort(key=lambda e: e.timestamp)
        self.ca_issuances.sort(key=lambda e: e.timestamp)
        self.pkinit_auths.sort(key=lambda e: e.timestamp)
        self.logon_sessions.sort(key=lambda e: e.timestamp)
        self.http_relays.sort(key=lambda e: e.timestamp)

    def compress_benign_routines(self) -> Dict[str, Any]:
        """
        Collapses repetitive benign host logons (4624/4769 from identical
        (user, client_ip, logon_type) tuples with no incident E_mut or anomalous
        E_crypto edges) into a single weighted Meta-Edge, while preserving 100% of
        nodes and edges involved in any E_mut or cross-principal E_crypto path.
        """
        critical_principals: Set[str] = set()
        critical_sids: Set[str] = set()

        for m in self.ldap_mutations:
            if m.actor_name:
                critical_principals.add(m.actor_name.lower().split('\\')[-1])
            if m.actor_sid:
                critical_sids.add(m.actor_sid.lower())
            dn_parts = m.object_dn.lower().split(',')
            for part in dn_parts:
                if part.startswith('cn='):
                    critical_principals.add(part.split('cn=')[-1])

        for c in self.ca_issuances:
            req_clean = c.requester_name.lower().split('\\')[-1].split('@')[0]
            san_clean = c.san_upn.lower().split('\\')[-1].split('@')[0]
            if req_clean != san_clean:
                critical_principals.add(req_clean)
                critical_principals.add(san_clean)
            if c.requester_sid:
                critical_sids.add(c.requester_sid.lower())

        for p in self.pkinit_auths:
            tgt_clean = p.target_user_name.lower().split('\\')[-1].split('@')[0]
            critical_principals.add(tgt_clean)
            if p.target_user_sid:
                critical_sids.add(p.target_user_sid.lower())

        for h in self.http_relays:
            if h.authenticated_identity:
                critical_principals.add(h.authenticated_identity.lower().split('\\')[-1])

        preserved_logons: List[LogonSessionEvent] = []
        benign_clusters: Dict[Tuple[str, str, int], List[LogonSessionEvent]] = {}

        raw_logon_count = len(self.logon_sessions)
        for lg in self.logon_sessions:
            u_clean = lg.user_name.lower().split('\\')[-1].split('@')[0]
            sid_clean = lg.user_sid.lower()

            if u_clean in critical_principals or sid_clean in critical_sids or lg.elevated_token:
                preserved_logons.append(lg)
            else:
                key = (u_clean, lg.client_ip, lg.logon_type)
                benign_clusters.setdefault(key, []).append(lg)

        meta_edges: List[MetaLogonEdge] = []
        for (u, ip, ltype), cluster in benign_clusters.items():
            first_ts = min(e.timestamp for e in cluster)
            last_ts = max(e.timestamp for e in cluster)
            sids = list({sid for e in cluster for sid in e.assigned_sids})
            meta_edges.append(MetaLogonEdge(
                user_name=u,
                client_ip=ip,
                logon_type=ltype,
                event_count=len(cluster),
                timestamp_start=first_ts,
                timestamp_end=last_ts,
                assigned_sids=sids
            ))

        self.logon_sessions = preserved_logons
        self.meta_logon_edges = meta_edges

        raw_total = (
            len(self.ldap_mutations) + len(self.ca_issuances) +
            len(self.pkinit_auths) + raw_logon_count + len(self.http_relays)
        )
        compressed_total = (
            len(self.ldap_mutations) + len(self.ca_issuances) +
            len(self.pkinit_auths) + len(self.logon_sessions) +
            len(self.meta_logon_edges) + len(self.http_relays)
        )

        compression_ratio = ((raw_total - compressed_total) / max(1, raw_total)) * 100.0

        return {
            "raw_total_events": raw_total,
            "compressed_graph_elements": compressed_total,
            "raw_logon_sessions": raw_logon_count,
            "preserved_critical_logons": len(preserved_logons),
            "meta_logon_edges": len(meta_edges),
            "compression_ratio_percent": round(compression_ratio, 2)
        }

