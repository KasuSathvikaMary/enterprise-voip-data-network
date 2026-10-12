import pytest
from tools.qos_simulator import QosBandwidthCalculator

def test_g711_bandwidth_calculation():
    calc = QosBandwidthCalculator()
    res = calc.calculate_call_bandwidth("G.711u")

    assert res["codec"] == "G.711u"
    assert res["raw_audio_kbps"] == 64.0
    assert res["payload_bytes"] == 160
    assert res["ip_packet_size_bytes"] == 200 # 160 + 40
    assert res["ethernet_frame_size_bytes"] == 222 # 200 + 22 (with 802.1Q)
    assert res["ip_bandwidth_kbps"] == 80.0
    assert res["total_ethernet_bandwidth_kbps"] == 88.8 # 222 * 8 * 50 / 1000

def test_g729_bandwidth_calculation():
    calc = QosBandwidthCalculator()
    res = calc.calculate_call_bandwidth("G.729")

    assert res["codec"] == "G.729"
    assert res["raw_audio_kbps"] == 8.0
    assert res["payload_bytes"] == 20
    assert res["total_ethernet_bandwidth_kbps"] == 32.8

def test_link_capacity_llq():
    calc = QosBandwidthCalculator()
    # 10 Mbps WAN link with 33% LLQ allocation = 3300 kbps budget
    cap = calc.calculate_link_capacity(link_speed_mbps=10.0, priority_percent=33.0, codec="G.711u")

    assert cap["priority_budget_kbps"] == 3300.0
    assert cap["max_concurrent_calls"] == 37 # 3300 // 88.8
    assert cap["serialization_delay_ms"] > 0
