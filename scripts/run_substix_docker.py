#!/usr/bin/env python3
"""Patch jq trojan C2 URL and run in docker amd64 against mock C2."""
import os
import shutil
import subprocess
import sys
import time
from pathlib import Path

ROOT = Path(__file__).resolve().parent
BIN_SRC = Path("/tmp/jq-malicious")
BIN = Path("/tmp/jq-patched")
MOCK_PORT = int(os.environ.get("MOCK_PORT", "8443"))
HOST_IP = os.environ.get("HOST_IP", "192.168.5.2")
PAYLOAD = os.environ.get("PAYLOAD", "stage2-test-payload")
DOCKER_HOST_OVERRIDE = os.environ.get("DOCKER_HOST_OVERRIDE")


def patch_url(path: Path, url: bytes) -> None:
    data = bytearray(path.read_bytes())
    needle = b"https://nixos-community.me/update"
    idx = data.find(needle)
    if idx < 0:
        raise SystemExit("URL string not found")
    if len(url) > 33:
        raise SystemExit(f"URL too long: {len(url)}")
    data[idx : idx + 33] = url.ljust(33, b"\x00")
    path.write_bytes(data)
    print(f"Patched @ {idx:#x}: {url.decode()}")


def main():
    if not BIN_SRC.exists():
        raise SystemExit(f"missing {BIN_SRC}")
    work_bin = ROOT / "jq-patched"
    shutil.copy2(BIN_SRC, work_bin)
    shutil.copy2(BIN_SRC, BIN)
    url = f"http://{HOST_IP}:{MOCK_PORT}/update".encode()
    patch_url(work_bin, url)
    patch_url(BIN, url)

    garbage = Path("/tmp/nix-collect-garbage")
    garbage.unlink(missing_ok=True)
    Path("/tmp/mock_c2_capture.json").unlink(missing_ok=True)

    mock = subprocess.Popen(
        [
            sys.executable,
            str(ROOT / "mock_c2.py"),
            "--port",
            str(MOCK_PORT),
            "--payload-text",
            PAYLOAD,
        ],
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
    )
    time.sleep(1.5)

    env = os.environ.copy()
    if DOCKER_HOST_OVERRIDE:
        env["DOCKER_HOST"] = DOCKER_HOST_OVERRIDE
    cmd = [
        "docker",
        "run",
        "--rm",
        "--platform",
        "linux/amd64",
        "-v",
        f"{work_bin}:/trojan/jq:ro",
        "-v",
        "/tmp:/tmp",
        "alpine:3.20",
        "/trojan/jq",
    ]
    print("Running:", " ".join(cmd))
    proc = subprocess.run(cmd, capture_output=True, text=True, env=env)
    print("=== stdout ===")
    print(proc.stdout)
    print("=== stderr ===")
    print(proc.stderr)
    print("exit", proc.returncode)

    mock.terminate()
    try:
        mock.wait(timeout=2)
    except subprocess.TimeoutExpired:
        mock.kill()

    if garbage.exists():
        data = garbage.read_bytes()
        print(f"\n=== /tmp/nix-collect-garbage ({len(data)} bytes) ===")
        print(data[:500])
        try:
            print("text:", data.decode("utf-8", "replace"))
        except Exception:
            pass
    else:
        print("\n(no /tmp/nix-collect-garbage)")


if __name__ == "__main__":
    main()
