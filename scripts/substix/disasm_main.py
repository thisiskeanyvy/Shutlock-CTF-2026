#!/usr/bin/env python3
"""Disassemble main.main with string resolution."""
import re
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

BIN = "/tmp/jq-malicious"
IMAGE = 0x400000
ENTRY = 0x620980


def file_to_va(d, fo):
    e_phoff = struct.unpack_from("<Q", d, 32)[0]
    e_phentsize = struct.unpack_from("<H", d, 54)[0]
    e_phnum = struct.unpack_from("<H", d, 56)[0]
    for i in range(e_phnum):
        o = e_phoff + i * e_phentsize
        p_type, _, p_offset, p_vaddr, _, p_filesz, _, _ = struct.unpack_from("<IIQQQQQQ", d, o)
        if p_type == 1 and p_offset <= fo < p_offset + p_filesz:
            return p_vaddr + (fo - p_offset)
    return IMAGE + fo


def rip_target(insn):
    m = re.search(r"rip ([+-]) 0x([0-9a-f]+)", insn.op_str)
    if not m:
        return None
    disp = int(m.group(2), 16)
    if m.group(1) == "-":
        disp = -disp
    return insn.address + insn.size + disp


def read_str(d, va, n=120):
    fo = va - IMAGE
    if fo < 0 or fo >= len(d):
        return None
    return d[fo : fo + n].split(b"\x00")[0].decode("latin1", "replace")


def main():
    d = open(BIN, "rb").read()
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    insns = list(md.disasm(d[ENTRY - IMAGE : ENTRY - IMAGE + 4500], ENTRY))
    for ins in insns:
        extra = ""
        if ins.mnemonic in ("lea", "mov") and "rip" in ins.op_str:
            t = rip_target(ins)
            if t:
                s = read_str(d, t)
                if s and len(s) >= 4 and s.isprintable():
                    extra = f'  ; "{s[:80]}"'
        if ins.mnemonic == "call":
            extra = f"  ; call"
        print(f"{ins.address:#x}:\t{ins.mnemonic}\t{ins.op_str}{extra}")


if __name__ == "__main__":
    main()
