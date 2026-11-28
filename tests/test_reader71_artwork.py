"""Reader 71 approved artwork, page placement, listings, and social metadata.

This focused contract uses only Python's standard library, preserving the
two-card social approval contract from issue #45.
"""
from __future__ import annotations
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import struct
import unittest

ROOT = Path(__file__).resolve().parents[1]
SLUG = "claude-lean-and-the-riemann-hypothesis"
ASSET = "/reader71/"


class HeadMetadata(HTMLParser):
    def __init__(self):
        super().__init__()
        self.in_head = False
        self.meta = {}
    def handle_starttag(self, tag, attrs):
        if tag == "head":
            self.in_head = True
        if self.in_head and tag == "meta":
            x = dict(attrs)
            key = x.get("name") or x.get("property")
            self.meta.setdefault(key, []).append(x.get("content"))
    def handle_endtag(self, tag):
        if tag == "head":
            self.in_head = False


class Reader71ArtTest(unittest.TestCase):
    def test_master_and_published_artwork_sha_dimensions(self):
        manifest = json.loads((ROOT / "content/reader-artwork/reader71-art-manifest.json").read_text())
        self.assertEqual(manifest["reader"], "reader:" + SLUG)
        for name, entry in manifest["masters"].items():
            file = ROOT / "content/reader-artwork" / ("reader71-"+("hero" if name=="hero" else "square")+"-original.png")
            data = file.read_bytes()
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])
            self.assertEqual(struct.unpack(">II", data[16:24]), tuple(entry["dimensions"]))
        for name, entry in manifest["published"].items():
            file = ROOT / "site" / entry["url"].lstrip("/")
            data = file.read_bytes()
            self.assertGreater(len(data), 20000)
            self.assertEqual(data[:8], b"\x89PNG\r\n\x1a\n")
            self.assertEqual(struct.unpack(">II", data[16:24]), tuple(entry["dimensions"]))
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["sha256"])

    def test_reader_hero_and_exact_social_head(self):
        src = (ROOT / "site" / SLUG / "index.html").read_text()
        self.assertIn('class="r71-hero-art"', src)
        self.assertEqual(src.count('src="/reader71/hero.png"'), 1)
        self.assertIn('Conceptual editorial artwork, not a mathematically validated plot', src)
        self.assertIn('width="1440" height="810"', src)
        self.assertNotIn('data-gm-aspect=', src)
        self.assertEqual(src.count('gm-reader-footer gm-site-footer'), 1)
        head = HeadMetadata()
        head.feed(src)
        host = "https://youtube.shareplane.malott.ai/reader71/og.png"
        for key, expected in [
            ("og:image", host), ("og:image:width", "1200"),
            ("og:image:height", "630"), ("twitter:image", host),
            ("twitter:card", "summary_large_image")
        ]:
            self.assertEqual(head.meta.get(key), [expected], key)

    def test_home_and_archive_publish_same_cover(self):
        for page in ["site/index.html","site/readers/index.html","site/readers/categories/2/index.html"]:
            markup = (ROOT/page).read_text()
            self.assertEqual(markup.count('src="/reader71/square.png"'), 1, page)
            self.assertIn('class="r71-card-cover"',markup)

    def test_theme_toggle_selects_exactly_one_icon(self):
        source = (ROOT / "content/readers/claude-lean-and-the-riemann-hypothesis.html").read_text()
        self.assertIn('.gm-theme-control .gm-theme-sun{display:block}', source)
        self.assertIn('.gm-theme-control .gm-theme-moon{display:none}', source)
        self.assertIn('html[data-theme="light"] .gm-theme-control .gm-theme-sun{display:none}', source)
        self.assertIn('html[data-theme="light"] .gm-theme-control .gm-theme-moon{display:block}', source)
        self.assertEqual(source.count('class="gm-theme-sun"'), 1)
        self.assertEqual(source.count('class="gm-theme-moon"'), 1)

    def test_social_issue45_scope_unchanged(self):
        from sys import path
        path.insert(0, str(ROOT / "scripts"))
        from social_cards import specs
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        self.assertEqual(set(specs(catalog)), {"/", "/the-inbox-was-a-boundary/"})
        self.assertNotIn("/" + SLUG + "/", specs(catalog))
        self.assertEqual({p.name for p in (ROOT / "site/social/previews").glob("*.png")}, {"home.png", "the-inbox-was-a-boundary.png"})


if __name__ == "__main__":
    unittest.main()
