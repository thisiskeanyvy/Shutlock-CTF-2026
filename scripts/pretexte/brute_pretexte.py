#!/usr/bin/env python3
"""Brute pretexte password via native binary (fast ~2ms/try)."""
import subprocess
import sys
from pathlib import Path

BIN = Path(__file__).parent / "pretexte"
THEME = """
pretexte pretext Pretexte PRETEXTE deadbeef reverse harder reverseharder magic nemo
Nemo blowfish Blowfish shutlock chione kingsley lena Lena mishell MiShell void sputnik
ghost eumelopos NESESK CIDPOEEK AKALSW PERMANENT WMS90 CRM propulsion insider
HateDeCommencer Lena_KINGSLEY everything execute illusion alibi excuse leurre mensonge
5498a641 algaes bloat harder nope dead beef pretexting alibi excuse camouflage
""".split()


def ok(pw: str) -> bool:
    try:
        r = subprocess.run([str(BIN), pw], capture_output=True, text=True, timeout=2)
        return "deadbeef" in (r.stdout + r.stderr)
    except (subprocess.TimeoutExpired, OSError):
        return False


def main():
    words = set(THEME)
    for p in (
        Path("/usr/share/dict/words"),
        Path("/usr/share/dict/web2"),
        Path("/usr/share/wordlists/rockyou.txt"),
    ):
        if p.exists():
            for line in p.read_text(errors="ignore").splitlines():
                w = line.strip()
                if 1 <= len(w) <= 32:
                    words.add(w)
                    if w.isalpha():
                        words.add(w.lower())
                        words.add(w.capitalize())

    for i, pw in enumerate(sorted(words, key=len)):
        if ok(pw):
            print("FOUND", pw, flush=True)
            return 0
        if i and i % 25000 == 0:
            print("progress", i, flush=True)
    print("not found", len(words))
    return 1


if __name__ == "__main__":
    sys.exit(main())
