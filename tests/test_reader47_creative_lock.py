"""Reader47 actual locked-copy and approved-integration regression checks."""
from pathlib import Path
from html import escape
import hashlib
import json
import re
import unittest

from test_reader46_creative_lock import missing_locked_blocks, ordered_blocks_present, missing_link_targets

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'the-second-brain-still-needs-a-judgment'
VIDEO = 'LP7bfT4vOlo'
MANUSCRIPT_SHA = 'd540a029105a1d9f9423e6e6503a4df2acc135ab2410f58ff1e3fb7144966407'


def locked_blocks(markdown):
    """All substantive blocks, headings and list items; exclude only Markdown rule."""
    result = []
    for block in markdown.split('\n\n'):
        if block == '---':
            continue
        if block.startswith('- '):
            result.extend(line[2:] for line in block.splitlines())
        else:
            result.append(block.lstrip('# '))
    return result


class Reader47CreativeLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.md_bytes = (ROOT / f'docs/intake/{VIDEO}-approved-public-source.md').read_bytes()
        cls.md = cls.md_bytes.decode()
        cls.page = (ROOT / f'site/{SLUG}/index.html').read_text()
        cls.record = next(r for r in json.loads((ROOT / 'content/catalog.json').read_text())['readers'] if r['slug'] == SLUG)

    def test_exact_owner_amended_manuscript_and_every_rendered_block(self):
        self.assertEqual(14794, len(self.md_bytes))
        self.assertEqual(MANUSCRIPT_SHA, hashlib.sha256(self.md_bytes).hexdigest())
        self.assertFalse(self.md_bytes.endswith(b'\n'))
        self.assertEqual([], missing_locked_blocks(locked_blocks(self.md), self.page))
        self.assertTrue(ordered_blocks_present(locked_blocks(self.md), self.page))

    def test_omission_and_compression_fail_for_real_brief_body_and_limits(self):
        for block in [self.record['overview'], self.record['ghostMeshTakeaway'],
                      'A proposal is not an approval.',
                      'The two reported nine-tenths reductions remain anecdotal observations, not generalizable results.',
                      'The ASR has not been checked by listening, and no visual or numerical claim was independently verified.']:
            # The denominator sentence includes its opening qualification in the lock.
            actual = 'Without those details, ' + block[0].lower() + block[1:] if block.startswith('The two reported') else block
            rendered = escape(actual)
            self.assertIn(rendered, self.page)
            changed = self.page.replace(rendered, 'Short substitute.')
            self.assertIn(actual, missing_locked_blocks([actual], changed))

    def test_wrong_body_order_is_detected(self):
        self.assertFalse(ordered_blocks_present(['An approval is not a deployment.', 'A proposal is not an approval.'], self.page))

    def test_exact_five_relationships_and_wrong_link_negative(self):
        local = ['reader:the-agent-a-company-owns', 'reader:the-harness-keeps-the-receipt',
                 'reader:the-cost-of-forgetting-where-the-tools-are']
        works = ['https://shareplane.malott.ai/artifacts/own-memory-rent-intelligence-agent-stack/',
                 'https://shareplane.malott.ai/artifacts/cognitive-capital/']
        self.assertEqual(local, [e['target'] for e in self.record['relationships']])
        self.assertEqual(works, [e['url'] for e in self.record['sharePlaneRelationships']])
        targets = ['/' + r.split(':', 1)[1] + '/' for r in local] + works
        self.assertEqual([], missing_link_targets(targets, self.page))
        changed = self.page.replace(works[0], 'https://example.com/wrong/')
        self.assertEqual([works[0]], missing_link_targets(targets, changed))
        for edge in self.record['relationships'] + self.record['sharePlaneRelationships']:
            self.assertEqual([], missing_locked_blocks([edge['reason']], self.page))

    def test_standard_player_and_both_compact_surfaces(self):
        self.assertNotIn('<iframe', self.page)
        self.assertIn('data-video-id="' + VIDEO + '"', self.page)
        # The home surface is a bounded recent-Reader selection, so Reader #47
        # eventually rotates out; the full archive must continue to carry it.
        self.assertIn('data-source-id="' + VIDEO + '"', (ROOT / 'site/readers/index.html').read_text())
        self.assertIn('data-source-id="', (ROOT / 'site/index.html').read_text())
        self.assertEqual(8, len(self.record['source']['creatorChapters']))
        self.assertIn('www.youtube-nocookie.com/embed/', self.page)
        self.assertEqual(1, self.page.count('id="at-a-glance"'))
        self.assertEqual(1, self.page.count('id="external-evidence"'))
        self.assertEqual(1, self.page.count('id="related-thinking"'))

    def test_two_cost_denominators_remain_unverified_and_separate(self):
        claims = self.record['claims'][:2]
        self.assertEqual(['unverified', 'unverified'], [c['status'] for c in claims])
        self.assertIn('inference time', claims[0]['proposition'])
        self.assertIn('maintenance and embedding costs', claims[1]['proposition'])
        self.assertEqual([[], []], [c['references'] for c in claims])

    def test_paper_evidence_and_precise_video_context_are_distinct(self):
        beir, rag = self.record['claims'][2:4]
        self.assertIn('BEIR published abstract', beir['sourceLocation'])
        self.assertIn('09:42', beir['sourceLocation'])
        self.assertEqual(['r47-beir'], beir['references'])
        self.assertIn('09:31', rag['sourceLocation'])
        points = json.loads((ROOT / f'content/source-maps/{SLUG}.json').read_text())['points']
        self.assertEqual([582], [p['atSeconds'] for p in points if beir['id'] in p['claimIds']])
        self.assertEqual([571], [p['atSeconds'] for p in points if rag['id'] in p['claimIds']])

    def test_single_staged_first_release_event(self):
        events = json.loads((ROOT / 'content/public-release-events.json').read_text())['events']
        own = [e for e in events if e['subjectId'] == 'reader:' + SLUG]
        self.assertEqual(1, len(own))
        self.assertEqual('reader:' + SLUG + ':first-public-release', own[0]['id'])
        self.assertEqual(1, (ROOT / 'site/feed.xml').read_text().count(own[0]['id']))


if __name__ == '__main__':
    unittest.main()
