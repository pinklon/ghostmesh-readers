import sys
from pathlib import Path
import unittest
from unittest.mock import patch

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import scout_provider_watch as watch


class ProviderWatchTests(unittest.TestCase):
    def setUp(self):
        self.source = {"id": "openai-news", "provider": "OpenAI",
                       "format": "rss", "url": "https://openai.com/news/rss.xml"}

    def test_rejects_unapproved_host_and_duplicates(self):
        with self.assertRaises(ValueError):
            watch.validate_registry({"schema": "ghostmesh-scout-provider-sources-v1",
                                     "sources": [dict(self.source, url="https://example.com/feed")]})
        with self.assertRaises(ValueError):
            watch.validate_registry({"schema": "ghostmesh-scout-provider-sources-v1",
                                     "sources": [self.source, self.source]})

    def test_rss_observation_is_not_publication(self):
        payload = b"<rss><channel><item><title>Decisions API</title><link>https://openai.com/index/decisions-api/</link><pubDate>Thu, 22 Oct 2026 00:00:00 GMT</pubDate></item></channel></rss>"
        with patch.object(watch, "fetch", return_value=payload):
            result = watch.collect({"schema": "ghostmesh-scout-provider-sources-v1",
                                    "sources": [self.source]}, "2026-10-23T12:00:00+00:00")
        self.assertEqual(result["publication_status"], "NOT_APPROVED")
        self.assertEqual(result["observations"][0]["status"], "observed")
        self.assertEqual(result["observations"][0]["entries"][0]["title"], "Decisions API")

    def test_failure_is_unknown_not_zero(self):
        with patch.object(watch, "fetch", side_effect=TimeoutError):
            record = watch.observe(self.source, "2026-10-23T12:00:00+00:00")
        self.assertEqual(record["status"], "unknown")
        self.assertNotIn("entries", record)

    def test_html_only_captures_headings(self):
        data = b"<script><h1>secret</h1></script><h1>New release</h1><h2>Generally available</h2>"
        self.assertEqual([x["text"] for x in watch.parse_html(data)],
                         ["New release", "Generally available"])


if __name__ == "__main__":
    unittest.main()
