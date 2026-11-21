import sys, unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
from scout_fresh_review_render import render, canonical_hash

class FreshReviewRenderTests(unittest.TestCase):
    def packet(self):
        return {'schema':'scout-fresh-blind-review-v0','case_count':2,'publication_authorized':False,'outreach_authorized':False,'cards':[{'review_id':f'SC2-{i}','sequence':i,'title':f'Title {i}','source_url':f'https://example.com/{i}','source_excerpt':'Unverified abstract','relevance':None,'novelty':None,'surprise':None} for i in (1,2)]}
    def test_digest_and_ids(self):
        p=self.packet(); result=render(p)
        self.assertIn(canonical_hash(p), result)
        self.assertIn('SC2-1', result)
        self.assertEqual(result, render(p))
    def test_cohort_rejected(self):
        p=self.packet(); p['cards'][0]['cohort']='TOPIC_MATCHED'
        with self.assertRaises(ValueError): render(p)
    def test_prior_score_rejected(self):
        p=self.packet(); p['cards'][0]['relevance']=3
        with self.assertRaises(ValueError): render(p)
    def test_duplicate_url_rejected(self):
        p=self.packet(); p['cards'][1]['source_url']=p['cards'][0]['source_url']
        with self.assertRaises(ValueError): render(p)
    def test_authority_rejected(self):
        p=self.packet(); p['outreach_authorized']=True
        with self.assertRaises(ValueError): render(p)

if __name__=='__main__': unittest.main()
