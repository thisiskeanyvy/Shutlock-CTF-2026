#!/usr/bin/env python3
"""Minimal Go pclntab parser for jq trojan (Go 1.25, amd64)."""
import struct
import sys

BIN = "/tmp/jq-malicious"


def u32(data, off):
    return struct.unpack_from("<I", data, off)[0]


def u64(data, off):
    return struct.unpack_from("<Q", data, off)[0]


def parse_pclntab(data: bytes):
    magic = u32(data, 0)
    if magic != 0xFFFFFFFB:
        raise ValueError(f"bad magic {magic:#x}")
    pad = u64(data, 4)
    first = u64(data, 12)
    last = u64(data, 20)
    ftablen = u64(data, 28)
    ptablen = u64(data, 36)
    pcquantum = u8(data, 44) if False else data[44]
    ptrsize = data[45]
    print(f"pcquantum={pcquantum} ptrsize={ptrsize}")
    print(f"text range {first:#x}-{last:#x} ftablen={ftablen} ptablen={ptablen}")
    ftab_off = 48
    ftab = []
    for i in range(ftablen):
        off = ftab_off + i * 8
        ftab.append(u64(data, off))
    # funcnametab starts after ftab + pctab
    pctab_off = ftab_off + ftablen * 8
    pctab = data[pctab_off : pctab_off + ptablen]
    nfunc = ftablen
    func_off = pctab_off + ptablen
    funcs = []
    for i in range(nfunc - 1):
        entry_off = func_off + i * 4 * ptrsize
        if ptrsize == 8:
            entry = u64(data, entry_off)
            name_off = u32(data, entry_off + 8)
            args = u32(data, entry_off + 12)
            defer = u32(data, entry_off + 16)
            pcsp = u32(data, entry_off + 20)
            pcfile = u32(data, entry_off + 24)
            pcln = u32(data, entry_off + 28)
            npcdata = u32(data, entry_off + 32)
            cu_off = u32(data, entry_off + 36)
            func_id = u32(data, entry_off + 40)
            frame = u32(data, entry_off + 44)
            flags = u32(data, entry_off + 48)
        else:
            continue
        funcs.append((entry, name_off, i))
    return funcs, ftab, data


def read_name(blob, name_off):
    end = blob.find(b"\x00", name_off)
    return blob[name_off:end].decode("latin1", "replace")


def main():
    raw = open(BIN, "rb").read()
    idx = raw.find(b"\xfb\xff\xff\xff")
    print("pclntab candidate @", idx)
    tab = raw[idx:]
    try:
        funcs, ftab, blob = parse_pclntab(tab)
    except Exception as e:
        print("parse fail", e)
        return
    # funcnametab is separate in newer Go - search names directly
    names = {}
    pos = 0
    while True:
        pos = raw.find(b"main.", pos)
        if pos < 0:
            break
        end = raw.find(b"\x00", pos)
        names[pos] = raw[pos:end].decode()
        pos = end + 1
    print("main symbols:", sorted(set(names.values())))


if __name__ == "__main__":
    main()
