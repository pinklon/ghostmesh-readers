"""Reader #49 mechanical preservation tests. Not independent editorial review."""
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_reader46_creative_lock import (
    missing_link_targets, missing_locked_blocks, normal, ordered_blocks_present,
)

ROOT = Path(__file__).resolve().parents[1]
SLUG = "offline-is-not-the-same-as-independent"
MANUSCRIPT_SHA = "25142c43241651adb1f0a916b644a855c135ee42154bbba674359dac1fac3132"
SOURCE_AID_SHA = "02f3dfb6203fb35dfac580a632af1e805053e31bde5d6f459b5c606ac51cee17"
TARGETS = [
    "https://youtube.shareplane.malott.ai/the-boundary-is-bigger-than-the-box/",
    "https://youtube.shareplane.malott.ai/the-stop-button-is-outside-the-chat/",
    "https://shareplane.malott.ai/artifacts/your-second-brain-is-not-a-production-architecture/",
]


def required_blocks(markdown):
    """All locked prose, list items and source limits, excluding duplicated headings."""
    blocks = []
    for chunk in markdown.strip().split("\n\n"):
        if chunk.startswith("#"):
            continue
        if chunk.startswith("- "):
            blocks.extend(line[2:] for line in chunk.splitlines())
        else:
            blocks.append(chunk)
    return blocks


class Reader49CreativeLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manuscript = (ROOT / f"content/drafts/{SLUG}.lock.md").read_text()
        cls.authored = (ROOT / f"content/readers/{SLUG}.html").read_text()
        cls.page = (ROOT / f"site/{SLUG}/index.html").read_text()
        cls.source_map = json.loads((ROOT / f"content/source-maps/{SLUG}.json").read_text())
        cls.catalog = next(r for r in json.loads((ROOT / "content/catalog.json").read_text())["readers"] if r["slug"] == SLUG)
        cls.blocks = required_blocks(cls.manuscript)

    def test_exact_lock_digest(self):
        self.assertEqual(MANUSCRIPT_SHA, hashlib.sha256(self.manuscript.encode()).hexdigest())

    def test_complete_copy_and_order(self):
        self.assertEqual([], missing_locked_blocks(self.blocks, self.authored))
        self.assertEqual([], missing_locked_blocks(self.blocks, self.page))
        self.assertTrue(ordered_blocks_present(self.blocks, self.page))

    def test_omission_and_compression_fail(self):
        block = "The presentation is theatrical. The underlying engineering is more interesting."
        self.assertIn(block, self.blocks)
        exact = "<p>The presentation is theatrical. The underlying engineering is more\ninteresting.</p>"
        self.assertIn(exact, self.page)
        for replacement in ["", "<p>Interesting demonstration.</p>"]:
            changed = self.page.replace(exact, replacement, 1)
            self.assertEqual([block], missing_locked_blocks([block], changed))
            self.assertFalse(ordered_blocks_present(self.blocks, changed))

    def test_wrong_relationship_destination_fails(self):
        first = TARGETS[0]
        self.assertEqual([], missing_link_targets([first], self.page))
        changed = re.sub('href="' + re.escape(first) + '"', 'href="/wrong-target/"', self.page)
        self.assertNotEqual(self.page, changed)
        self.assertEqual([first], missing_link_targets([first], changed))

    def test_source_map_coverage_and_correct_performance_cue(self):
        self.assertEqual(SOURCE_AID_SHA, self.source_map["sourceAidSha256"])
        self.assertEqual("UXaET1n3i7I", self.source_map["sourceId"])
        mapped = {claim for point in self.source_map["points"] for claim in point["claimIds"]}
        self.assertEqual({c["id"] for c in self.catalog["claims"]}, mapped)
        performance = next(p for p in self.source_map["points"] if "claim-3" in p["claimIds"][0])
        self.assertEqual(146, performance["atSeconds"])
        self.assertIn('data-seek="146"', self.page)
        for point in self.source_map["points"]:
            self.assertIn('id="' + point["sectionId"] + '"', self.page)

    def test_approved_links_and_source_privacy(self):
        self.assertEqual([], missing_link_targets(TARGETS, self.page))
        for forbidden in ["reasonpack-private/", "/home/tony-malott/", "transcript.vtt", "transcript.txt"]:
            self.assertNotIn(forbidden, self.page)
        self.assertIn("Source scope and limitations", self.page)
        self.assertIn('id="external-evidence"', self.page)


if __name__ == "__main__":
    unittest.main()
