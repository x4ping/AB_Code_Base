# Presentation Guide: Modbus (M221) vs. Allen-Bradley (MicroLogix 1400) Memory Architectures

When extracting memory from PLCs, the script you use relies entirely on how the device's brain organizes data. Here is a breakdown of why our two scripts (`m221_read_mem.py` and `ab1400_read_mem.py`) are fundamentally different.

## 1. The Schneider M221 (Modbus) Approach: "Flat Memory"

The M221 script uses the Modbus TCP protocol (and a specific Unity payload). It is built around a **Flat Memory Architecture**.

* **How it works:** Memory is treated like one massive, continuous block of silicon—analogous to a single giant spreadsheet or raw hard drive space. 
* **The Extraction Script (`m221_read_mem.py`):** Because it operates on a flat sandbox, the researcher only needs to provide a raw physical offset (e.g., "Start at memory address `0x0000`") and a byte size (e.g., "Read 50,000 bytes"). The script blindly loops through the physical silicon sequentially until it hits the end, dumping everything it touches into one massive `.bin` hex chunk.
* **The Catch:** You get everything incredibly fast, but it is completely unformatted. You have no idea what bytes belong to a timer, a counter, or an output wire just by looking at the raw dump. You have to reverse-engineer the structure yourself natively.

---

## 2. The Allen-Bradley MicroLogix 1400 (PCCC) Approach: "Abstracted File Memory"

The Allen-Bradley PLC uses the PCCC (Programmable Controller Communication Commands) protocol. Unlike the M221, Allen-Bradley wraps its physical memory inside an internal operating system tier. It uses an **Abstracted File Architecture**.

* **How it works:** The researcher is explicitly blocked from touching the raw physical silicon. The PLC firmware hides the physical RAM addresses and forces you to request data via "Logical Data Files" (e.g., "Give me Integers from File 7", or "Give me Outputs from File 0"). 
* **The Extraction Script (`ab1400_read_mem.py`):** We cannot just say "give me 50,000 bytes starting at physical address 0". Instead, our script has to act like a directory crawler. It systematically probes **Slots 0 through 255** and asks the firmware, "Do you have a file mapped here?". When it finds one (like `N7`), it dynamically discovers how many elements are inside it, handles complex dictionary structures (like Timers), and then issues chunked extraction requests.
* **The Catch:** While it is significantly harder to write an extraction script for Allen-Bradley (because we have to brute-force map 255 slots, parse complex structures, and bypass tag syntax bugs), the resulting dump is **infinitely more valuable**. The data comes back pre-categorized. You get an isolated `N7_dump.txt` full of just integers, and an `O0_dump` exactly showcasing the hardware output coil states.

---

## Summary Takeaways for Presentation
**M221 / Modbus** extractions behave like a classic physical hard drive image. You rip the raw 1s and 0s physically from the board efficiently, but parsing it later to find what variables do what is immensely difficult.

**Allen-Bradley MicroLogix** behaves like a modern categorized file system. The firmware aggressively protects the physical RAM logic, forcing researchers to logically interrogate 256 structural "Slots". Extracting it is harder, but gives you pre-classified, surgically organized intelligence on the exact operational state of the machine.
