#!/usr/bin/env python3
"""Emulate 6c8 via Unicorn with full Mach-O segments -> compare JIT."""
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM, UC_HOOK_CODE
from unicorn.arm64_const import (
    UC_ARM64_REG_X0,
    UC_ARM64_REG_X1,
    UC_ARM64_REG_X2,
    UC_ARM64_REG_X3,
    UC_ARM64_REG_X4,
    UC_ARM64_REG_SP,
    UC_ARM64_REG_LR,
)

BIN = Path(__file__).parent / "pretexte"
BASE = 0x100000000
STOP = 0xDEAD0000


def load_segments(mu: Uc, data: bytes) -> None:
    mu.mem_map(BASE, 0x4000)  # TEXT + cstring
    mu.mem_map(BASE + 0x4000, 0x4000)  # DATA_CONST got
    mu.mem_map(BASE + 0x8000, 0x4000)  # DATA
    mu.mem_write(BASE, data[:0x4000])
    mu.mem_write(BASE + 0x4000, data[0x4000:0x8000])
    mu.mem_write(BASE + 0x8000, data[0x8000:0xC000] if len(data) > 0x8000 else b"\x00" * 0x4000)
    blob = data[0x237C : 0x237C + 0x110] + b"\x00" * (0x200 - 0x110)
    mu.mem_write(BASE + 0x8000, blob)


def build_jit_native() -> bytes:
    data = BIN.read_bytes()
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(0x20000000, 0x200000)
    load_segments(mu, data)

    sp = 0x20100000
    jit_out = sp + 0x58
    mu.reg_write(UC_ARM64_REG_SP, sp + 0x500)
    mu.reg_write(UC_ARM64_REG_X0, BASE + 0x8000)
    mu.reg_write(UC_ARM64_REG_X1, 0x200)
    mu.reg_write(UC_ARM64_REG_X2, BASE + 0x778)
    mu.reg_write(UC_ARM64_REG_X3, BASE + 0x788)
    mu.reg_write(UC_ARM64_REG_X4, jit_out)
    mu.reg_write(UC_ARM64_REG_LR, STOP)

    stubs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}

    def hook(mu_, addr, size, user_data):
        if addr == STOP:
            mu_.emu_stop()
            return
        if addr in stubs:
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(UC_ARM64_REG_X2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    mu.hook_add(UC_HOOK_CODE, hook, None)
    try:
        mu.emu_start(BASE + 0x6C8, STOP, count=20_000_000)
    except Exception as e:
        raise RuntimeError(f"emu failed: {e}") from e
    return bytes(mu.mem_read(jit_out, 0x200))


if __name__ == "__main__":
    import importlib.util

    nat = build_jit_native()
    Path("/tmp/jit_native.bin").write_bytes(nat)
    spec = importlib.util.spec_from_file_location("ps", Path(__file__).parent / "pretexte_solve.py")
    ps = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(ps)
    py = ps.build_jit()
    print("match", nat == py)
    if nat != py:
        for i in range(0, 0x200, 16):
            if nat[i : i + 16] != py[i : i + 16]:
                print(f"diff @{i:03x} nat={nat[i:i+16].hex()} py={py[i:i+16].hex()}")
    print("head nat", nat[:32].hex())
    print("head py ", py[:32].hex())
