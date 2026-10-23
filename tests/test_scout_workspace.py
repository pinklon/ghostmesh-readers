import sys,unittest
from pathlib import Path
sys.path.insert(0,str(Path(__file__).resolve().parents[1]/"scripts"))
from scout_workspace import build
class WorkspaceTests(unittest.TestCase):
 def test_navigation_and_escape(self):
  view='<!doctype html><html><head><meta name="robots" content="noindex,nofollow"></head><body><p title="x">\"&lt;demo&gt;</p></body></html>'
  html=build({"discovery":view,"relationships":view,"history":view,"claims":view,"people":view})
  self.assertIn('role="tablist"',html)
  self.assertIn('sandbox="allow-scripts allow-popups"',html)
  self.assertIn('srcdoc="',html)
  self.assertIn('&quot;',html)
  self.assertNotIn('allow-same-origin',html)
 def test_requires_privacy(self):
  with self.assertRaises(ValueError):build({"discovery":"<html></html>","relationships":"<html></html>","history":"<html></html>"})
 def test_requires_exact_inputs(self):
  with self.assertRaises(ValueError):build({})
if __name__=="__main__":unittest.main()
