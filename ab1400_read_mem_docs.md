# MicroLogix 1400 Memory Extractor (`ab1400_read_mem.py`)

This tool is designed to actively download and extract binary data directly from the active RAM of an Allen-Bradley MicroLogix 1400 PLC over EtherNet/IP (PCCC). 

It is capable of performing surgical, single-file element extracts or executing a brute-force complete extraction of the entire PLC memory mapping footprint.

## Prerequisites
* Python 3.x
* The `pycomm3` library (`pip install pycomm3`)
* Network access to the target PLC

## Features

* **Intelligent Chunking:** Automatically breaks down massive file requests into 256-element chunks to bypass the strict PCCC network payload limits without crashing.
* **Complex Data Support:** Directly packs standard data (Integers, Floats, Binary Coils) into raw binary, while safely isolating and formatting complex dictionary structs (like Timers `T`, Counters `C`, and Control `R`) into cleanly readable JSON.
* **Hex Formatting:** Built-in ability to cleanly format outputs into a human-readable `hexdump` structure.

## Usage

### 1. Single File Directed Dump
If you want to extract a specific memory array (for example, pulling exactly 100 elements starting at `N7:0`), you must specify the exact logical address and the number of elements to pull.

```powershell
python ab1400_read_mem.py <PLC_IP> --addr <START_ADDRESS> --elements <COUNT> --out <OUTPUT_FILE>
```
**Example:** `python ab1400_read_mem.py 192.168.3.10 --addr N7:0 --elements 100 --out N7_dump.bin`

### 2. Full Complete PLC Dump
If you do not know the exact file layout, or simply want to archive/investigate the entire controller state, you can use the brute-force extraction mode. This method systematically pings all 256 possible Data File slots, maps their array boundaries, and extracts them internally.

```powershell
python ab1400_read_mem.py <PLC_IP> --dump-all --out <OUTPUT_FOLDER_NAME>
```
**Example:** `python ab1400_read_mem.py 192.168.3.10 --dump-all --out plc_full_dump`

### 3. Hex-Readable Output Mode (`--hex`)
By default, the script packs standard elements into raw `.bin` binary files. If you want to analyze the data visually without a dedicated hex editor, simply append the `--hex` flag. The script will output clean `.txt` files formatted identically to standard Linux `hexdump` outputs instead.

**Example:** `python ab1400_read_mem.py 192.168.3.10 --dump-all --hex --out plc_full_dump`
