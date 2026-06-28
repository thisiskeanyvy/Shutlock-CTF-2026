#!/usr/bin/env python3
"""Brute Blowfish P-array leak against rockyou wordlist."""
import importlib.util
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
LEAKED = [
    845768460, 3329329542, 2701147703, 3469349130, 446106929,
    1090006798, 2265458680, 1310627640, 4013947393, 3572411605,
    2492910940, 1493463374, 1578120307, 16333685, 2195655910,
    454870479, 2411137534, 2607526894,
]


def load_bf():
    spec = importlib.util.spec_from_file_location("bf", str(ROOT / "bf.py"))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def flat_p(cipher):
    return [x for pair in cipher.P for x in pair]


def matches(bf, key: bytes) -> bool:
    if len(key) < 4 or len(key) > 56:
        return False
    try:
        return flat_p(bf.Cipher(key)) == LEAKED
    except Exception:
        return False


def main():
    bf = load_bf()
    wordlists = [
        ROOT.parent / "tryhackme-hydra" / "rockyou-top20k.txt",
        Path("/usr/share/wordlists/rockyou.txt"),
    ]
    extra = [
        "One Fish, Twofish, Red Fish, Blowfish",
        "One Fish Twofish Red Fish Blowfish",
        "OneFishTwofishRedFishBlowfish",
        "Nemo", "Dory", "Bloat", "Marlin", "Bruce Schneier",
        "Tetraodontidae", "pufferfish", "Big Brother", "big brother",
        "Finding Nemo", "Kevin Wall", "SchneierFacts", "1605",
    ]
    for w in extra:
        if matches(bf, w.encode()):
            print("FOUND:", w)
            return 0

    quote = "One Fish, Twofish, Red Fish, Blowfish"
    for i in range(len(quote)):
        for j in range(i + 4, min(i + 57, len(quote) + 1)):
            k = quote[i:j].encode()
            if matches(bf, k):
                print("FOUND substring:", k.decode())
                return 0

    for wl in wordlists:
        if not wl.exists():
            continue
        print("wordlist", wl)
        n = 0
        with open(wl, "rb") as f:
            for line in f:
                n += 1
                if n > 10000:
                    break
                w = line.rstrip(b"\r\n")
                if matches(bf, w):
                    print("FOUND:", w.decode("utf-8", "replace"))
                    return 0
                if n % 2000 == 0:
                    print(f"  ...{n}", flush=True)
        print(f"  done {n} lines, no match")
    return 1


if __name__ == "__main__":
    sys.exit(main())
