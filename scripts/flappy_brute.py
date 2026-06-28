#!/usr/bin/env python3
"""Brute 4-byte XOR keys for FlappyBug flag.dat."""
import os
import sys

DATA_PATH = os.environ.get("FLAPPY_FLAG_DAT", "flag.dat")


def main():
    data = open(DATA_PATH, "rb").read()
    best = []
    for k0 in range(256):
        if k0 % 32 == 0:
            print(f"k0={k0}", file=sys.stderr)
        for k1 in range(256):
            for k2 in range(256):
                for k3 in range(256):
                    key = bytes([k0, k1, k2, k3])
                    dec = bytes(data[j] ^ key[j % 4] for j in range(len(data)))
                    # longest printable run
                    run = cur = 0
                    for b in dec:
                        if 32 <= b < 127 or b in (10, 13):
                            cur += 1
                            run = max(run, cur)
                        else:
                            cur = 0
                    if run < 30:
                        continue
                    s = dec.decode("latin-1")
                    score = run
                    if "SHLK{" in s:
                        score += 1000
                    if "flag" in s.lower():
                        score += 50
                    best.append((score, key.hex(), s[s.find("SHLK{") : s.find("}", s.find("SHLK{")) + 1] if "SHLK{" in s else s[:80]))
    best.sort(reverse=True)
    for item in best[:20]:
        print(item)


if __name__ == "__main__":
    main()
