#!/usr/bin/env python3
"""Reproduce jq trojan deriveKey (XOR) and build flag candidates."""
import hashlib
import struct

BIN = "/tmp/jq-malicious"
IMAGE = 0x400000


def read_at(d, ptr, n):
    fo = ptr - IMAGE
    if fo < 0:
        if ptr >= 0x678000:
            fo = 0x278000 + (ptr - 0x678000)
        elif ptr >= 0x91F000:
            fo = 0x51F000 + (ptr - 0x91F000)
    return d[fo : fo + n]


def read_slice(d, next_rip, disp):
    addr = next_rip + disp
    fo = addr - IMAGE
    ptr, length, _cap = struct.unpack_from("<QQQ", d, fo)
    return read_at(d, ptr, length)


def derive_key(path=BIN):
    d = open(path, "rb").read()
    b1 = read_slice(d, 0x620DAE, 0x33B702)
    b2 = read_slice(d, 0x620DC5, 0x33B70B)
    return bytes(a ^ b for a, b in zip(b1, b2))


def flag_md5(package, key, c2):
    h = hashlib.md5(f"{package}:{key}:{c2}".encode()).hexdigest()
    return f"SHLK{{{h}}}"


if __name__ == "__main__":
    key = derive_key().split(b"\x00")[0].decode()
    print("derived key:", key)
    c2 = "https://nixos-community.me/update"
    for pkg in ("jq", "jq-1.7.1", "jq-1.7.1-bin", "0q85yfxd70aq8iv4n43hqcmh2dbyb80z-jq-1.7.1-bin"):
        print(flag_md5(pkg, key, c2))
