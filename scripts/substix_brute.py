#!/usr/bin/env python3
"""Brute Substix flag md5(package:key:c2) candidates."""
import hashlib
import itertools

PKGS = [
    "jq",
    "jq-1.7.1",
    "jq-1.7.1-bin",
    "0q85yfxd70aq8iv4n43hqcmh2dbyb80z-jq-1.7.1-bin",
    "iwkr16nxhp1lzl5r8diqx6ajdxj1n4nh-jq-1.7.1",
]
KEYS = [
    "83zMUZVWbI0dL2XEVC54/hIuknxsrAmYdaYCGkEhi/9dA2faDX6r2gbXZMzdXg/5zRcLH1yjkCeotHRTWBw",
    "H92t9H9rHt3H",
    "fMFYexYbxTh3tLlX93HLSGTuqLWR8MrdeihhymJcsIyUQFNLS/1DJxJUOJ6JIXkGt08adE3wdTEmNH38I+r+Cw==",
    "substix-nix-cache:ggiTJONsWRiQpkJOrP2Km/CI4omYwCssO6O4qbmZCdA=",
    "ggiTJONsWRiQpkJOrP2Km/CI4omYwCssO6O4qbmZCdA=",
    "17nip6p4y6brqh869qsiipc6bn945fm40x9484mmb2xqsfc2vxf2",
]
C2S = [
    "https://nixos-community.me/update",
    "http://substix.shutlock.fr:5000",
    "https://substix.shutlock.fr",
    "substix.shutlock.fr:5000",
    "nixos-community.me/update",
]

if __name__ == "__main__":
    for pkg, key, c2 in itertools.product(PKGS, KEYS, C2S):
        h = hashlib.md5(f"{pkg}:{key}:{c2}".encode()).hexdigest()
        print(f"SHLK{{{h}}} | {pkg} | {key[:40]} | {c2}")
