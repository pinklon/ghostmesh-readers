#!/usr/bin/env python3
"""Build a static, public-only search index from two canonical projections.

The producer of each input is responsible for supplying a current snapshot.
The CLI requires an independently verified canonical source-catalog digest;
a count floor alone cannot establish current production coverage.
"""
import argparse
import json
import re
from pathlib import Path
from urllib.parse import urlparse


SCHEMA = "ghostmesh-unified-search-v1"
HOSTS = {"Readers": "youtube.shareplane.malott.ai", "SharePlane": "shareplane.malott.ai"}


def public_url(host, path):
    if not isinstance(path, str) or not path.strip():
        raise ValueError("Missing publication route")
    if path.startswith("https://"):
        parsed = urlparse(path)
        if (parsed.netloc != host or parsed.username or parsed.password or
                parsed.query or parsed.fragment or not re.fullmatch(r"/[a-z0-9/-]+/", parsed.path) or
                "//" in parsed.path or ".." in parsed.path):
            raise ValueError("Unexpected external search target")
        return path
    if (not re.fullmatch(r"/[a-z0-9/-]+/", path) or "//" in path or
            ".." in path.split("/")):
        raise ValueError("Unsafe publication route")
    return "https://" + host + "/" + path.lstrip("/")


def build(readers, shareplane, *, min_readers=1, min_shareplane=1, expected_source_sha=None):
    if readers.get("schema") != "ghostmesh-public-reader-text-v1":
        raise ValueError("Unsupported Reader search schema")
    reader_items = readers.get("readers")
    if not isinstance(reader_items, list) or len(reader_items) != readers.get("readerCount"):
        raise ValueError("Reader index count mismatch")
    if len(reader_items) < min_readers:
        raise ValueError("Reader index is below required coverage")
    if shareplane.get("schemaVersion") != "shareplane.reader-public-works-snapshot.v1":
        raise ValueError("Unsupported SharePlane public Work corpus schema")
    digest = shareplane.get("sourceCatalogSha256")
    if not isinstance(digest, str) or not re.fullmatch(r"[a-fA-F0-9]{64}", digest):
        raise ValueError("SharePlane corpus source hash missing or invalid")
    if expected_source_sha is not None and digest.lower() != expected_source_sha.lower():
        raise ValueError("SharePlane source catalog digest does not match approved current source")
    works = shareplane.get("records")
    if not isinstance(works, list) or not all(x.get("publiclyAccessible") is True for x in works):
        raise ValueError("SharePlane corpus contains unverified public routes")
    if shareplane.get("publicWorkCount") != len(works) or shareplane.get("verifiedPublicRouteCount") != len(works):
        raise ValueError("SharePlane public corpus count mismatch")
    if len(works) < min_shareplane:
        raise ValueError(f"SharePlane coverage incomplete: {len(works)} < {min_shareplane}")
    records = []
    for x in reader_items:
        if not x.get("title") or not x.get("text") or len(x["text"]) < 100:
            raise ValueError("Reader missing searchable text")
        records.append({
            "id": x["id"], "source": "Readers", "title": x["title"],
            "url": public_url(HOSTS["Readers"], x["url"]),
            "category": x.get("category", "Reader"), "text": x["text"],
            "indexDepth": "full-text",
        })
    for x in works:
        if not x.get("title") or not x.get("canonicalUrl") or not x.get("id"):
            raise ValueError("Published SharePlane Work lacks identity or route")
        fields = [x.get("thesis", ""), x.get("abstract", ""), x.get("text", "")]
        fields += x.get("topics", [])
        text = " ".join(str(v) for v in fields if v).strip()
        if not text:
            raise ValueError("Published SharePlane Work lacks searchable metadata")
        route = public_url(HOSTS["SharePlane"], x["canonicalUrl"])
        if not re.fullmatch(r"https://shareplane\.malott\.ai/(artifacts|market)/[a-z0-9-]+/", route):
            raise ValueError("SharePlane Work has non-canonical public route")
        records.append({
            "id": x["id"], "source": "SharePlane", "title": x["title"],
            "url": route,
            "category": x.get("kind", "Work"), "text": text,
            "indexDepth": "public-corpus",
        })
    ids = [x["id"] for x in records]
    urls = [x["url"] for x in records]
    if len(ids) != len(set(ids)) or len(urls) != len(set(urls)):
        raise ValueError("Duplicate cross-site search identity")
    return {
        "schema": SCHEMA,
        "sources": {
            "Readers": {"count": len(reader_items), "indexDepth": "full-text"},
            "SharePlane": {"count": len(works), "indexDepth": "public-corpus",
                           "sourceCatalogSha256": shareplane.get("sourceCatalogSha256"),
                           "observedAt": shareplane.get("observedAt")},
        },
        "records": sorted(records, key=lambda x: (x["source"], x["title"])),
    }


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--readers", type=Path, required=True)
    parser.add_argument("--shareplane", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--min-readers", type=int, default=1)
    parser.add_argument("--min-shareplane", type=int, default=100)
    args = parser.parse_args()
    result = build(json.loads(args.readers.read_text()), json.loads(args.shareplane.read_text()),
                   min_readers=args.min_readers, min_shareplane=args.min_shareplane,
                   expected_source_sha=args.expected_source_sha)
    args.output.write_text(json.dumps(result, indent=2, ensure_ascii=False) + "\n")
    print(f"PASS unified index: {result['sources']['Readers']['count']} Readers, "
          f"{result['sources']['SharePlane']['count']} SharePlane Works")


if __name__ == "__main__":
    main()
