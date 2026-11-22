"""No-network tests for bounded Scout source collector."""
import io
import sys
import unittest
from email.message import Message
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_source_collector import collect
from scout_evidence_intake import MAX_BYTES

class Response:
    status = 200
    def __init__(self, body=b"Public research source", kind="text/plain"):
        self.stream = io.BytesIO(body)
        self.headers = Message()
        self.headers["Content-Type"] = kind
    def read(self, count):
        return self.stream.read(count)
    def __enter__(self):
        return self
    def __exit__(self, *args):
        pass

class Opener:
    def __init__(self, response):
        self.response = response
        self.calls = 0
    def open(self, request, timeout):
        self.calls += 1
        return self.response

class CollectorTests(unittest.TestCase):
    def test_allowed_public_source(self):
        opener = Opener(Response())
        result = collect("https://arxiv.org/abs/2601.19921", opener)
        self.assertEqual(opener.calls, 1)
        self.assertFalse(result["evidence_verified"])
        self.assertFalse(result["outreach_authorized"])
    def test_reject_private_or_unapproved(self):
        for url in ("https://127.0.0.1/a", "https://example.org/a",
                    "http://arxiv.org/a", "https://arxiv.org:8443/a",
                    "https://user:pass@arxiv.org/a"):
            with self.subTest(url=url):
                with self.assertRaises(ValueError):
                    collect(url, Opener(Response()))
    def test_reject_nontext(self):
        with self.assertRaises(ValueError):
            collect("https://arxiv.org/a", Opener(Response(kind="application/pdf")))
    def test_reject_large_response(self):
        with self.assertRaises(ValueError):
            collect("https://arxiv.org/a", Opener(Response(body=b"x" * (MAX_BYTES + 1))))
    def test_reject_status(self):
        response = Response()
        response.status = 404
        with self.assertRaises(ValueError):
            collect("https://arxiv.org/a", Opener(response))

if __name__ == "__main__":
    unittest.main()
