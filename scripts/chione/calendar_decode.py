#!/usr/bin/env python3
"""Generate MiShell accessCode candidates from eumelopos calendar matrix."""
import itertools
import subprocess
import urllib.parse

# Grid from image2.jpg (5 cols x 4 data rows)
# Headers: TLEN/CLIENT, AYS/DAYS, RPS/PROS, WS/WEEKS, ANS/ANS
WORDS = ["CLIENT", "DAYS", "PROS", "WEEKS", "ANS"]

# (row 1-4, col 0-4, day_value, mark: 'c'=circle, 'k'=check, 'r'=red text)
MARKED = [
    (2, 4, 10, "c"),   # ANS row2
    (3, 3, 19, "k"),   # WS row3
    (3, 4, 25, "c"),   # ANS row3
    (4, 0, 20, "r"),   # CLIENT row4 red
    (4, 1, 20, "c"),   # DAYS row4 circled
    (4, 3, 26, "k"),   # WS row4 check (col4 = index 3)
]

GRID = [
    [None, 2, 3, 5, 7],
    [8, 7, 8, 12, 10],
    [15, 15, 16, 19, 25],
    [20, 20, 23, 26, 3],
]

MISSING = "CIDOEEK"  # CI+D+O+EEK
CLOCK = ["AFRS", "1YEARS", "1YEARS", "7YEARS", "7YEARS"]


def letter_at_row(word: str, row: int) -> str:
    if row < 1 or row > len(word):
        return ""
    return word[row - 1]


def letter_at_value(word: str, val: int) -> str:
    if not val:
        return ""
    return word[(val - 1) % len(word)]


def build_candidates() -> set[str]:
    codes: set[str] = set()

    # --- row-based letters on marked cells ---
    for marks in [MARKED, [m for m in MARKED if m[3] == "c"], [m for m in MARKED if m[3] in "ck"]]:
        for order in ("grid", "col", "val"):
            chars = []
            ms = sorted(marks, key=lambda m: (m[0], m[1]) if order == "grid" else (m[1], m[0]) if order == "col" else m[2])
            for row, col, val, _ in ms:
                w = WORDS[col]
                for fn in (lambda: letter_at_row(w, row), lambda: letter_at_value(w, val)):
                    ch = fn()
                    if ch:
                        chars.append(ch)
            if chars:
                codes.add("".join(chars))

    # --- diagonal / matrix paths ---
    concat = "".join(WORDS)
    for path_name, cells in [
        ("diag", [(i, i, GRID[i][i]) for i in range(4) if GRID[i][i] is not None]),
        ("marked_vals", [(m[0], m[1], m[2]) for m in MARKED]),
    ]:
        s = ""
        for row, col, val in cells:
            s += letter_at_row(WORDS[col], row) or letter_at_value(WORDS[col], val)
        if s:
            codes.add(s)

    # --- missing letters permutations ---
    base_parts = ["CIDO", "CIDOEEK", "CDO", "DICO", "CODE", MISSING]
    for p in base_parts:
        codes.add(p)
        for suffix in ["", "10", "1000", "10h00", "10:00", "_10h00"]:
            codes.add(p + suffix)
            codes.add(suffix + p)

    # --- PERMANENT / clock combos ---
    for perm in ["PERMANENT", "PERMANANCE", "permanent"]:
        for mid in ["", "CIDO", "CIDOEEK", "AFRS", "CLIENT", "DAYS"]:
            codes.add(perm + mid)
            codes.add(mid + perm)
            codes.add(f"{perm}{mid}10")
            codes.add(f"{perm}{mid}10h00")

    for seg in CLOCK + ["AFRS1YEARS7YEARS", "AFRS17", "1YEARS7YEARS"]:
        codes.add(seg)
        codes.add("CIDO" + seg)
        codes.add(seg + "CIDO")

    # --- marked day numbers as string / A1Z26 ---
    vals = sorted({m[2] for m in MARKED})
    codes.add("".join(map(str, vals)))
    codes.add("".join(map(str, sorted(vals))))
    a1z = "".join(chr(64 + (v % 26) or 26) for v in sorted(vals))
    codes.add(a1z)

    # --- pick letters from concat at day indices ---
    for v in vals:
        if v <= len(concat):
            codes.add(concat[v - 1])
    picks = "".join(concat[v - 1] for v in sorted(vals) if v <= len(concat))
    if picks:
        codes.add(picks)

    # --- row4 all columns ---
    rows_letters = []
    for col in range(5):
        rows_letters.append(letter_at_row(WORDS[col], 4))
    codes.add("".join(rows_letters))

    # --- Place + decode (mail address puzzle) ---
    for tail in ["CIDO", "CIDOEEK", "Logistique", "la Logistique", "de la Logistique",
                 "Madeleine", "de la Madeleine", "PERMANENT", "PERMANENT CIDO"]:
        codes.add("Place " + tail)
        codes.add("Place de " + tail)
        codes.add("Place de la " + tail)

    # --- permutations of 4-7 char subsets from ESKN etc ---
    manual = ["ESKN", "ESSEN", "NESS", "SENSE", "NSES", "LSEN", "ESLN", "KENS",
              "ESKNE", "CLIENT", "WEEKS", "PROS", "JSTYZ", "PPEEN", "CIDEK", "CIDEEK"]
    codes.update(manual)

    return {c.strip() for c in codes if c and len(c) <= 64}


def test_codes(codes, nom="Lena Kingsley"):
    hits = []
    name_q = urllib.parse.quote(nom)
    for code in sorted(codes):
        c = urllib.parse.quote(code)
        r = subprocess.run(
            ["curl", "-s", "-w", "%{http_code}", "-o", "/tmp/mishell_hit.json",
             f"https://search.shutlock.fr/api/personnes/search?nom={name_q}&accessCode={c}"],
            capture_output=True, text=True,
        )
        if r.stdout.strip() == "200":
            body = open("/tmp/mishell_hit.json").read()
            hits.append((code, body))
            print("HIT accessCode=", repr(code))
            print(body[:2000])
    return hits


if __name__ == "__main__":
    codes = build_candidates()
    print(f"Generated {len(codes)} candidates")
    hits = test_codes(codes)
    if not hits:
        # also try swapping nom=accessCode (unlikely)
        for nom in ["CIDO", "PERMANENT", "CLIENTCIDO"]:
            h = test_codes({"": ""}, nom=nom)  # noop
        print("No hits on primary batch")
