import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_receipt_report import report

class ReceiptReportTests(unittest.TestCase):
    def test_verified_and_tamper_rejection(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            raw=b"real source"
            sha=hashlib.sha256(raw).hexdigest()
            (root/"case.snapshot").write_bytes(raw)
            (root/"case.json").write_text(json.dumps({
                "source_url":"https://arxiv.org/abs/a", "snapshot_sha256":sha,
                "snapshot_bytes":len(raw), "substantive_text":{"extraction_status":"EXTRACTED_UNVERIFIED","excerpt":"real source"}}))
            (root/"manifest.json").write_text(json.dumps({
                "schema":"scout-live-trial-v0", "publication_authorized":False,
                "outreach_authorized":False, "results":[{
                    "id":"case","source_url":"https://arxiv.org/abs/a",
                    "status":"FETCHED_UNVERIFIED","snapshot_sha256":sha,"snapshot_bytes":len(raw)}]}))
            self.assertIn("Editorial interpretation", report(root))
            (root/"case.snapshot").write_bytes(b"tampered")
            with self.assertRaisesRegex(ValueError,"Receipt mismatch"):
                report(root)
    def test_no_pub_authority(self):
        with tempfile.TemporaryDirectory() as folder:
            root=Path(folder)
            (root/"manifest.json").write_text(json.dumps({"schema":"scout-live-trial-v0",
                "publication_authorized":True, "outreach_authorized":False,"results":[]}))
            with self.assertRaises(ValueError): report(root)
if __name__=="__main__": unittest.main()
