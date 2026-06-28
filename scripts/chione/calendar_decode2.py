#!/usr/bin/env python3
"""Exhaustive calendar matrix → MiShell accessCode."""
import itertools
import subprocess
import urllib.parse

WORDS = ["CLIENT", "DAYS", "PROS", "WEEKS", "ANS"]
GRID = [
    [None, 2, 3, 5, 7],
    [8, 7, 8, 12, 10],
    [15, 15, 16, 19, 25],
    [20, 20, 23, 26, 3],
]
MARKED = [
    (2, 4, 10, "c"),
    (3, 3, 19, "k"),
    (3, 4, 25, "c"),
    (4, 0, 20, "r"),
    (4, 1, 20, "c"),
    (4, 3, 26, "k"),
]
CONCAT = "".join(WORDS)
MISSING_BY_COL = ["CI", "D", "O", "EEK", ""]


def row_letter(col, row):
    w = WORDS[col]
    return w[row - 1] if 1 <= row <= len(w) else ""


def val_letter(col, val):
    w = WORDS[col]
    return w[(val - 1) % len(w)] if val else ""


def gen() -> set[str]:
    codes = set()

    # all row-wise decoded strings
    for r in range(1, 5):
        codes.add("".join(row_letter(c, r) for c in range(5)))

    # marked subsets all permutations
    for r in range(1, len(MARKED) + 1):
        for combo in itertools.permutations(MARKED, r):
            for mode in ("row", "val", "col"):
                s = "".join(
                    row_letter(m[1], m[0]) if mode == "row" else val_letter(m[1], m[2]) if mode == "val" else WORDS[m[1]][0]
                    for m in combo
                )
                if s:
                    codes.add(s)

    # grid order marked
    for mode in ("row", "val"):
        ms = sorted(MARKED, key=lambda m: (m[0], m[1]))
        s = "".join(row_letter(m[1], m[0]) if mode == "row" else val_letter(m[1], m[2]) for m in ms)
        codes.add(s)

    # only circled / only checks
    for filt in ("c", "k", "ck", "r"):
        ms = [m for m in MARKED if m[3] in filt or (filt == "ck" and m[3] in "ck")]
        if ms:
            codes.add("".join(row_letter(m[1], m[0]) for m in ms))
            codes.add("".join(val_letter(m[1], m[2]) for m in ms))

    # missing letters combos
    for parts in itertools.permutations(["CI", "D", "O", "EEK"], 4):
        codes.add("".join(parts))
    for base in ["CIDO", "CIDOEEK", "CIDOEK", "CIDEK", "CIDEEK", "DCIO", "ODIC"]:
        for suf in ["", "10", "1000", "10h00", "10:00", "PERMANENT", "AFRS"]:
            codes.add(base + suf)
            codes.add(suf + base)

    # PERMANENT indexed by marked values
    perm = "PERMANENT"
    for order in (sorted(MARKED, key=lambda m: m[2]), MARKED):
        s = "".join(perm[(m[2] - 1) % len(perm)] for m in order)
        codes.add(s)

    # concat indexed
    for v in [10, 19, 20, 25, 26]:
        if v <= len(CONCAT):
            codes.add(CONCAT[v - 1])
    codes.add("".join(CONCAT[v - 1] for v in sorted([10, 19, 20, 25, 26]) if v <= len(CONCAT)))

    # Place completions
    for tail in codes.copy():
        if 3 <= len(tail) <= 20:
            codes.add("Place " + tail)
            codes.add("Place de la " + tail)

    # nom/access swap candidates stored separately
    return {c for c in codes if c and len(c) <= 48}


def test(codes, nom="Lena Kingsley"):
    qn = urllib.parse.quote(nom)
    for code in sorted(codes):
        qc = urllib.parse.quote(code)
        st = subprocess.check_output(
            ["curl", "-s", "-w", "%{http_code}", "-o", "/tmp/h.json",
             f"https://search.shutlock.fr/api/personnes/search?nom={qn}&accessCode={qc}"],
            text=True,
        ).strip()
        if st == "200":
            body = open("/tmp/h.json").read()
            print("HIT", repr(code), body[:1500])
            return code, body
    return None, None


if __name__ == "__main__":
    codes = gen()
    print("candidates", len(codes))
    # sample interesting
    for s in sorted(codes, key=len)[:30]:
        print(" ", s)
    test(codes)
    # swap nom
    for nom in ["CIDO", "PERMANENT", "CLIENT", "NESESK", "ESKNE"]:
        test({""}, nom=nom)
