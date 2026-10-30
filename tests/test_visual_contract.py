import json
import html
import copy
import re
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self):
        super().__init__()
        self.tags = []

    def handle_starttag(self, tag, attrs):
        self.tags.append((tag, dict(attrs)))


class VisualContractTest(unittest.TestCase):
    def test_player_and_related_projection_preserve_mobile_review_surface(self):
        catalog = json.loads((ROOT / 'content/catalog.json').read_text())
        by_id = {reader['id']: reader for reader in catalog['readers']}
        css = (ROOT / 'site/assets/reader-refresh.css').read_text()
        self.assertIn('.gm-media-frame.player:has(.launch)>img', css)
        self.assertIn('aspect-ratio:var(--gm-media-ratio);object-fit:contain;opacity:1', css)
        self.assertIn('@media(max-width:760px){.gm-related .gm-cards{grid-template-columns:1fr}', css)
        for reader in catalog['readers']:
            with self.subTest(slug=reader['slug']):
                page = (ROOT / 'site' / reader['slug'] / 'index.html').read_text()
                if 'class="player gm-media-frame"' in page:
                    self.assertIn('id="launch"', page)
                    self.assertIn(f'data-gm-aspect="{reader["source"]["mediaAspect"]}"', page)
                    self.assertNotIn('<iframe', page)
                    if reader['source'].get('title'):
                        self.assertIn(html.escape(reader['source']['title']), page)
                for edge in reader['relationships']:
                    target = by_id[edge['target']]
                    self.assertIn(f'<a href="/{target["slug"]}/">', page)
                    self.assertIn(html.escape(edge['reason']), page)

    def test_approved_home_hero_and_distinct_destinations(self):
        home = (ROOT / 'site/index.html').read_text()
        self.assertIn('THE ALGORITHM GOT YOUR ATTENTION.</span> <span class="gm-hero-question">DID THE ARGUMENT EARN IT?', home)
        self.assertIn('<title>The algorithm got your attention. Did the argument earn it? | GhostMesh Readers</title>', home)
        for name, url in (
            ('ghostmesh', 'https://ghostmesh.ai/'),
            ('malott', 'https://malott.ai/'),
            ('shareplane', 'https://shareplane.malott.ai/'),
        ):
            self.assertIn(f'class="gm-destination gm-destination-{name}" href="{url}"', home)
        self.assertEqual(home.count('class="gm-destination gm-destination-'), 3)
        self.assertIn('Context, evidence and continuity <span>Conceptual illustration · Human authority</span>', home)
        self.assertNotIn('GM / CONCEPTUAL SIGNAL ARCHITECTURE', home)

    def test_single_shared_shell_and_full_archive(self):
        catalog = json.loads((ROOT / 'content/catalog.json').read_text())
        routes = ['index.html', 'readers/index.html', 'knowledge/index.html'] + [
            f'{r["slug"]}/index.html' for r in catalog['readers']
        ]
        for route in routes:
            with self.subTest(route=route):
                parsed = Tags()
                parsed.feed((ROOT / 'site' / route).read_text())
                self.assertEqual(sum(tag == 'header' and 'gm-site-header' in a.get('class', '').split()
                                     for tag, a in parsed.tags), 1)
                self.assertEqual(sum('data-theme-toggle' in a for _, a in parsed.tags), 1)
                self.assertEqual(sum(tag == 'h1' for tag, _ in parsed.tags), 1)
                self.assertIn('<p class="gm-site-tagline">Context endures. Possibility evolves.</p>',
                              (ROOT / 'site' / route).read_text())
                if route not in {'index.html', 'readers/index.html', 'knowledge/index.html'}:
                    self.assertEqual(sum('data-gm-share' in a for _, a in parsed.tags), 1)
                    self.assertEqual(sum('gm-reader-footer' in a.get('class', '').split()
                                         for _, a in parsed.tags), 1)
        archive = (ROOT / 'site/readers/index.html').read_text()
        for reader in catalog['readers']:
            self.assertIn(f'href="/{reader["slug"]}/"', archive)

    def test_home_posters_are_source_typed_and_playback_is_opt_in(self):
        home = (ROOT / 'site/index.html').read_text()
        parsed = Tags()
        parsed.feed(home)
        panels = [a for _, a in parsed.tags if 'data-home-player' in a]
        catalog = json.loads((ROOT / 'content/catalog.json').read_text())
        by_id = {reader['id']: reader for reader in catalog['readers']}
        recent = sorted(catalog['readers'], key=lambda reader: (reader['published'], reader['slug']), reverse=True)
        selected = [by_id[catalog['featuredId']]] + [reader for reader in recent if reader['id'] != catalog['featuredId']][:6]
        written_count = sum(reader['source'].get('kind') in {'paper', 'article', 'repository'} for reader in selected)
        playable = [reader for reader in selected
                    if reader['source'].get('kind') not in {'paper', 'article', 'repository'}
                    and reader['source']['mediaAspect'] != 'unknown']
        self.assertEqual(len(panels), len(playable))
        self.assertCountEqual([a.get('data-source-platform') for a in panels],
                              [reader['source']['platform'] for reader in playable])
        self.assertEqual(home.count('class="gm-home-visual gm-home-paper"'), written_count)
        self.assertEqual(sum(tag == 'iframe' for tag, _ in parsed.tags), 0)
        self.assertEqual(home.count('class="gm-home-open"'), 7)
        self.assertEqual(home.count('class="gm-home-source"'), 7)
        script = (ROOT / 'site/assets/home-player.js').read_text()
        self.assertIn('button.addEventListener', script)
        self.assertNotIn('autoplay=1', script)
        self.assertNotIn('download', script)

    def test_visible_deconstruction_numbers_are_unique(self):
        catalog = json.loads((ROOT / 'content/catalog.json').read_text())
        numbers = []
        for reader in catalog['readers']:
            page = (ROOT / 'site' / reader['slug'] / 'index.html').read_text()
            label = re.search(r'Video Deconstruction\s+(\d+)', page, re.I)
            if label:
                numbers.append(int(label.group(1)))
        self.assertEqual(len(numbers), len(set(numbers)))

    def test_light_signal_has_distinct_theme_tokens(self):
        css = (ROOT / 'site/assets/knowledge.css').read_text()
        svg = (ROOT / 'content/home-signal.svg').read_text()
        for token in ('signal-face-top', 'signal-logo-white', 'signal-flow'):
            self.assertIn(token, svg)
            self.assertRegex(css, rf'\.{re.escape(token)}')
        self.assertIn('html[data-theme="light"] body#home{--signal-grid:', css)

    def test_local_map_matches_catalog_relationship_inventory(self):
        catalog = json.loads((ROOT / 'content/catalog.json').read_text())
        page = (ROOT / 'site/map/index.html').read_text()
        parsed = Tags()
        parsed.feed(page)
        entries = [a for _, a in parsed.tags if 'gm-atlas-entry' in a.get('class', '').split()]
        links = [a for _, a in parsed.tags if 'gm-atlas-link' in a.get('class', '').split()]
        graph = json.loads((ROOT / 'site/map/relationships.json').read_text())
        self.assertEqual(len(entries), len(catalog['readers']))
        self.assertEqual(len(links), sum(len(r['relationships']) for r in catalog['readers']))
        self.assertEqual((len(catalog['readers']), len(catalog['readers']), len(links)),
                         (graph['readerCount'], graph['assessmentCount'], graph['relationshipCount']))
        self.assertEqual({(r['id'], e['target'], e['reason']) for r in catalog['readers'] for e in r['relationships']},
                         {(e['from'], e['to'], e['reason']) for e in graph['edges']})
        self.assertIn('/map/relationships.json', page)
        self.assertIn('Its named editorial links help you navigate and do not prove a claim.',
                      (ROOT / 'site/knowledge/index.html').read_text())
        self.assertIn('not independent corroboration or agreement', page)
        for reader in catalog['readers']:
            self.assertIn(f'id="map-reader-{reader["editorialOrder"] + 1:02d}"', page)
            for edge in reader['relationships']:
                target = next(r for r in catalog['readers'] if r['id'] == edge['target'])
                self.assertIn(f'href="/{target["slug"]}/"', page)
        self.assertIn('Both Readers examine the Amap fleet', page)
        self.assertIn('Wilson considers services designed for agent customers', page)
        self.assertIn('The physics benchmark reports 49 of 50 bounded calculations', page)
        self.assertIn('This paper grades open-ended research contributions', page)
        self.assertIn('limited inference from Anthropic emotion-representation', page)

    def test_catalog_aspect_and_share_source_are_explicit(self):
        catalog = json.loads((ROOT / 'content/catalog.json').read_text())
        archive = (ROOT / 'site/readers/index.html').read_text()
        parsed = Tags()
        parsed.feed(archive)
        frames = [a for _, a in parsed.tags if 'gm-library-frame' in a.get('class', '').split()]
        media = [r for r in catalog['readers'] if r['source'].get('kind') not in {'paper', 'article', 'repository'}]
        known_aspect = [reader for reader in media if reader['source']['mediaAspect'] != 'unknown']
        self.assertEqual(len(frames), len(known_aspect))
        self.assertCountEqual([a['data-gm-aspect'] for a in frames],
                              [r['source']['mediaAspect'] for r in known_aspect])
        self.assertEqual(archive.count('Source shape unverified. Open the Reader for the original link.'),
                         len(media) - len(known_aspect))
        self.assertIn('class="gm-paper-cover"', archive)
        self.assertIn('LLM<br>personas', archive)
        self.assertIn('TabPFN<br>distribution', archive)
        self.assertIn('TWO RESEARCH QUESTIONS', archive)
        self.assertEqual(sum(tag == 'iframe' for tag, _ in parsed.tags), 0)
        self.assertIn('Search covers this published Reader library only.', archive)
        home = (ROOT / 'site/index.html').read_text()
        self.assertIn('action="/readers/" method="get"', home)
        for reader in catalog['readers']:
            generated = (ROOT / 'site' / reader['slug'] / 'index.html').read_text()
            self.assertIn(f'name="gm-share-description" content="{html.escape(reader["overview"], quote=True)}"', generated)
        share = (ROOT / 'site/assets/reader-share.js').read_text()
        self.assertIn('navigator.share({title, text:description, url:canonical})', share)

    def test_theme_icon_control_has_named_keyboard_action(self):
        home = (ROOT / 'site/index.html').read_text()
        self.assertIn('data-theme-toggle type="button" aria-label="Light appearance" aria-pressed="false"', home)
        self.assertIn('class="gm-theme-sun"', home)
        self.assertIn('class="gm-theme-moon"', home)
        script = (ROOT / 'site/assets/theme.js').read_text()
        self.assertIn("control.addEventListener('click'", script)
        self.assertIn("localStorage.setItem('gm-appearance', choice)", script)

    def test_unknown_aspect_stays_direct_link_only_in_browse_surfaces(self):
        from scripts.generate_site import card, home_card
        reader = copy.deepcopy(json.loads((ROOT / 'content/catalog.json').read_text())['readers'][0])
        reader['rank'] = 1
        reader['source']['mediaAspect'] = 'unknown'
        for rendered in (card(reader), home_card(reader, 1)):
            self.assertNotIn('data-home-player', rendered)
            self.assertNotIn('data-home-play', rendered)
            self.assertNotIn('<iframe', rendered)
            self.assertIn('Source shape unverified', rendered)
            self.assertIn(html.escape(reader['source']['url'], quote=True), rendered)


if __name__ == '__main__':
    unittest.main()
