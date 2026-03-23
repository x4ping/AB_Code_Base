# MicroLogix 1400 Memory Enumerator (`ab1400_scanner.py`)

This tool is designed to perform a rapid, read-only reconnaissance scan of an Allen-Bradley MicroLogix 1400 PLC over EtherNet/IP (PCCC). Instead of downloading raw memory bytes, it identifies exactly which isolated Data Files (Slots 0-255) are currently allocated in the PLC's active logic.

## Why use this tool?
Before executing a full memory dump (which can take several minutes), it is crucial to know which Data Files actually exist. Attempting to dump unallocated files yields no data and creates unnecessary network overhead. The scanner acts as an `ls` or `dir` command, instantly revealing the live memory footprint of the device.

## Prerequisites
* Python 3.x
* The `pycomm3` library (`pip install pycomm3`)
* TCP/EtherNet access to the target PLC

## Usage

### Basic Console Scan
To scan a PLC and print the valid memory file locations to the terminal in real-time:
```powershell
python ab1400_scanner.py <PLC_IP_ADDRESS>
```
**Example:** `python ab1400_scanner.py 192.168.1.20`

### Export Scan Results to Text File
To save the evaluated file structure to a text document for later analysis, append the `--out` argument:
```powershell
python ab1400_scanner.py 192.168.1.20 --out my_targets.txt
```
This commands the script to document the located file slots precisely line-by-line (e.g., `Slot 7: N7`), which is highly useful when preparing specific memory block extraction attacks.

## How It Works Under the Hood
The Allen-Bradley MicroLogix OS abstracts physical memory into 256 independent Data File slots. 

The python scanner script iterates through slots `0` to `255`. For each slot, it probes element `0` of the most likely logical data type array via PCCC logical reads.

### Default Data File Slots
In Allen-Bradley MicroLogix devices, slots 0 through 8 are strictly reserved for the system's foundational data types. Slots 9 through 255 are dynamically allocated by the programmer structure.

| Slot Number | Default File Name | Meaning | Scanner Query Tag |
| :--- | :--- | :--- | :--- |
| **0** | `O0` | Physical Outputs | `O0:0` |
| **1** | `I1` | Physical Inputs | `I1:0` |
| **2** | `S2` | System Status | `S:0` *(syntax exception)* |
| **3** | `B3` | Binary / Internal Bools | `B3:0` |
| **4** | `T4` | Timers | `T4:0` |
| **5** | `C5` | Counters | `C5:0` |
| **6** | `R6` | Control Registers | `R6:0` |
| **7** | `N7` | Integers (16-bit) | `N7:0` |
| **8** | `F8` | Floats (32-bit) | `F8:0` |
| **9-255** | `N9`, `B12`, etc. | User-Defined Files | Dynamically tested |

If the PLC responds successfully without a protocol exception on a probe, the script confirms the slot is actively mapped and loaded into the processor's active RAM.

*(Note: Slot 2 is dynamically formatted as `S:0` internally rather than `S2:0` to bypass a formal syntactic requirement inside the underlying `pycomm3` driver codebase).*
