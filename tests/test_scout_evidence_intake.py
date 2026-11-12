"""Scout offline intake boundary tests."""
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_evidence_intake import build_packet, MAX_BYTES

class EvidenceIntakeTests(unittest.TestCase):
    def test_unverified_by_default(self):
        p = build_packet("https://example.org/paper", b"Original research excerpt")
        self.assertFalse(p["evidence_verified"])
        self.assertFalse(p["outreach_authorized"])
        self.assertFalse(p["publication_authorized"])
        self.assertEqual(p["claims"]["contribution"]["status"], "UNKNOWN")
    def test_draft_not_fact(self):
        p = build_packet("https://example.org", b"Evidence", {"contribution": "Possible novelty"})
        self.assertEqual(p["claims"]["contribution"]["status"], "OPERATOR_DRAFT")
    def test_reject_credentials(self):
        with self.assertRaises(ValueError):
            build_packet("https://user:secret@example.org", b"x")
    def test_reject_http(self):
        with self.assertRaises(ValueError):
            build_packet("http://example.org", b"x")
    def test_reject_large_snapshot(self):
        with self.assertRaises(ValueError):
            build_packet("https://example.org", b"x" * (MAX_BYTES + 1))
    def test_reject_unknown_claims(self):
        with self.assertRaises(ValueError):
            build_packet("https://example.org", b"x", {"outreach_authorized": "true"})
    def test_reject_empty(self):
        with self.assertRaises(ValueError):
            build_packet("https://example.org", b"   ")

if __name__ == "__main__":
    unittest.main()
