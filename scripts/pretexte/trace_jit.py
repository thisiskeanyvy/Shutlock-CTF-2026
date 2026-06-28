#!/usr/bin/env python3
"""Trace JIT execution: log reads from password buffer."""
import sys
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn import UC_HOOK_CODE, UC_HOOK_MEM_READ
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
PW_ADDR = 0x300000000
STOP = 0xDEAD0000


def main():
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
    pw = (sys.argv[1] if len(sys.argv) > 1 else "test").encode() + b"\x00"
    mu.mem_write(PW_ADDR, pw)
    sp = 0x300080000
    mu.reg_write(UC_ARM64_REG_SP, sp)
    mu.reg_write(UC_ARM64_REG_X29, sp - 0x40)  # caller frame like main()
    mu.reg_write(UC_ARM64_REG_X0, PW_ADDR)
    mu.reg_write(UC_ARM64_REG_LR, STOP)
    stubs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}
    printed = []
    steps = 0

    def code(mu_, addr, size, _):
        nonlocal steps
        steps += 1
        if addr == STOP:
            mu_.emu_stop()
        if addr in stubs:
            if addr == BASE + 0x2360:
                x0 = mu_.reg_read(UC_ARM64_REG_X0)
                try:
                    s = bytes(mu_.mem_read(x0, 48)).split(b"\x00")[0]
                    printed.append(s.decode(errors="replace"))
                except Exception:
                    pass
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(UC_ARM64_REG_X2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    def mem(mu_, access, addr, size, value, _):
        if PW_ADDR <= addr < PW_ADDR + len(pw):
            off = addr - PW_ADDR
            print(f"  read pw[{off}] @ pc={hex(mu_.reg_read(UC_ARM64_REG_PC))}")

    mu.hook_add(UC_HOOK_CODE, code)
    mu.hook_add(UC_HOOK_MEM_READ, mem)
    try:
        mu.emu_start(JIT_BASE, STOP, count=200000)
    except Exception as e:
        print("emu err", e)
    print("steps", steps, "x0", hex(mu.reg_read(UC_ARM64_REG_X0)), "printed", printed)


if __name__ == "__main__":
    main()
