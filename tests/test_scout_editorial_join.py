import hashlib
import json
import sys
import tempfile
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_editorial_join import join

class EditorialJoinTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name)
        raw=b"fixed sourced evidence"
        self.sha=hashlib.sha256(raw).hexdigest()
        (self.root/"c.snapshot").write_bytes(raw)
        (self.root/"c.json").write_text(json.dumps({
            "source_url":"https://arxiv.org/abs/a","snapshot_sha256":self.sha,
            "snapshot_bytes":len(raw),"substantive_text":{"extraction_status":"EXTRACTED_UNVERIFIED","excerpt":"fixed sourced evidence"}}))
        (self.root/"manifest.json").write_text(json.dumps({
            "schema":"scout-live-trial-v0","publication_authorized":False,"outreach_authorized":False,
            "results":[{"id":"c","status":"FETCHED_UNVERIFIED","source_url":"https://arxiv.org/abs/a","snapshot_sha256":self.sha,"snapshot_bytes":len(raw)}]}))
        self.data={"schema":"scout-editorial-assessments-v0","review_state":"AUTHOR_DRAFT_NOT_INDEPENDENTLY_REVIEWED",
            "outreach_authorized":False,"publication_authorized":False,
            "cases":[{"id":"c","snapshot_sha256":self.sha,"recommendation":"FOLLOW","contribution":"hypothesis",
                "ghostmesh_gap":"gap","counterargument":"objection","joint_experiment":"fixed test"}]}
        self.path=self.root/"assessments.json"

    def run_join(self):
        self.path.write_text(json.dumps(self.data))
        return join(self.root,self.path)

    def test_source_linked_draft(self):
        out=self.run_join()
        self.assertIn("NOT INDEPENDENTLY REVIEWED",out)
        self.assertIn(self.sha,out)
        self.assertIn("fixed test",out)
    def test_stale_binding_rejected(self):
        self.data["cases"][0]["snapshot_sha256"]="0"*64
        with self.assertRaisesRegex(ValueError,"hash mismatch"):
            self.run_join()
    def test_tampered_snapshot_rejected(self):
        (self.root/"c.snapshot").write_bytes(b"tampered")
        with self.assertRaisesRegex(ValueError,"Receipt mismatch"):
            self.run_join()
    def test_outreach_or_publication_not_allowed(self):
        self.data["outreach_authorized"]=True
        with self.assertRaises(ValueError):
            self.run_join()
        self.data["outreach_authorized"]=False
        self.data["publication_authorized"]=True
        with self.assertRaises(ValueError):
            self.run_join()
    def test_coverage_not_optional(self):
        self.data["cases"]=[]
        with self.assertRaises(ValueError):
            self.run_join()

if __name__=="__main__":
    unittest.main()
