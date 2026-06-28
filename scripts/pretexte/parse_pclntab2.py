#!/usr/bin/env python3
"""Correct Go 1.20 gopclntab parser for jq trojan."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

BIN = "/tmp/jq-malicious"
PCLNTAB = 0x37DBC0


def u32(d, o):
    return struct.unpack_from("<I", d, o)[0]


def u64(d, o):
    return struct.unpack_from("<Q", d, o)[0]


def parse():
    d = open(BIN, "rb").read()
    base = PCLNTAB
    magic = u32(d, base)
    assert magic == 0xFFFFFFF1
    ptrsize = d[base + 7]
    nfunc = u64(d, base + 8)
    nfiles = u64(d, base + 16)
    text_start = u64(d, base + 24)
    funcname_off = u64(d, base + 32)
    cu_off = u64(d, base + 40)
    filetab_off = u64(d, base + 48)
    pctab_off = u64(d, base + 56)
    pcln_off = u64(d, base + 64)
    print(f"nfunc={nfunc} text_start={text_start:#x} pcln_off={pcln_off:#x}")

    functab = base + 72  # header is 72 bytes for go1.20
    names_base = base + funcname_off

    def name_at(off):
        s = d[names_base + off : d.find(b"\x00", names_base + off)]
        return s.decode("latin1", "replace")

    mains = []
    for i in range(nfunc):
        ft = functab + i * 8
        entryoff = u32(d, ft)
        funcoff = u32(d, ft + 4)
        if i + 1 < nfunc:
            next_entry = u32(d, ft + 8)
            size = next_entry - entryoff
        else:
            size = 0
        entry = text_start + entryoff
        fo = base + pcln_off + funcoff
        name_off = u32(d, fo + 4)  # entryOff u32 then nameOff i32 at +4
        name = name_at(name_off)
        if name.startswith("main."):
            mains.append((name, entry, size, funcoff))
    return mains, d, text_start


def disasm(d, entry, n=600):
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    off = entry - 0x400000
    for insn in md.disasm(d[off : off + n], entry):
        yield f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}"


if __name__ == "__main__":
    mains, d, _ = parse()
    for name, entry, size, fo in sorted(mains):
        print(f"{name}: entry={entry:#x} size={size} funcoff={fo:#x}")
    for target in ["main.deriveKey", "main.main"]:
        hits = [m for m in mains if m[0] == target]
        if not hits:
            continue
        name, entry, size, _ = hits[0]
        print(f"\n=== {name} ===")
        for line in list(disasm(d, entry, 900))[:100]:
            print(line)
