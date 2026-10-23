import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_multi_source_preview import render
class PreviewTests(unittest.TestCase):
 def test_escaped_and_authority(self):
  a={"schema":"scout-multisource-intake-v0","sampled_leads":[{"url":"https://example.org/a","title":"<script>alert(1)</script>","description":"Hello","lane":"research","source":"example"}],"publication_authorized":False,"outreach_authorized":False}
  t={"schema":"scout-relevance-triage-v0","entries":[{"url":"https://example.org/a","topics":[]}],"publication_authorized":False,"outreach_authorized":False}
  e={"schema":"scout-private-edition-v0","candidates":[],"publication_authorized":False,"outreach_authorized":False}
  r={"schema":"scout-reconciliation-v0","publication_authorized":False,"outreach_authorized":False,"new_to_sample":1}
  html=render(a,t,e,r)
  self.assertIn("&lt;script&gt;",html)
  self.assertNotIn("<script>alert",html)
  self.assertIn("No signals match",html)
  a["publication_authorized"]=True
  with self.assertRaises(ValueError):render(a,t,e,r)
if __name__=="__main__":unittest.main()
