"""Opt-in public-source collector for Scout research. No automatic crawling."""
from __future__ import annotations
import argparse
import hashlib
import json
import ssl
import urllib.request
from pathlib import Path
from urllib.parse import urlsplit
from scout_evidence_intake import build_packet, MAX_BYTES

HOSTS = {"arxiv.org", "www.arxiv.org", "raw.githubusercontent.com"}
MAX_REDIRECTS = 0

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None

def collect(url: str, opener=None) -> dict:
    parts = urlsplit(url)
    if parts.scheme != "https" or parts.hostname not in HOSTS or parts.port not in (None, 443):
        raise ValueError("URL outside allowed public-source hosts")
    if parts.username or parts.password or parts.fragment:
        raise ValueError("URL must not contain credentials or fragment")
    opener = opener or urllib.request.build_opener(
        urllib.request.HTTPSHandler(context=ssl.create_default_context()), NoRedirect())
    request = urllib.request.Request(url, headers={"User-Agent": "GhostMesh-Scout-Research/0.1", "Accept": "text/plain, text/html"})
    with opener.open(request, timeout=8) as response:
        if response.status != 200:
            raise ValueError("Source returned non-200 status")
        kind = response.headers.get_content_type()
        if kind not in ("text/plain", "text/html"):
            raise ValueError("Unsupported content type")
        payload = response.read(MAX_BYTES + 1)
    packet = build_packet(url, payload)
    packet["source_capture"] = "HTTPS GET of allowlisted host; no redirects; content not independently authenticated"
    packet["retrieval"] = {"http_status": 200, "content_type": kind}
    return packet

def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    args = parser.parse_args()
    print(json.dumps(collect(args.url), indent=2, ensure_ascii=False))

if __name__ == "__main__":
    main()
