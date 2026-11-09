"""Reader #48 locked-copy regressions; no editorial or release acceptance.

Administrative exclusions: draft identity/source metadata (lines 1–5), headings,
relationship date/group labels (101, 108), and bibliographic formatting (95).
Those are represented by the page title, source links/notes and catalog review
fields. Brief labels use the existing wrapper labels; their complete prose and
the verdict remain required. The amended source disclosure (97) and final
relationship qualification (113) are required in full, not excluded as custody.
"""
import hashlib
import json
from pathlib import Path
import re
import unittest

from test_reader46_creative_lock import (
    missing_link_targets, missing_locked_blocks, normal,
    ordered_blocks_present, visible,
)

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'the-paper-is-not-the-experiment'
MANUSCRIPT_SHA = '788dfb434d62d074f71774218050fb91ad7e442a4288af5e9c946eab4e46c249'
SOURCE_AID_SHA = '95d4a375a431d4a4c38344981ca2678df2e2a0f360cb797808c3b1fc6ea2cb3d'
TARGETS = [
    '/the-experiment-ran-did-the-research-advance/',
    '/the-grader-is-part-of-the-harness/',
    '/the-harness-keeps-the-receipt/',
    '/the-success-hid-the-failure/',
    'https://shareplane.malott.ai/artifacts/stop-prompting-agents-start-managing-workers/',
    'https://shareplane.malott.ai/artifacts/own-memory-rent-intelligence-agent-stack/',
]


def required_copy(manuscript):
    brief_section = manuscript.split('## The brief\n\n', 1)[1].split('\n## A paper', 1)[0]
    brief = [block.split('** ', 1)[1] for block in brief_section.strip().split('\n\n')]
    body_section = manuscript.split('## A paper is an account of work, not the work itself\n\n', 1)[1].split('\n## Sources and limits', 1)[0]
    body = []
    for block in body_section.strip().split('\n\n'):
        if block.startswith('#'):
            continue
        if block.startswith('- '):
            body.extend(line[2:] for line in block.splitlines())
        else:
            body.append(block)
    relationship_section = manuscript.split('## Proposed directed editorial connections', 1)[1]
    reasons = [line.split(': ', 1)[1] for line in relationship_section.splitlines()
               if line.startswith('- **')]
    disclosure = next(line for line in manuscript.splitlines() if line.startswith('Cloud Codes video,'))
    qualification = next(line for line in manuscript.splitlines() if line.startswith('These are editorial comparisons,'))
    return brief, body, reasons, disclosure, qualification


class Reader48CreativeLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manuscript = (ROOT / f'content/drafts/{SLUG}.md').read_text()
        cls.lock = (ROOT / f'content/drafts/{SLUG}.lock.md').read_text()
        cls.page = (ROOT / f'site/{SLUG}/index.html').read_text()
        cls.authored = (ROOT / f'content/readers/{SLUG}.html').read_text()
        cls.record = next(r for r in json.loads((ROOT / 'content/catalog.json').read_text())['readers'] if r['slug'] == SLUG)
        cls.source_map = json.loads((ROOT / f'content/source-maps/{SLUG}.json').read_text())
        cls.brief, cls.body, cls.reasons, cls.disclosure, cls.qualification = required_copy(cls.manuscript)

    def test_amended_lock_and_source_digest(self):
        self.assertEqual(MANUSCRIPT_SHA, hashlib.sha256(self.manuscript.encode()).hexdigest())
        self.assertIn(MANUSCRIPT_SHA, self.lock)
        self.assertIn('Private ReasonPack verified by private source custodian;', self.disclosure)
        self.assertEqual(SOURCE_AID_SHA, self.source_map['sourceAidSha256'])
        for document in [self.lock, self.authored, self.page]:
            self.assertIn(SOURCE_AID_SHA, document)

    def test_all_30_body_blocks_full_brief_and_final_limits(self):
        self.assertEqual((4, 30, 6), (len(self.brief), len(self.body), len(self.reasons)))
        blocks = self.brief + self.body + self.reasons + [self.qualification, self.disclosure]
        self.assertEqual([], missing_locked_blocks(blocks, self.page))
        self.assertTrue(ordered_blocks_present(blocks, self.page))
        self.assertEqual([], missing_locked_blocks(self.body + self.reasons[4:] + [self.disclosure, self.qualification], self.authored))

    def test_six_catalog_rationales_equal_approved_manuscript_verbatim(self):
        edges = self.record['relationships'] + self.record['sharePlaneRelationships']
        self.assertEqual(self.reasons, [edge['reason'] for edge in edges])
        targets = ['/' + edge['target'].removeprefix('reader:') + '/' for edge in self.record['relationships']]
        targets += [edge['url'] for edge in self.record['sharePlaneRelationships']]
        self.assertEqual(TARGETS, targets)
        self.assertEqual(['extends', 'companion', 'informs architecture', 'extends', 'foundation', 'companion'],
                         [edge['type'] for edge in edges])

    def test_each_full_rationale_has_its_own_exact_destination(self):
        self.assertEqual([], missing_link_targets(TARGETS, self.page))
        for reason, target in zip(self.reasons, TARGETS):
            with self.subTest(target=target):
                # Bind the destination to its explanation, not any other page link.
                items = re.findall(r'<article\b[^>]*>.*?</article>|<li\b[^>]*>.*?</li>', self.page, re.S)
                item = next(item for item in items if normal(reason) in visible(item))
                self.assertEqual([], missing_link_targets([target], item))
                for replacement in ['', ' href="/wrong-destination/"']:
                    changed = item.replace(f' href="{target}"', replacement)
                    self.assertNotEqual(item, changed)
                    self.assertEqual([target], missing_link_targets([target], changed))

    def test_omission_and_compression_of_every_required_block_fail(self):
        blocks = self.brief + self.body + self.reasons + [self.disclosure, self.qualification]
        for block in blocks:
            for replacement in ['', 'Compressed substitute.']:
                with self.subTest(block=block[:70], replacement=replacement):
                    def mutate(match):
                        return replacement if normal(block) in visible(match.group()) else match.group()
                    changed = re.sub(r'<(p|li)\b[^>]*>.*?</\1>', mutate, self.page, flags=re.S)
                    self.assertNotEqual(self.page, changed)
                    self.assertIn(block, missing_locked_blocks(blocks, changed))

    def test_wrong_order_in_brief_body_relationships_and_limits_fails(self):
        for blocks in [self.brief, self.body, self.reasons, [self.qualification, self.disclosure]]:
            with self.subTest(first=blocks[0][:70]):
                self.assertTrue(ordered_blocks_present(blocks, self.page))
                swapped = [blocks[1], blocks[0]] + blocks[2:]
                self.assertFalse(ordered_blocks_present(swapped, self.page))

    def test_source_map_claims_and_anchors_remain_bound(self):
        self.assertEqual('reader:' + SLUG, self.source_map['readerId'])
        self.assertEqual('ULIGFaPLd_Y', self.source_map['sourceId'])
        self.assertEqual({claim['id'] for claim in self.record['claims']},
                         {claim for point in self.source_map['points'] for claim in point['claimIds']})
        for point in self.source_map['points']:
            self.assertIn('id="' + point['sectionId'] + '"', self.page)
            self.assertIn('not listening-certified', point['privateAidCheck'])


if __name__ == '__main__':
    unittest.main()
