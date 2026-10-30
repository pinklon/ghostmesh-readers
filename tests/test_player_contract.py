import unittest

from scripts.generate_site import player_contract, validate_link_only_source, validate_media_source

SOURCE_URL = 'https://example.org/source'


class PlayerContractTest(unittest.TestCase):
    def test_declared_shapes_use_one_shared_frame(self):
        source = '<section class="wrap source-grid"><div class="video-shell"></div></section>'
        for aspect in ('16:9', '9:16', '1:1'):
            with self.subTest(aspect=aspect):
                rendered = player_contract(source, aspect, SOURCE_URL)
                self.assertIn(f'data-gm-aspect="{aspect}"', rendered)
                self.assertIn('class="wrap source-grid gm-source-layout"', rendered)
                self.assertEqual(rendered.count('gm-media-frame'), 1)

    def test_unknown_does_not_guess_from_platform_or_template(self):
        with self.assertRaisesRegex(ValueError, 'link-only fallback'):
            player_contract('<div class="player"></div>', 'unknown', SOURCE_URL)
        link = '<a href="https://example.org/source">Source</a>'
        self.assertEqual(player_contract(link, 'unknown', SOURCE_URL), link)

    def test_unknown_rejects_disguised_player_and_dormant_embed(self):
        link = '<a href="https://example.org/source">Source</a>'
        for snippet in (
            '<div class="new-player"></div>',
            '<iframe src="about:blank"></iframe>',
            '<button onclick="startPlayback()">Play</button>',
            '<script>document.createElement("iframe")</script>',
            '<script src="/assets/new-player.js"></script>',
            '<a href="javascript:startPlayback()">Play</a>',
        ):
            with self.subTest(snippet=snippet), self.assertRaisesRegex(ValueError, 'link-only fallback'):
                player_contract(link + snippet, 'unknown', SOURCE_URL)

    def test_unknown_requires_exact_direct_source_link(self):
        for snippet in ('<a href="https://example.org/other">Source</a>',
                        '<a href="/source">Source</a>', '<p>Source</p>'):
            with self.subTest(snippet=snippet), self.assertRaisesRegex(ValueError, 'direct source link'):
                validate_link_only_source(snippet, SOURCE_URL)

    def test_explicit_unknown_youtube_player_keeps_source_shape_unknown(self):
        url = 'https://www.youtube.com/watch?v=RHMsAm4ODDU'
        source = f'<div class="player"></div><a href="{url}">Original source</a>'
        rendered = player_contract(source, 'unknown', url, unknown_aspect_player_approved=True)
        self.assertIn('class="player gm-media-frame" data-gm-aspect="unknown"', rendered)
        with self.assertRaisesRegex(ValueError, 'direct source link'):
            player_contract('<div class="player"></div>', 'unknown', url, unknown_aspect_player_approved=True)
        with self.assertRaisesRegex(ValueError, 'exact YouTube watch URL'):
            player_contract(source, 'unknown', SOURCE_URL, unknown_aspect_player_approved=True)
        metadata = {'platform': 'YouTube', 'mediaAspect': 'unknown', 'videoId': 'RHMsAm4ODDU',
                    'url': url, 'unknownAspectPlayerApproved': True}
        validate_media_source(metadata)
        with self.assertRaisesRegex(ValueError, 'explicit YouTube approval'):
            validate_media_source({**metadata, 'url': 'https://www.youtube.com/watch?v=AAAAAAAAAAA'})


if __name__ == '__main__':
    unittest.main()
