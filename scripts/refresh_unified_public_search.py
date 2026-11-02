#!/usr/bin/env python3
"""Refresh Reader+SharePlane search from a verified, publicly published corpus.

A publisher-owned stable corpus URL must be provided. This consumer deliberately
does not scrape catalog pages, infer eligibility, or publish private offline data.
On failure, the last-good index remains untouched.
"""
import argparse
import hashlib
import json
import os
from pathlib import Path
import tempfile
from urllib.parse import urlparse
from urllib.request import Request, urlopen

if __package__:
    from .build_unified_search_index import build
else:
    from build_unified_search_index import build

MAX_BYTES = 16 * 1024 * 1024


def fetch_shareplane_bytes(url):
    parsed = urlparse(url)
    if (parsed.scheme != "https" or parsed.netloc != "shareplane.malott.ai"
            or parsed.username or parsed.password or parsed.query or parsed.fragment
            or not parsed.path.startswith("/")):
        raise ValueError("Only canonical public SharePlane HTTPS sources are permitted")
    req = Request(url, headers={"User-Agent": "GhostMesh-Readers-Static-Index/1"})
    with urlopen(req, timeout=25) as response:
        final = urlparse(response.geturl())
        if final.scheme != "https" or final.netloc != "shareplane.malott.ai":
            raise ValueError("Public corpus redirected outside canonical SharePlane")
        body = response.read(MAX_BYTES + 1)
    if not body or len(body) > MAX_BYTES:
        raise ValueError("Empty or oversized public SharePlane snapshot")
    return body


def refresh(readers_path, corpus_url, catalog_url, output_path, min_readers, min_works):
    # Independent live-catalog bytes establish the expected digest. Never trust
    # the digest merely because the corpus asserts it.
    catalog = fetch_shareplane_bytes(catalog_url)
    source_sha = hashlib.sha256(catalog).hexdigest()
    corpus_bytes = fetch_shareplane_bytes(corpus_url)
    corpus = json.loads(corpus_bytes)
    readers = json.loads(Path(readers_path).read_text(encoding="utf-8"))
    output = build(readers, corpus, min_readers=min_readers,
                   min_shareplane=min_works, expected_source_sha=source_sha)
    serialized = json.dumps(output, indent=2, ensure_ascii=False) + "\n"
    target = Path(output_path)
    target.parent.mkdir(parents=True, exist_ok=True)
    # One atomic update after every source/route/coverage check succeeds.
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=target.parent,
                                     prefix=".unified-search-", delete=False) as temp:
        temp.write(serialized)
        pending = Path(temp.name)
    try:
        os.replace(pending, target)
    finally:
        pending.unlink(missing_ok=True)
    print(f"PASS public unified search: {output['sources']['Readers']['count']} Readers, "
          f"{output['sources']['SharePlane']['count']} SharePlane Works; catalog {source_sha}")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--readers", type=Path, default=Path("site/readers/search-index.json"))
    parser.add_argument("--corpus-url", required=True,
                        help="Publisher-owned stable public Works corpus URL")
    parser.add_argument("--catalog-url", default="https://shareplane.malott.ai/native/v3/assets/catalog.js")
    parser.add_argument("--output", type=Path, default=Path("site/readers/unified-search-index.json"))
    parser.add_argument("--min-readers", type=int, default=40)
    parser.add_argument("--min-shareplane", type=int, default=114)
    args = parser.parse_args()
    refresh(args.readers, args.corpus_url, args.catalog_url, args.output,
            args.min_readers, args.min_shareplane)


if __name__ == "__main__":
    main()
