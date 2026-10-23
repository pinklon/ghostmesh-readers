import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_html_extract import extract

class HtmlExtractTests(unittest.TestCase):
    def test_metadata(self):
        doc = '<html><head><meta name="citation_title" content="Paper A"><meta name="citation_abstract" content="A testable method"></head><body><nav>noise</nav></body></html>'
        result = extract(doc)
        self.assertEqual(result["title"], "Paper A")
        self.assertEqual(result["excerpt"], "A testable method")
    def test_no_bogus_evidence(self):
        self.assertEqual(extract("<nav>Menu</nav><footer>Legal</footer>")["extraction_status"], "INSUFFICIENT")
    def test_main_without_navigation(self):
        result = extract("<nav>Skip</nav><main><p>Actual research</p></main><footer>Noise</footer>")
        self.assertIn("Actual research", result["excerpt"])
        self.assertNotIn("Skip", result["excerpt"])
    def test_description_fallback(self):
        result = extract('<meta name="description" content="A useful source">')
        self.assertEqual(result["excerpt"], "A useful source")
if __name__ == "__main__":
    unittest.main()
