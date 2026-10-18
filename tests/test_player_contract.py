import unittest

from scripts.generate_site import player_contract


class PlayerContractTest(unittest.TestCase):
    def test_declared_shapes_use_one_shared_frame(self):
        source = '<section class="wrap source-grid"><div class="video-shell"></div></section>'
        for aspect in ('16:9', '9:16', '1:1'):
            with self.subTest(aspect=aspect):
                rendered = player_contract(source, aspect)
                self.assertIn(f'data-gm-aspect="{aspect}"', rendered)
                self.assertIn('class="wrap source-grid gm-source-layout"', rendered)
                self.assertEqual(rendered.count('gm-media-frame'), 1)

    def test_unknown_does_not_guess_from_platform_or_template(self):
        with self.assertRaisesRegex(ValueError, 'link-only fallback'):
            player_contract('<div class="player"></div>', 'unknown')
        self.assertEqual(player_contract('<a href="https://example.org/source">Source</a>', 'unknown'),
                         '<a href="https://example.org/source">Source</a>')


if __name__ == '__main__':
    unittest.main()
