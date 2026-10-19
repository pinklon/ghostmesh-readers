"""Source identity, opt-in viewer, and public-boundary checks for the paper Reader."""

from html.parser import HTMLParser
from pathlib import Path
import copy
import json
import re
import unittest

from scripts.generate_site import validate_media_source, validate_paper_source


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

    def test_source_is_pinned_with_inert_original_host_viewer(self):
        self.assertIn(f"https://arxiv.org/abs/{ARXIV}", self.scan.links)
        self.assertIn(f"https://arxiv.org/html/{ARXIV}", self.scan.links)
        self.assertIn(f"https://arxiv.org/pdf/{ARXIV}", self.scan.links)
        forbidden = {"video", "audio", "embed", "object", "source", "track", "canvas"}
        self.assertFalse(forbidden.intersection(tag for tag, _ in self.scan.tags))
        frames = [attrs for tag, attrs in self.scan.tags if tag == "iframe"]
        self.assertEqual(len(frames), 1)
        self.assertNotIn("src", frames[0])
        self.assertIn("hidden", frames[0])
        self.assertEqual(frames[0]["referrerpolicy"], "no-referrer")
        self.assertIn("data-paper-frame", frames[0])
        openers = [attrs for tag, attrs in self.scan.tags if tag == "button" and "data-paper-open" in attrs]
        self.assertEqual(len(openers), 1)
        self.assertIn("hidden", openers[0])
        self.assertIn('data-paper-original href="https://arxiv.org/pdf/2607.27191v2"', self.raw)
        self.assertIn('src="/assets/paper-viewer.js"', self.raw)
        self.assertNotRegex(self.raw, r"data-home-player|data-home-play|data-start|youtube-nocookie|Play original here")
        self.assertFalse(any(name.startswith("on") for _, attrs in self.scan.tags for name in attrs))

    def test_article_keeps_shared_slots_and_visible_source_before_analysis(self):
        for slot in ("HEAD", "CONTROLS", "BRIEF", "EVIDENCE", "RELATED"):
            self.assertEqual(self.raw.count(f"<!--GM_{slot}-->"), 1)
        self.assertLess(self.raw.index("<!--GM_BRIEF-->"), self.raw.index('id="source"'))
        self.assertLess(self.raw.index('id="source"'), self.raw.index('id="interpretation"'))
        self.assertEqual(sum(tag == "main" for tag, _ in self.scan.tags), 1)
        self.assertEqual(sum(tag == "h1" for tag, _ in self.scan.headings), 1)
        self.assertTrue(all(link.startswith(("https://", "/", "#", "mailto:")) for link in self.scan.links))

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

    def test_paper_source_identity_rejects_video_fields_and_unpinned_links(self):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        entry = next(r for r in catalog["readers"] if r["slug"] == PAPER.stem)
        source = entry["source"]
        self.assertEqual(source["identity"], "arxiv:" + ARXIV)
        self.assertNotIn("mediaAspect", source)
        self.assertNotIn("platform", source)
        validate_paper_source(self.raw, source)
        for change in (
            {"mediaAspect": "unknown"},
            {"version": "v1"},
            {"url": "https://arxiv.org/abs/2607.27191v1"},
            {"versionDate": "not-a-date"},
        ):
            with self.subTest(change=change), self.assertRaises(ValueError):
                validate_paper_source(self.raw, {**source, **change})
        for marker in ('<iframe src="about:blank"></iframe>', '<div class="player"></div>',
                       '<script src="https://example.test/viewer.js"></script>', '<script>alert(1)</script>'):
            with self.subTest(marker=marker), self.assertRaises(ValueError):
                validate_paper_source(self.raw + marker, copy.deepcopy(source))
        with self.assertRaises(ValueError):
            validate_paper_source(self.raw.replace('data-paper-frame title=', 'data-paper-frame src="https://example.test/copy.pdf" title='), source)
        with self.assertRaises(ValueError):
            validate_paper_source(self.raw.replace('data-paper-frame title=', 'data-paper-frame srcdoc="<h1>copy</h1>" title='), source)
        with self.assertRaises(ValueError):
            validate_paper_source(self.raw.replace('data-paper-original href="https://arxiv.org/pdf/2607.27191v2"',
                                                   'data-paper-original href="https://example.test/copy.pdf"'), source)

    def test_schema_discriminates_paper_from_legacy_media(self):
        schema = json.loads((ROOT / "content/catalog.schema.json").read_text())
        source_rule = schema["$defs"]["reader"]["properties"]["source"]
        self.assertEqual(source_rule["oneOf"], [
            {"$ref": "#/$defs/mediaSource"}, {"$ref": "#/$defs/paperSource"}
        ])
        self.assertEqual(schema["$defs"]["paperSource"]["properties"]["kind"], {"const": "paper"})
        self.assertFalse(schema["$defs"]["paperSource"]["additionalProperties"])
        self.assertEqual(schema["$defs"]["mediaSource"]["not"], {"required": ["kind"]})
        self.assertFalse(schema["$defs"]["mediaSource"]["additionalProperties"])
        self.assertNotIn("identity", schema["$defs"]["mediaSource"]["properties"])

    def test_media_source_rejects_paper_fields_without_affecting_legacy_records(self):
        catalog = json.loads((ROOT / "content/catalog.json").read_text())
        media = [r["source"] for r in catalog["readers"] if r["source"].get("kind") != "paper"]
        for source in media:
            validate_media_source(source)
        for extra in ("identity", "htmlUrl", "pdfUrl", "authors", "publisher", "version", "versionDate"):
            with self.subTest(extra=extra), self.assertRaises(ValueError):
                validate_media_source({**media[0], extra: "paper metadata"})

    def test_generated_paper_keeps_shared_brief_and_no_media_controls(self):
        rendered = (ROOT / "site" / PAPER.stem / "index.html").read_text()
        self.assertIn("What the paper studied", rendered)
        self.assertIn('id="external-evidence"', rendered)
        self.assertIn('id="related-thinking"', rendered)
        self.assertIn("External study / outside the Reader graph", rendered)
        self.assertIn("No local Reader examines these two shadow evaluations", rendered)
        self.assertIn('href="https://proceedings.mlr.press/v267/wijk25a.html"', rendered)
        self.assertIn('href="https://arxiv.org/abs/2504.08066"', rendered)
        self.assertIn('data-gm-share=""', rendered)
        self.assertNotIn("data-home-player", rendered)
        self.assertNotIn("data-gm-aspect", rendered)
        paper = json.loads((ROOT / "content/catalog.json").read_text())["readers"][-1]
        self.assertEqual(paper['relationships'], [])
        validate_paper_source(rendered, paper['source'])


if __name__ == "__main__":
    unittest.main()
