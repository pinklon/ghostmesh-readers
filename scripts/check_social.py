#!/usr/bin/env python3
"""Static metadata and byte-exact raster checks for two selected cards."""
from __future__ import annotations

from functools import lru_cache
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import struct
import sys
import zlib

from social_cards import HEIGHT, HOST, WIDTH, SELECTED_KEYS, approval, specs
import hashlib

ROOT = Path(__file__).resolve().parents[1]
REQUIRED_OG = ("og:type", "og:title", "og:description", "og:url", "og:image",
               "og:image:width", "og:image:height", "og:image:alt")
REQUIRED_TWITTER = ("twitter:card", "twitter:image")
PRIVATE = re.compile(rb"/Users/|/private/|BEGIN [A-Z ]*PRIVATE KEY|(?:ghp_|sk-)[A-Za-z0-9_-]{12,}", re.I)
OWNER_SELECTED_ORIGINAL_HASHES = {
    "home": "71e54f781a46749952cc8aa754dfdd4294f021b1a7f4d6a1508b2a68c8145def",
    "the-inbox-was-a-boundary": "5086a14f86fcc604dd83bb2d53c614bf9849ebc91bfbabbfc01c56dfd4389ea3",
}
OWNER_SELECTED_PREVIEW_HASHES = {
    "home": "0cdac0d2c22e4165ae639e4802460ee60662703071947abfca13172b21670a56",
    "the-inbox-was-a-boundary": "7b89cdad4a9851b306cea4c891346d1dddc32cd2af9dd83b66b57e6a878a920e",
}


class Head(HTMLParser):
    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.inside = False
        self.meta: dict[str, list[str]] = {}
        self.canonical: list[str] = []

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        if tag == "head":
            self.inside = True
        if not self.inside:
            return
        values = dict(attrs)
        if tag == "meta":
            key = values.get("property") or values.get("name")
            if key:
                self.meta.setdefault(key, []).append(values.get("content") or "")
        if tag == "link" and values.get("rel") == "canonical":
            self.canonical.append(values.get("href") or "")

    def handle_endtag(self, tag: str) -> None:
        if tag == "head":
            self.inside = False


@lru_cache(maxsize=128)
def png_size(payload: bytes) -> tuple[int, int] | None:
    """Validate the complete, decodable RGB/RGBA PNG, not just its header."""
    if not payload.startswith(b"\x89PNG\r\n\x1a\n"):
        return None
    offset, chunks, compressed = 8, [], bytearray()
    while offset + 12 <= len(payload):
        size = struct.unpack(">I", payload[offset:offset + 4])[0]
        end = offset + size + 12
        if end > len(payload):
            return None
        kind, body = payload[offset + 4:offset + 8], payload[offset + 8:end - 4]
        crc = struct.unpack(">I", payload[end - 4:end])[0]
        if zlib.crc32(kind + body) & 0xffffffff != crc:
            return None
        if kind not in (b"IHDR", b"IDAT", b"IEND", b"tEXt"):
            return None
        if kind == b"tEXt" and body != b"Approval\x00PREVIEW ONLY - NOT APPROVED":
            return None
        chunks.append(kind)
        if kind == b"IDAT":
            compressed.extend(body)
        offset = end
        if kind == b"IEND":
            break
    if offset != len(payload) or chunks[0:1] != [b"IHDR"] or chunks[-1:] != [b"IEND"] or b"IDAT" not in chunks:
        return None
    if struct.unpack(">I", payload[8:12])[0] != 13:
        return None
    width, height, depth, color, compression, filtering, interlace = struct.unpack(">IIBBBBB", payload[16:29])
    if (width, height) != (WIDTH, HEIGHT) or depth != 8 or color not in (2, 6) or (compression, filtering, interlace) != (0, 0, 0):
        return None
    stride = width * (3 if color == 2 else 4) + 1
    try:
        decoder = zlib.decompressobj()
        raw = decoder.decompress(compressed, stride * height + 1)
    except zlib.error:
        return None
    if (len(raw) != stride * height or not decoder.eof or decoder.unused_data
            or any(raw[row * stride] > 4 for row in range(height)) or PRIVATE.search(raw)):
        return None
    return width, height


def check(root: Path = ROOT, release: bool = False) -> list[str]:
    errors: list[str] = []
    for key, expected_hash in OWNER_SELECTED_ORIGINAL_HASHES.items():
        original = root / "content/social-artwork" / f"{key}-original.png"
        if not original.is_file() or hashlib.sha256(original.read_bytes()).hexdigest() != expected_hash:
            errors.append(f"Selected original artwork changed: {key}")
    catalog = json.loads((root / "content/catalog.json").read_text())
    approval(root)
    pages = specs(catalog)
    expected_images = set()
    if set(pages) != {"/", "/the-inbox-was-a-boundary/"}:
        errors.append("Social scope exceeds two selected routes")
    for route, spec in pages.items():
        page = root / "site" / route.strip("/") / "index.html" if route != "/" else root / "site/index.html"
        if not page.is_file():
            errors.append(f"Social page missing: {route}")
            continue
        head = Head()
        head.feed(page.read_text().split("</head>", 1)[0] + "</head>")
        expected = {
            "og:type": spec["kind"], "og:title": spec["title"],
            "og:description": spec["description"], "og:url": HOST + route,
            "og:image": spec["imageUrl"], "og:image:width": str(WIDTH),
            "og:image:height": str(HEIGHT), "og:image:alt": spec["alt"],
            "twitter:card": "summary_large_image", "twitter:image": spec["imageUrl"],
        }
        for key in (*REQUIRED_OG, *REQUIRED_TWITTER):
            if head.meta.get(key) != [expected[key]]:
                errors.append(f"Social metadata {key}: {route}")
        if head.canonical != [HOST + route]:
            errors.append(f"Social canonical mismatch: {route}")
        image = root / "site" / spec["image"].lstrip("/")
        expected_images.add(image)
        if not image.is_file():
            errors.append(f"Social image missing: {spec['image']}")
            continue
        payload = image.read_bytes()
        if len(payload) < 256 or png_size(payload) != (WIDTH, HEIGHT):
            errors.append(f"Social PNG signature or dimensions: {spec['image']}")
        if PRIVATE.search(payload):
            errors.append(f"Private marker in social image: {spec['image']}")
        key = Path(spec["image"]).stem
        selected = root / "content/social-artwork" / f"{key}-1200x630.png"
        if (key not in SELECTED_KEYS or not selected.is_file()
                or hashlib.sha256(selected.read_bytes()).hexdigest() != OWNER_SELECTED_PREVIEW_HASHES[key]
                or payload != selected.read_bytes()):
            errors.append(f"Selected preview art differs from source asset: {spec['image']}")
    actual_images = set((root / "site/social").rglob("*.png"))
    if actual_images != expected_images:
        errors.append("Social image inventory differs from the metadata manifest")
    return errors


if __name__ == "__main__":
    problems = check(release="--release" in sys.argv)
    for problem in problems:
        print("FAIL:", problem)
    if problems:
        raise SystemExit(1)
    print("PASS: two selected social cards, metadata, dimensions, hashes and PNG inventory")
