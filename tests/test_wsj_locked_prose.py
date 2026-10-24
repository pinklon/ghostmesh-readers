"""Guard the owner supplied analysis against silent compression or rewriting."""

from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import unittest


ROOT = Path(__file__).resolve().parents[1]
ARTICLE = ROOT / "content/readers/the-missing-step-is-not-more-intelligence.html"
LOCKED_BLOCKS_SHA256 = "73ec70e5a5b327ec9796ef3b7db5b4e5022c91cc7d94214af390316a3fa0871e"


class LockedBlocks(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.active = None
        self.text = ""
        self.blocks = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        key = attrs.get("data-locked-paragraph", attrs.get("data-locked-heading"))
        if key is not None:
            self.active = int(key)
            self.text = ""

    def handle_data(self, data):
        if self.active is not None:
            self.text += data

    def handle_endtag(self, tag):
        if self.active is not None and tag in {"h2", "p"}:
            self.blocks.append((self.active, self.text))
            self.active = None


class WsjLockedProseTest(unittest.TestCase):
    def test_owner_supplied_analysis_is_exact_and_complete(self):
        source = ARTICLE.read_text()
        parsed = LockedBlocks()
        parsed.feed(source)
        self.assertEqual([index for index, _ in parsed.blocks], list(range(1, 23)))
        serialized = json.dumps(
            [text for _, text in parsed.blocks], ensure_ascii=False, separators=(",", ":")
        ).encode()
        self.assertEqual(hashlib.sha256(serialized).hexdigest(), LOCKED_BLOCKS_SHA256)
        self.assertNotIn("Draft deconstruction:", source)
        self.assertNotIn("This is a private draft", source)


if __name__ == "__main__":
    unittest.main()
