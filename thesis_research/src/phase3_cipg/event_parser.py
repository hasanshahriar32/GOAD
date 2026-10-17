"""
event_parser.py — Parser for Windows Security & CA Provenance Event Logs
========================================================================
Extracts and parses Event IDs 5136 (LDAP Modifications), 4886/4887 (CA Issuance),
4768 (Kerberos PKINIT), and 4624 (Logon) from raw Windows XML/EVTX and JSON exports.
"""

import xml.etree.ElementTree as ET
from datetime import datetime
import json
import os
import re
from typing import List, Dict, Any, Optional

from .models import (
    LDAPMutationEvent, CAIssuanceEvent, PKINITAuthEvent,
    LogonSessionEvent, HTTPRelayEvent, MutationOpType, CrossLayerGraph
)

class ProvenanceEventParser:
    """Lossless parser for Windows Security event streams."""

    @staticmethod
    def _safe_int(val: Any, default: int = 0) -> int:
        if val is None:
            return default
        try:
            val_str = str(val).strip()
            if not val_str or val_str == "-":
                return default
            return int(val_str)
        except (ValueError, TypeError):
            return default

    @staticmethod
    def parse_windows_timestamp(time_str: str) -> float:
        """Parse ISO timestamp e.g. '2026-10-16T12:00:00.000000000Z' into epoch seconds."""
        if not time_str:
            return 0.0
        try:
            # Strip fractional seconds beyond microseconds for strptime
            clean_time = re.sub(r'(\.\d{6})\d*Z', r'\1Z', time_str)
            clean_time = clean_time.replace("Z", "+00:00")
            dt = datetime.fromisoformat(clean_time)
            return dt.timestamp()
        except Exception:
            return 0.0

    @classmethod
    def parse_xml_event(cls, xml_text: str) -> Optional[Any]:
        """Parse a single raw Windows Event XML record into a typed dataclass."""
        try:
            root = ET.fromstring(xml_text)
        except Exception:
            return None

        # Namespace map for Windows Events
        ns = {'w': 'http://schemas.microsoft.com/win/2004/08/events/event'}
        system = root.find('w:System', ns)
        if system is None:
            # Fallback if no namespace
            system = root.find('System')
            event_data = root.find('EventData')
        else:
            event_data = root.find('w:EventData', ns)

        if system is None:
            return None

        event_id_el = system.find('w:EventID', ns) if 'w' in ns else system.find('EventID')
        event_id = int(event_id_el.text) if event_id_el is not None and event_id_el.text else 0

        time_el = system.find('w:TimeCreated', ns) if 'w' in ns else system.find('TimeCreated')
        time_created_str = time_el.attrib.get('SystemTime', '') if time_el is not None else ''
        timestamp = cls.parse_windows_timestamp(time_created_str)

        # Extract EventData key-value pairs
        data_dict = {}
        if event_data is not None:
            for data in event_data.findall('w:Data', ns) if 'w' in ns else event_data.findall('Data'):
                name = data.attrib.get('Name')
                text = data.text or ''
                if name:
                    data_dict[name] = text

        # Parse by EventID
        if event_id == 5136:
            # OperationType: %%14674 = Value Added, %%14675 = Value Deleted
            op_raw = data_dict.get('OperationType', '')
            op_type = MutationOpType.VALUE_DELETED if '14675' in op_raw or 'Deleted' in op_raw else MutationOpType.VALUE_ADDED

            return LDAPMutationEvent(
                timestamp=timestamp,
                actor_name=data_dict.get('SubjectUserName', ''),
                actor_sid=data_dict.get('SubjectUserSid', ''),
                object_dn=data_dict.get('ObjectDN', ''),
                object_class=data_dict.get('ObjectClass', ''),
                attribute_name=data_dict.get('AttributeLDAPDisplayName', ''),
                op_type=op_type,
                attribute_value=data_dict.get('AttributeValue', ''),
                correlation_id=data_dict.get('OpCorrelationID', '')
            )

        elif event_id in (4728, 4732, 4756, 4729, 4733, 4757):
            # Security Group Membership Modification Events
            # 4728/4732/4756 = Member Added (VALUE_ADDED)
            # 4729/4733/4757 = Member Removed (VALUE_DELETED)
            is_added = event_id in (4728, 4732, 4756)
            op_type = MutationOpType.VALUE_ADDED if is_added else MutationOpType.VALUE_DELETED
            target_group = data_dict.get('TargetUserName', '')
            member_val = data_dict.get('MemberName', data_dict.get('MemberSid', data_dict.get('TargetSid', target_group)))

            return LDAPMutationEvent(
                event_id=event_id,
                timestamp=timestamp,
                actor_name=data_dict.get('SubjectUserName', ''),
                actor_sid=data_dict.get('SubjectUserSid', ''),
                object_dn=target_group,
                object_class="group",
                attribute_name="member",
                op_type=op_type,
                attribute_value=member_val,
                correlation_id=f"{target_group}:{member_val}"
            )

        elif event_id in (4886, 4887):
            skid = data_dict.get('SubjectKeyIdentifier', '').replace(" ", "").lower()
            subj = data_dict.get('Subject', '')
            return CAIssuanceEvent(
                event_id=event_id,
                timestamp=timestamp,
                request_id=cls._safe_int(data_dict.get('RequestId', '0'), 0),
                requester_name=data_dict.get('Requester', ''),
                requester_sid=data_dict.get('SubjectUserSid', ''),
                template_name=data_dict.get('CertificateTemplate', ''),
                san_upn=data_dict.get('SubjectAlternativeName', data_dict.get('Subject', '')),
                cert_serial=data_dict.get('CertificateSerialNumber', '').replace(" ", "").lower(),
                cert_thumbprint=data_dict.get('CertificateThumbprint', '').replace(" ", "").lower(),
                subject_key_identifier=skid,
                subject_cn=subj,
                asn1_san_upn="",
                client_ip=data_dict.get('ClientAddress', ''),
                on_behalf_of=data_dict.get('OnBehalfOf', ''),
                ca_name=data_dict.get('CAName', '')
            )

        elif event_id == 4768:
            # PreAuthType 15/16 indicates PKINIT
            pre_auth = cls._safe_int(data_dict.get('PreAuthType', '0'), 0)
            return PKINITAuthEvent(
                timestamp=timestamp,
                target_user_name=data_dict.get('TargetUserName', ''),
                target_user_sid=data_dict.get('TargetSid', ''),
                cert_issuer=data_dict.get('CertIssuerName', ''),
                cert_serial=data_dict.get('CertSerialNumber', '').replace(" ", "").lower(),
                cert_thumbprint=data_dict.get('CertThumbprint', '').replace(" ", "").lower(),
                pre_auth_type=pre_auth,
                client_ip=data_dict.get('IpAddress', '').replace("::ffff:", ""),
                service_name=data_dict.get('ServiceName', 'krbtgt'),
                ticket_session_id=data_dict.get('TicketOptions', '')
            )

        elif event_id == 4624:
            assigned_raw = data_dict.get('GroupMembership', '')
            assigned_sids = [s.strip() for s in assigned_raw.split() if s.strip()]
            return LogonSessionEvent(
                timestamp=timestamp,
                user_name=data_dict.get('TargetUserName', ''),
                user_sid=data_dict.get('TargetUserSid', ''),
                logon_id=data_dict.get('TargetLogonId', ''),
                logon_type=cls._safe_int(data_dict.get('LogonType', '3'), 3),
                client_ip=data_dict.get('IpAddress', '').replace("::ffff:", ""),
                assigned_sids=assigned_sids,
                elevated_token=bool(data_dict.get('ElevatedToken', ''))
            )

        return None

    @classmethod
    def ingest_xml_stream(cls, xml_file_path: str, graph: CrossLayerGraph) -> int:
        """Parse multi-event XML file into CrossLayerGraph."""
        count = 0
        with open(xml_file_path, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read()

        # Split multiple <Event>...</Event> records if concatenated
        event_chunks = re.findall(r'<Event[\s\S]*?</Event>', content)
        for chunk in event_chunks:
            parsed = cls.parse_xml_event(chunk)
            if parsed is not None:
                if isinstance(parsed, LDAPMutationEvent):
                    graph.add_ldap_mutation(parsed)
                elif isinstance(parsed, CAIssuanceEvent):
                    graph.add_ca_issuance(parsed)
                elif isinstance(parsed, PKINITAuthEvent):
                    graph.add_pkinit_auth(parsed)
                elif isinstance(parsed, LogonSessionEvent):
                    graph.add_logon_session(parsed)
                count += 1

        graph.sort_all_events()
        return count

    @classmethod
    def load_ca_db_bridge(cls, bridge_csv_path: str, graph: CrossLayerGraph) -> int:
        """
        Loads srv03_ca_db_bridge.csv and enriches CAIssuanceEvent records in graph.
        Bridges the CA (Event 4887: RequestId, SubjectKeyIdentifier) to the
        Domain Controller (Event 4768: CertSerialNumber, CertThumbprint).
        """
        import csv
        if not os.path.exists(bridge_csv_path):
            return 0

        bridge_by_req: Dict[int, Dict[str, str]] = {}
        bridge_by_skid: Dict[str, Dict[str, str]] = {}

        with open(bridge_csv_path, 'r', encoding='utf-8', errors='ignore') as f:
            reader = csv.reader(f)
            header = None
            for row in reader:
                if not row:
                    continue
                if header is None:
                    header = [c.strip().strip('"') for c in row]
                    continue
                if len(row) < len(header):
                    continue
                rec = dict(zip(header, [c.strip().strip('"') for c in row]))
                try:
                    req_id = int(rec.get("Issued Request ID", "0") or 0)
                except ValueError:
                    continue

                clean_serial = rec.get("Serial Number", "").replace(" ", "").lower()
                clean_hash = rec.get("Certificate Hash", "").replace(" ", "").lower()
                clean_skid = rec.get("Issued Subject Key Identifier", "").replace(" ", "").lower()
                upn = rec.get("User Principal Name", "")
                if upn == "EMPTY":
                    upn = ""
                cn = rec.get("Issued Common Name", "")
                tmpl = rec.get("Certificate Template", "")

                data = {
                    "request_id": req_id,
                    "serial": clean_serial,
                    "thumbprint": clean_hash,
                    "skid": clean_skid,
                    "upn": upn,
                    "common_name": cn,
                    "template": tmpl
                }
                bridge_by_req[req_id] = data
                if clean_skid:
                    bridge_by_skid[clean_skid] = data
                if clean_serial:
                    bridge_by_serial = getattr(cls, "_tmp_serial", None)
                    if bridge_by_serial is None:
                        bridge_by_serial = {}
                        cls._tmp_serial = bridge_by_serial
                    bridge_by_serial[clean_serial] = data
                if clean_hash:
                    bridge_by_thumb = getattr(cls, "_tmp_thumb", None)
                    if bridge_by_thumb is None:
                        bridge_by_thumb = {}
                        cls._tmp_thumb = bridge_by_thumb
                    bridge_by_thumb[clean_hash] = data

        bridge_by_serial = getattr(cls, "_tmp_serial", {})
        bridge_by_thumb = getattr(cls, "_tmp_thumb", {})
        cls._tmp_serial = {}
        cls._tmp_thumb = {}

        enriched_count = 0
        for ca_ev in graph.ca_issuances:
            match = None
            if ca_ev.request_id in bridge_by_req:
                match = bridge_by_req[ca_ev.request_id]
            elif ca_ev.subject_key_identifier and ca_ev.subject_key_identifier in bridge_by_skid:
                match = bridge_by_skid[ca_ev.subject_key_identifier]

            if match:
                if not ca_ev.cert_serial and match["serial"]:
                    ca_ev.cert_serial = match["serial"]
                if not ca_ev.cert_thumbprint and match["thumbprint"]:
                    ca_ev.cert_thumbprint = match["thumbprint"]
                if not ca_ev.subject_key_identifier and match["skid"]:
                    ca_ev.subject_key_identifier = match["skid"]
                if not ca_ev.subject_cn and match["common_name"]:
                    ca_ev.subject_cn = match["common_name"]
                if match["template"] and not ca_ev.template_name:
                    ca_ev.template_name = match["template"]
                if match["upn"]:
                    ca_ev.asn1_san_upn = match["upn"]
                    ca_ev.san_upn = match["upn"]
                enriched_count += 1

        for pk_ev in graph.pkinit_auths:
            pk_match = None
            if pk_ev.cert_serial and pk_ev.cert_serial in bridge_by_serial:
                pk_match = bridge_by_serial[pk_ev.cert_serial]
            elif pk_ev.cert_thumbprint and pk_ev.cert_thumbprint in bridge_by_thumb:
                pk_match = bridge_by_thumb[pk_ev.cert_thumbprint]

            if pk_match:
                if not pk_ev.subject_key_identifier and pk_match["skid"]:
                    pk_ev.subject_key_identifier = pk_match["skid"]
                if not pk_ev.cert_serial and pk_match["serial"]:
                    pk_ev.cert_serial = pk_match["serial"]
                if not pk_ev.cert_thumbprint and pk_match["thumbprint"]:
                    pk_ev.cert_thumbprint = pk_match["thumbprint"]

        return enriched_count
