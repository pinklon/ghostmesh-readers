"""Issue 45 social metadata and diagnostic preview PNGs.

The raster output is deliberately marked PREVIEW ONLY. It is engineering
scaffolding, not owner-approved GhostMesh artwork.
"""
from __future__ import annotations

import hashlib
from html import escape
import json
from pathlib import Path
import re
import struct
import zlib

HOST = "https://youtube.shareplane.malott.ai"
WIDTH, HEIGHT = 1200, 630
PREVIEW_PREFIX = "/social/previews/"
OWNER_SELECTED_PREVIEW_KEYS = frozenset({"home", "the-inbox-was-a-boundary"})
CATEGORIES = ["AI & Technology", "Society & Politics", "Science", "Business", "Ethics & Culture", "Other"]


def approval(root: Path) -> dict:
    value = json.loads((root / "content/social-approval.json").read_text())
    if value.get("schema") != "ghostmesh-social-approval-v1" or value.get("issue") != "https://github.com/pinklon/ghostmesh-readers/issues/45":
        raise ValueError("Invalid social approval record")
    # This branch contains no final-art approval mechanism. A later reviewed
    # change must implement Tony's exact approval before Production can open.
    if value.get("status") != "pending":
        raise ValueError("Final social artwork requires a separate owner-approved release change")
    preview_base = value.get("previewBaseUrl")
    if preview_base is not None and (not isinstance(preview_base, str)
                                     or not re.fullmatch(r"https://[a-z0-9-]+\.netlify\.app", preview_base)):
        raise ValueError("Invalid Netlify preview base URL")
    return value


def specs(catalog: dict, preview_base: str | None = None) -> dict[str, dict]:
    count = len(catalog["readers"])
    values = {
        "/": ("home", "GhostMesh Readers", "Original readings that keep public sources, claim evidence and human judgment in view.", "website"),
        "/readers/": ("readers", "The Reader library", f"Browse all {count} public Readers and their source-grounded analysis.", "website"),
        "/knowledge/": ("knowledge", "Public knowledge data", f"Inspect source-only knowledge records for {count} public Readers.", "website"),
        "/map/": ("map", "Reader relationship map", "Explore qualified editorial routes between public Readers.", "website"),
    }
    for index, category in enumerate(CATEGORIES):
        values[f"/readers/categories/{index}/"] = (
            f"category-{index}", f"{category} Readers",
            f"Browse GhostMesh Readers in {category}.", "website",
        )
    for reader in catalog["readers"]:
        values[f"/{reader['slug']}/"] = (
            reader["slug"], reader["title"], reader["overview"], "article",
        )
    result = {}
    for route, (key, title, description, kind) in values.items():
        if not title or not description or "\u2014" in title + description:
            raise ValueError(f"Invalid public social text for {route}")
        result[route] = {
            "route": route, "title": title, "description": description,
            "kind": kind, "image": PREVIEW_PREFIX + key + ".png",
            "imageUrl": (preview_base or HOST) + PREVIEW_PREFIX + key + ".png",
            "alt": f"PREVIEW ONLY, unapproved GhostMesh social card for {title}",
        }
    return result


def tags(spec: dict) -> str:
    url = HOST + spec["route"]
    image = spec["imageUrl"]
    properties = [
        ("og:type", spec["kind"]), ("og:title", spec["title"]),
        ("og:description", spec["description"]), ("og:url", url),
        ("og:image", image), ("og:image:width", str(WIDTH)),
        ("og:image:height", str(HEIGHT)), ("og:image:alt", spec["alt"]),
    ]
    output = "".join(f'<meta property="{key}" content="{escape(value, quote=True)}">' for key, value in properties)
    output += '<meta name="twitter:card" content="summary_large_image">'
    output += f'<meta name="twitter:image" content="{escape(image, quote=True)}">'
    return output


def inject(raw: str, spec: dict) -> str:
    """Replace only social head tags, preserving existing editorial meta text."""
    match = re.search(r"<head\b[^>]*>.*?</head>", raw, re.I | re.S)
    if not match:
        raise ValueError(f"Missing head for {spec['route']}")
    head = match.group()
    head = re.sub(
        r'<meta\b(?=[^>]*(?:property|name)\s*=\s*["\'](?:og:|twitter:))[^>]*?/?>',
        "", head, flags=re.I | re.S,
    )
    head = re.sub(r"(?m)^[ \t]+$", "", head)
    head = re.sub(r"</head>", tags(spec) + "</head>", head, count=1, flags=re.I)
    return raw[:match.start()] + head + raw[match.end():]


# A small diagnostic font for the fixed placeholder label. This is not a
# GhostMesh visual template and must not be promoted as finished artwork.
GLYPHS = {
    " ": ["00000"] * 7,
    "A": ["01110","10001","10001","11111","10001","10001","10001"],
    "D": ["11110","10001","10001","10001","10001","10001","11110"],
    "E": ["11111","10000","10000","11110","10000","10000","11111"],
    "I": ["11111","00100","00100","00100","00100","00100","11111"],
    "L": ["10000","10000","10000","10000","10000","10000","11111"],
    "N": ["10001","11001","10101","10011","10001","10001","10001"],
    "O": ["01110","10001","10001","10001","10001","10001","01110"],
    "P": ["11110","10001","10001","11110","10000","10000","10000"],
    "R": ["11110","10001","10001","11110","10100","10010","10001"],
    "S": ["01111","10000","10000","01110","00001","00001","11110"],
    "T": ["11111","00100","00100","00100","00100","00100","00100"],
    "U": ["10001","10001","10001","10001","10001","10001","01110"],
    "V": ["10001","10001","10001","10001","10001","01010","00100"],
    "W": ["10001","10001","10001","10101","10101","10101","01010"],
    "Y": ["10001","10001","01010","00100","00100","00100","00100"],
    "4": ["00110","01010","10010","11111","00010","00010","00010"],
    "5": ["11111","10000","11110","00001","00001","10001","01110"],
}


def _chunk(kind: bytes, content: bytes) -> bytes:
    return struct.pack(">I", len(content)) + kind + content + struct.pack(">I", zlib.crc32(kind + content) & 0xffffffff)


def preview_png(spec: dict) -> bytes:
    """Render a unique, visibly unapproved 1200x630 engineering placeholder."""
    pixels = bytearray(bytes((12, 13, 17)) * WIDTH * HEIGHT)

    def rect(x: int, y: int, width: int, height: int, color: tuple[int, int, int]) -> None:
        row = bytes(color) * width
        for yy in range(y, y + height):
            start = (yy * WIDTH + x) * 3
            pixels[start:start + width * 3] = row

    def label(value: str, x: int, y: int, scale: int, color: tuple[int, int, int]) -> None:
        for char in value:
            glyph = GLYPHS[char]
            for gy, row in enumerate(glyph):
                for gx, bit in enumerate(row):
                    if bit == "1":
                        rect(x + gx * scale, y + gy * scale, scale, scale, color)
            x += 6 * scale

    rect(0, 0, WIDTH, 20, (194, 16, 46))
    rect(0, HEIGHT - 20, WIDTH, 20, (194, 16, 46))
    rect(56, 70, 190, 8, (194, 16, 46))
    label("ISSUE 45", 60, 98, 6, (245, 246, 248))
    label("PREVIEW ONLY", 60, 210, 12, (245, 246, 248))
    label("NOT APPROVED", 60, 335, 10, (237, 84, 105))
    digest = hashlib.sha256(json.dumps(spec, sort_keys=True).encode()).digest()
    for index, byte in enumerate(digest):
        rect(60 + index * 32, 515, 18, 15 + byte % 55, (194, 16, 46) if byte % 2 else (245, 246, 248))
    scanlines = b"".join(b"\x00" + pixels[y * WIDTH * 3:(y + 1) * WIDTH * 3] for y in range(HEIGHT))
    ihdr = struct.pack(">IIBBBBB", WIDTH, HEIGHT, 8, 2, 0, 0, 0)
    return (b"\x89PNG\r\n\x1a\n" + _chunk(b"IHDR", ihdr)
            + _chunk(b"tEXt", b"Approval\x00PREVIEW ONLY - NOT APPROVED")
            + _chunk(b"IDAT", zlib.compress(scanlines, 9)) + _chunk(b"IEND", b""))


def asset_outputs(catalog: dict, preview_base: str | None = None) -> dict[str, bytes]:
    output = {}
    artwork = Path(__file__).resolve().parents[1] / "content/social-artwork"
    for spec in specs(catalog, preview_base=preview_base).values():
        key = Path(spec["image"]).stem
        output[spec["image"].lstrip("/")] = (
            (artwork / f"{key}-1200x630.png").read_bytes()
            if key in OWNER_SELECTED_PREVIEW_KEYS else preview_png(spec)
        )
    return output
