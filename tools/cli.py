"""
Command-Line Interface for Cisco VoIP Config Audit & QoS Calculations.
"""
import argparse
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from tools.voip_auditor import VoipConfigAuditor
from tools.qos_simulator import QosBandwidthCalculator

def print_banner():
    banner = """
    ╔═══════════════════════════════════════════════════════════════╗
    ║      🏢 ENTERPRISE CONVERGED VOIP & DATA NETWORK SUITE       ║
    ║        Cisco Voice VLAN, CME, & MQC QoS Validation Tool       ║
    ╚═══════════════════════════════════════════════════════════════╝
    """
    print(banner)

def cmd_audit(args):
    print_banner()
    auditor = VoipConfigAuditor()
    config_dir = args.dir

    if os.path.isfile(args.target):
        targets = [args.target]
    elif os.path.isdir(args.target):
        targets = [os.path.join(args.target, f) for f in os.listdir(args.target) if f.endswith(".ios")]
    else:
        targets = [os.path.join(config_dir, f) for f in os.listdir(config_dir) if f.endswith(".ios")]

    print(f"🔍 Auditing {len(targets)} Cisco IOS configuration files...\n")
    all_passed = True

    for target in sorted(targets):
        res = auditor.audit_file(target)
        status_symbol = "✅" if res["score"] == 100 else "⚠️"
        print(f"{status_symbol} [{res['device_type']}] {res['filename']} - Score: {res['score']}% ({res['passed_rules']}/{res['total_rules']} rules passed)")
        for chk in res["checks"]:
            mark = "  ✓" if chk["passed"] else "  ✗"
            print(f"   {mark} [{chk['category']}] {chk['rule']}: {chk['detail']}")
        print()
        if res["score"] < 100:
            all_passed = False

    if all_passed:
        print("🎉 All Cisco configurations are 100% compliant with Cisco Enterprise Voice SRND!")
    else:
        print("⚠️ Some configurations have compliance warnings. See details above.")

def cmd_qos(args):
    print_banner()
    calc = QosBandwidthCalculator()

    print(f"📊 Calculating VoIP QoS Capacity for Link Speed: {args.link_speed} Mbps (LLQ Budget: {args.llq}%)\n")

    for codec in ["G.711u", "G.729", "G.722"]:
        cap = calc.calculate_link_capacity(args.link_speed, args.llq, codec)
        print(f"🔹 Codec: {codec}")
        print(f"   Bandwidth per call (L2 Ethernet): {cap['bandwidth_per_call_kbps']} kbps")
        print(f"   Max concurrent calls in LLQ:     {cap['max_concurrent_calls']} calls")
        print(f"   Packet serialization delay:      {cap['serialization_delay_ms']} ms")
        print()

def main():
    parser = argparse.ArgumentParser(description="Enterprise Converged Voice & Data Network Tool")
    subparsers = parser.add_subparsers(dest="command")

    # Audit command
    audit_parser = subparsers.add_parser("audit", help="Audit Cisco IOS configuration files")
    audit_parser.add_argument("--target", "-t", default="configs", help="Path to config file or configs directory")
    audit_parser.add_argument("--dir", "-d", default="configs", help="Configs directory")

    # QoS command
    qos_parser = subparsers.add_parser("qos", help="Calculate VoIP bandwidth and LLQ capacity")
    qos_parser.add_argument("--link-speed", "-s", type=float, default=10.0, help="Link speed in Mbps")
    qos_parser.add_argument("--llq", type=float, default=33.0, help="Priority LLQ percent (default: 33%%)")

    args = parser.parse_args()
    if not args.command:
        args.command = "audit"
        args.target = "configs"
        args.dir = "configs"

    if args.command == "audit":
        cmd_audit(args)
    elif args.command == "qos":
        cmd_qos(args)

if __name__ == "__main__":
    main()
