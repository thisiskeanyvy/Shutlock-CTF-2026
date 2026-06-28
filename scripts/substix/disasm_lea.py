#!/usr/bin/env python3
"""Scan amd64 RIP-relative LEA/MOV to rodata targets in jq trojan."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

BIN = "/tmp/jq-malicious"
TARGETS = {
    "key_b64": 0x400F88,
    "salt": 0x44B34F,
    "c2": 0x705AC5,
}


def main():
    data = open(BIN, "rb").read()
    text = data[0:0x277611]  # first LOAD exec segment
    base = 0x400000
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    hits = {k: [] for k in TARGETS}
    for insn in md.disasm(text, base):
        if insn.mnemonic not in ("lea", "mov", "movabs"):
            continue
        for op in insn.operands:
            if op.type != 3:  # mem
                continue
            if op.mem.base != 41:  # X86_REG_RIP in capstone x86? check
                pass
            if "rip" not in insn.op_str:
                continue
            tgt = insn.address + insn.size + op.mem.disp
            for name, va in TARGETS.items():
                if abs(tgt - va) <= 2:
                    hits[name].append((insn.address, f"{insn.mnemonic} {insn.op_str}"))
    for name, lst in hits.items():
        print(f"{name}: {len(lst)} hits")
        for addr, dis in lst[:10]:
            print(f"  0x{addr:x}: {dis}")

    # disasm around first key hit
    if hits["key_b64"]:
        start = hits["key_b64"][0][0] - 0x100
        print(f"\n=== disasm 0x{start:x} ===")
        off = start - base
        for insn in md.disasm(text[off : off + 0x400], start):
            mark = ""
            if any(h[0] == insn.address for h in hits["key_b64"] + hits["salt"] + hits["c2"]):
                mark = " <--"
            print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}{mark}")


if __name__ == "__main__":
    main()
