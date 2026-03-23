# Allen-Bradley MicroLogix 1400 Memory Mapping Guide

Unlike traditional flat-memory PLCs (such as Modbus on an M221) where you access data via raw physical silicon addresses (e.g., `0x08001000`), the Allen-Bradley MicroLogix 1400 abstracts its memory into isolated **Data Files**.

Because the PLC firmware obscures the physical hardware memory, logical addressing (e.g., `N7:10` or `B3:0`) is the only way to request data. When you dump a specific data file (like `N7_dump.txt`) into a hex-readable format, the leftmost column of `00000000` is simply the byte offset from the start of that specific file, not a global RAM address.

## Common MicroLogix Data File Types

| Letter | File Type | Description | Size per Element |
| :--- | :--- | :--- | :--- |
| **O** | Output | Physical relay/transistor output states | 1 Word (16-bits) |
| **I** | Input | Physical sensor input states | 1 Word (16-bits) |
| **S** | Status | PLC system diagnostics and errors | 1 Word (16-bits) |
| **B** | Binary | Software boolean coils / flags | 1 Word (16-bits) |
| **T** | Timer | Complex structure (PRE, ACC, DN, TT, EN) | 3 Words (48-bits)|
| **C** | Counter | Complex structure (PRE, ACC, DN, CU, CD) | 3 Words (48-bits)|
| **R** | Control | Complex control structures (Lengths/Positions) | 3 Words (48-bits)|
| **N** | Integer | Standard 16-bit signed math storage | 1 Word (16-bits) |
| **F** | Float | 32-bit floating-point decimals | 2 Words (32-bits)|
| **L** | Long | 32-bit signed integers | 2 Words (32-bits)|

## Converting Hex Dumps back to PLC Addresses

Because most standard MicroLogix files (`O`, `I`, `B`, `T`, `C`, `N`) store data in **2-byte (16-bit) words**, it is very easy to mathematically map a text file offset back to a PLC address:

1. **Take the hex offset** from the left column of your txt file.
2. **Convert it to Decimal.**
3. **Divide by 2** (because elements are 2 bytes long).
4. The result is your exact PLC Element index.

### Example Walkthrough:
Suppose you are reading `N7_dump.txt` and you find interesting data at offset `0000001A`:
- The hex offset is `1A`.
- Convert hex `1A` to decimal => `26`.
- Divide by 2 (bytes per integer word): `26 / 2 = 13`.
- Your data perfectly maps to the PLC address: **`N7:13`**.
