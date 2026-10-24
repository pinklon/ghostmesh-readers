"""Scope and failure checks for the two selected issue 45 social cards."""
import json
import shutil
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_social import check, png_size
from social_cards import HOST, approval, specs


class SelectedSocialCards(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "content").mkdir()
        for name in ("catalog.json", "social-approval.json"):
            shutil.copy2(ROOT / "content" / name, self.root / "content" / name)
        shutil.copytree(ROOT / "content/social-artwork", self.root / "content/social-artwork")
        (self.root / "site/social").mkdir(parents=True)
        shutil.copytree(ROOT / "site/social/previews", self.root / "site/social/previews")
        shutil.copy2(ROOT / "site/index.html", self.root / "site/index.html")
        shutil.copytree(ROOT / "site/the-inbox-was-a-boundary", self.root / "site/the-inbox-was-a-boundary")

    def tearDown(self):
        self.tmp.cleanup()

    def test_only_selected_cards_pass_technical_gate(self):
        self.assertEqual([], check(self.root, release=True))
        pages = specs(json.loads((self.root / "content/catalog.json").read_text()))
        self.assertEqual({"/", "/the-inbox-was-a-boundary/"}, set(pages))
        self.assertEqual(HOST + "/social/previews/home.png", pages["/"]["imageUrl"])

    def test_extra_placeholder_or_changed_owner_scope_fails(self):
        extra = self.root / "site/social/previews/unapproved.png"
        extra.write_bytes((self.root / "site/social/previews/home.png").read_bytes())
        self.assertIn("Social image inventory", " ".join(check(self.root)))
        extra.unlink()
        record = json.loads((self.root / "content/social-approval.json").read_text())
        record["selectedKeys"].append("unapproved")
        (self.root / "content/social-approval.json").write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "limited to the two"):
            approval(self.root)

    def test_missing_image_or_wrong_url_fails(self):
        image = self.root / "site/social/previews/home.png"
        image.unlink()
        self.assertIn("Social image missing", " ".join(check(self.root)))
        shutil.copy2(ROOT / "site/social/previews/home.png", image)
        page = self.root / "site/index.html"
        page.write_text(page.read_text().replace(
            HOST + "/social/previews/home.png", "https://external.example/card.png"))
        self.assertIn("Social metadata og:image", " ".join(check(self.root)))

    def test_corrupt_or_swapped_selected_asset_fails(self):
        image = self.root / "site/social/previews/home.png"
        original = image.read_bytes()
        for payload in (b"not a PNG" + original, original[:-1] + bytes([original[-1] ^ 1])):
            image.write_bytes(payload)
            self.assertIsNone(png_size(payload))
            self.assertIn("Social PNG signature", " ".join(check(self.root)))
        image.write_bytes((self.root / "site/social/previews/the-inbox-was-a-boundary.png").read_bytes())
        self.assertIn("Selected preview art differs", " ".join(check(self.root)))

    def test_original_swap_and_private_png_metadata_fail(self):
        original = self.root / "content/social-artwork/home-original.png"
        original.write_bytes(b"substitute")
        self.assertIn("Selected original artwork changed", " ".join(check(self.root)))
        shutil.copy2(ROOT / "content/social-artwork/home-original.png", original)
        image = self.root / "site/social/previews/home.png"
        payload = image.read_bytes()
        body = b"Source\x00\x00" + zlib.compress(b"/Users/private/transcript-source.txt")
        kind = b"zTXt"
        chunk = struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
        image.write_bytes(payload[:33] + chunk + payload[33:])
        self.assertIn("Social PNG signature", " ".join(check(self.root)))


if __name__ == "__main__":
    unittest.main()
