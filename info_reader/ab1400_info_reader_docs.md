# Allen-Bradley 1400 Information Reader

The script `ab1400_info_reader.py` leverages `pycomm3` to send a CIP "**Identity**" request to the PLC over TCP Port 44818. This returns basic hardware and firmware information about the controller without needing to know any of the specific Data File allocations or memory addresses.

## Requirements

You must have `pycomm3` installed:

```bash
pip install pycomm3
```

## Basic Usage

Print the PLC's identity information to the console:

```bash
python ab1400_info_reader.py <IP_ADDRESS>
```

**Example:**
```bash
python ab1400_info_reader.py 192.168.1.10
```

## Advanced Usage

Save the raw identity information to a `.json` file:

```bash
python ab1400_info_reader.py <IP_ADDRESS> --out <FILENAME>.json
```

**Example:**
```bash
python ab1400_info_reader.py 192.168.1.10 --out plc_identity.json
```

## What it Outputs

You can expect to receive the following data classes from a successful identity query:
- **Vendor:** E.g., Rockwell Automation/Allen-Bradley
- **Product Name:** Standard name programmed into the hardware
- **Product Type:** The general hardware category
- **Product Code:** Identifying hardware model code
- **Revision:** Firmware version running on the PLC (Major and Minor)
- **Serial:** Hardware serial number inside the silicon
- **Status:** Basic bitmap of device status (e.g. faulted, run mode, etc.)
