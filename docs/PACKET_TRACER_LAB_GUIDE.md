# 📘 Cisco Packet Tracer Enterprise VoIP & Data Converged Network Lab Guide

## 📌 Lab Overview
This guide provides step-by-step instructions for deploying a fully converged enterprise Voice over IP (VoIP) and Data Local Area Network in **Cisco Packet Tracer**.

---

## 🛠️ Required Packet Tracer Devices

| Device Icon | Device Model | Quantity | Role |
| :--- | :--- | :---: | :--- |
| **Router** | Cisco 2811 / 2901 / 2911 | 1 | CME Voice Gateway, Inter-VLAN Routing, DHCP Option 150 Server, MQC QoS Engine |
| **Switch (L3/Core)** | Cisco Catalyst 3560-24PS | 1 | Core Switch, 802.1Q Trunk aggregation, MLS QoS Trust propagation |
| **Switch (L2/Access)**| Cisco Catalyst 2960-24TT | 2 | Access layer switches (Floor 1 & Floor 2) with Voice VLAN & PortFast |
| **IP Phone** | Cisco 7960 IP Phone | 4 | IP Telephony endpoints (Extensions 1001, 1002, 1003, 1004) |
| **Workstation** | Generic PC / Laptop | 4 | Data endpoints daisy-chained to IP Phones |

---

## 🔌 Cabling & Physical Topology Matrix

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

### Cabling Connections Table:
1. **R1 `Gig0/0`** <--- Copper Straight-Through ---> **SW1 `Gig0/1`**
2. **SW1 `Gig0/2`** <--- Copper Straight-Through ---> **SW2 `Gig0/1`**
3. **SW1 `Gig0/3`** <--- Copper Straight-Through ---> **SW3 `Gig0/1`**
4. **SW2 `Fa0/1`** <--- Copper Straight-Through ---> **IP Phone 1 (SW Port)**
5. **IP Phone 1 (PC Port)** <--- Copper Straight-Through ---> **PC-EXEC (FastEthernet0)**
6. **SW2 `Fa0/2`** <--- Copper Straight-Through ---> **IP Phone 2 (SW Port)**
7. **IP Phone 2 (PC Port)** <--- Copper Straight-Through ---> **PC-ENG (FastEthernet0)**

---

## ⚡ Step-by-Step Build Instructions

### Step 1: Connect Power to Cisco 7960 IP Phones
> **IMPORTANT (Packet Tracer Nuance)**: By default, Cisco 7960 IP Phones in Packet Tracer are powered off because PoE is not enabled on standard switch ports.
1. Click on each **Cisco 7960 IP Phone**.
2. Go to the **Physical** tab.
3. Locate the black power adapter brick in the bottom right corner.
4. Drag and drop the power cord into the round power plug hole at the back of the phone.
5. The display on the phone will light up and begin booting.

---

### Step 2: Configure R1 Voice Gateway Router
1. Open the CLI on **R1-VOICE-GW**.
2. Paste the contents of `configs/R1-Voice-Gateway.ios`.
3. Verify the subinterfaces are created:
   ```cisco
   show ip interface brief
   ```
4. Verify the DHCP pools:
   ```cisco
   show ip dhcp binding
   ```

---

### Step 3: Configure SW1 Core Switch
1. Open the CLI on **SW1-CORE-SWITCH**.
2. Paste the contents of `configs/SW1-Core-Switch.ios`.
3. Verify 802.1Q trunking:
   ```cisco
   show interfaces trunk
   ```

---

### Step 4: Configure Access Switches (SW2 & SW3)
1. Open the CLI on **SW2-ACCESS-FLOOR1** and paste `configs/SW2-Access-Floor1.ios`.
2. Open the CLI on **SW3-ACCESS-FLOOR2** and paste `configs/SW3-Access-Floor2.ios`.
3. Verify access and voice VLAN configuration:
   ```cisco
   show interfaces FastEthernet0/1 switchport
   ```
   *Expected Output:*
   - `Administrative Mode: static access`
   - `Access Mode VLAN: 10 (DATA_VLAN)`
   - `Voice VLAN: 20 (VOICE_VLAN)`

---

## 🧪 Verification & Testing

### 1. Verify IP Phone DHCP & Option 150 Registration
1. Click on **IP Phone 1** -> **GUI** tab.
2. Verify that the IP Phone has received an IP in subnet `192.168.20.0/24`.
3. Notice the top line displays:
   ```
   Line 1: 1001   (Executive-Office)
   ```
4. Verify on R1 router CLI:
   ```cisco
   show ephone
   ```

### 2. Verify Workstation Data VLAN DHCP
1. Click on **PC-EXEC** -> **Desktop** -> **IP Configuration**.
2. Switch to **DHCP**.
3. Verify the PC acquires an IP from `192.168.10.0/24` (Data VLAN), completely isolated from Voice VLAN 20!

### 3. Placing an Active VoIP Call in Packet Tracer
1. Open **IP Phone 1 (Ext: 1001)** and **IP Phone 2 (Ext: 1002)** side-by-side in Packet Tracer.
2. On IP Phone 1, click the handset to pick it up (you will hear a dial tone).
3. Dial `1002` on the keypad.
4. On IP Phone 2, notice the phone rings with `Ring From 1001`.
5. Pick up the handset on IP Phone 2.
6. The screens will display **Connected**, verifying bidirectional RTP voice stream!

### 4. Packet Tracer Simulation Mode (QoS & 802.1Q Verification)
1. Switch to **Simulation Mode** (Shift + S) in Packet Tracer.
2. Generate traffic from PC and IP Phone.
3. Click on the packet envelope passing through the switch trunk link:
   - Voice Packet: Check the **802.1Q Tag** -> `VLAN: 20`, `Priority: 5 (CoS 5)`, `IP Header DSCP: 0x2E (EF 46)`.
   - Data Packet: Check the **802.1Q Tag** -> `VLAN: 10`, `Priority: 0 (CoS 0)`, `IP Header DSCP: 0x00 (Best Effort)`.
