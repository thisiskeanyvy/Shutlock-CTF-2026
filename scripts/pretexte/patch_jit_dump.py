#!/usr/bin/env python3
"""Patch pretexte to write JIT to /tmp/jit_real.bin before mprotect (syscall write)."""
from pathlib import Path

BIN = Path(__file__).parent / "pretexte"
OUT = Path(__file__).parent / "pretexte_jitout"
# File offset of VMA 0x1000008dc (after memcpy to mmap, x0=mmap addr in [sp+0x20])
PATCH_VMA = 0x8DC
TEXT_VMA = 0x598
TEXT_OFF = 1432
CAVE_VMA = 0x2750


def vma_to_off(vma: int) -> int:
    return TEXT_OFF + (vma - TEXT_VMA)


def enc_movz(rd: int, imm16: int) -> bytes:
    return (0xD2800000 | ((imm16 & 0xFFFF) << 5) | (rd & 0x1F)).to_bytes(4, "little")


def enc_movk(rd: int, imm16: int, shift: int) -> bytes:
    hw = (shift // 16) & 3
    return (0xF2800000 | (hw << 21) | ((imm16 & 0xFFFF) << 5) | (rd & 0x1F)).to_bytes(4, "little")


def enc_bl(off_from_insn: int) -> bytes:
    imm26 = (off_from_insn >> 2) & 0x3FFFFFF
    return (0x94000000 | imm26).to_bytes(4, "little")


def build_cave() -> bytes:
  # x20 = mmap JIT addr (saved from x0)
  # write(2, x20, 0x200)  fd=2 stderr
    insns = []
    insns.append((0xA9BF7BFD).to_bytes(4, "little"))  # stp x29,x30,[sp,#-16]!
    insns.append(enc_movz(16, 4))  # write syscall
    insns.append(enc_movz(0, 2))  # fd stderr
    insns.append((0xAA1403E1).to_bytes(4, "little"))  # mov x1, x20
    insns.append(enc_movz(2, 0x200))
    insns.append((0xD4001001).to_bytes(4, "little"))  # svc #0x80
    insns.append((0xA8C17BFD).to_bytes(4, "little"))  # ldp x29,x30,[sp],#16
    insns.append((0xD65F03C0).to_bytes(4, "little"))  # ret
    return b"".join(insns)


def main():
    data = bytearray(BIN.read_bytes())
    cave = build_cave()
    cave_off = vma_to_off(CAVE_VMA)
    data[cave_off : cave_off + len(cave)] = cave

    patch_off = vma_to_off(PATCH_VMA)
    # ldr x20, [sp, #0x20]  ; mmap addr
    data[patch_off : patch_off + 4] = (0xF9400A94).to_bytes(4, "little")
    bl_off = CAVE_VMA - (PATCH_VMA + 4)
    data[patch_off + 4 : patch_off + 8] = enc_bl(bl_off)
    # original: ldr x1, [sp, #0x40] at 0x8e0 - keep next insn
    OUT.write_bytes(data)
    OUT.chmod(0o755)
    print("wrote", OUT)


if __name__ == "__main__":
    main()
