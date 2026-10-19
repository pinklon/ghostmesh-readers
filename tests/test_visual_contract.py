import json
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
                self.assertEqual(sum('data-theme-choice' in a for _, a in parsed.tags), 1)
                self.assertEqual(sum(tag == 'h1' for tag, _ in parsed.tags), 1)
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
        self.assertEqual(len(panels), 7)
        self.assertEqual(sum(a.get('data-source-platform') == 'YouTube' for a in panels), 6)
        self.assertEqual(sum(a.get('data-source-platform') == 'Instagram' for a in panels), 1)
        self.assertEqual(sum(tag == 'iframe' for tag, _ in parsed.tags), 0)
        self.assertEqual(home.count('class="gm-home-open"'), 7)
        self.assertEqual(home.count('class="gm-home-source"'), 7)
        script = (ROOT / 'site/assets/home-player.js').read_text()
        self.assertIn('button.addEventListener', script)
        self.assertNotIn('autoplay=1', script)
        self.assertNotIn('download', script)

    def test_light_signal_has_distinct_theme_tokens(self):
        css = (ROOT / 'site/assets/knowledge.css').read_text()
        svg = (ROOT / 'content/home-signal.svg').read_text()
        for token in ('signal-face-top', 'signal-logo-white', 'signal-flow'):
            self.assertIn(token, svg)
            self.assertRegex(css, rf'\.{re.escape(token)}')
        self.assertIn('html[data-theme="light"] body#home{--signal-grid:', css)


if __name__ == '__main__':
    unittest.main()
