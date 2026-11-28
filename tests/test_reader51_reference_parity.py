"""Ensure Reader 51 preview uses the actual approved Reader 50 experience."""
import unittest
from pathlib import Path
from html.parser import HTMLParser

ROOT = Path(__file__).resolve().parents[1]

class Nodes(HTMLParser):
    def __init__(self):
        super().__init__();self.ids=set();self.classes=set();self.attrs=[]
    def handle_starttag(self,tag,attrs):
        d=dict(attrs);self.ids.add(d.get('id'));self.classes.update((d.get('class') or '').split());self.attrs.append((tag,d))

class Reader51ReferenceParity(unittest.TestCase):
    def test_reference_experience_not_just_css(self):
        a=Nodes();b=Nodes()
        a.feed((ROOT/'content/readers/when-every-ai-website-looks-good.html').read_text())
        b.feed((ROOT/'site/__drafts/more-skills-worse-agents/index.html').read_text())
        required_classes={'reading','rail','prose','player','chapter-guide','full-deconstruction','gm-evidence','gm-claim-list','gm-source-list','gm-publication-status'}
        required_ids={'film','source-video','chapters','full-deconstruction','claim-register','external-evidence'}
        self.assertFalse(required_classes-a.classes)
        self.assertFalse(required_classes-b.classes)
        self.assertFalse(required_ids-a.ids)
        self.assertFalse(required_ids-b.ids)
        self.assertGreaterEqual(sum('data-seek' in d for _,d in b.attrs),6)
        self.assertTrue(any(d.get('data-video-id')=='45-qbcAeUbM' for _,d in b.attrs))
        self.assertTrue(any(d.get('aria-label')=='In this reading' for _,d in b.attrs))
    def test_three_moves_and_reasonpack_provenance(self):
        s=(ROOT/'site/__drafts/more-skills-worse-agents/index.html').read_text()
        self.assertEqual(s.count('class="gm-brief"'),1)
        self.assertEqual(s.count('class="gm-brief-point"'),3)
        self.assertEqual(s.count('id="at-a-glance"'),1)
        self.assertIn('The reading / in three moves',s)
        for label in ('What the video is about','Why you should care','What GhostMesh takes away'):
            self.assertIn(label,s)
        self.assertIn('id="reasonpack-provenance"',s)
        for evidence in ('HTTP 429','whisper.cpp 1.9.5-dev','803 timestamped VTT cues','reasonpack verify','0060da049408edbc81df1f6ba8e9e61f730d3e254085a1e9905c3093326551f7','Machine ASR has not been manually checked'):
            self.assertIn(evidence,s)

    def test_preview_cannot_impersonate_reader50(self):
        s=(ROOT/'site/__drafts/more-skills-worse-agents/index.html').read_text()
        self.assertNotIn('when-every-ai-website-looks-good/',s)
        self.assertNotIn('mImbbszCjCI',s)
        self.assertIn('Publication status:',s)
        self.assertNotIn('/home/tony-malott/',s)
