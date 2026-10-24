"""Offline proof that live trial writes authentic collector-origin bytes."""
import hashlib
import json
import tempfile
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_live_trial import trial
from scout_evidence_intake import build_packet

class LiveTrialTests(unittest.TestCase):
    def test_retains_snapshot_and_hash(self):
        raw = b"Original independently inspectable research bytes"
        def collector(url, snapshot_callback):
            snapshot_callback(raw)
            p = build_packet(url, raw)
            p["substantive_text"] = {"extraction_status": "EXTRACTED_UNVERIFIED", "excerpt": raw.decode()}
            return p
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder) / "new"
            m = trial(root, [("case-a", "https://arxiv.org/abs/2601.19921")], collector)
            self.assertEqual((root / "case-a.snapshot").read_bytes(), raw)
            self.assertEqual(m["results"][0]["snapshot_sha256"], hashlib.sha256(raw).hexdigest())
            self.assertFalse(json.loads((root / "manifest.json").read_text())["publication_authorized"])
            with self.assertRaises(ValueError):
                trial(root, [("case-a", "https://arxiv.org/abs/2601.19921")], collector)
    def test_failure_is_explicit(self):
        def broken(url, snapshot_callback):
            raise RuntimeError("network down")
        with tempfile.TemporaryDirectory() as folder:
            m = trial(Path(folder) / "out", [("bad", "https://arxiv.org/a")], broken)
            self.assertEqual(m["results"][0]["status"], "FETCH_FAILED")
            self.assertEqual(m["results"][0]["error_type"], "RuntimeError")

if __name__ == "__main__":
    unittest.main()
