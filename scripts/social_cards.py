"""Static social metadata for the two owner-selected issue 45 cards.

Other routes retain their existing metadata until their artwork is selected.
"""
from __future__ import annotations

from html import escape
import json
from pathlib import Path
import re

HOST = "https://youtube.shareplane.malott.ai"
WIDTH, HEIGHT = 1200, 630
SELECTED_KEYS = frozenset({"home", "the-inbox-was-a-boundary"})


def approval(root: Path) -> dict:
    value = json.loads((root / "content/social-approval.json").read_text())
    if (value.get("schema") != "ghostmesh-social-approval-v1"
            or value.get("issue") != "https://github.com/pinklon/ghostmesh-readers/issues/45"
            or value.get("status") != "approved-selected-only"
            or set(value.get("selectedKeys", [])) != SELECTED_KEYS):
        raise ValueError("Issue 45 approval is limited to the two selected cards")
    return value


def specs(catalog: dict) -> dict[str, dict]:
    inbox = next(r for r in catalog["readers"] if r["slug"] == "the-inbox-was-a-boundary")
    values = {
        "/": ("home", "GhostMesh Readers",
              "Original readings that keep public sources, claim evidence and human judgment in view.", "website",
              "GhostMesh Readers: Context Endures. Possibility Evolves."),
        "/the-inbox-was-a-boundary/": ("the-inbox-was-a-boundary", inbox["title"],
              inbox["overview"], "article", "The Inbox Was a Boundary, GhostMesh Readers analysis"),
    }
    return {
        route: {"route": route, "title": title, "description": description,
                "kind": kind, "image": f"/social/previews/{key}.png",
                "imageUrl": f"{HOST}/social/previews/{key}.png", "alt": alt}
        for route, (key, title, description, kind, alt) in values.items()
    }


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
    """Replace only social head tags, preserving all authored article text."""
    match = re.search(r"<head\b[^>]*>.*?</head>", raw, re.I | re.S)
    if not match:
        raise ValueError(f"Missing head for {spec['route']}")
    head = match.group()
    head = re.sub(
        r'<meta\b(?=[^>]*(?:property|name)\s*=\s*["\x27](?:og:|twitter:))[^>]*?/?>',
        "", head, flags=re.I | re.S,
    )
    head = re.sub(r"</head>", tags(spec) + "</head>", head, count=1, flags=re.I)
    return raw[:match.start()] + head + raw[match.end():]
