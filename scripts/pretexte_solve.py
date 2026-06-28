#!/usr/bin/env python3
"""Emulate pretexte JIT builder + password check via Unicorn."""
import struct
import sys
from pathlib import Path

from unicorn import Uc, UC_ARCH_ARM64, UC_MODE_ARM
from unicorn.arm64_const import UC_ARM64_REG_X0, UC_ARM64_REG_SP, UC_ARM64_REG_LR

BIN = Path(__file__).parent / "pretexte"
TEXT_VMA, TEXT_OFF = 0x598, 1432
BASE = 0x100000000
STOP = 0xDEAD0000


def load_tables():
    data = BIN.read_bytes()
    sbox = data[0x248C : 0x248C + 256]
    sbox2 = data[0x2597 : 0x2597 + 256]
    xor_tab = data[0x258C : 0x258C + 11]
    context = bytearray(data[0x237C : 0x237C + 0x110])
    context.extend(b"\x00" * (0x200 - len(context)))
    template = data[TEXT_OFF + (0x778 - TEXT_VMA) : TEXT_OFF + (0x778 - TEXT_VMA) + 0x200]
    chunk16 = template[0x10:0x20]
    return sbox, sbox2, xor_tab, context, template, chunk16


def fn1698(b: int) -> int:
    b &= 0xFF
    return (((b >> 7) & 1) * 0x1B ^ ((b << 1) & 0xFF)) & 0xFF


def fn124c(dst: bytearray, key: int, table: bytes) -> None:
    for i in range(4):
        for j in range(4):
            idx = (key << 4) + (i << 2) + j
            if idx < len(table):
                dst[i * 4 + j] ^= table[idx]


def fn9a0(dst: bytearray, src: bytes, sbox: bytes, xor_tab: bytes) -> None:
    for i in range(4):
        for j in range(4):
            dst[i * 4 + j] = src[i * 4 + j]
    for i in range(4, 0x2C):
        b = [dst[(i - 1) * 4 + k] for k in range(4)]
        if i % 4 == 0:
            b = [b[1], b[2], b[3], b[0]]
            b = [sbox[x] for x in b]
            b[0] ^= xor_tab[i // 4]
        rd, rs = (i - 4) * 4, i * 4
        for k in range(4):
            dst[rs + k] = dst[rd + k] ^ b[k]


def fn16c8(buf: bytearray) -> None:
    t = buf[13]
    buf[13], buf[9], buf[5], buf[1] = buf[9], buf[5], buf[1], t
    buf[2], buf[10] = buf[10], buf[2]
    buf[6], buf[14] = buf[14], buf[6]
    t = buf[3]
    buf[3], buf[7], buf[11], buf[15] = buf[7], buf[11], buf[15], t


def fn17b8(buf: bytearray, sbox2: bytes) -> None:
    for i in range(16):
        buf[i] = sbox2[buf[i]]


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
    stubs = {BASE + a for a in (0x230C, 0x2318, 0x2324, 0x2330, 0x2348, 0x2354, 0x2360, 0x236C)}

    def hook(mu_, addr, size, _):
        if addr == STOP:
            mu_.emu_stop()
            return
        if addr in stubs:
            if addr in (BASE + 0x230C, BASE + 0x2330):
                dst = mu_.reg_read(UC_ARM64_REG_X0)
                src = mu_.reg_read(UC_ARM64_REG_X1)
                ln = min(mu_.reg_read(2), 0x10000)
                mu_.mem_write(dst, bytes(mu_.mem_read(src, ln)))
            mu_.reg_write(UC_ARM64_REG_PC, mu_.reg_read(UC_ARM64_REG_LR))

    mu.hook_add(1, hook)
    mu.emu_start(BASE + 0x1860, STOP, count=500000)
    buf16[:] = mu.mem_read(0x20010000, 16)


def fn124c_dual(main: bytearray, main_pos: int, ref: bytes, key: int) -> None:
    for i in range(4):
        for j in range(4):
            idx = (key << 4) + (i << 2) + j
            if idx < len(ref):
                main[main_pos + i * 4 + j] ^= ref[idx]


def fn124c_region(jit: bytearray, pos: int, key: int) -> None:
    fn124c_dual(jit, pos, jit, key)


def fn16c8_region(jit: bytearray, pos: int) -> None:
    b = pos
    t = jit[b + 13]
    jit[b + 13], jit[b + 9], jit[b + 5], jit[b + 1] = jit[b + 9], jit[b + 5], jit[b + 1], t
    jit[b + 2], jit[b + 10] = jit[b + 10], jit[b + 2]
    jit[b + 6], jit[b + 14] = jit[b + 14], jit[b + 6]
    t = jit[b + 3]
    jit[b + 3], jit[b + 7], jit[b + 11], jit[b + 15] = jit[b + 7], jit[b + 11], jit[b + 15], t


def fn17b8_region(jit: bytearray, pos: int, sbox2: bytes) -> None:
    for i in range(4):
        for j in range(4):
            p = pos + i * 4 + j
            jit[p] = sbox2[jit[p]]


def e70_inplace(jit: bytearray, pos: int) -> None:
    e70_dual(jit, pos, jit)


def e70_dual(main: bytearray, main_pos: int, ref: bytes) -> None:
    _, sbox2, _, _, _, _ = load_tables()
    fn124c_dual(main, main_pos, ref, 10)
    for counter in range(9, -1, -1):
        fn16c8_region(main, main_pos)
        fn17b8_region(main, main_pos, sbox2)
        fn124c_dual(main, main_pos, ref, counter)
        if counter:
            tmp = bytearray(main[main_pos : main_pos + 16])
            run1860(tmp)
            main[main_pos : main_pos + 16] = tmp


def fa4_region(jit: bytearray, pos: int, key_pos: int) -> None:
    fa4_dual(jit, pos, jit, key_pos)


def fa4_dual(main: bytearray, main_pos: int, ref: bytes, key_pos: int) -> None:
    for i in range(16):
        main[main_pos + i] ^= ref[key_pos + i]


def fn1008(main: bytearray, ref: bytearray, length: int) -> None:
    pos = 0
    while pos < length:
        saved = bytearray(main[pos : pos + 16])
        e70_dual(main, pos, ref)
        fa4_dual(main, pos, ref, 0xB0)
        ref[0xB0:0xC0] = saved
        pos += 16


def fn1008_single(jit: bytearray, length: int) -> None:
    pos = 0
    while pos < length:
        saved = bytearray(jit[pos : pos + 16])
        e70_inplace(jit, pos)
        fa4_region(jit, pos, 0xB0)
        jit[0xB0:0xC0] = saved
        pos += 16


def build_jit() -> bytes:
    sbox, sbox2, xor_tab, context, template, chunk16 = load_tables()
    main = bytearray(context)
    ref = bytearray(context)
    fn9a0(ref, template, sbox, xor_tab)
    ref[0xB0:0xC0] = chunk16
    fn1008(main, ref, 0x200)
    return bytes(main)


def mov_imm(ins: int):
    if (ins & 0xFF800000) == 0x52800000:
        return (ins >> 5) & 0xFFFF
    if (ins & 0xFF800000) == 0x12800000:
        return (~((ins >> 5) & 0xFFFF)) & 0xFFFF
    return None


def run_jit(jit: bytes, password: str) -> tuple[int, str]:
    """Returns (return_value, output_hint)."""
    mu = Uc(UC_ARCH_ARM64, UC_MODE_ARM)
    mu.mem_map(0x10000, 0x20000)
    mu.mem_map(0x30000, 0x10000)
    mu.mem_map(BASE, 0x100000)
    data = BIN.read_bytes()
    mu.mem_write(BASE + 0x2697, data[TEXT_OFF + (0x2697 - TEXT_VMA) : TEXT_OFF + (0x2697 - TEXT_VMA) + 32])
    mu.mem_write(0x10000, jit[:0x200])
    pw = password.encode() + b"\x00"
    mu.mem_write(0x30000, pw)
    mu.reg_write(UC_ARM64_REG_SP, 0x20000)
    mu.reg_write(UC_ARM64_REG_X0, 0x30000)
    mu.reg_write(UC_ARM64_REG_LR, STOP)
    printed = []

    def hook(mu_, addr, size, _):
        if addr == STOP:
            mu_.emu_stop()
        elif BASE + 0x2360 <= addr < BASE + 0x2364:
            x0 = mu_.reg_read(UC_ARM64_REG_X0)
            try:
                s = bytes(mu_.mem_read(x0, 32)).split(b"\x00")[0]
                printed.append(s.decode(errors="replace"))
            except Exception:
                pass

    mu.hook_add(1, hook)
    try:
        mu.emu_start(0x10000, STOP, count=5000)
    except Exception:
        pass
    return mu.reg_read(UC_ARM64_REG_X0) & 0xFFFFFFFF, "|".join(printed)


def check_password_subprocess(pw: str) -> bool:
    """Ground truth via native binary (~2ms)."""
    import subprocess

    for name in ("pretexte", "pretexte_copy", "pretexte_nodebug"):
        bin_path = BIN.parent / name
        if not bin_path.is_file():
            continue
        try:
            r = subprocess.run(
                [str(bin_path), pw],
                capture_output=True,
                text=True,
                timeout=2,
            )
            if "deadbeef" in (r.stdout + r.stderr):
                return True
        except (subprocess.TimeoutExpired, OSError):
            continue
    return False


def extract_password(jit=None) -> str:
    """Invert embedded check at jit+0xb0 (validated vs native 6c8)."""
    jit = jit or build_jit()

    def rotr8(v: int, n: int) -> int:
        v &= 0xFF
        return ((v >> n) | (v << (8 - n))) & 0xFF

    def inverse(target: int, i: int) -> int:
        w5 = (target + 0x22) & 0xFF
        w5 ^= (i * 7) & 0xFF
        w5 = rotr8(w5, 3)
        w5 = (w5 - 0x13) & 0xFF
        w5 ^= 0x55
        return w5 & 0xFF

    pwd = bytearray()
    for i in range(64):
        e = jit[0xB0 + i]
        if e == 0:
            break
        pwd.append(inverse(e, i))
    return pwd.decode("latin-1")


def check_password_emulated(pw: str, jit=None) -> bool:
    jit = jit or build_jit()
    for i, c in enumerate(pw.encode("latin-1")):
        w5 = c & 0xFF
        w5 ^= 0x55
        w5 = (w5 + 0x13) & 0xFF
        w5 = ((w5 << 3) | (w5 >> 5)) & 0xFF
        w5 ^= (i * 7) & 0xFF
        w5 = (w5 - 0x22) & 0xFF
        if w5 != jit[0xB0 + i]:
            return False
    return jit[0xB0 + len(pw)] == 0


def check_password(pw: str, jit=None) -> bool:
    return check_password_emulated(pw, jit)


def main():
    jit = build_jit()
    pwd = extract_password(jit)
    print("password", pwd)
    print("flag", f"SHLK{{{pwd}}}")
    Path("/tmp/jit_emulated.bin").write_bytes(jit)
    print("jit saved", len(jit), "hex head", jit[:32].hex())
    from capstone import Cs, CS_ARCH_ARM64, CS_MODE_ARM

    for i in Cs(CS_ARCH_ARM64, CS_MODE_ARM).disasm(jit[:0x40], 0):
        print(f"  {i.address:04x} {i.mnemonic} {i.op_str}")

    if len(sys.argv) > 1:
        for pw in sys.argv[1:]:
            rv, out = run_jit(jit, pw)
            print(pw, hex(rv), out, "OK" if check_password(pw, jit) else "fail")
        return

  # brute
    words = set()
    wpath = Path("/usr/share/dict/words")
    if wpath.exists():
        for line in wpath.read_text(errors="ignore").splitlines():
            if 3 <= len(line) <= 24:
                words.add(line)
                words.add(line.lower())
    for w in ["deadbeef", "reverse", "reverseharder", "pretexte", "pretext", "magic", "nemo", "bloat", "harder"]:
        words.add(w)
    for pw in sorted(words):
        if check_password(pw, jit):
            print("FOUND", pw)
            return
    print("not found in wordlist")


if __name__ == "__main__":
    main()
