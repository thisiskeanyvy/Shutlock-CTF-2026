#!/usr/bin/env python3
"""Mock C2 for jq trojan - captures User-Agent and returns payload."""
import argparse
import json
import ssl
import subprocess
import tempfile
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path

CAPTURE = {"requests": []}
PAYLOAD = b"SHLK{test_payload_from_mock_c2}\n"


class Handler(BaseHTTPRequestHandler):
    def do_GET(self):
        ua = self.headers.get("User-Agent", "")
        host = self.headers.get("Host", "")
        rec = {"path": self.path, "user_agent": ua, "host": host, "headers": dict(self.headers)}
        CAPTURE["requests"].append(rec)
        Path("/tmp/mock_c2_capture.json").write_text(json.dumps(CAPTURE, indent=2))
        print(f"[C2] GET {self.path} UA={ua!r} Host={host!r}")
        if self.path.rstrip("/") != "/update":
            self.send_response(404)
            self.end_headers()
            return
        body = PAYLOAD
        self.send_response(200)
        self.send_header("Content-Type", "application/octet-stream")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def log_message(self, fmt, *args):
        pass


def make_cert(cert_dir: Path):
    cert_dir.mkdir(parents=True, exist_ok=True)
    cert = cert_dir / "cert.pem"
    key = cert_dir / "key.pem"
    if cert.exists() and key.exists():
        return cert, key
    # SAN required for Go TLS client
    cnf = cert_dir / "openssl.cnf"
    cnf.write_text(
        "[req]\n"
        "distinguished_name=req\n"
        "x509_extensions=v3\n"
        "[v3]\n"
        "subjectAltName=DNS:nixos-community.me\n"
    )
    subprocess.run(
        [
            "openssl", "req", "-x509", "-newkey", "rsa:2048",
            "-keyout", str(key), "-out", str(cert),
            "-days", "1", "-nodes",
            "-subj", "/CN=nixos-community.me",
            "-config", str(cnf), "-extensions", "v3",
        ],
        check=True,
        capture_output=True,
    )
    return cert, key


def main():
    global PAYLOAD
    ap = argparse.ArgumentParser()
    ap.add_argument("--port", type=int, default=8443)
    ap.add_argument("--payload-file")
    ap.add_argument("--payload-text", default="SHLK{mock_c2_response}")
    ap.add_argument("--https", action="store_true")
    ap.add_argument("--cert-dir", default="/tmp/mockc2-certs")
    args = ap.parse_args()
    if args.payload_file:
        PAYLOAD = Path(args.payload_file).read_bytes()
    else:
        PAYLOAD = args.payload_text.encode()
    httpd = HTTPServer(("0.0.0.0", args.port), Handler)
    if args.https:
        cert_dir = Path(args.cert_dir)
        cert, key = make_cert(cert_dir)
        ctx = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
        ctx.check_hostname = False
        ctx.verify_mode = ssl.CERT_NONE
        ctx.load_cert_chain(cert, key)
        httpd.socket = ctx.wrap_socket(httpd.socket, server_side=True)
        print(f"HTTPS on :{args.port} cert={cert}")
    else:
        print(f"HTTP on :{args.port}")
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        pass
    out = Path("/tmp/mock_c2_capture.json")
    out.write_text(json.dumps(CAPTURE, indent=2))
    print("saved", out)


if __name__ == "__main__":
    main()
