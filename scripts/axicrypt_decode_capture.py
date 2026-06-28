#!/usr/bin/env python3
"""Decode the AXI-Lite transaction trace from AXICrypt's sigrok archive."""

from __future__ import annotations

import sys
import zipfile
from pathlib import Path


SIGNALS = [
    *[f"addr{i}" for i in range(8)],
    *[f"data{i}" for i in range(32)],
    "awvalid",
    "awready",
    "wvalid",
    "wready",
    "bvalid",
    "bready",
    "arvalid",
    "arready",
    "rvalid",
    "rready",
]


def sample_bits(sample: bytes) -> dict[str, int]:
    value = int.from_bytes(sample, "little")
    return {name: (value >> i) & 1 for i, name in enumerate(SIGNALS)}


def bus_value(bits: dict[str, int], prefix: str, width: int) -> int:
    return sum(bits[f"{prefix}{i}"] << i for i in range(width))


def hex_block(words: list[int]) -> str:
    return "".join(word.to_bytes(4, "big").hex() for word in words)


def decode(sr_path: Path) -> None:
    with zipfile.ZipFile(sr_path) as zf:
        logic_name = next(name for name in zf.namelist() if name.endswith("logic-1-1"))
        raw = zf.read(logic_name)

    samples = [sample_bits(raw[i : i + 7]) for i in range(0, len(raw), 7)]
    writes: list[tuple[int, int, int]] = []
    reads: list[tuple[int, int, int]] = []
    pending_write_addr: int | None = None
    pending_read_addr: int | None = None

    prev = {name: 0 for name in SIGNALS}
    for idx, bits in enumerate(samples):
        aw_fire = bits["awvalid"] and bits["awready"] and not (prev["awvalid"] and prev["awready"])
        w_fire = bits["wvalid"] and bits["wready"] and not (prev["wvalid"] and prev["wready"])
        ar_fire = bits["arvalid"] and bits["arready"] and not (prev["arvalid"] and prev["arready"])
        r_fire = bits["rvalid"] and bits["rready"] and not (prev["rvalid"] and prev["rready"])

        if aw_fire:
            pending_write_addr = bus_value(bits, "addr", 8)
        if w_fire:
            data = bus_value(bits, "data", 32)
            if pending_write_addr is None:
                raise RuntimeError(f"write data without address at sample {idx}")
            writes.append((idx, pending_write_addr, data))
            pending_write_addr = None
        if ar_fire:
            pending_read_addr = bus_value(bits, "addr", 8)
        if r_fire:
            data = bus_value(bits, "data", 32)
            if pending_read_addr is None:
                raise RuntimeError(f"read data without address at sample {idx}")
            reads.append((idx, pending_read_addr, data))
            pending_read_addr = None
        prev = bits

    print("WRITES")
    for idx, addr, data in writes:
        print(f"  sample={idx:03d} addr=0x{addr:02x} data=0x{data:08x}")

    print("READS")
    for idx, addr, data in reads:
        print(f"  sample={idx:03d} addr=0x{addr:02x} data=0x{data:08x}")

    reg = {addr: data for _, addr, data in writes}
    out = {addr: data for _, addr, data in reads}
    iv_words = [reg[a] for a in range(0x10, 0x20, 4)]
    plain_words = [reg[a] for a in range(0x20, 0x30, 4)]
    cipher_words = [out[a] for a in range(0x30, 0x40, 4)]

    print(f"IV_BE      {hex_block(iv_words)}")
    print(f"PLAIN_BE   {hex_block(plain_words)}")
    print(f"CIPHER_BE  {hex_block(cipher_words)}")
    print(f"CONTROL    start=0x{reg.get(0x00, 0):08x} status=0x{out.get(0x04, 0):08x}")


def main() -> int:
    if len(sys.argv) != 2:
        print(f"usage: {Path(sys.argv[0]).name} bus_capture.sr", file=sys.stderr)
        return 2
    decode(Path(sys.argv[1]))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
