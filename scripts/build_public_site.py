#!/usr/bin/env python3
"""Build the verified static search projection for any static hosting provider.

The canonical publisher feeds are public; no credential or provider setting is
required for a normal build. A mismatch or unavailable feed holds the build.
Independent SharePlane-triggered refresh remains separately commissioned.
"""
import argparse
import os
from pathlib import Path
import shutil
import sys

from .refresh_unified_public_search import refresh
from .project_public_origin import project

CANONICAL_CORPUS = "https://shareplane.malott.ai/native/v3/discovery/public-work-corpus.json"
CANONICAL_CATALOG = "https://shareplane.malott.ai/native/v3/assets/catalog.js"
MIN_READERS = 75
MIN_WORKS = 119


def main(argv=()):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--canonical-output', type=Path,
                        help='New, empty-path destination for the canonical Reader hostname')
    args = parser.parse_args(argv)
    url = os.environ.get("SHAREPLANE_PUBLIC_CORPUS_URL", CANONICAL_CORPUS).strip()
    catalog = os.environ.get("SHAREPLANE_PUBLIC_CATALOG_URL", CANONICAL_CATALOG).strip()
    if url != CANONICAL_CORPUS or catalog != CANONICAL_CATALOG:
        raise SystemExit("Unified search requires the canonical public publisher feeds")
    source = Path("site")
    output = args.canonical_output or source
    if args.canonical_output:
        if output.exists() or output.resolve().is_relative_to(source.resolve()):
            raise SystemExit("Canonical output must be a new location outside site/")
        shutil.copytree(source, output)
    refresh(
        source / "readers/search-index.json",
        url,
        catalog,
        output / "readers/unified-search-index.json",
        MIN_READERS,
        MIN_WORKS,
        source / "catalog.json",
    )
    if args.canonical_output:
        receipt = project(output)
        print(f"PASS canonical origin projection: {len(receipt['files'])} delivery files")


if __name__ == "__main__":
    main(sys.argv[1:])
