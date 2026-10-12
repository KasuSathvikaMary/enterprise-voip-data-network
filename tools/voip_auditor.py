"""
Cisco IOS Configuration VoIP & QoS Compliance Auditor.
Parses Cisco IOS configurations and verifies compliance against Cisco Enterprise SRND rules:
- Voice VLAN and Data VLAN separation
- Switchport QoS trust boundary (mls qos trust device cisco-phone)
- DHCP Option 150 TFTP server specification
- MQC Low Latency Queueing (LLQ) priority policies
- Call Manager Express (telephony-service) parameters
"""
import re
import os
from typing import Dict, List, Any

class VoipConfigAuditor:
    def __init__(self):
        pass

    def audit_file(self, file_path: str) -> Dict[str, Any]:
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"Configuration file not found: {file_path}")

        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        return self.audit_content(content, os.path.basename(file_path))

    def audit_content(self, content: str, filename: str = "config.ios") -> Dict[str, Any]:
        checks = []

        is_router = "telephony-service" in content or "policy-map" in content or "interface GigabitEthernet0/0." in content
        is_core_switch = "CORE" in filename.upper() or ("switchport trunk encapsulation" in content and "switchport voice vlan" not in content)
        is_access_switch = "switchport voice vlan" in content or "ACCESS" in filename.upper()

        if is_router:
            device_type = "Router (CME/Voice GW)"
        elif is_core_switch:
            device_type = "Core Switch (L3/Aggregation)"
        else:
            device_type = "Access Switch (L2 Edge)"

        # Check: Router checks
        if is_router:
            has_policy_map = bool(re.search(r"^\s*policy-map\s+([A-Za-z0-9_-]+)", content, re.MULTILINE))
            checks.append({
                "rule": "MQC Policy-Map Configured",
                "category": "QoS",
                "passed": has_policy_map,
                "detail": "Router has MQC policy-map configured" if has_policy_map else "Missing policy-map"
            })

            has_llq = bool(re.search(r"priority\s+(percent\s+\d+|\d+)", content, re.IGNORECASE))
            checks.append({
                "rule": "Low Latency Queueing (LLQ) Priority",
                "category": "QoS",
                "passed": has_llq,
                "detail": "Strict priority queue allocated for voice" if has_llq else "Voice class lacks priority queue"
            })

            has_dscp_ef = bool(re.search(r"match\s+ip\s+dscp\s+ef", content, re.IGNORECASE))
            checks.append({
                "rule": "DSCP EF (Expedited Forwarding) Classification",
                "category": "Classification",
                "passed": has_dscp_ef,
                "detail": "RTP voice matched against DSCP EF (46)" if has_dscp_ef else "Missing 'match ip dscp ef'"
            })

            has_option_150 = bool(re.search(r"option\s+150\s+ip\s+\d+\.\d+\.\d+\.\d+", content, re.IGNORECASE))
            checks.append({
                "rule": "DHCP Option 150 (TFTP Server)",
                "category": "Telephony",
                "passed": has_option_150,
                "detail": "DHCP Option 150 provided for Cisco IP Phones" if has_option_150 else "Missing Option 150 TFTP pointer"
            })

            has_cme = "telephony-service" in content
            checks.append({
                "rule": "Call Manager Express (CME)",
                "category": "Telephony",
                "passed": has_cme,
                "detail": "CME telephony-service initialized" if has_cme else "Missing telephony-service"
            })

            has_voice_subif = bool(re.search(r"encapsulation\s+dot1Q\s+20", content, re.IGNORECASE))
            has_data_subif = bool(re.search(r"encapsulation\s+dot1Q\s+10", content, re.IGNORECASE))
            checks.append({
                "rule": "802.1Q Subinterfaces (Voice & Data)",
                "category": "VLAN",
                "passed": has_voice_subif and has_data_subif,
                "detail": "Dedicated 802.1Q subinterfaces configured" if (has_voice_subif and has_data_subif) else "Missing subinterfaces for VLAN 10/20"
            })

        # Check: Core Switch checks
        elif is_core_switch:
            has_mls_qos = bool(re.search(r"^\s*mls qos\b", content, re.MULTILINE))
            checks.append({
                "rule": "Global MLS QoS Enabled",
                "category": "QoS",
                "passed": has_mls_qos,
                "detail": "Core switch has 'mls qos' enabled" if has_mls_qos else "Missing global 'mls qos'"
            })

            has_cos_dscp = "mls qos map cos-dscp" in content
            checks.append({
                "rule": "CoS-to-DSCP Mapping Configured",
                "category": "QoS",
                "passed": has_cos_dscp,
                "detail": "Standard CoS-to-DSCP trust mapping present" if has_cos_dscp else "Missing cos-dscp mapping"
            })

            has_trunk = "switchport mode trunk" in content
            checks.append({
                "rule": "802.1Q Trunk Aggregation",
                "category": "Trunking",
                "passed": has_trunk,
                "detail": "Core trunk interfaces configured for 802.1Q" if has_trunk else "Missing 802.1Q trunking"
            })

            has_vlans = "vlan 10" in content and "vlan 20" in content
            checks.append({
                "rule": "Enterprise VLANs (Data & Voice)",
                "category": "VLAN",
                "passed": has_vlans,
                "detail": "VLAN 10 (Data) & VLAN 20 (Voice) defined" if has_vlans else "Missing VLAN 10 or 20"
            })

            has_trust = "mls qos trust" in content
            checks.append({
                "rule": "QoS Trust Propagation",
                "category": "QoS",
                "passed": has_trust,
                "detail": "Switch propagates DSCP/CoS trust" if has_trust else "Missing mls qos trust"
            })

        # Check: Access Switch checks
        elif is_access_switch:
            has_mls_qos = bool(re.search(r"^\s*mls qos\b", content, re.MULTILINE))
            checks.append({
                "rule": "Global MLS QoS Enabled",
                "category": "QoS",
                "passed": has_mls_qos,
                "detail": "Switch has 'mls qos' enabled" if has_mls_qos else "Missing global 'mls qos'"
            })

            has_voice_vlan = bool(re.search(r"switchport\s+voice\s+vlan\s+\d+", content, re.IGNORECASE))
            checks.append({
                "rule": "Dedicated Voice VLAN on Access Ports",
                "category": "VLAN",
                "passed": has_voice_vlan,
                "detail": "Access ports configured with 'switchport voice vlan'" if has_voice_vlan else "Missing voice vlan assignment"
            })

            has_access_vlan = bool(re.search(r"switchport\s+access\s+vlan\s+\d+", content, re.IGNORECASE))
            checks.append({
                "rule": "Dedicated Data VLAN on Access Ports",
                "category": "VLAN",
                "passed": has_access_vlan,
                "detail": "Access ports configured with 'switchport access vlan'" if has_access_vlan else "Missing data vlan assignment"
            })

            has_trust_phone = "mls qos trust device cisco-phone" in content or "mls qos trust cos" in content
            checks.append({
                "rule": "QoS Trust Boundary (Cisco IP Phone)",
                "category": "QoS",
                "passed": has_trust_phone,
                "detail": "Switch trusts CoS/DSCP from validated Cisco phones" if has_trust_phone else "Missing 'mls qos trust' command"
            })

            has_portfast = "spanning-tree portfast" in content
            checks.append({
                "rule": "Spanning Tree PortFast Enabled",
                "category": "Switching",
                "passed": has_portfast,
                "detail": "PortFast enabled for instant phone initialization" if has_portfast else "Missing PortFast on access ports"
            })

        total_rules = len(checks)
        passed_rules = sum(1 for c in checks if c["passed"])
        score = (passed_rules / total_rules * 100) if total_rules > 0 else 0

        return {
            "filename": filename,
            "device_type": "Router (CME/Voice GW)" if is_router else "Switch (L2/L3)",
            "score": round(score, 1),
            "passed_rules": passed_rules,
            "total_rules": total_rules,
            "checks": checks
        }
