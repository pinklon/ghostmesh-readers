"""Scout private HTML review tests, no browser/server/network."""
import json,sys,unittest,tempfile,hashlib
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_private_preview import render,REVIEW

class PreviewTests(unittest.TestCase):
    def test_all_cases_and_escape(self):
        with tempfile.TemporaryDirectory() as d:
            root=Path(d)
            cases=[]; results=[]
            for i,key in enumerate(REVIEW):
                raw=("source bytes for "+key).encode(); sha=hashlib.sha256(raw).hexdigest()
                (root/(key+".snapshot")).write_bytes(raw)
                (root/(key+".json")).write_text(json.dumps({"source_url":"https://arxiv.org/abs/"+key,"snapshot_sha256":sha,"snapshot_bytes":len(raw),"substantive_text":{"title":"<script>alert(1)</script>","excerpt":"<img src=x onerror=alert(1)>","extraction_status":"EXTRACTED_UNVERIFIED"}}))
                results.append({"id":key,"source_url":"https://arxiv.org/abs/"+key,"status":"FETCHED_UNVERIFIED","snapshot_sha256":sha,"snapshot_bytes":len(raw)})
                cases.append({"id":key,"snapshot_sha256":sha,"recommendation":"INVESTIGATE","contribution":"a", "ghostmesh_gap":"b","counterargument":"c","joint_experiment":"d"})
            (root/"manifest.json").write_text(json.dumps({"schema":"scout-live-trial-v0","publication_authorized":False,"outreach_authorized":False,"results":results}))
            ed=root/"ed.json";ed.write_text(json.dumps({"schema":"scout-editorial-assessments-v0","review_state":"AUTHOR_DRAFT_NOT_INDEPENDENTLY_REVIEWED","publication_authorized":False,"outreach_authorized":False,"cases":cases}))
            html=render(root,ed)
            self.assertIn("NO_CONNECTION_JUSTIFIED",html)
            self.assertIn("FOLLOW",html)
            self.assertIn("&lt;script&gt;",html)
            self.assertNotIn("<script>alert",html)
            self.assertNotIn("<img src=x",html)
            self.assertIn("noindex,nofollow",html)
            (root/"debate.snapshot").write_bytes(b"changed")
            with self.assertRaisesRegex(ValueError,"Receipt mismatch"):
                render(root,ed)

if __name__=="__main__":unittest.main()
