#!/usr/bin/env python3
import sys
import argparse
import time

try:
    from pycomm3 import SLCDriver
except ImportError:
    sys.exit("[ERROR] pycomm3 is not installed. Run: pip install pycomm3")

def scan_plc_files(ip, out_file=None):
    print(f"Connecting to {ip} to perform a rapid existence scan (0-255)...\n")
    
    standard_files = {
        0: 'O', 1: 'I', 2: 'S', 3: 'B', 
        4: 'T', 5: 'C', 6: 'R', 7: 'N', 8: 'F'
    }
    
    found_count = 0
    found_list = []
    try:
        with SLCDriver(ip) as driver:
            driver.open()
            
            # MicroLogix allows up to file 255
            for file_num in range(256):
                sys.stdout.write(f"Checking slot {file_num:<3} ... ")
                sys.stdout.flush()
                
                if file_num in standard_files:
                    types_to_try = [standard_files[file_num]]
                else:
                    types_to_try = ['N', 'F', 'B', 'T', 'C', 'R', 'L']
                
                found_type = None
                for t in types_to_try:
                    query_str = "S" if (t == 'S' and file_num == 2) else f"{t}{file_num}"
                    try:
                        test = driver.read(f"{query_str}:0")
                        if not test.error:
                            found_type = f"{t}{file_num}"
                            break
                    except Exception:
                        pass
                
                if found_type:
                    print(f"[ FOUND ] as {found_type}")
                    found_list.append((file_num, found_type))
                    found_count += 1
                else:
                    print("[ Not Found ]")
                        
    except Exception as e:
        print(f"\n[ERROR] Connection failed: {e}")
        
    print("-" * 55)
    print(f"Scan complete. Found {found_count} allocated data files.")
    
    if out_file and found_count > 0:
        if not out_file.endswith('.txt'): out_file += '.txt'
        try:
            with open(out_file, "w") as f:
                f.write(f"MicroLogix 1400 Scan Results for {ip}\n")
                f.write("-" * 40 + "\n")
                for num, ft in found_list:
                    f.write(f"Slot {num}: {ft}\n")
            print(f"[+] Saved results to {out_file}")
        except Exception as e:
            print(f"[ERROR] Could not write to {out_file}: {e}")

def main():
    parser = argparse.ArgumentParser(description="MicroLogix 1400 Memory Enumerator")
    parser.add_argument("plc_ip", help="IP address of the PLC to scan")
    parser.add_argument("--out", default="", help="Optional text file to save the found file names")
    
    args = parser.parse_args()
    scan_plc_files(args.plc_ip, args.out)

if __name__ == '__main__':
    main()
