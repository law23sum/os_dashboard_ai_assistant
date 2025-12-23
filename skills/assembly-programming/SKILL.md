---
name: assembly-programming
description: Write, read, and analyze assembly code. Use for disassembly, calling conventions, low-level performance work, or binary analysis on macOS.
---

# Assembly Programming

## Overview
Work with assembly on the host architecture and use tooling for disassembly and debugging.

## Quick Start
- Identify architecture with `uname -m` and `file`.
- Pick syntax (AT and T vs Intel) and toolchain (clang, as, objdump, otool, lldb).

## Workflow
1. Determine target architecture and OS ABI.
2. Assemble and link with `clang` or `as` and validate symbols with `nm`.
3. Disassemble with `objdump -d` or `otool -tvV`.
4. Debug with `lldb`; verify register usage and stack alignment.

## Common Tasks
- Implement small routines with clear prologue and epilogue.
- Translate compiler output to understand performance hotspots.
- Patch instructions with attention to encoding and alignment.

## Guardrails
- State calling convention explicitly (AAPCS64, System V, etc).
- Preserve callee-saved registers and stack alignment.
- Avoid undefined behavior when interfacing with C or C++.
