#!/usr/bin/env python3
"""Netlify static build entrypoint for unified public search.

The publisher supplies SHAREPLANE_PUBLIC_CORPUS_URL only after its public
snapshot and route qualification are commissioned. An unset URL keeps the
existing Reader-only preview functional until that handoff is accepted.
"""
import os
from pathlib import Path

from .refresh_unified_public_search import refresh


def main():
    url = os.environ.get("SHAREPLANE_PUBLIC_CORPUS_URL", "").strip()
    required = os.environ.get("SHAREPLANE_UNIFIED_SEARCH_REQUIRED", "").lower() == "true"
    if not url:
        if required:
            raise SystemExit("Public SharePlane corpus URL is required for production search")
        print("Public corpus not configured: Reader-only fallback retained")
        return
    refresh(
        Path("site/readers/search-index.json"),
        url,
        os.environ.get("SHAREPLANE_PUBLIC_CATALOG_URL",
                       "https://shareplane.malott.ai/native/v3/assets/catalog.js"),
        Path("site/readers/unified-search-index.json"),
        40,
        114,
    )


if __name__ == "__main__":
    main()
