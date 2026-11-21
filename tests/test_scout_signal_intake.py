import sys,unittest,json
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_signal_intake import xml_items,github_items,hn_items,normalize,run,FEEDS,API_GITHUB,HN_URL
class IntakeTests(unittest.TestCase):
 def test_rss_and_atom(self):
  rss=b'<rss><channel><item><title>One</title><link>https://example.org/one</link></item></channel></rss>'
  atom=b'<feed xmlns="http://www.w3.org/2005/Atom"><entry><title>Two</title><link href="https://example.org/two"/></entry></feed>'
  self.assertEqual(xml_items(rss,"x","research")[0]["title"],"One")
  self.assertEqual(xml_items(atom,"x","research")[0]["title"],"Two")
 def test_rejects_unsafe_url(self):
  self.assertIsNone(normalize("x","x","p","http://127.0.0.1/a"))
  self.assertIsNone(normalize("x","x","p","https://user:secret@example.org/a"))
 def test_github_not_virality(self):
  data=json.dumps({"items":[{"full_name":"a/b","html_url":"https://github.com/a/b","stargazers_count":44}]}).encode()
  x=github_items("a",data)[0]
  self.assertEqual(x["metrics"]["stars"],44)
  self.assertEqual(x["status"],"UNREVIEWED_LEAD")
 def test_hn(self):
  ids=b"[12]"
  def fetch(url):return json.dumps({"type":"story","title":"New system","score":3,"url":"https://example.org/story"}).encode()
  self.assertEqual(hn_items(ids,fetch)[0]["lane"],"attention")
 def test_failing_one_source_does_not_fail_all(self):
  rss=b'<rss><channel><item><title>Example</title><link>https://example.org/a</link></item></channel></rss>'
  def fetch(url):
   if "huggingface" in url:raise RuntimeError("blocked")
   if url==HN_URL:return b"[]"
   if url.startswith(API_GITHUB):return b'{"items":[]}'
   return rss
  result=run(fetch,cap=1)
  self.assertFalse(result["publication_authorized"])
  self.assertTrue(any(d["state"]=="ERROR" for d in result["diagnostics"]))
  self.assertTrue(result["sampled_leads"])
if __name__=="__main__":unittest.main()
