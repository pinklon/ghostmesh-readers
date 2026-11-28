import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

from scripts.refresh_unified_public_search import fetch_shareplane_bytes, refresh
from test_unified_search_index import fixtures


class PublicRefreshTests(unittest.TestCase):
    def test_netlify_compatibility_entry_uses_same_build(self):
        from scripts import build_public_site, netlify_unified_search_build
        self.assertIs(netlify_unified_search_build.main, build_public_site.main)

    def test_incumbent_build_uses_canonical_public_feeds(self):
        from scripts import build_public_site as build
        with patch.dict("os.environ", {}, clear=True), patch.object(build, "refresh") as run:
            build.main()
            run.assert_called_once_with(
                Path("site/readers/search-index.json"), build.CANONICAL_CORPUS,
                build.CANONICAL_CATALOG, Path("site/readers/unified-search-index.json"),
                build.MIN_READERS, build.MIN_WORKS, Path("site/catalog.json"))

    def test_incumbent_build_rejects_noncanonical_override(self):
        from scripts import build_public_site as build
        with patch.dict("os.environ", {"SHAREPLANE_PUBLIC_CORPUS_URL": "https://shareplane.malott.ai/other.json"}, clear=True), patch.object(build, "refresh") as run:
            with self.assertRaises(SystemExit):
                build.main()
            run.assert_not_called()

    def test_rejects_untrusted_corpus_host(self):
        for url in ("http://shareplane.malott.ai/corpus.json",
                    "https://evil.example/corpus.json",
                    "https://shareplane.malott.ai@evil.example/corpus.json"):
            with self.subTest(url=url), self.assertRaises(ValueError):
                fetch_shareplane_bytes(url)

    def test_verified_refresh_and_last_good_on_drift(self):
        readers, works = fixtures()
        catalog = b"current public catalog"
        works["sourceCatalogSha256"] = hashlib.sha256(catalog).hexdigest()
        corpus = json.dumps(works).encode()
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary)
            reader_path = path / "readers.json"
            output_path = path / "unified.json"
            reader_path.write_text(json.dumps(readers))
            with patch("scripts.refresh_unified_public_search.fetch_shareplane_bytes",
                       side_effect=[catalog, corpus]):
                refresh(reader_path, "https://shareplane.malott.ai/works.json",
                        "https://shareplane.malott.ai/catalog.js", output_path, 1, 1)
            result = json.loads(output_path.read_text())
            self.assertEqual(len(result["records"]), 2)
            good = output_path.read_bytes()

            works["sourceCatalogSha256"] = "0" * 64
            drifted = json.dumps(works).encode()
            with patch("scripts.refresh_unified_public_search.fetch_shareplane_bytes",
                       side_effect=[catalog, drifted]):
                with self.assertRaisesRegex(ValueError, "approved current source"):
                    refresh(reader_path, "https://shareplane.malott.ai/works.json",
                            "https://shareplane.malott.ai/catalog.js", output_path, 1, 1)
            self.assertEqual(output_path.read_bytes(), good)


if __name__ == "__main__":
    unittest.main()
