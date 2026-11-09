"""Regression for the actual Reader46 omissions; this is not editorial acceptance."""
from html import escape, unescape
from html.parser import HTMLParser
import hashlib
import json
from pathlib import Path
import re
import unittest

ROOT = Path(__file__).resolve().parents[1]
SLUG = 'the-cost-of-forgetting-where-the-tools-are'


class Text(HTMLParser):
    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, value):
        self.parts.append(value)


def normal(value):
    value = re.sub(r'\[([^\]]+)\]\([^)]*\)', r'\1', value)
    value = re.sub(r'[*`]', '', value)
    return re.sub(r'\s+', ' ', unescape(value).replace('’', "'")).strip()


def visible(raw):
    parser = Text()
    parser.feed(raw)
    return normal(''.join(parser.parts))


def required_copy(manuscript):
    body = manuscript.split('## What is the video about?\n\n', 1)[1].split('\n## Where to watch', 1)[0]
    paragraphs = [normal(p) for p in body.split('\n\n') if p.strip() and not p.startswith('#')]
    brief = [normal(re.search(r'^\*\*' + label + r':\*\* (.+)$', manuscript, re.M).group(1))
             for label in ['What happened', 'Why it matters', 'GhostMesh takeaway']]
    reasons = [normal(m.group(1)) for m in re.finditer(r'^- \*\*[^*]+:\*\* \[[^\]]+\]\([^)]+\)\. (.+)$', manuscript, re.M)]
    final = normal(next(line for line in manuscript.splitlines() if line.startswith('**What would change the assessment:**')))
    return paragraphs, brief, reasons, final


def missing_copy(manuscript, page):
    paragraphs, brief, reasons, final = required_copy(manuscript)
    text = visible(page)
    return [block for block in paragraphs + brief + reasons + [final] if block not in text]


class Reader46CreativeLock(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manuscript = (ROOT / 'docs/intake/P5QCrpdr9gU-approved-public-source.md').read_text()
        cls.page = (ROOT / f'site/{SLUG}/index.html').read_text()
        cls.authored = (ROOT / f'content/readers/{SLUG}.html').read_text()
        cls.record = next(r for r in json.loads((ROOT / 'content/catalog.json').read_text())['readers'] if r['slug'] == SLUG)

    def test_all_locked_body_brief_relationships_and_final_limits_present(self):
        self.assertEqual('9c8d19d278b82d340c9b2e2cbf3e3646d6ecbbf46410af37979768fd62d51132', hashlib.sha256(self.manuscript.encode()).hexdigest())
        paragraphs, brief, reasons, final = required_copy(self.manuscript)
        self.assertEqual((39, 3, 6), (len(paragraphs), len(brief), len(reasons)))
        self.assertEqual([], missing_copy(self.manuscript, self.page))

    def test_removed_final_limit_is_detected(self):
        changed = re.sub(r'<p><strong>What would change the assessment:</strong>.*?</p>', '', self.page)
        self.assertNotEqual(self.page, changed)
        self.assertIn(required_copy(self.manuscript)[3], missing_copy(self.manuscript, changed))

    def test_removed_relationship_reason_is_detected(self):
        reason = required_copy(self.manuscript)[2][0]
        changed = self.page.replace(reason, '')
        self.assertNotEqual(self.page, changed)
        self.assertIn(reason, missing_copy(self.manuscript, changed))

    def test_compressed_brief_is_detected(self):
        paragraph = required_copy(self.manuscript)[1][0]
        changed = self.page.replace(escape(paragraph), 'Microsoft reports a cost improvement.')
        self.assertNotEqual(self.page, changed)
        self.assertIn(paragraph, missing_copy(self.manuscript, changed))

    def test_single_brief_claim_register_and_reader_relationship_group(self):
        self.assertEqual(1, self.page.count('id="at-a-glance"'))
        self.assertEqual(1, self.page.count('id="external-evidence"'))
        self.assertEqual(1, self.page.count('id="related-thinking"'))
        self.assertLess(self.page.index('<h1>'), self.page.index('id="at-a-glance"'))
        self.assertLess(self.page.index('id="at-a-glance"'), self.page.index('id="film"'))
        self.assertNotIn('<section id="brief"><h2>Three questions before you watch</h2></section>', self.authored)
        self.assertNotIn('<!--GM_EVIDENCE-->', self.authored)
        for claim in self.record['claims']:
            self.assertEqual(1, self.page.count('id="' + claim['id'] + '"'))
            self.assertIn(normal(claim['proposition']), visible(self.page))

    def test_paper_is_counterevidence_to_universal_quality_and_repeat_use_claims(self):
        for claim in self.record['claims'][1:3]:
            self.assertEqual('contradicted', claim['status'])
            self.assertEqual([], claim['references'])
            self.assertEqual(['src-token-economizer-paper'], claim['counterevidence'])
        self.assertIn('Overstated as a universal condition.', self.record['claims'][2]['assessment'])
        self.assertEqual('unverified', self.record['claims'][3]['status'])

    def test_companion_label_is_preserved_without_admitting_arbitrary_types(self):
        schema = json.loads((ROOT / 'content/catalog.schema.json').read_text())
        types = schema['$defs']['sharePlaneRelationship']['properties']['type']['enum']
        self.assertIn('companion', types)
        self.assertNotIn('automatic corroboration', types)
        self.assertEqual('companion', self.record['sharePlaneRelationships'][2]['type'])


if __name__ == '__main__':
    unittest.main()
