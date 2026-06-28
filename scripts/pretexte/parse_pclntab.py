#!/usr/bin/env python3
"""Parse Go 1.20+ .gopclntab and disassemble main.deriveKey."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

BIN = "/tmp/jq-malicious"
PCLNTAB_OFF = 0x37DBC0
TEXT_START = 0x401000


def u64(d, o):
    return struct.unpack_from("<Q", d, o)[0]


def u32(d, o):
    return struct.unpack_from("<I", d, o)[0]


def parse_pclntab(data: bytes):
    off = PCLNTAB_OFF
    magic = u32(data, off)
    assert magic == 0xFFFFFFF1, hex(magic)
    ptrsize = data[off + 7]
    nfunc = u64(data, off + 8)
    nfiles = u64(data, off + 16)
    text_start = u64(data, off + 24)
    funcname_off = u64(data, off + 32)
    cu_off = u64(data, off + 40)
    filetab_off = u64(data, off + 48)
    pctab_off = u64(data, off + 56)
    pcln_off = u64(data, off + 64)
    print(f"nfunc={nfunc} text_start={text_start:#x}")
    print(f"funcname_off={funcname_off:#x} pctab_off={pctab_off:#x} pcln_off={pcln_off:#x}")

    def read_name(name_off):
        base = PCLNTAB_OFF + funcname_off
        s = data[base + name_off : data.find(b"\x00", base + name_off)]
        return s.decode("latin1", "replace")

    funcs = []
    # Go 1.20 func tab: each entry is fixed size
    functab_off = PCLNTAB_OFF + 0x60  # after header - need func tab offset
    # func tab is right after header for go1.20: at offset 0x60 from pclntab start
    ftab = PCLNTAB_OFF + 0x60
    for i in range(nfunc):
        entry_pc = u64(data, ftab + i * 8)
        if i + 1 >= nfunc:
            break
        next_pc = u64(data, ftab + (i + 1) * 8)
        # func metadata at pcln_off + i * funcSize
        # Go 1.20 funcInfo is 40 bytes (approx)
        fi_off = PCLNTAB_OFF + pcln_off + i * 40
        name_off = u32(data, fi_off + 0)
        # actually go1.20 layout: uint32 nameOff; uint32 args; ...
        name = read_name(name_off)
        if name.startswith("main."):
            funcs.append((name, entry_pc, next_pc - entry_pc))
    return funcs, data


def disasm_func(data, entry, size=512):
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    off = entry - 0x400000  # first segment mapping
    code = data[off : off + size]
    lines = []
    for insn in md.disasm(code, entry):
        lines.append(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
    return lines


def main():
    data = open(BIN, "rb").read()
    funcs, data = parse_pclntab(data)
    print("\nmain.* functions:")
    targets = {}
    for name, entry, sz in sorted(funcs):
        print(f"  {name}: entry={entry:#x} size~{sz}")
        targets[name] = entry

    for fn in ["main.deriveKey", "main.main"]:
        if fn not in targets:
            continue
        print(f"\n=== {fn} disasm ===")
        for line in disasm_func(data, targets[fn], 800)[:80]:
            print(line)


if __name__ == "__main__":
    main()
