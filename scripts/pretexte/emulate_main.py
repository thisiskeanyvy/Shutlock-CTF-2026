#!/usr/bin/env python3
"""Emulate pretexte main (argc=2) and dump mmap'd JIT."""
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import (
    UC_ARM64_REG_X0,
    UC_ARM64_REG_X1,
    UC_ARM64_REG_X2,
    UC_ARM64_REG_X8,
    UC_ARM64_REG_SP,
    UC_ARM64_REG_LR,
    UC_ARM64_REG_PC,
)

BIN = Path(__file__).parent / "pretexte"
BASE = 0x100000000
STOP = 0xDEAD0000
MMAP_BASE = 0x0000000105000000


def emulate_main(password: str) -> tuple[bytes, list[bytes]]:
    data = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(BASE, 0x4000)
    mu.mem_map(BASE + 0x4000, 0x4000)
    mu.mem_map(BASE + 0x8000, 0x4000)
    mu.mem_map(0x20000000, 0x400000)
    mu.mem_map(MMAP_BASE, 0x10000)
    mu.mem_write(BASE, data[:0x4000])
    mu.mem_write(BASE + 0x4000, data[0x4000:0x8000])
    blob = data[0x237C : 0x237C + 0x110] + b"\x00" * (0x200 - 0x110)
    mu.mem_write(BASE + 0x8000, blob)
    guard = 0x201F0000
    mu.mem_write(guard, (0xDEADBEEF).to_bytes(8, "little"))
    mu.mem_write(BASE + 0x4010, guard.to_bytes(8, "little"))

    pw = password.encode() + b"\x00"
    pw_addr = 0x20010000
    mu.mem_write(pw_addr, pw)
    argv0 = 0x20010080
    mu.mem_write(argv0, b"pretexte\x00")
    argv = 0x20010100
    mu.mem_write(argv, pw_addr.to_bytes(8, "little"))
    mu.mem_write(argv + 8, (0).to_bytes(8, "little"))

    sp = 0x20100000
    mu.reg_write(UC_ARM64_REG_SP, sp + 0x500)
    mu.reg_write(UC_ARM64_REG_X0, 2)
    mu.reg_write(UC_ARM64_REG_X1, argv)
    mu.reg_write(UC_ARM64_REG_LR, STOP)

    stubs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}
    printed: list[bytes] = []
    mmap_addr = MMAP_BASE
  # patch mmap return: after bl 0x233c at 0x8a4, force x0=mmap_addr
    mmap_ret = BASE + 0x8A8

    def hook(mu_, addr, size, user_data):
        if addr == STOP:
            mu_.emu_stop()
            return
        if addr == mmap_ret:
            mu_.reg_write(UC_ARM64_REG_X0, mmap_addr)
        if addr == BASE + 0x920:  # blr jit - dump
            jit_ptr = mu_.reg_read(UC_ARM64_REG_X8)
            printed.append(b"JIT@" + hex(jit_ptr).encode())
            printed.append(bytes(mu_.mem_read(jit_ptr, 0x40)))
        if addr in stubs:
            if addr == BASE + 0x2360:
                x0 = mu_.reg_read(UC_ARM64_REG_X0)
                try:
                    printed.append(bytes(mu_.mem_read(x0, 64)).split(b"\x00")[0])
                except Exception:
                    pass
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(UC_ARM64_REG_X2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            if addr == BASE + 0x2348:  # mprotect - return 0
                mu_.reg_write(UC_ARM64_REG_X0, 0)
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    mu.hook_add(UC_HOOK_CODE, hook, None)
    try:
        mu.emu_start(BASE + 0x848, STOP, count=30_000_000)
    except Exception as e:
        printed.append(f"ERR:{e}@pc{mu.reg_read(UC_ARM64_REG_PC):#x}".encode())
    jit = bytes(mu.mem_read(mmap_addr, 0x200))
    return jit, printed


if __name__ == "__main__":
    pw = "c0n5TrucTor-oVer_h3RriNg"
    jit, out = emulate_main(pw)
    Path("/tmp/jit_mmap.bin").write_bytes(jit)
    print("jit head", jit[:32].hex())
    for o in out:
        print("out", o)
