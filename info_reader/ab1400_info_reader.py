#!/usr/bin/env python3
import sys
import argparse
import json

try:
    from pycomm3 import CIPDriver
except ImportError:
    sys.exit("[ERROR] pycomm3 is not installed. Run: pip install pycomm3")

def read_plc_info(ip, out_file=None):
    print(f"Connecting to {ip} to query device identity...\n")
    
    try:
        # CIPDriver.list_identity queries the identity of the target without needing a full PCCC session
        info = CIPDriver.list_identity(ip)
        
        if not info:
            print(f"[ERROR] No identity response from {ip}. Ensure the PLC is online.")
            return
        
        print("--- PLC Identity Information ---")
        for key, value in info.items():
            if isinstance(value, bytes):
                value = value.decode('utf-8', errors='ignore')
            elif isinstance(value, dict):
                # Sometimes revision is represented as a dictionary {major: X, minor: Y}
                value = f"v{value.get('major', '?')}.{value.get('minor', '?')}"
            elif key == 'serial' and isinstance(value, int):
                # Convert integer serials into nicely formatted HEX strings
                value = f"{value:08X}"
                    
            print(f"{key.replace('_', ' ').title():<15}: {value}")
        print("--------------------------------")
        
        if out_file:
            with open(out_file, "w") as f:
                # default=str handles un-serializable properties just in case
                json.dump(info, f, indent=4, default=str) 
            print(f"\n[+] Saved raw identity information to {out_file}")
            
    except Exception as e:
        print(f"\n[ERROR] Connection or Identity request failed: {e}")

def main():
    parser = argparse.ArgumentParser(description="MicroLogix 1400 Identity Reader")
    parser.add_argument("plc_ip", help="IP address of the PLC to query")
    parser.add_argument("--out", default="", help="Optional JSON file to save the raw identity data")
    
    args = parser.parse_args()
    read_plc_info(args.plc_ip, args.out)

if __name__ == '__main__':
    main()
