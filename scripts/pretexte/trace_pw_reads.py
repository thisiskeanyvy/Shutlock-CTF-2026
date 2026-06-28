#!/usr/bin/env python3
"""Trace password buffer reads during JIT execution (Unicorn)."""
import sys
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE, UC_HOOK_MEM_READ_UNMAPPED, UC_HOOK_MEM_READ
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
PW = 0x300000000
STOP = 0xDEAD0000


def trace(password: str) -> None:
    sys.path.insert(0, str(Path(__file__).parent))
    from pretexte_solve import build_jit

    jit = build_jit()
    data = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(BASE, 0x10000)
    mu.mem_map(JIT_BASE, 0x10000)
    mu.mem_map(0x300000000, 0x100000)
    mu.mem_write(BASE, data[:16384])
    mu.mem_write(BASE + 0x4000, data[16384:32768])
    mu.mem_write(JIT_BASE, jit)
    pw_b = password.encode() + b"\x00"
    mu.mem_write(PW, pw_b)
    sp = 0x300080000
    mu.reg_write(UC_ARM64_REG_SP, sp)
    mu.reg_write(UC_ARM64_REG_X29, sp - 0x50)
    mu.reg_write(UC_ARM64_REG_X0, PW)
    mu.reg_write(UC_ARM64_REG_LR, STOP)
    stubs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}
    printed = []

    def code(mu_, addr, size, _):
        if addr == STOP:
            mu_.emu_stop()
            return
        if addr in stubs:
            if addr == BASE + 0x2360:
                x0 = mu_.reg_read(UC_ARM64_REG_X0)
                try:
                    printed.append(bytes(mu_.mem_read(x0, 48)).split(b"\x00")[0])
                except Exception:
                    pass
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(UC_ARM64_REG_X2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    def mem_read(mu_, access, addr, size, value, _):
        if PW <= addr < PW + len(pw_b):
            off = addr - PW
            pc = mu_.reg_read(UC_ARM64_REG_PC)
            print(f"  read pw[{off}] size={size} @pc={pc:#x}")

    mu.hook_add(UC_HOOK_CODE, code)
    mu.hook_add(UC_HOOK_MEM_READ, mem_read)
    try:
        mu.emu_start(JIT_BASE, STOP, count=200000)
    except Exception as e:
        print("emu end:", e, "pc", hex(mu.reg_read(UC_ARM64_REG_PC)))
    print("printed:", printed)


if __name__ == "__main__":
    trace(sys.argv[1] if len(sys.argv) > 1 else "test")
