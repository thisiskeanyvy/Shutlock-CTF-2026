#!/usr/bin/env python3
"""Reverse jq trojan: pclntab + xref strings + emulate deriveKey."""
import base64
import hashlib
import re
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

BIN = "/tmp/jq-malicious"
IMAGE_BASE = 0x400000
PCLNTAB_OFF = 0x37DBC0


def u32(d, o):
    return struct.unpack_from("<I", d, o)[0]


def u64(d, o):
    return struct.unpack_from("<Q", d, o)[0]


def i32(d, o):
    return struct.unpack_from("<i", d, o)[0]


def read_cstr(d, off):
    end = d.find(b"\x00", off)
    return d[off:end].decode("latin1", "replace")


def parse_pclntab(d):
    b = PCLNTAB_OFF
    assert u32(d, b) == 0xFFFFFFF1
    nfunc = u64(d, b + 8)
    text_start = u64(d, b + 24)
    funcname_off = u64(d, b + 32)
    pcln_off = u64(d, b + 64)
    names = b + funcname_off

    def name_at(no):
        return read_cstr(d, names + no)

    # functab is after funcdata; scan _func records in pcln region
    fd_base = b + pcln_off
    funcs = {}
    for off in range(0, min(0x300000, len(d) - fd_base), 4):
        fo = fd_base + off
        no = i32(d, fo + 4)
        if no < 0 or no > 0x500000:
            continue
        try:
            nm = name_at(no)
        except Exception:
            continue
        if not nm or len(nm) > 200 or nm[0] not in "main.(":
            continue
        if nm.startswith("main.") and nm not in funcs:
            eo = u32(d, fo)
            funcs[nm] = text_start + eo
    return funcs, text_start


def rip_target(insn):
    m = re.search(r"rip ([+-]) 0x([0-9a-f]+)", insn.op_str)
    if not m:
        return None
    disp = int(m.group(2), 16)
    if m.group(1) == "-":
        disp = -disp
    return insn.address + insn.size + disp


def disasm_range(d, start, size=2000):
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    off = start - IMAGE_BASE
    return list(md.disasm(d[off : off + size], start))


def find_xrefs(d, target_va, seg=(0x401000, 0x700000)):
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    hits = []
    s, e = seg
    off = s - IMAGE_BASE
    for insn in md.disasm(d[off : e - IMAGE_BASE], s):
        if "rip" not in insn.op_str:
            continue
        t = rip_target(insn)
        if t is not None and abs(t - target_va) < 8:
            hits.append(insn)
    return hits


def main():
    d = open(BIN, "rb").read()
    funcs, text = parse_pclntab(d)
    mains = {k: v for k, v in funcs.items() if k.startswith("main.")}
    print("main.* functions:")
    for k, v in sorted(mains.items(), key=lambda x: x[1]):
        print(f"  {k}: {v:#x}")

    key_va = IMAGE_BASE + d.find(b"83zMUZVWbI0dL2XEVC54")
    c2_va = IMAGE_BASE + d.find(b"https://nixos-community.me/update")
    salt_va = IMAGE_BASE + d.find(b"H92t9H9rHt3H")
    print(f"\nkey={key_va:#x} c2={c2_va:#x} salt={salt_va:#x}")

    for label, va in [("key", key_va), ("c2", c2_va), ("salt", salt_va)]:
        x = find_xrefs(d, va)
        print(f"xrefs {label}: {len(x)}")
        for ins in x[:5]:
            print(f"  {ins.address:#x}: {ins.mnemonic} {ins.op_str}")

    if "main.deriveKey" in funcs:
        print("\n=== main.deriveKey ===")
        for ins in disasm_range(d, funcs["main.deriveKey"], 800)[:60]:
            print(f"{ins.address:#x}:\t{ins.mnemonic}\t{ins.op_str}")

    if "main.main" in funcs:
        print("\n=== main.main (calls) ===")
        insns = disasm_range(d, funcs["main.main"], 2500)
        for i, ins in enumerate(insns):
            if ins.mnemonic == "call":
                print(f"{ins.address:#x}:\tcall\t{ins.op_str}")
            if "deriveKey" in str(ins) or (ins.mnemonic == "lea" and rip_target(ins) in (key_va, c2_va, salt_va)):
                print(f"  * {ins.address:#x}:\t{ins.mnemonic}\t{ins.op_str} -> {rip_target(ins):#x}")


if __name__ == "__main__":
    main()
