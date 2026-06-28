#!/usr/bin/env python3
"""Forge Schnorr proof for Frozen Love (impose Y from chosen s)."""
import hashlib
import json
import socket
import sys

# secp256k1
p = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEFFFFFC2F
q = 0xFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFFEBAAEDCE6AF48A03BBFD25E8CD0364141
Gx = 0x79BE667EF9DCBBAC55A06295CE870B07029BFCDB2DCE28D959F2815B16F81798
Gy = 0x483ADA7726A3C4655DA4FBFC0E1108A8FD17B448A68554199C47D08FFB10D4B8


def modinv(a, m):
    return pow(a, -1, m)


def point_add(P, Q):
    if P is None:
        return Q
    if Q is None:
        return P
    x1, y1 = P
    x2, y2 = Q
    if x1 == x2 and (y1 + y2) % p == 0:
        return None
    if P != Q:
        lam = ((y2 - y1) * modinv((x2 - x1) % p, p)) % p
    else:
        if y1 == 0:
            return None
        lam = ((3 * x1 * x1) * modinv((2 * y1) % p, p)) % p
    x3 = (lam * lam - x1 - x2) % p
    y3 = (lam * (x1 - x3) - y1) % p
    return (x3, y3)


def point_mul(k, P):
    k %= q
    if k == 0 or P is None:
        return None
    R = None
    Q = P
    while k:
        if k & 1:
            R = point_add(R, Q)
        Q = point_add(Q, Q)
        k >>= 1
    return R


G = (Gx, Gy)


def fiat_shamir(R, Gpt):
    h = hashlib.sha256()
    h.update(hex(R[0]).encode())
    h.update(hex(Gpt[0]).encode())
    return int(h.hexdigest(), 16) % q


def solve(host, port=8000, s_val=12345):
    sock = socket.create_connection((host, port), timeout=15)
    f = sock.makefile("rwb")

    def read_until(sub):
        buf = b""
        while sub not in buf:
            chunk = f.readline()
            if not chunk:
                break
            buf += chunk
        return buf

    read_until(b"Here it is:")
    line = ""
    while not line.strip():
        line = f.readline().decode().strip()
    coords = json.loads(line)
    Rx = int(coords[0], 16)
    Ry = int(coords[1], 16)
    R = (Rx, Ry)

    read_until(b"Now try")

    c = fiat_shamir(R, G)
    if c == 0:
        c = 1
    sG = point_mul(s_val, G)
    cY = point_add(sG, point_mul(q - 1, R))  # sG - R
    Y = point_mul(modinv(c, q), cY)
    if Y is None:
        raise SystemExit("degenerate Y")

    payload = json.dumps({"Y": [hex(Y[0]), hex(Y[1])], "s": s_val})
    f.write(payload.encode() + b"\n")
    f.flush()
    resp = f.read(4096)
    sock.close()
    return resp.decode("utf-8", "replace")


if __name__ == "__main__":
    host = sys.argv[1] if len(sys.argv) > 1 else "dynamic-challenges.shutlock.fr"
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    print(solve(host, port))
