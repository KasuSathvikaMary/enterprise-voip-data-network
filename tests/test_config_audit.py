import os
import pytest
from tools.voip_auditor import VoipConfigAuditor

def test_router_voice_gateway_compliance():
    auditor = VoipConfigAuditor()
    router_config_path = os.path.join(os.path.dirname(__file__), "..", "configs", "R1-Voice-Gateway.ios")

    res = auditor.audit_file(router_config_path)
    assert res["score"] == 100.0
    assert res["passed_rules"] == res["total_rules"]

    # Verify specific key components
    rules_dict = {c["rule"]: c["passed"] for c in res["checks"]}
    assert rules_dict["MQC Policy-Map Configured"] is True
    assert rules_dict["Low Latency Queueing (LLQ) Priority"] is True
    assert rules_dict["DSCP EF (Expedited Forwarding) Classification"] is True
    assert rules_dict["DHCP Option 150 (TFTP Server)"] is True
    assert rules_dict["Call Manager Express (CME)"] is True
    assert rules_dict["802.1Q Subinterfaces (Voice & Data)"] is True

def test_core_switch_compliance():
    auditor = VoipConfigAuditor()
    sw1_path = os.path.join(os.path.dirname(__file__), "..", "configs", "SW1-Core-Switch.ios")

    res = auditor.audit_file(sw1_path)
    rules_dict = {c["rule"]: c["passed"] for c in res["checks"]}
    assert rules_dict["Global MLS QoS Enabled"] is True

def test_access_switch_floor1_compliance():
    auditor = VoipConfigAuditor()
    sw2_path = os.path.join(os.path.dirname(__file__), "..", "configs", "SW2-Access-Floor1.ios")

    res = auditor.audit_file(sw2_path)
    assert res["score"] == 100.0
    rules_dict = {c["rule"]: c["passed"] for c in res["checks"]}
    assert rules_dict["Dedicated Voice VLAN on Access Ports"] is True
    assert rules_dict["Dedicated Data VLAN on Access Ports"] is True
    assert rules_dict["QoS Trust Boundary (Cisco IP Phone)"] is True
    assert rules_dict["Spanning Tree PortFast Enabled"] is True

def test_access_switch_floor2_compliance():
    auditor = VoipConfigAuditor()
    sw3_path = os.path.join(os.path.dirname(__file__), "..", "configs", "SW3-Access-Floor2.ios")

    res = auditor.audit_file(sw3_path)
    assert res["score"] == 100.0
