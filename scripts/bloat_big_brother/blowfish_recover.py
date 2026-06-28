#!/usr/bin/env python3
"""Correct Blowfish key expansion + P-array leak recovery."""
import itertools
import string
from pathlib import Path

P_INIT = [
    0x243F6A88, 0x85A308D3, 0x13198A2E, 0x03707344,
    0xA4093822, 0x299F31D0, 0x082EFA98, 0xEC4E6C89,
    0x452821E6, 0x38D01377, 0xBE5466CF, 0x34E90C6C,
    0xC0AC29B7, 0xC97C50DD, 0x3F84D5B5, 0xB5470917,
    0x9216D5D9, 0x8979FB1B,
]

PI_HEX = (
    "243f6a8885a308d313198a2e03707344a4093822299f31d0082efa98ec4e6c89"
    "452821e638d01377be5466cf34e90c6cc0ac29b7c97c50dd3f84d5b5b5470917"
    "9216d5d98979fb1bbcaeb7da7ff9f2cf3722c4545154f2ed136858094cf4b795e"
    "46215c8d9a002210b92e4e6e650381e7f95e8028be6b5930a366b4a1c2f7bc9a"
    "655b5a5369e7595b9b8e98fba638b5dd293a501b6549d036c84bbe2e6309d349"
    "f8ce874a672f5e2f8201f2e8e3a96fb3268e7ef18eb3314adfb5bd6fd886978"
    "0719a1d0a38d4787a72175464b9751e647f30d271fe89c4b87b7d117b5c4c04"
    "f9df4178fa67ce0f477415dafa9e9e3070be85ce23c3fdb9440f12dc9a1d6f7"
    "a4066e0878f4d48a70c9abf2b8f56204fbeef121332751f2ce1b2121370c92"
    "aa47e3b2eb1d5b5fe4c4c52a06a5a15faa6a02a1bbd25934cf626f5f9e4b2c0"
    "a430b5fe26fc923f6d88d2a704fc97881a57de786a77f2ea7c2b4f013edf5c2"
    "d08be9ffcd9e1f5616a100d6426f9a8a6b1e0077b6aa3750e2c7f9f2cf3722"
)

LEAKED = [
    845768460, 3329329542, 2701147703, 3469349130, 446106929,
    1090006798, 2265458680, 1310627640, 4013947393, 3572411605,
    2492910940, 1493463374, 1578120307, 16333685, 2195655910,
    454870479, 2411137534, 2607526894,
]


def init_sboxes():
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "bf", Path(__file__).with_name("bf.py")
    )
    bf_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bf_mod)
    return [list(box) for box in bf_mod.PI_S_BOXES]


def matches(key: bytes) -> bool:
    import importlib.util

    spec = importlib.util.spec_from_file_location(
        "bf", Path(__file__).with_name("bf.py")
    )
    bf_mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(bf_mod)
    flat = [x for p in bf_mod.Cipher(key).P for x in p]
    return flat == LEAKED


def f_func(x, s):
    a, b, c, d = (x >> 24) & 0xFF, (x >> 16) & 0xFF, (x >> 8) & 0xFF, x & 0xFF
    return ((s[0][a] + s[1][b]) & 0xFFFFFFFF ^ s[2][c] + s[3][d]) & 0xFFFFFFFF


def expand_key(key: bytes):
    p = P_INIT[:]
    s = init_sboxes()
    j = 0
    kl = len(key)
    for i in range(18):
        data = 0
        for _ in range(4):
            data = ((data << 8) | key[j]) & 0xFFFFFFFF
            j = (j + 1) % kl
        p[i] ^= data
    left, right = 0, 0
    for i in range(0, 18, 2):
        left, right = f_func(left, s) ^ p[i], left
        right, left = f_func(right, s) ^ p[i + 1], right
        p[i], p[i + 1] = left, right
    for i in range(4):
        for j in range(0, 256, 2):
            left, right = f_func(left, s) ^ p[0], left
            right, left = f_func(right, s) ^ p[1], right
            s[i][j], s[i][j + 1] = left, right
    return p


def matches_old_expand(key: bytes) -> bool:
    return expand_key(key) == LEAKED


if __name__ == "__main__":
    words = [
        "Nemo", "nemo", "NEMO", "Bloat", "bloat", "BLOWFISH", "Blowfish",
        "Tetraodontidae", "pufferfish", "BigBrother", "bigbrother", "Schneier",
        "Bruce Schneier", "Dory", "Marlin", "SHLK", "shutlock", "deadbeef",
        "CHIONE", "BloatBigBrother", "bloat_big_brother", "Finding Nemo",
        "globe", "ballon", "Poisson", "poisson", "Bruce", "SchneierFacts",
        "1605", "fact1605", "WMS90", "CIDO", "PERMANENT",
        "One Fish, Twofish, Red Fish, Blowfish",
        "One Fish Twofish Red Fish Blowfish",
        "OneFishTwofishRedFishBlowfish",
        "c0n5TrucTor-oVer_h3RriNg",
    ]
    for w in words:
        if matches(w.encode()):
            print("KEY FOUND:", w)
    print("done (wordlist only)")
