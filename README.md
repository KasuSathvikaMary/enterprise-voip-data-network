# 🏢 Enterprise Converged Voice (VoIP) and Data Network

[![Cisco IOS](https://img.shields.io/badge/Cisco%20IOS-15.x-blue.svg)](https://www.cisco.com/)
[![Packet Tracer](https://img.shields.io/badge/Simulator-Cisco%20Packet%20Tracer-green.svg)]()
[![QoS Standards](https://img.shields.io/badge/QoS-RFC%204594%20%2F%20Cisco%20SRND-orange.svg)]()
[![Tests](https://img.shields.io/badge/Compliance%20Tests-100%25%20Passing-brightgreen.svg)]()
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

An enterprise-grade reference architecture, configuration suite, and validation toolkit for deploying a **converged Voice over IP (VoIP) and Data Local Area Network (LAN)** with automated Quality of Service (QoS) prioritization.

---

## 🎯 Executive Summary & Objectives

The primary objective of this project is to deploy a **unified enterprise LAN infrastructure** capable of strictly prioritizing latency-sensitive, real-time voice communications (RTP streams and call signaling) over standard data traffic (web, email, file transfers).

```
                      +-------------------------+
                      |   R1-VOICE-GW (2811)    |
                      |   CME / DHCP Option 150 │
                      +------------+------------+
                                   | Gig0/0
                                   | (802.1Q Trunk)
                                   | Gig0/1
                      +------------+------------+
                      |    SW1-CORE (3560)      |
                      +-----+--------------+----+
                     Gig0/2 |              | Gig0/3
             (802.1Q Trunk) |              | (802.1Q Trunk)
                            |              |
           +----------------+----+    +----+----------------+
           | SW2-ACCESS-FL1 (2960)|   | SW3-ACCESS-FL2 (2960)|
           +----------+----------+    +----------+----------+
               Fa0/1  |  Fa0/2            Fa0/1  |  Fa0/2
                      |                          |
               +------+------+            +------+------+
               | IP Phone 1  |            | IP Phone 3  |
               | (Ext: 1001) |            | (Ext: 1003) |
               +------+------+            +------+------+
               PC Port|                   PC Port|
                      |                          |
               +------+------+            +------+------+
               |  PC-EXEC    |            |  PC-SALES   |
               |  (VLAN 10)  |            |  (VLAN 10)  |
               +-------------+            +-------------+
```

---

## 🔑 Key Components & Protocols

### 1. Voice VLANs & Dual-VLAN Access Ports
* **802.1Q Tagged Voice Traffic**: Access switches separate latency-sensitive voice frames from bulk data using **Voice VLAN 20** (`switchport voice vlan 20`) alongside untagged native **Data VLAN 10** (`switchport access vlan 10`).
* **Daisy-Chained Cisco IP Phones**: Connects PC to IP Phone PC port, saving physical switch ports while maintaining strict Layer 2 broadcast domain isolation.
* **QoS Trust Boundary & Security**: Employs `mls qos trust device cisco-phone` and `mls qos trust cos`. Untrusted PC data marked with priority is rewritten to Best Effort (CoS 0), defeating QoS spoofing.

### 2. Traffic Prioritization & Modular QoS CLI (MQC)
* **Layer 3 DSCP Classification**:
  * Voice RTP Media: **DSCP EF** (Expedited Forwarding - decimal 46).
  * Call Control / Signaling: **DSCP CS3** / **AF31** (decimal 24 / 26).
  * Best Effort Data: **DSCP 0** (Default).
* **Layer 2 802.1p CoS Mapping**:
  * Voice RTP: **CoS 5**.
  * Call Signaling: **CoS 3**.
* **Low Latency Queueing (LLQ)**: Low Latency Queue (`priority percent 33`) guarantees real-time voice packets bypass data queues with zero jitter.
* **Class-Based Weighted Fair Queueing (CBWFQ)**: Allocates guaranteed bandwidth (`bandwidth percent 5`) for SIP/SCCP signaling and Random Early Detection (WRED) for bulk data.

### 3. IP Telephony Infrastructure & Call Manager Express (CME)
* **DHCP Option 150**: Voice DHCP pool passes Option 150 (`option 150 ip 192.168.20.1`) informing Cisco 7960 IP Phones of their TFTP boot server.
* **Cisco Call Manager Express (CME)**: Integrated telephony PBX service hosting extensions, dial-peers, and button configurations.
* **SCCP / Skinny Call Control**: Port 2000 registration with automated extension assignment (`ephone-dn 1` to `ephone-dn 4`).

---

## 📁 Repository Structure

```
enterprise-voip-data-network/
├── README.md                      # Architecture overview, topology, and guides
├── LICENSE                        # MIT License
├── requirements.txt               # Dependencies
├── configs/
│   ├── R1-Voice-Gateway.ios       # Cisco 2811/2911 CME Router, MQC QoS, DHCP Option 150
│   ├── SW1-Core-Switch.ios        # Cisco Catalyst 3560 Core Switch, MLS QoS, 802.1Q Trunks
│   ├── SW2-Access-Floor1.ios      # Cisco Catalyst 2960 Floor 1 Access Switch (Voice VLAN 20)
│   └── SW3-Access-Floor2.ios      # Cisco Catalyst 2960 Floor 2 Access Switch (Voice VLAN 20)
├── docs/
│   ├── PACKET_TRACER_LAB_GUIDE.md # Step-by-step build instructions for Cisco Packet Tracer
│   ├── QOS_DESIGN_SPEC.md         # In-depth RFC 4594 / SRND QoS calculations & trust boundary
│   └── CME_TELEPHONY_REFERENCE.md # Call Manager Express reference & DHCP Option 150 guide
├── tools/
│   ├── voip_auditor.py            # Cisco IOS compliance auditor & rule checker
│   ├── qos_simulator.py           # Codec bandwidth calculator (G.711 / G.729 / G.722)
│   └── cli.py                     # CLI for config audits and QoS calculations
├── tests/
│   ├── test_config_audit.py       # Automated unit tests verifying 100% config compliance
│   └── test_qos_calculations.py   # Unit tests verifying MQC queue bandwidth & codecs
└── scripts/
    ├── audit_configs.sh           # One-line script to audit all IOS configs
    └── run_tests.sh               # Run automated pytest verification
```

---

## 🖥️ Cisco Packet Tracer Quick Start

### 1. Build the Physical Topology
1. Place **1x Cisco 2811 Router**, **1x Catalyst 3560 Switch**, and **2x Catalyst 2960 Switches**.
2. Place **4x Cisco 7960 IP Phones** and **4x Workstation PCs**.
3. **Power on Cisco IP Phones**: Click each 7960 IP Phone -> Physical tab -> Drag the power cord into the round power receptacle.
4. Cable the devices as outlined in [Packet Tracer Lab Guide](docs/PACKET_TRACER_LAB_GUIDE.md).

### 2. Apply Cisco IOS Configurations
Copy and paste the configuration files from the [`configs/`](configs/) folder directly into the CLI of each respective device:
- `configs/R1-Voice-Gateway.ios` ➡️ **R1-VOICE-GW**
- `configs/SW1-Core-Switch.ios` ➡️ **SW1-CORE-SWITCH**
- `configs/SW2-Access-Floor1.ios` ➡️ **SW2-ACCESS-FLOOR1**
- `configs/SW3-Access-Floor2.ios` ➡️ **SW3-ACCESS-FLOOR2**

### 3. Verify IP Phone Registration & Dialing
1. Verify on R1 router CLI:
   ```cisco
   show ephone
   ```
2. Verify extension numbers on phone displays:
   - IP Phone 1: **Ext 1001** (Executive-Office)
   - IP Phone 2: **Ext 1002** (Engineering-Lead)
   - IP Phone 3: **Ext 1003** (Sales-Floor)
   - IP Phone 4: **Ext 1004** (Helpdesk-Support)
3. Pick up IP Phone 1 handset and dial **1002** to initiate a live voice call.

---

## 🧪 Automated Auditing & QoS Calculation Toolkit

### 1. Audit Cisco Configurations
Run the automated compliance auditor to verify your configuration files against Cisco Enterprise SRND standards:
```bash
python3 tools/cli.py audit
```
*Output:*
```
✅ [Router (CME/Voice GW)] R1-Voice-Gateway.ios - Score: 100.0% (6/6 rules passed)
✅ [Switch (L2/L3)] SW1-Core-Switch.ios - Score: 100.0% (5/5 rules passed)
✅ [Switch (L2/L3)] SW2-Access-Floor1.ios - Score: 100.0% (5/5 rules passed)
✅ [Switch (L2/L3)] SW3-Access-Floor2.ios - Score: 100.0% (5/5 rules passed)

🎉 All Cisco configurations are 100% compliant with Cisco Enterprise Voice SRND!
```

### 2. Calculate Codec Bandwidth & LLQ Link Capacity
Calculate voice payload overhead and concurrent call capacities:
```bash
python3 tools/cli.py qos --link-speed 10 --llq 33
```
*Output:*
```
🔹 Codec: G.711u
   Bandwidth per call (L2 Ethernet): 88.8 kbps
   Max concurrent calls in LLQ:     37 calls
   Packet serialization delay:      0.1776 ms

🔹 Codec: G.729
   Bandwidth per call (L2 Ethernet): 32.8 kbps
   Max concurrent calls in LLQ:     100 calls
   Packet serialization delay:      0.0656 ms
```

### 3. Run Automated Tests
```bash
pytest tests/ -v
```
*(All 7 unit tests passing)*

---

## 🛡️ License
Released under the [MIT License](LICENSE).
Author: **Kasu Sathvika Mary** (<kasusathvika@gmail.com>)
