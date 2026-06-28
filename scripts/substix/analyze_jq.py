#!/usr/bin/env python3
"""Static analysis helpers for Substix trojan jq Go binary."""
import re
import struct
import sys

BIN = "/tmp/jq-malicious"


def go_buildinfo(path: str):
    data = open(path, "rb").read()
    # Go build info trailer: \xff Go buildinf:
    magic = b"\xff Go buildinf:"
    idx = data.rfind(magic)
    if idx < 0:
        print("no buildinfo magic")
        return
    print("buildinfo @", idx)
    chunk = data[idx : idx + 512]
    strings = re.findall(rb"[\x20-\x7e]{4,120}", chunk)
    for s in strings:
        print(" ", s.decode("latin1", "replace"))


def find_custom_strings(path: str):
    data = open(path, "rb").read()
    interesting = []
    for m in re.finditer(rb"[\x20-\x7e]{6,90}", data):
        s = m.group().decode("latin1", "replace")
        if any(
            x in s
            for x in [
                "main.",
                "/build/",
                "fetch",
                "unauthorized",
                "nixos",
                "substix",
                "83zMUZ",
                "H92t9",
                "derive",
                "SERVICE",
                "update",
                "Authorization",
                "Bearer",
            ]
        ):
            if "runtime" not in s and "crypto/" not in s and "x509:" not in s:
                interesting.append(s)
    for s in sorted(set(interesting)):
        print(s)


def xref_string(path: str, needle: bytes):
    data = open(path, "rb").read()
    idx = 0
    while True:
        idx = data.find(needle, idx)
        if idx < 0:
            break
        print(f"string {needle!r} @ 0x{idx:x}")
        idx += 1


if __name__ == "__main__":
    go_buildinfo(BIN)
    print("\n--- custom strings ---")
    find_custom_strings(BIN)
    print("\n--- xrefs ---")
    for n in [b"main.deriveKey", b"H92t9H9rHt3H", b"83zMUZ", b"nixos-community"]:
        xref_string(BIN, n)
