#!/usr/bin/env python3
"""Rebuild pretexte_patched: NOP anti-debug branch + stack_chk fail stubs."""
from pathlib import Path

SRC = Path(__file__).parent / "pretexte"
OUT = Path(__file__).parent / "pretexte_copy"
TEXT_VMA = 0x598
TEXT_OFF = 1432
NOP = b"\x1f\x20\x03\xd5"  # nop


def off(vma: int) -> int:
    return TEXT_OFF + (vma - TEXT_VMA)


def main():
    data = bytearray(SRC.read_bytes())
  # cbnz w8, debugger path -> nop (always copy blob)
    data[off(0x5EC) : off(0x5EC) + 4] = NOP
  # stack_chk_fail calls -> nop (optional, from pretexte_dbg)
    for vma in (0x6B4, 0x764, 0x95C, 0x10D0):
        if data[off(vma) : off(vma) + 4] == b"\xed\x06\x00\x94" or True:
            data[off(vma) : off(vma) + 4] = NOP
    OUT.write_bytes(data)
    OUT.chmod(0o755)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
