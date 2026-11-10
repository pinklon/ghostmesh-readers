"""Keep the scoped Reader 47-style presentation and existing source posture."""

from pathlib import Path
import re
import unittest


ROOT = Path(__file__).resolve().parents[1]
SLUG = "when-every-ai-website-looks-good"


class NateHerkReadingPattern(unittest.TestCase):
    def test_reading_and_evidence_sections(self):
        for path in (
            ROOT / "content/readers" / f"{SLUG}.html",
            ROOT / "site" / SLUG / "index.html",
        ):
            with self.subTest(path=path):
                content = path.read_text()
                self.assertIn('id="related-thinking"', content)
                self.assertIn('class="gm-cards"', content)
                self.assertEqual(3, len(re.findall(r'class="gm-related-index"', content)))
                self.assertIn('Corroboration &amp; counterevidence', content)
                self.assertEqual(9, len(re.findall(r'<details id="when-every-ai-website-looks-good--', content)))
                self.assertIn("No independent experiment", content)
                self.assertIn("45% is a conversion rate, not a lift", content)
                self.assertIn('id="published-shareplane-works-proposed-secondary-routes"', content)


if __name__ == "__main__":
    unittest.main()
