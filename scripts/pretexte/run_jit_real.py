#!/usr/bin/env python3
"""Execute JIT like pretexte: map binary at BASE, JIT at mmap addr."""
import struct
import sys
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import (
    UC_ARM64_REG_X0,
    UC_ARM64_REG_X1,
    UC_ARM64_REG_X2,
    UC_ARM64_REG_SP,
    UC_ARM64_REG_LR,
    UC_ARM64_REG_PC,
    UC_ARM64_REG_X29,
)

BIN = Path(__file__).parent / "pretexte"
BASE = 0x100000000
JIT_BASE = 0x200000000
STOP = 0xDEAD0000


def run_jit_real(jit: bytes, password: str) -> tuple[int, list[str]]:
    data = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(BASE, 0x10000)
    mu.mem_map(JIT_BASE, 0x10000)
    mu.mem_map(0x300000000, 0x100000)

    mu.mem_write(BASE, data[:16384])
    mu.mem_write(BASE + 0x4000, data[16384:32768])
    mu.mem_write(BASE + 0x8000, data[32768:49152])
    mu.mem_write(JIT_BASE, jit[:0x200])

    pw = password.encode() + b"\x00"
    pw_addr = 0x300000000
    mu.mem_write(pw_addr, pw)

    sp = 0x300080000
    mu.reg_write(UC_ARM64_REG_SP, sp)
    mu.reg_write(UC_ARM64_REG_X29, sp)
    mu.reg_write(UC_ARM64_REG_X0, pw_addr)
    mu.reg_write(UC_ARM64_REG_LR, STOP)

    stubs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}
    printed: list[str] = []

    def hook(mu_, addr, size, _):
        if addr == STOP:
            mu_.emu_stop()
            return
        if addr in stubs:
            if addr == BASE + 0x2360:  # printf
                x0 = mu_.reg_read(UC_ARM64_REG_X0)
                try:
                    s = bytes(mu_.mem_read(x0, 64)).split(b"\x00")[0]
                    printed.append(s.decode(errors="replace"))
                except Exception:
                    pass
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(UC_ARM64_REG_X2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    mu.hook_add(1, hook)
    try:
        mu.emu_start(JIT_BASE, STOP, count=50000)
    except Exception:
        pass
    return mu.reg_read(UC_ARM64_REG_X0) & 0xFFFFFFFF, printed


if __name__ == "__main__":
    sys.path.insert(0, str(Path(__file__).parent))
    from pretexte_solve import build_jit

    jit = build_jit()
    for pw in sys.argv[1:] or ["test", "deadbeef"]:
        rv, out = run_jit_real(jit, pw)
        print(pw, hex(rv), out)
