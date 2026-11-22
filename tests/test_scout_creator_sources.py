import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_signal_intake import devto_items,FEEDS,run
class NewCreatorSourcesTests(unittest.TestCase):
 def test_dev_entries_are_unverified_public_leads(self):
  src=[{"title":"Small agent tools","url":"https://dev.to/example/small-agent-tools","description":"Interesting independent work","published_at":"2026-10-23","user":{"username":"example"}},
       {"title":"Outside","url":"https://untrusted.invalid/p","user":{"username":"spoof"}}]
  rows=devto_items(json.dumps(src).encode())
  self.assertEqual(len(rows),1)
  self.assertEqual(rows[0]["lane"],"creator")
  self.assertEqual(rows[0]["metrics"]["author_handle_unverified"],"example")
  self.assertFalse(rows[0]["outreach_authorized"])
 def test_added_feeds_are_public_and_explicit(self):
  self.assertIn("planet-python",FEEDS)
  self.assertIn("arxiv-ml",FEEDS)
 def test_malformed_feed_fails_closed(self):
  with self.assertRaises(ValueError):devto_items(b'{"items": "not list"}')
 def test_malicious_external_link_excluded(self):
  src=[{"title":"Attack","url":"https://dev.to.evil.invalid/p"}]
  self.assertEqual(devto_items(json.dumps(src).encode()),[])
if __name__=="__main__":unittest.main()
