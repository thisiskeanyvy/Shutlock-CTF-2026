#!/usr/bin/env python3
"""Solve Shutlock 2026 "Back to Block".

The service leaks the AES master-key diagonal k[0], k[5], k[10], k[15].
Those bytes let us choose plaintexts whose state after round 1 is a
standard Square/integral structure. Two 256-query structures recover the
last round key byte-by-byte; the AES-128 key schedule is then inverted.
"""

from __future__ import annotations

import argparse
import socket
import time
from typing import Iterable

from aes_given import encrypt, inv_mix_columns, inv_s_box, s_box


DIAGONAL_POSITIONS = (0, 5, 10, 15)
MAX_QUERIES = 512


def xor_all(values: Iterable[int]) -> int:
    acc = 0
    for value in values:
        acc ^= value
    return acc


def inv_mix_vector(vector: list[int]) -> list[int]:
    state = [vector[:], [0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0]]
    inv_mix_columns(state)
    return state[0]


def make_structure(diagonal: bytes, constants: tuple[int, int, int]) -> list[bytes]:
    """Build 256 plaintexts with one active byte after the first AES round."""
    plaintexts: list[bytes] = []
    for x in range(256):
        target_after_mix = [x, *constants]
        before_mix = inv_mix_vector(target_after_mix)
        pt = bytearray(16)
        for idx, position in enumerate(DIAGONAL_POSITIONS):
            pt[position] = inv_s_box[before_mix[idx]] ^ diagonal[idx]
        plaintexts.append(bytes(pt))
    return plaintexts


def recover_last_round_key(ciphertexts_sets: list[list[bytes]]) -> bytes:
    key = bytearray(16)
    for pos in range(16):
        candidates = []
        for guess in range(256):
            if all(
                xor_all(inv_s_box[ct[pos] ^ guess] for ct in ciphertexts) == 0
                for ciphertexts in ciphertexts_sets
            ):
                candidates.append(guess)
        if len(candidates) != 1:
            raise ValueError(f"ambiguous last-round byte {pos}: {candidates}")
        key[pos] = candidates[0]
    return bytes(key)


def schedule_core(word: list[int], round_index: int) -> list[int]:
    rcon = [0x00, 0x01, 0x02, 0x04, 0x08, 0x10, 0x20]
    rotated = word[1:] + word[:1]
    rotated = [s_box[b] for b in rotated]
    rotated[0] ^= rcon[round_index]
    return rotated


def invert_key_schedule(round5_key: bytes) -> bytes:
    words: list[list[int] | None] = [None] * 24
    for i in range(4):
        words[20 + i] = list(round5_key[4 * i : 4 * (i + 1)])

    for i in range(23, 3, -1):
        assert words[i] is not None
        assert words[i - 1] is not None
        previous = schedule_core(words[i - 1], i // 4) if i % 4 == 0 else words[i - 1]
        words[i - 4] = [a ^ b for a, b in zip(words[i], previous)]

    master_words = words[:4]
    if any(word is None for word in master_words):
        raise ValueError("failed to invert AES key schedule")
    return bytes(sum((word for word in master_words if word is not None), []))


def local_oracle(key: bytes):
    def query(plaintext: bytes) -> bytes:
        return encrypt(plaintext, key)

    return query


class RemoteOracle:
    def __init__(self, host: str, port: int, delay: float = 0.08) -> None:
        self.host = host
        self.port = port
        self.delay = delay
        self.sock = socket.create_connection((host, port), timeout=15)
        self.file = self.sock.makefile("rwb")
        self.diagonal = bytes.fromhex(self.file.readline().strip().decode())
        self.file.readline()
        self.queries = 0

    def query(self, plaintext: bytes) -> bytes:
        if self.queries >= MAX_QUERIES:
            raise RuntimeError("query budget exhausted")
        self.file.write(plaintext.hex().encode() + b"\n")
        self.file.flush()
        line = self.file.readline().strip()
        self.queries += 1
        time.sleep(self.delay)
        return bytes.fromhex(line.decode())

    def submit_key(self, key: bytes) -> str:
        self.file.write(b"KEY:" + key.hex().encode() + b"\n")
        self.file.flush()
        return self.file.readline().strip().decode(errors="replace")

    def close(self) -> None:
        self.file.close()
        self.sock.close()


def recover_key(diagonal: bytes, query) -> bytes:
    structures = [
        make_structure(diagonal, (0, 0, 0)),
        make_structure(diagonal, (1, 2, 3)),
    ]
    ciphertexts_sets = [[query(pt) for pt in structure] for structure in structures]
    last_round_key = recover_last_round_key(ciphertexts_sets)
    master_key = invert_key_schedule(last_round_key)
    if bytes(master_key[i] for i in DIAGONAL_POSITIONS) != diagonal:
        raise ValueError("recovered key does not match leaked diagonal")
    if encrypt(structures[0][0], master_key) != ciphertexts_sets[0][0]:
        raise ValueError("recovered key failed local ciphertext verification")
    return master_key


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--host")
    parser.add_argument("--port", type=int)
    parser.add_argument("--delay", type=float, default=0.08)
    parser.add_argument("--submit", action="store_true")
    parser.add_argument("--self-test", action="store_true")
    args = parser.parse_args()

    if args.self_test:
        key = bytes.fromhex("00112233445566778899aabbccddeeff")
        diagonal = bytes(key[i] for i in DIAGONAL_POSITIONS)
        recovered = recover_key(diagonal, local_oracle(key))
        print(f"self-test key={recovered.hex()} ok={recovered == key}")
        return 0 if recovered == key else 1

    if not args.host or not args.port:
        parser.error("--host and --port are required unless --self-test is used")

    oracle = RemoteOracle(args.host, args.port, args.delay)
    try:
        key = recover_key(oracle.diagonal, oracle.query)
        print(f"diagonal={oracle.diagonal.hex()}")
        print(f"queries={oracle.queries}")
        print(f"key={key.hex()}")
        if args.submit:
            print(oracle.submit_key(key))
    finally:
        oracle.close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
