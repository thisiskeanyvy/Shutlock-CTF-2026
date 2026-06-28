#!/bin/bash
# Run jq trojan against local mock C2 via qemu-x86_64
set -euo pipefail
ROOT="$(cd "$(dirname "$0")" && pwd)"
BIN_SRC="/tmp/jq-malicious"
BIN="/tmp/jq-patched"
MOCK_PORT="${MOCK_PORT:-8443}"
PAYLOAD="${PAYLOAD:-stage2-test-payload}"
QEMU="$(brew --prefix qemu)/bin/qemu-x86_64"

cp "$BIN_SRC" "$BIN"
python3 - "$BIN" "$MOCK_PORT" <<'PY'
import sys
path, port = sys.argv[1], sys.argv[2]
url = f"http://127.0.0.1:{port}/update".encode()
assert len(url) <= 33
url = url.ljust(33, b"\x00")
data = bytearray(open(path, "rb").read())
needle = b"https://nixos-community.me/update"
idx = data.find(needle)
if idx < 0:
    raise SystemExit("URL not found")
data[idx : idx + 33] = url
open(path, "wb").write(data)
shown = url.split(b"\x00")[0]
print(f"Patched URL @ {idx:#x} -> {shown!r}")
PY

rm -f /tmp/nix-collect-garbage /tmp/mock_c2_capture.json
python3 "$ROOT/mock_c2.py" --port "$MOCK_PORT" --payload-text "$PAYLOAD" &
MOCK_PID=$!
sleep 1

echo "=== running trojan ==="
"$QEMU" "$BIN" 2>&1 || true
sleep 0.5
kill "$MOCK_PID" 2>/dev/null || true

echo "=== /tmp/nix-collect-garbage ==="
if [[ -f /tmp/nix-collect-garbage ]]; then
  ls -la /tmp/nix-collect-garbage
  xxd /tmp/nix-collect-garbage | head -20
  echo "--- strings ---"
  strings /tmp/nix-collect-garbage
else
  echo "(missing)"
fi
