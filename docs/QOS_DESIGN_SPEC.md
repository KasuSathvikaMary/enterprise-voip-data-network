# 📊 Quality of Service (QoS) Technical Design Specification

## 🎯 Design Objectives
Real-time Voice over IP (VoIP) streams demand deterministic network performance:
* **One-Way Latency (Delay)**: $\le 150\text{ ms}$ (ITU-T G.114)
* **Jitter (Delay Variation)**: $\le 30\text{ ms}$
* **Packet Loss**: $\le 1\%$
* **Bandwidth Guarantee**: Dedicated Low Latency Queueing (LLQ) to prevent starvation during data bursts.

---

## 🏷️ Traffic Classification & Marking Standard (Cisco SRND)

| Traffic Class | Application Type | Layer 2 802.1p CoS | Layer 3 DSCP | DSCP Hex / Decimal | Queueing Strategy |
| :--- | :--- | :---: | :---: | :---: | :--- |
| **Voice Payload** | RTP Audio Streams | **5** | **EF** (Expedited Forwarding) | `0x2E` / `46` | **LLQ** (Priority Queue - 33%) |
| **Call Signaling** | SIP / SCCP (Skinny) | **3** | **CS3** / **AF31** | `0x18` / `24` or `26` | **CBWFQ** (Guaranteed 5%) |
| **Network Mgmt** | SSH, SNMP, NTP | **2** | **CS2** | `0x10` / `16` | **CBWFQ** (Guaranteed 3%) |
| **Best-Effort Data**| Web, Email, File Transfer | **0** | **BE** (Default) | `0x00` / `0` | Fair-Queueing & WRED |

---

## 🛡️ Trust Boundary Architecture

```
   [Untrusted PC]
         | (CoS 0 / Best Effort Default)
         v
  [PC Port on Cisco 7960 Phone]
         |
  [Internal 3-Port Switch] ---- Tag Voice RTP with CoS 5 / DSCP EF
         |
         | (802.1Q Tagged Trunk to Access Switch)
         v
  [Catalyst Switch Port: Fa0/1]
     - switchport mode access
     - switchport access vlan 10
     - switchport voice vlan 20
     - mls qos trust device cisco-phone
     - mls qos trust cos
```

### The Trust Boundary Rule:
1. The switch port dynamically authenticates the connected device using Cisco Discovery Protocol (CDP).
2. If CDP identifies a genuine **Cisco IP Phone**, the switch trusts the CoS 5 marking on the Voice VLAN (VLAN 20).
3. If an unauthorized PC or rogue device attempts to send packets with CoS 5 on Data VLAN 10, the switch **rewrites the CoS/DSCP to 0 (Best Effort)**, preventing QoS spoofing attacks.

---

## 🧮 Bandwidth & Priority Queue Calculations

### 1. Single G.711 Call Bandwidth Consumption:
* Voice Payload: $64\text{ kbps}$ (80 bytes per 10 ms packet or 160 bytes per 20 ms)
* RTP/UDP/IP Headers: $40\text{ bytes}$
* Ethernet Frame Overhead: $18\text{ bytes} + 4\text{ bytes (802.1Q)} = 22\text{ bytes}$
* Total packet size per 20 ms: $160 + 40 + 22 = 222\text{ bytes}$
* Packet rate: $50\text{ packets/second}$
$$\text{Total Bandwidth per G.711 Call} = 222 \times 8 \times 50 = 87.2\text{ kbps}$$

### 2. Low Latency Queueing (LLQ) Allocation Rule:
Cisco best practices recommend provisioning no more than **33%** of total interface bandwidth for priority voice traffic:
$$\text{Priority Bandwidth} \le 0.33 \times C_{\text{link}}$$
For a 10 Mbps WAN link:
$$\text{Priority Queue Budget} = 3.3\text{ Mbps}$$
Maximum concurrent G.711 calls supported:
$$N_{\text{calls}} = \frac{3300\text{ kbps}}{87.2\text{ kbps}} \approx 37\text{ concurrent calls}$$
