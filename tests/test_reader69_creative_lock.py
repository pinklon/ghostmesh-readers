"""Reader #69 Creative Lock assertions on authored and projected HTML."""
from hashlib import sha256
from html import unescape
from pathlib import Path
import re
import unittest

from test_reader46_creative_lock import missing_link_targets

ROOT = Path(__file__).resolve().parents[1]
SLUG = "the-cheap-answer-can-be-an-expensive-job"
SOURCE = "https://www.youtube.com/watch?v=gCK2hv9De5U"
LOCKED_TEXT = "fe6f67d80821327efb77285ebd75d30a3f857fa79b36f9f2bec26aa878b64de7"
BLOCK = re.compile(r"<(h[12]|p)\b[^>]*\bdata-locked-block\b[^>]*>(.*?)</\1>", re.S)


def locked_text(raw):
    # Ordered public manuscript only. Excludes instructions and source/cue
    # bookkeeping outside the lock markers, plus generated site furniture.
    return [unescape(re.sub(r"<[^>]+>", "", value)) for _, value in BLOCK.findall(raw)]


def matches_lock(raw):
    text = locked_text(raw)
    return len(text) == 44 and sha256("\n\n".join(text).encode()).hexdigest() == LOCKED_TEXT


class Reader69CreativeLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.authored = (ROOT / f"content/readers/{SLUG}.html").read_text()
        cls.page = (ROOT / f"site/{SLUG}/index.html").read_text()

    def test_authored_and_generated_text_match_the_verified_public_blocks(self):
        for page in (self.authored, self.page):
            with self.subTest(generated=page is self.page):
                self.assertTrue(matches_lock(page))
                self.assertIn(f'<a href="{SOURCE}">Watch the original</a>', page)

    def test_omission_compression_and_reordering_do_not_pass(self):
        matches = list(BLOCK.finditer(self.page))
        a, b = matches[4:6]
        reordered = self.page[:a.start()] + b[0] + self.page[a.end():b.start()] + a[0] + self.page[b.end():]
        for changed in (
            self.page.replace(matches[-1][0], "", 1),
            self.page.replace(matches[3][0], "<p data-locked-block>Watch.</p>", 1),
            reordered,
        ):
            self.assertFalse(matches_lock(changed))

    def test_single_column_evidence_intro_is_not_sticky(self):
        # The shared reader-refresh.css intentionally makes evidence intros
        # sticky in two-column layouts. Reader 69 uses a single column.
        override = ".r69-main .gm-evidence-intro { position: static; top: auto; align-self: stretch;"
        for page in (self.authored, self.page):
            self.assertIn(override, page)

    def test_locked_source_and_approved_reader_destinations(self):
        targets = [
            SOURCE,
            "https://www.vals.ai/models/openai_gpt-6.2-astra",
            "https://openai.com/index/introducing-gpt-6-2-astra-sol/",
            "/the-best-model-shouldnt-do-every-job/",
            "/the-machine-is-learning-to-improve-the-machine/",
        ]
        self.assertEqual([], missing_link_targets(targets, self.page))
        self.assertNotIn("the-most-expensive-model-is-often-compensation-for-missing-control", self.page)
        for target in targets:
            with self.subTest(target=target):
                wrong = self.page.replace(f'href="{target}"', 'href="/wrong/"')
                self.assertEqual([target], missing_link_targets(targets, wrong))


if __name__ == "__main__":
    unittest.main()
