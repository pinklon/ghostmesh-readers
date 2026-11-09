"""Reusable locked-copy checks and Reader46 regressions, not editorial acceptance."""
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
        self.links = []
        self.noncontent = 0

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag in {'script', 'style'}:
            self.noncontent += 1
        if tag == 'a' and 'href' in attrs:
            self.links.append(attrs['href'])

    def handle_endtag(self, tag):
        if tag in {'script', 'style'} and self.noncontent:
            self.noncontent -= 1

    def handle_data(self, value):
        if not self.noncontent:
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
    return missing_locked_blocks(paragraphs + brief + reasons + [final], page)


def missing_locked_blocks(blocks, page):
    """Pass the complete approved block set; extraction/exclusions are edition-specific."""
    text = visible(page)
    return [block for block in blocks if normal(block) not in text]


def ordered_blocks_present(blocks, page):
    text = visible(page)
    cursor = 0
    for block in blocks:
        position = text.find(normal(block), cursor)
        if position < 0:
            return False
        cursor = position + len(normal(block))
    return True


def missing_link_targets(targets, page):
    parser = Text()
    parser.feed(page)
    return sorted(set(targets) - set(parser.links))


def offline_asset_gaps(page):
    """External render dependencies prevent self-contained delivery; links are allowed."""
    class Assets(HTMLParser):
        def __init__(self):
            super().__init__()
            self.references = []

        def handle_starttag(self, tag, pairs):
            attrs = dict(pairs)
            if tag == 'link' and 'stylesheet' in attrs.get('rel', '').split():
                self.references.append(attrs.get('href', ''))
            if tag == 'script' and 'src' in attrs:
                self.references.append(attrs['src'])
            if tag == 'img':
                self.references.append(attrs.get('src', ''))
            if tag in {'img', 'source'}:
                # A srcset can fetch even when src is embedded. Fail closed here;
                # standalone review files should embed one chosen rendition.
                if attrs.get('srcset'):
                    self.references.append('srcset:' + attrs['srcset'])
            if tag in {'source', 'video', 'audio'} and 'src' in attrs:
                self.references.append(attrs['src'])
            if tag == 'video' and 'poster' in attrs:
                self.references.append(attrs['poster'])
            if tag in {'image', 'use'}:
                self.references.append(attrs.get('href', attrs.get('xlink:href', '')))

    parser = Assets()
    parser.feed(page)
    css_urls = re.findall(r'url\(\s*[\'"]?([^\)\'"\s]+)', page, re.I)
    imports = re.findall(r'@import\s+[\'"]([^\'"]+)', page, re.I)
    return sorted(set(ref for ref in parser.references + css_urls + imports
                      if not ref.startswith(('data:', '#'))))


class ReusableIntakeChecks(unittest.TestCase):
    blocks = ['A complete opening brief.', 'The unchanged body and its condition.',
              'This relationship concerns operating cost.', 'Final limits remain explicit.']
    page = '<main>' + ''.join('<p>' + escape(b) + '</p>' for b in blocks) + '</main>'

    def test_other_edition_without_reader46_headings_passes(self):
        self.assertEqual([], missing_locked_blocks(self.blocks, self.page))
        self.assertTrue(ordered_blocks_present(self.blocks, self.page))

    def test_every_omitted_or_compressed_block_fails(self):
        for block in self.blocks:
            for replacement in ['', 'Short substitute.']:
                with self.subTest(block=block, replacement=replacement):
                    changed = self.page.replace(block, replacement)
                    self.assertIn(block, missing_locked_blocks(self.blocks, changed))

    def test_wrong_order_and_missing_ordered_text_fail(self):
        self.assertFalse(ordered_blocks_present(list(reversed(self.blocks)), self.page))
        self.assertFalse(ordered_blocks_present(self.blocks + ['Missing section.'], self.page))

    def test_script_or_style_copy_cannot_hide_an_omission(self):
        for tag in ['script', 'style']:
            changed = self.page.replace(self.blocks[1], '') + f'<{tag}>{self.blocks[1]}</{tag}>'
            self.assertIn(self.blocks[1], missing_locked_blocks(self.blocks, changed))

    def test_exact_link_destinations_not_just_labels(self):
        target = '/the-harness-keeps-the-receipt/'
        self.assertEqual([], missing_link_targets([target], f'<a href="{target}">Related</a>'))
        for page in ['<a>Related</a>', '<a href="/wrong/">Related</a>']:
            self.assertEqual([target], missing_link_targets([target], page))

    def test_inline_offline_resources_and_navigation_pass(self):
        page = '<style>body{color:black}</style><svg><use href="#logo"/></svg>'
        page += '<img src="data:image/png;base64,AAAA"><script>void 0</script>'
        page += '<a href="https://www.youtube.com/watch?v=example">Original</a>'
        self.assertEqual([], offline_asset_gaps(page))

    def test_missing_or_network_render_assets_fail_offline(self):
        for page in ['<link rel="stylesheet" href="/assets/site.css">',
                     '<script src="reader.js"></script>', '<img src="/brand.svg">',
                     '<img>', '<style>@import "remote.css";</style>',
                     '<style>body{background:url(https://example.com/image.png)}</style>',
                     '<img src="data:image/png;base64,AAAA" srcset="/large.png 2x">',
                     '<picture><source srcset="/assets/photo.webp 1x"><img src="data:image/png;base64,AAAA"></picture>',
                     '<video poster="/assets/poster.jpg"></video>',
                     '<video><source src="clip.mp4"></video>']:
            with self.subTest(page=page):
                self.assertTrue(offline_asset_gaps(page))


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
        self.assertTrue(ordered_blocks_present(['The Cost of Forgetting Where the Tools Are',
                                               required_copy(self.manuscript)[1][0],
                                               required_copy(self.manuscript)[3]], self.page))
        self.assertNotIn('<section id="brief"><h2>Three questions before you watch</h2></section>', self.authored)
        self.assertNotIn('<!--GM_EVIDENCE-->', self.authored)
        for claim in self.record['claims']:
            self.assertEqual(1, self.page.count('id="' + claim['id'] + '"'))
            self.assertIn(normal(claim['proposition']), visible(self.page))

    def test_approved_relationship_destinations_survive_rendering(self):
        targets = ['/' + edge['target'].removeprefix('reader:') + '/'
                   for edge in self.record['relationships']]
        targets += [edge['url'] for edge in self.record['sharePlaneRelationships']]
        self.assertEqual([], missing_link_targets(targets, self.page))

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
