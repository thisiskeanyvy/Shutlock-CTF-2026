#!/usr/bin/env python3
"""pretexte_instrument: dump stack JIT (sp+0x58) after 6c8 to stderr."""
from pathlib import Path

SRC = Path(__file__).parent / "pretexte"
OUT = Path(__file__).parent / "pretexte_instrument"
TEXT_VMA = 0x598
TEXT_OFF = 1432
NOP = b"\x1f\x20\x03\xd5"
PATCH_VMA = 0x88C  # after bl 6c8 returns
CAVE_VMA = 0x2760


def off(vma: int) -> int:
    return TEXT_OFF + (vma - TEXT_VMA)


def enc_bl(off_from_insn: int) -> bytes:
    imm26 = (off_from_insn >> 2) & 0x3FFFFFF
    return (0x94000000 | imm26).to_bytes(4, "little")


def build_cave() -> bytes:
    # write(2, sp+0x58, 0x200)
    insns = [
        0xA9BF7BFD,  # stp x29,x30,[sp,#-16]!
        0x910163E1,  # add x1, sp, #0x58
        0xD2800040,  # mov x0, #2
        0x52804002,  # mov w2, #0x200
        0xD2800200,  # mov x16, #1 -> wait syscall write is 0x2000004 on mac? 
    ]
    # macOS arm64 write = 4 = 0x2000004 in some docs, but binary uses mov w16,#4; svc
    insns = [
        0xA9BF7BFD,
        0x910163E1,  # add x1, sp, #0x58
        0xD2800040,  # mov x0, #2  stderr
        0x52804002,  # mov w2, #0x200
        0x52800810,  # mov w16, #4
        0xD4001001,  # svc #0x80
        0xA8C17BFD,  # ldp x29,x30,[sp],#16
        0xD65F03C0,  # ret
    ]
    return b"".join(i.to_bytes(4, "little") for i in insns)


def main():
    data = bytearray(SRC.read_bytes())
    data[off(0x5EC) : off(0x5EC) + 4] = NOP
    for vma in (0x6B4, 0x764, 0x95C, 0x10D0):
        data[off(vma) : off(vma) + 4] = NOP

    cave = build_cave()
    data[off(CAVE_VMA) : off(CAVE_VMA) + len(cave)] = cave

    patch_off = off(PATCH_VMA)
    orig = bytes(data[patch_off : patch_off + 8])
    data[patch_off : patch_off + 4] = enc_bl(CAVE_VMA - (PATCH_VMA + 4))
    # keep original ldr x1,[sp,#0x40] at +4
    print("patched", OUT, "orig after bl:", orig[4:8].hex())
    OUT.write_bytes(data)
    OUT.chmod(0o755)


if __name__ == "__main__":
    main()
