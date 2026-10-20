"""Failure modes for issue 45 metadata, image files, and owner approval."""
import shutil
import json
import struct
import sys
import tempfile
import unittest
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from check_social import check, png_size
from social_cards import approval, specs


class SocialPreviewGate(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        (self.root / "content").mkdir()
        for name in ("catalog.json", "social-approval.json"):
            shutil.copy2(ROOT / "content" / name, self.root / "content" / name)
        shutil.copytree(ROOT / "site", self.root / "site")

    def tearDown(self):
        self.tmp.cleanup()

    def test_provisional_pages_pass_technical_gate_but_fail_release(self):
        self.assertEqual([], check(self.root))
        self.assertIn("Owner creative approval", " ".join(check(self.root, release=True)))

    def test_missing_image_and_wrong_url_are_rejected(self):
        image = self.root / "site/social/previews/home.png"
        image.unlink()
        self.assertIn("Social image missing", " ".join(check(self.root)))
        page = self.root / "site/index.html"
        page.write_text(page.read_text().replace(
            "https://youtube.shareplane.malott.ai/social/previews/home.png",
            "https://external.example/card.png"))
        self.assertIn("Social metadata og:image", " ".join(check(self.root)))

    def test_bad_signature_dimensions_and_crc_are_rejected(self):
        image = self.root / "site/social/previews/home.png"
        original = image.read_bytes()
        for payload in (b"not a PNG" + original, original[:16] + b"\x00\x00\x00\x01" + original[20:],
                        original[:-1] + bytes([original[-1] ^ 1])):
            with self.subTest(payload=payload[:20]):
                image.write_bytes(payload)
                self.assertIsNone(png_size(payload))
                self.assertIn("Social PNG signature or dimensions", " ".join(check(self.root)))

    def test_private_metadata_and_removed_preview_marker_are_rejected(self):
        image = self.root / "site/social/previews/home.png"
        original = image.read_bytes()
        image.write_bytes(original + b"/Users/private/source")
        self.assertIn("Private marker", " ".join(check(self.root)))
        image.write_bytes(original.replace(b"PREVIEW ONLY - NOT APPROVED", b"DRAFT ONLY - NOT APPROVED"))
        self.assertIn("Provisional image lacks", " ".join(check(self.root)))

    def test_compressed_private_png_metadata_is_rejected(self):
        image = self.root / "site/social/previews/home.png"
        original = image.read_bytes()
        body = b"Source\x00\x00" + zlib.compress(b"/Users/private/transcript-source.txt")
        kind = b"zTXt"
        chunk = struct.pack(">I", len(body)) + kind + body + struct.pack(">I", zlib.crc32(kind + body))
        image.write_bytes(original[:33] + chunk + original[33:])
        self.assertIn("Social PNG signature or dimensions", " ".join(check(self.root)))

    def test_final_art_cannot_be_self_approved_in_manifest(self):
        path = self.root / "content/social-approval.json"
        record = json.loads(path.read_text())
        record["status"] = "approved"
        record["approvalCommentUrl"] = "https://github.com/pinklon/ghostmesh-readers/issues/45#issuecomment-6303394081"
        path.write_text(json.dumps(record))
        with self.assertRaisesRegex(ValueError, "separate owner-approved release change"):
            approval(self.root)

    def test_preview_image_url_uses_actual_netlify_base(self):
        catalog = json.loads((self.root / "content/catalog.json").read_text())
        example = specs(catalog, preview_base="https://deploy-preview-45--readers.netlify.app")["/"]
        self.assertEqual("https://deploy-preview-45--readers.netlify.app/social/previews/home.png", example["imageUrl"])


if __name__ == "__main__":
    unittest.main()
