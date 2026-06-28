#!/usr/bin/env python3
"""Run fn1860 from pretexte via Unicorn."""
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_SP, UC_ARM64_REG_LR, UC_ARM64_REG_PC

BIN = Path(__file__).parent / "pretexte"
TEXT_VMA, TEXT_OFF = 0x598, 1432
BASE = 0x100000000
STOP = 0xDEAD0000


def run1860(buf16: bytearray) -> None:
    data = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(BASE, 0x400000)
    mu.mem_map(0x20000000, 0x100000)
    mu.mem_write(BASE + TEXT_VMA, data[TEXT_OFF : TEXT_OFF + 0x1D74])
    mu.mem_write(BASE + 0x4010, (0).to_bytes(8, "little"))
    mu.mem_write(0x20010000, bytes(buf16))
    mu.reg_write(UC_ARM64_REG_X0, 0x20010000)
    mu.reg_write(UC_ARM64_REG_SP, 0x20080000)
    mu.reg_write(UC_ARM64_REG_LR, STOP)

    stub_addrs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}

    def hook(mu_, addr, size, _):
        if addr == STOP:
            mu_.emu_stop()
            return
        if addr in stub_addrs:
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    mu.hook_add(1, hook)
    mu.emu_start(BASE + 0x1860, STOP, count=500000)
    buf16[:] = mu.mem_read(0x20010000, 16)


if __name__ == "__main__":
    b = bytearray(range(16))
    run1860(b)
    print("in ", list(range(16)))
    print("out", list(b))
