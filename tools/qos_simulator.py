"""
QoS Bandwidth & Latency Calculator for Converged Voice/Data Networks.
Models codec overhead, packetization delay, LLQ queue limits, and concurrent call capacity.
"""
from typing import Dict, Any

CODEC_PROFILES = {
    "G.711u": {
        "bitrate_kbps": 64.0,
        "sample_size_bytes": 160, # 20ms packetization
        "packet_interval_ms": 20,
        "description": "Pulse Code Modulation (PCM) uncompressed audio, pristine enterprise quality"
    },
    "G.729": {
        "bitrate_kbps": 8.0,
        "sample_size_bytes": 20,  # 20ms packetization
        "packet_interval_ms": 20,
        "description": "CS-ACELP compressed audio, high-efficiency WAN codec"
    },
    "G.722": {
        "bitrate_kbps": 64.0,
        "sample_size_bytes": 160, # 20ms packetization
        "packet_interval_ms": 20,
        "description": "Wideband 7kHz HD Voice codec"
    }
}

# Standard header overheads (bytes)
OVERHEADS = {
    "RTP": 12,
    "UDP": 8,
    "IP": 20,
    "Ethernet_8021Q": 18 + 4 # 14 MAC + 4 802.1Q + 4 FCS
}

class QosBandwidthCalculator:
    def __init__(self):
        pass

    def calculate_call_bandwidth(self, codec: str = "G.711u") -> Dict[str, Any]:
        if codec not in CODEC_PROFILES:
            raise ValueError(f"Unknown codec {codec}. Choose from {list(CODEC_PROFILES.keys())}")

        profile = CODEC_PROFILES[codec]
        payload_bytes = profile["sample_size_bytes"]
        interval_ms = profile["packet_interval_ms"]
        pps = 1000.0 / interval_ms

        l3_headers = OVERHEADS["RTP"] + OVERHEADS["UDP"] + OVERHEADS["IP"] # 40 bytes
        l2_headers = OVERHEADS["Ethernet_8021Q"] # 22 bytes

        ip_packet_size = payload_bytes + l3_headers
        ethernet_frame_size = ip_packet_size + l2_headers

        ip_bandwidth_kbps = (ip_packet_size * 8 * pps) / 1000.0
        ethernet_bandwidth_kbps = (ethernet_frame_size * 8 * pps) / 1000.0

        return {
            "codec": codec,
            "description": profile["description"],
            "raw_audio_kbps": profile["bitrate_kbps"],
            "payload_bytes": payload_bytes,
            "packets_per_second": pps,
            "ip_packet_size_bytes": ip_packet_size,
            "ethernet_frame_size_bytes": ethernet_frame_size,
            "ip_bandwidth_kbps": round(ip_bandwidth_kbps, 2),
            "total_ethernet_bandwidth_kbps": round(ethernet_bandwidth_kbps, 2)
        }

    def calculate_link_capacity(self, link_speed_mbps: float, priority_percent: float = 33.0, codec: str = "G.711u") -> Dict[str, Any]:
        call_info = self.calculate_call_bandwidth(codec)
        total_kbps = link_speed_mbps * 1000.0
        priority_budget_kbps = total_kbps * (priority_percent / 100.0)

        max_calls = int(priority_budget_kbps // call_info["total_ethernet_bandwidth_kbps"])

        # Serialization delay for 1 voice packet on this link
        frame_bits = call_info["ethernet_frame_size_bytes"] * 8
        serialization_delay_ms = (frame_bits / (total_kbps * 1000.0)) * 1000.0

        return {
            "link_speed_mbps": link_speed_mbps,
            "priority_allocation_percent": priority_percent,
            "priority_budget_kbps": round(priority_budget_kbps, 1),
            "codec": codec,
            "bandwidth_per_call_kbps": call_info["total_ethernet_bandwidth_kbps"],
            "max_concurrent_calls": max_calls,
            "serialization_delay_ms": round(serialization_delay_ms, 4)
        }
