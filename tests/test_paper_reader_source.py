"""Source-only checks for the proposed paper Reader variant.

The shared generator has not admitted papers yet. These tests protect the draft
input while its schema and projection are integrated after the design freeze.
"""

from html.parser import HTMLParser
from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
PAPER = ROOT / "content/readers/the-experiment-ran-did-the-research-advance.html"
ARXIV = "2607.27191v2"


class SourceScan(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.tags = []
        self.links = []
        self.headings = []
        self._heading = None

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.tags.append((tag, attrs))
        if tag == "a":
            self.links.append(attrs.get("href", ""))
        if tag in {"h1", "h2", "h3"}:
            self._heading = [tag, ""]

    def handle_endtag(self, tag):
        if self._heading and self._heading[0] == tag:
            self.headings.append(tuple(self._heading))
            self._heading = None

    def handle_data(self, data):
        if self._heading:
            self._heading[1] += data


class PaperReaderSourceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.raw = PAPER.read_text()
        cls.scan = SourceScan()
        cls.scan.feed(cls.raw)

    def test_source_is_pinned_and_link_only(self):
        self.assertIn(f"https://arxiv.org/abs/{ARXIV}", self.scan.links)
        self.assertIn(f"https://arxiv.org/html/{ARXIV}", self.scan.links)
        self.assertIn(f"https://arxiv.org/pdf/{ARXIV}", self.scan.links)
        forbidden = {"iframe", "video", "audio", "embed", "object", "source", "track", "canvas"}
        self.assertFalse(forbidden.intersection(tag for tag, _ in self.scan.tags))
        self.assertNotRegex(self.raw, r"data-home-player|data-home-play|data-start|youtube-nocookie|Play original here")
        self.assertFalse(any(name.startswith("on") for _, attrs in self.scan.tags for name in attrs))

    def test_article_keeps_shared_slots_and_visible_source_before_analysis(self):
        for slot in ("HEAD", "CONTROLS", "BRIEF", "EVIDENCE", "RELATED"):
            self.assertEqual(self.raw.count(f"<!--GM_{slot}-->"), 1)
        self.assertLess(self.raw.index("<!--GM_BRIEF-->"), self.raw.index('id="source"'))
        self.assertLess(self.raw.index('id="source"'), self.raw.index('id="interpretation"'))
        self.assertEqual(sum(tag == "main" for tag, _ in self.scan.tags), 1)
        self.assertEqual(sum(tag == "h1" for tag, _ in self.scan.headings), 1)
        self.assertTrue(all(link.startswith(("https://", "/", "#")) for link in self.scan.links))

    def test_editorial_limits_and_public_boundary_are_explicit(self):
        for fact in (
            "two selected", "non-blind", "120 hours", "24 hours", "more GPU time",
            "withheld", "August 7", "August 24", "partial", "not independently verified",
        ):
            self.assertIn(fact.casefold(), self.raw.casefold())
        self.assertNotIn("\u2014", self.raw)
        self.assertNotIn("/Users/", self.raw)
        self.assertNotRegex(self.raw, r"(?i)\.vtt|\.srt|\.webm|signed[_ -]?url")
        self.assertLess(len(re.sub(r"<[^>]+>", "", self.raw)), 15000)


if __name__ == "__main__":
    unittest.main()
