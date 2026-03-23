# Allen-Bradley MicroLogix 1400

This repository contains tools and documentation for interacting with and analyzing the memory of an Allen-Bradley MicroLogix 1400 PLC over EtherNet/IP.

## Contents

- **file_scanner**: Contains a Python script (`ab1400_scanner.py`) to quickly scan the PLC for allocated data files (N, B, O, I, T, C, R, F, L, ST, etc.) and identity their types.
- **mem_reader**: Contains a Python script (`ab1400_read_mem.py`) to read specific memory addresses and Data Files from the PLC once they are identified.
- **memory_mapping_guide.md**: A guide explaining how the Allen-Bradley MicroLogix 1400 abstracts its memory into isolated Data Files and how to map hex dumps back to PLC addresses.
- **m221_vs_ab1400_presentation.md**: A comparison presentation between Schneider Electric's M221 and the Allen-Bradley MicroLogix 1400 PLCs.

## Setup

These scripts utilize the `pylogix` library to communicate with the PLC over EtherNet/IP.

```bash
pip install pylogix
```

Please refer to the documentation within each respective directory for usage instructions.
