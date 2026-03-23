#!/usr/bin/env python3
import struct
import argparse
import sys
import time
import os

try:
    from pycomm3 import SLCDriver
except ImportError:
    sys.exit(
        "\n[ERROR] pycomm3 is not installed.\n"
        "  Install it with:  pip install pycomm3\n"
    )

def read_ab1400_memory_chunked(driver, start_addr, elements):
    """
    Reads elements in chunks to avoid PCCC packet size limits for MicroLogix 1400.
    """
    file_part, elem_part = start_addr.split(':', 1)
    start_idx = int(elem_part)
    all_data = []
    max_chunk = 256  # Maximum possible chunk size
    
    remained = elements
    current_idx = start_idx
    
    while remained > 0:
        fragment = max_chunk if remained >= max_chunk else remained
        address = f"{file_part}:{current_idx}{{{fragment}}}"
        
        try:
            result = driver.read(address)
            if result.error:
                if len(all_data) == 0:
                    return None
                break
        except Exception:
            if len(all_data) == 0:
                return None
            break
            
        if fragment == 1:
            all_data.append(result.value)
        else:
            all_data.extend(result.value)
            
        remained -= fragment
        current_idx += fragment
        
    return all_data

def discover_file_size(driver, file_str, max_elements=256):
    """
    Binary search (or linear fallback) to find the size of a data file.
    MicroLogix data files are generally capped at 256 elements in older platforms, 
    but we can just try to read the highest bound we can until it errors out.
    """
    # A simple way is to read element by element until it errors out,
    # or read large chunks and stop when an error occurs.
    # To be fast, let's just do a chunked read from 0 to 256. 
    # If the file size is 50, reading 0-100 will fail, so we read 1 by 1 or chunk by chunk
    
    # Check if the file exists at all by reading element 0
    try:
        test = driver.read(f"{file_str}:0")
        if test.error:
            return 0
    except Exception:
        return 0

    # It exists. Let's find its size. (Max elements for MicroLogix is typically 256 per file)
    size = 0
    chunk = 16
    while size <= 256:
        res = driver.read(f"{file_str}:{size}{{{chunk}}}")
        if res.error:
            # Reverted to 1-by-1 to find exact edge
            for i in range(size, size + chunk):
                single = driver.read(f"{file_str}:{i}")
                if single.error:
                    return i
                size += 1
            return size
        else:
            size += chunk
            
    return size

def pack_data(data_list, file_type):
    char_type = file_type[0].upper()
    if char_type in ('N', 'B', 'T', 'C', 'R', 'S', 'O', 'I'):
        fmt = f"<{len(data_list)}H"
        unsigned_data = [int(x) & 0xFFFF for x in data_list]
        return struct.pack(fmt, *unsigned_data)
    elif char_type == 'F':
        fmt = f"<{len(data_list)}f"
        return struct.pack(fmt, *data_list)
    elif char_type == 'L':
        fmt = f"<{len(data_list)}i"
        return struct.pack(fmt, *data_list)
    else:
        fmt = f"<{len(data_list)}H"
        unsigned_data = [int(x) & 0xFFFF for x in data_list]
        return struct.pack(fmt, *unsigned_data)

def write_output_file(filename, data_list, use_hex, file_type):
    """
    Writes data as raw binary (.bin), readable hex (.txt), or structured JSON for complex types.
    """
    if not data_list: return
    
    if isinstance(data_list[0], dict):
        import json
        filename = filename.replace('.bin', '') + '_structured.json'
        with open(filename, "w") as f:
            json.dump(data_list, f, indent=4)
        return
        
    bin_data = pack_data(data_list, file_type)
    
    if use_hex:
        filename = filename.replace('.bin', '') + '.txt'
        with open(filename, "w") as f:
            for i in range(0, len(bin_data), 16):
                chunk = bin_data[i:i+16]
                hex_str = " ".join(f"{b:02x}" for b in chunk)
                ascii_str = "".join(chr(b) if 32 <= b <= 126 else "." for b in chunk)
                f.write(f"{i:08x}  {hex_str:<48} |{ascii_str}|\n")
    else:
        if not filename.endswith('.bin'):
            filename += '.bin'
        with open(filename, "wb") as f:
            f.write(bin_data)

def dump_all_memory(ip, output_dir, use_hex):
    """
    Scans through all possible MicroLogix data files and dumps them to a directory.
    """
    if not os.path.exists(output_dir):
        os.makedirs(output_dir)
        
    print(f"Connecting to {ip} for full memory extraction mapping...")
    
    # Map of known default file types by number
    standard_files = {
        0: 'O', 1: 'I', 2: 'S', 3: 'B', 
        4: 'T', 5: 'C', 6: 'R', 7: 'N', 8: 'F'
    }
    
    dumped_count = 0
    try:
        with SLCDriver(ip) as driver:
            driver.open()
            
            # Scan files 0 through 255 (MicroLogix max file number is 255)
            for file_num in range(256):
                # Guess the type letter. User files (9-255) are typically N, B or F.
                # If we don't know, we will try N, F, B in that order.
                if file_num in standard_files:
                    types_to_try = [standard_files[file_num]]
                else:
                    types_to_try = ['N', 'F', 'B', 'L']
                
                for t in types_to_try:
                    query_str = "S" if (t == 'S' and file_num == 2) else f"{t}{file_num}"
                    
                    # 1. Discover if file exists and get its size
                    size = discover_file_size(driver, query_str)
                    if size > 0:
                        print(f"[*] Found Memory File: {t}{file_num} (Size: {size} elements)")
                        
                        # 2. Extract the file
                        data = read_ab1400_memory_chunked(driver, f"{query_str}:0", size)
                        if data:
                            if not isinstance(data, list): data = [data]
                            
                            # 3. Write output (handles structs internally)
                            outfile = os.path.join(output_dir, f"{t}{file_num}_dump")
                            write_output_file(outfile, data, use_hex, t)
                            
                            dumped_count += 1
                        
                        # Once we found the file under one type (e.g., 'N10'), 
                        # we don't need to try 'F10', etc.
                        break
                        
    except Exception as e:
        print(f"[ERROR] Failed during full dump: {e}")
        
    print(f"\n[+] Full memory extraction complete. {dumped_count} memory files dumped into '{output_dir}'.")

def main():
    parser = argparse.ArgumentParser(description="MicroLogix 1400 Extractor")
    
    parser.add_argument("plc_ip", help="IP address of the PLC")
    parser.add_argument("--dump-all", action="store_true", help="Brute-force scan and dump ALL data files into a folder")
    parser.add_argument("--addr", default="", help="Single start memory address (e.g., N7:0)")
    parser.add_argument("--elements", type=int, default=0, help="Number of elements to read for single address")
    parser.add_argument("--out", default="plc_dump", help="Output file (or directory if using --dump-all)")

    parser.add_argument("--hex", action="store_true", help="Output in readable hex format instead of raw binary")

    args = parser.parse_args()

    if args.dump_all:
        dump_all_memory(args.plc_ip, args.out, args.hex)
    else:
        if not args.addr or args.elements <= 0:
            sys.exit("Error: Must provide --addr and --elements if not using --dump-all")
            
        print(f"Connecting to {args.plc_ip}...")
        try:
            with SLCDriver(args.plc_ip) as driver:
                driver.open()
                data = read_ab1400_memory_chunked(driver, args.addr, args.elements)
                if data is None:
                    sys.exit(1)
                if not isinstance(data, list): data = [data]
                
                ftype = args.addr.split(':')[0].strip('0123456789')
                
                write_output_file(args.out, data, args.hex, ftype)
                print(f"Successfully dumped {len(data)} elements to {args.out}")
        except Exception as e:
            sys.exit(f"Error: {e}")

if __name__ == '__main__':
    main()
