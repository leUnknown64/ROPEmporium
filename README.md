# ROP Emporium Writeups
This repository contains my writeups and solution scripts for the [ROP Emporium](https://ropemporium.com/) challenges. ROP Emporium features eight CTF-style problems specifically designed to teach return-oriented programming (ROP) in isolation. The binaries are Unix/Linux-based (ELF), with four different architectures currently supported: `x86_64`, `x86 (32-bit)`, `ARMv5`, and `MIPS`.

These served as my proper introduction to creating ROP chain exploits for ELF binaries.

## Tools I Use
- **Debugger:** `GDB` + `GEF` (GDB Enhanced Features)
- **Gadget Hungers:** `ropper`
- **Exploitation Framework:** `pwntools` for Python 3

## Repository Structure
Starting from the root of the repository, the following directory layout is used:
```
[architecture, i.e., x86_64, ARMv5]
\__[challenge]
	\__[challenge].md
	\__solution.py
```

Each challenge contains a writeup formatted with markdown (`[challenge].md`) and a Python script (`solution.py`) with the final solution.