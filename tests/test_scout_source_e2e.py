"""Three independent offline source-shape qualification cases for Scout."""
import hashlib
import io
import sys
import unittest
from email.message import Message
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_source_collector import collect

class Response:
    status = 200
    def __init__(self, body, content_type):
        self._stream = io.BytesIO(body)
        self.headers = Message()
        self.headers["Content-Type"] = content_type
    def read(self, n):
        return self._stream.read(n)
    def __enter__(self): return self
    def __exit__(self, *args): pass

class Opener:
    def __init__(self, response): self.response = response
    def open(self, request, timeout=8): return self.response

class EndToEndTests(unittest.TestCase):
    def test_arxiv_abstract_metadata(self):
        raw = b'<html><head><meta name="citation_title" content="Independent reasoning"/><meta name="citation_abstract" content="Repeated agent samples may be correlated."/></head><body><nav>Site menu</nav></body></html>'
        packet = collect("https://arxiv.org/abs/2601.19921", Opener(Response(raw, "text/html")))
        self.assertEqual(packet["snapshot_sha256"], hashlib.sha256(raw).hexdigest())
        self.assertIn("correlated", packet["substantive_text"]["excerpt"])
        self.assertNotIn("Site menu", packet["substantive_text"]["excerpt"])
        self.assertFalse(packet["evidence_verified"])
    def test_arxiv_main_fallback(self):
        raw = b'<html><body><header>Navigation</header><main><h1>Human agent knowledge work</h1><p>Authorship remains traceable.</p></main></body></html>'
        packet = collect("https://arxiv.org/abs/2606.09840", Opener(Response(raw, "text/html")))
        self.assertIn("Authorship remains traceable", packet["substantive_text"]["excerpt"])
        self.assertNotIn("Navigation", packet["substantive_text"]["excerpt"])
    def test_readme_negative_control(self):
        raw = b'CPython is the reference implementation of the Python language.'
        packet = collect("https://raw.githubusercontent.com/python/cpython/main/README.rst", Opener(Response(raw, "text/plain")))
        self.assertIn("CPython", packet["substantive_text"]["excerpt"])
        self.assertEqual(packet["recommendation"], "UNASSESSED")
        self.assertIsNone(packet["claims"]["contribution"]["value"])
        self.assertFalse(packet["outreach_authorized"])

if __name__ == "__main__":
    unittest.main()
