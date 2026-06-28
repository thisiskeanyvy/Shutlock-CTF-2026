#!/usr/bin/env python3
"""Disassemble jq trojan around string xrefs to infer deriveKey."""
import struct
from capstone import Cs, CS_ARCH_X86, CS_MODE_64

BIN = "/tmp/jq-malicious"


def parse_elf(data: bytes):
    if data[:4] != b"\x7fELF":
        raise ValueError("not ELF")
    e_phoff = struct.unpack_from("<Q", data, 0x20)[0]
    e_phentsize = struct.unpack_from("<H", data, 0x36)[0]
    e_phnum = struct.unpack_from("<H", data, 0x38)[0]
    segs = []
    for i in range(e_phnum):
        off = e_phoff + i * e_phentsize
        p_type, p_flags, p_offset, p_vaddr, p_paddr, p_filesz, p_memsz, p_align = struct.unpack_from(
            "<IIQQQQQQ", data, off
        )
        if p_type == 1:  # PT_LOAD
            segs.append((p_vaddr, p_offset, p_filesz, p_memsz, p_flags))
    return segs


def vaddr_to_offset(segs, va):
    for p_vaddr, p_offset, p_filesz, p_memsz, p_flags in segs:
        if p_vaddr <= va < p_vaddr + p_filesz:
            return p_offset + (va - p_vaddr)
    return None


def file_offset_to_vaddr(segs, fo):
    for p_vaddr, p_offset, p_filesz, p_memsz, p_flags in segs:
        if p_offset <= fo < p_offset + p_filesz:
            return p_vaddr + (fo - p_offset)
    return None


def main():
    data = open(BIN, "rb").read()
    segs = parse_elf(data)
    ro_strings = {
        "key_b64": 0xF88,
        "salt": 0x4B34F,
        "c2": 0x305ACD,
        "fetch_failed": 0x2FE006,
    }
    print("String VAs:")
    vas = {}
    for name, fo in ro_strings.items():
        va = file_offset_to_vaddr(segs, fo)
        vas[name] = va
        print(f"  {name}: file 0x{fo:x} -> va 0x{va:x} -> {data[fo:fo+60]!r}")

    # scan executable segments for RIP-relative LEA/MOV to these VAs
    md = Cs(CS_ARCH_X86, CS_MODE_64)
    md.detail = True
    hits = []
    for p_vaddr, p_offset, p_filesz, p_memsz, p_flags in segs:
        if not (p_flags & 1):
            continue
        code = data[p_offset : p_offset + p_filesz]
        for insn in md.disasm(code, p_vaddr):
            if insn.mnemonic in ("lea", "mov") and "rip" in insn.op_str:
                # parse disp
                for op in insn.operands:
                    if op.type == 3:  # X86_OP_MEM
                        target = insn.address + insn.size + op.mem.disp
                        for name, va in vas.items():
                            if va and abs(target - va) < 16:
                                hits.append((name, insn.address, f"{insn.mnemonic} {insn.op_str}"))
    print(f"\nXref hits: {len(hits)}")
    for name, addr, dis in hits[:30]:
        print(f"  0x{addr:x} {name}: {dis}")

    # disassemble around deriveKey candidates (functions using both key and salt)
    key_addrs = {h[1] for h in hits if h[0] == "key_b64"}
    salt_addrs = {h[1] for h in hits if h[0] == "salt"}
    both = []
    for ka in key_addrs:
        for sa in salt_addrs:
            if abs(ka - sa) < 0x500:
                both.append(min(ka, sa))
    if both:
        start = min(both) - 0x80
        print(f"\nDisasm around key+salt cluster @ 0x{start:x}")
        for p_vaddr, p_offset, p_filesz, _, _ in segs:
            if p_vaddr <= start < p_vaddr + p_filesz:
                off = p_offset + (start - p_vaddr)
                code = data[off : off + 0x300]
                for insn in md.disasm(code, start):
                    print(f"0x{insn.address:x}:\t{insn.mnemonic}\t{insn.op_str}")
                break


if __name__ == "__main__":
    main()
