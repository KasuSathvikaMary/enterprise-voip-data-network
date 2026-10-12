# 📞 Cisco Call Manager Express (CME) Telephony Reference

## 1. What is Cisco Call Manager Express?
**Cisco Call Manager Express (CME)** is an embedded IP telephony call processing system built directly into Cisco IOS routers (e.g., 2800, 2900, 3900 series). It provides IP PBX features for small-to-medium branches or enterprise distributed offices without requiring a dedicated external server cluster.

---

## 2. DHCP Option 150 vs Option 66

In standard IP networks, DHCP provides IP address, subnet mask, default gateway, and DNS servers. For IP Telephony, IP phones also require the IP address of their **TFTP server** to download configuration XML files (`SEP<MAC>.cnf.xml`) and firmware binaries.

| DHCP Option | Standard | Supported Format | Why Option 150 is Preferred by Cisco |
| :--- | :--- | :--- | :--- |
| **Option 150** | Cisco Proprietary | Array of 32-bit IPv4 addresses (supports backup TFTP servers) | Cisco IP phones natively query Option 150 first. Allows listing primary and secondary TFTP servers. |
| **Option 66** | RFC 2132 | Single Hostname (FQDN) or IP string | Generic standard; does not support multiple redundant TFTP servers natively. |

### IOS Syntax:
```cisco
ip dhcp pool VOICE_POOL
 network 192.168.20.0 255.255.255.0
 default-router 192.168.20.1
 option 150 ip 192.168.20.1
```

---

## 3. Cisco CME Configuration Hierarchy

### Step 1: Telephony Service Global Settings
```cisco
telephony-service
 max-ephones 24             ! Maximum physical phones allowed to register
 max-dn 48                  ! Maximum directory numbers (extensions)
 ip source-address 192.168.20.1 port 2000  ! SCCP socket binding
 auto assign 1 to 24        ! Automatically bind newly booted phones
 create cnf-files           ! Generates XML configuration files in router flash:/
```

### Step 2: Directory Numbers (`ephone-dn`)
An `ephone-dn` is a virtual extension or line representation:
```cisco
ephone-dn 1
 number 1001
 name Executive-Office
 description Executive Line Ext 1001
```

### Step 3: Physical Phones (`ephone`)
An `ephone` represents the physical hardware device identified by its Ethernet MAC address:
```cisco
ephone 1
 mac-address 0001.965A.3201
 type 7960
 button 1:1                 ! Line 1 bound to ephone-dn 1
```

---

## 4. Troubleshooting Commands

| Command | Purpose |
| :--- | :--- |
| `show telephony-service` | Displays global CME registration status, total configured phones, and source IP socket |
| `show ephone` | Shows registered IP phones, IP addresses, MAC addresses, and active button status |
| `show ephone-dn` | Lists all extension directory numbers and line states (IDLE / RINGING / CONNECTED) |
| `show ip dhcp binding` | Verifies lease granted to Cisco phones on Voice VLAN |
| `debug ephone register` | Real-time debug output during phone registration |
