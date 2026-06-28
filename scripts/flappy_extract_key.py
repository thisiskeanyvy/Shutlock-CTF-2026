#!/usr/bin/env python3
"""Extract FlappyBug XOR key from IL2CPP metadata v39."""
import struct
import sys
from pathlib import Path

META = Path(__file__).parent / "Flappy_bug/flappy_bug_Data/il2cpp_data/Metadata/global-metadata.dat"
FLAG = Path(__file__).parent / "Flappy_bug/flappy_bug_Data/StreamingAssets/flag.dat"


class Reader:
    def __init__(self, data: bytes):
        self.data = data
        self.pos = 0

    def u32(self) -> int:
        v = struct.unpack_from("<I", self.data, self.pos)[0]
        self.pos += 4
        return v

    def u16(self) -> int:
        v = struct.unpack_from("<H", self.data, self.pos)[0]
        self.pos += 2
        return v

    def i32(self) -> int:
        v = struct.unpack_from("<i", self.data, self.pos)[0]
        self.pos += 4
        return v

    def read(self, n: int) -> bytes:
        v = self.data[self.pos : self.pos + n]
        self.pos += n
        return v

    def seek(self, pos: int):
        self.pos = pos


def idx_size(count: int) -> int:
    if count <= 0xFF:
        return 1
    if count <= 0xFFFF:
        return 2
    return 4


def read_idx(r: Reader, size: int) -> int:
    if size == 1:
        return r.read(1)[0]
    if size == 2:
        return struct.unpack("<H", r.read(2))[0]
    return r.i32()


def read_section(r: Reader):
    return {"offset": r.u32(), "size": r.u32(), "count": r.u32()}


def read_string(data: bytes, strings_off: int, index: int) -> str:
    pos = strings_off + index
    end = data.index(b"\x00", pos)
    return data[pos:end].decode("utf-8", "replace")


def main():
    data = META.read_bytes()
    r = Reader(data)
    assert r.read(4) == b"\xaf\x1b\xb1\xfa"
    version = r.u32()
    print("metadata version", version)
    header = {}
    for name in [
        "stringLiterals",
        "stringLiteralData",
        "strings",
        "events",
        "properties",
        "methods",
        "parameterDefaultValues",
        "fieldDefaultValues",
        "fieldAndParameterDefaultValueData",
        "fieldMarshaledSizes",
        "parameters",
        "fields",
        "genericParameters",
        "genericParameterConstraints",
        "genericContainers",
        "nestedTypes",
        "interfaces",
        "vtableMethods",
        "interfaceOffsets",
        "typeDefinitions",
    ]:
        header[name] = read_section(r)
    header["images"] = read_section(r)
    header["assemblies"] = read_section(r)
    header["fieldRefs"] = read_section(r)
    header["referencedAssemblies"] = read_section(r)
    header["attributeData"] = read_section(r)
    header["attributeDataRanges"] = read_section(r)

    type_def_idx_size = idx_size(header["typeDefinitions"]["count"])
    type_idx_size = 4
    if header["interfaceOffsets"]["count"]:
        actual = header["interfaceOffsets"]["size"] // max(header["interfaceOffsets"]["count"], 1)
        type_idx_size = {8: 4, 6: 2, 5: 1}.get(actual, 4)
    param_idx_size = idx_size(header["parameters"]["count"]) if version >= 39 else 4
    field_idx_size = 4
    default_data_idx_size = 4
    generic_container_idx_size = idx_size(header["genericContainers"]["count"])
    method_idx_size = 4
    event_idx_size = property_idx_size = nested_idx_size = interfaces_idx_size = 4

    # type defs (Il2CppTypeDefinition v38+)
    r.seek(header["typeDefinitions"]["offset"])
    type_defs = []
    for _ in range(header["typeDefinitions"]["count"]):
        name_index = r.u32()
        namespace_index = r.u32()
        byval_idx = read_idx(r, type_idx_size)
        declaring_type_idx = read_idx(r, type_idx_size)
        parent_idx = read_idx(r, type_idx_size)
        generic_container_idx = read_idx(r, generic_container_idx_size)
        flags = r.u32()
        field_start = read_idx(r, field_idx_size)
        method_start = read_idx(r, method_idx_size)
        event_start = read_idx(r, event_idx_size)
        property_start = read_idx(r, property_idx_size)
        nested_start = read_idx(r, nested_idx_size)
        interfaces_start = read_idx(r, interfaces_idx_size)
        vtable_start = r.i32()
        interface_offsets_start = read_idx(r, interfaces_idx_size)
        method_count = r.u16()
        property_count = r.u16()
        field_count = r.u16()
        event_count = r.u16()
        nested_type_count = r.u16()
        vtable_count = r.u16()
        interfaces_count = r.u16()
        interface_offsets_count = r.u16()
        bitfield = r.u32()
        token = r.u32()
        type_defs.append(
            {
                "name_index": name_index,
                "field_start": field_start,
                "field_count": field_count,
            }
        )

    # field defs
    r.seek(header["fields"]["offset"])
    field_defs = []
    for _ in range(header["fields"]["count"]):
        name_index = r.u32()
        type_index = read_idx(r, type_idx_size)
        token = r.u32()
        field_defs.append({"name_index": name_index, "type_index": type_index})

    # field default values
    r.seek(header["fieldDefaultValues"]["offset"])
    fdv_by_field = {}
    for _ in range(header["fieldDefaultValues"]["count"]):
        field_index = read_idx(r, field_idx_size)
        type_index = read_idx(r, type_idx_size)
        data_index = read_idx(r, default_data_idx_size)
        fdv_by_field[field_index] = {"type_index": type_index, "data_index": data_index}

    strings_off = header["strings"]["offset"]
    default_data_off = header["fieldAndParameterDefaultValueData"]["offset"]

    t = type_defs[8879]
    print(f"Type 8879 fields {t['field_start']}..{t['field_start']+t['field_count']-1}")
    cipher = FLAG.read_bytes()
    for fi in range(t["field_start"], t["field_start"] + t["field_count"]):
        fname = read_string(data, strings_off, field_defs[fi]["name_index"])
        print(f"  field[{fi}] {fname[:64]}...")
        if fi not in fdv_by_field:
            continue
        di = fdv_by_field[fi]["data_index"]
        ptr = default_data_off + di
        n = 110 if "BCD26" in fname else 188 if "DF73" in fname else 4
        blob = data[ptr : ptr + n]
        print(f"    dataIndex={di} ptr=0x{ptr:x} head={blob[:16].hex()}")
        if "BCD26" in fname:
            key = blob[:4]
            dec = bytes(cipher[i] ^ key[i % 4] for i in range(len(cipher)))
            print(f"    XOR key={key.hex()}")
            print(f"    dec head={dec[:120]}")
            p = dec.find(b"SHLK{")
            if p >= 0:
                e = dec.find(b"}", p)
                print(f"    FLAG={dec[p:e+1].decode()}")


if __name__ == "__main__":
    main()
