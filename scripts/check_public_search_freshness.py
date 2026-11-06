#!/usr/bin/env python3
"""Determine whether the published Reader index lags the public Works corpus.

Exit codes: 0 = current, 10 = verified source changed, 1 = invalid source.
A failed source check never triggers a deployment.
"""
import argparse
import hashlib
import json
import sys
from urllib.error import HTTPError

from .refresh_unified_public_search import fetch_shareplane_bytes


def needs_refresh(corpus_url, catalog_url, deployed_index_url):
    catalog = fetch_shareplane_bytes(catalog_url)
    source_sha = hashlib.sha256(catalog).hexdigest()
    corpus = json.loads(fetch_shareplane_bytes(corpus_url))
    if corpus.get("schemaVersion") != "shareplane.reader-public-works-snapshot.v1":
        raise ValueError("Unsupported public corpus")
    if corpus.get("sourceCatalogSha256") != source_sha:
        raise ValueError("Public corpus and current catalog differ")
    works = corpus.get("records")
    if (not isinstance(works, list) or len(works) < 114 or
            corpus.get("publicWorkCount") != len(works) or
            corpus.get("verifiedPublicRouteCount") != len(works) or
            not all(row.get("publiclyAccessible") is True for row in works)):
        raise ValueError("Public corpus qualification or coverage incomplete")
    # Fetch only same-origin Readers static output, not an arbitrary endpoint.
    from urllib.parse import urlparse
    from urllib.request import urlopen
    parsed = urlparse(deployed_index_url)
    if parsed.scheme != "https" or parsed.netloc != "youtube.shareplane.malott.ai":
        raise ValueError("Unexpected deployed Reader index host")
    try:
        with urlopen(deployed_index_url, timeout=25) as response:
            deployed = json.loads(response.read(16 * 1024 * 1024))
    except HTTPError as error:
        if error.code == 404:
            return True
        raise
    except json.JSONDecodeError:
        # Some static hosts serve the HTML fallback at an absent JSON route.
        return True
    return (deployed.get("schema") != "ghostmesh-unified-search-v1" or
            deployed.get("sources", {}).get("SharePlane", {}).get("sourceCatalogSha256") != source_sha or
            deployed.get("sources", {}).get("SharePlane", {}).get("count") != len(works))


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--corpus-url", required=True)
    parser.add_argument("--catalog-url", default="https://shareplane.malott.ai/native/v3/assets/catalog.js")
    parser.add_argument("--index-url", default="https://youtube.shareplane.malott.ai/readers/unified-search-index.json")
    args = parser.parse_args()
    try:
        changed = needs_refresh(args.corpus_url, args.catalog_url, args.index_url)
    except Exception as error:
        print(f"BLOCK source reconciliation: {error}", file=sys.stderr)
        return 1
    if changed:
        print("NEEDS_REFRESH verified published Works source differs")
        return 10
    print("CURRENT published unified search matches Works source")
    return 0


if __name__ == "__main__":
    sys.exit(main())
