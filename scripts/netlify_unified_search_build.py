#!/usr/bin/env python3
"""Build the verified static search projection in the existing Netlify Git build.

The canonical publisher feeds are public; no credential or provider setting is
required for a normal build. A mismatch or unavailable feed holds the build.
Independent SharePlane-triggered refresh remains separately commissioned.
"""
import os
from pathlib import Path

from .refresh_unified_public_search import refresh

CANONICAL_CORPUS = "https://shareplane.malott.ai/native/v3/discovery/public-work-corpus.json"
CANONICAL_CATALOG = "https://shareplane.malott.ai/native/v3/assets/catalog.js"
MIN_READERS = 75
MIN_WORKS = 119


def main():
    url = os.environ.get("SHAREPLANE_PUBLIC_CORPUS_URL", CANONICAL_CORPUS).strip()
    catalog = os.environ.get("SHAREPLANE_PUBLIC_CATALOG_URL", CANONICAL_CATALOG).strip()
    if url != CANONICAL_CORPUS or catalog != CANONICAL_CATALOG:
        raise SystemExit("Unified search requires the canonical public publisher feeds")
    refresh(
        Path("site/readers/search-index.json"),
        url,
        catalog,
        Path("site/readers/unified-search-index.json"),
        MIN_READERS,
        MIN_WORKS,
        Path("site/catalog.json"),
    )


if __name__ == "__main__":
    main()
