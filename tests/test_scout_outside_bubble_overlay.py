import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_outside_bubble_overlay import render
def fixture():
 return {"schema":"scout-outside-bubble-v0","publication_authorized":False,"outreach_authorized":False,
 "topic_matched":0,"outside_topic_vocabulary":1,"total":1,"outside_sampled":1,"source_diversity":1,
 "outside_sample":[{"source":"dev-community","title":"<script>bad</script>","url":"https://dev.to/u/p",
 "human_review_result":"NOT_REVIEWED","outreach_authorized":False}]}
class OverlayTests(unittest.TestCase):
 def test_private_source_escape(self):
  h=render('<meta content="noindex,nofollow"><main></main>',fixture())
  self.assertIn("&lt;script&gt;",h)
  self.assertNotIn("<script>bad",h)
 def test_preserve_review_pending(self):
  x=fixture();x["outside_sample"][0]["human_review_result"]="PROMISING"
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',x)
 def test_reject_counts(self):
  x=fixture();x["topic_matched"]=4
  with self.assertRaises(ValueError):render('<meta content="noindex,nofollow"><main></main>',x)
if __name__=="__main__":unittest.main()
