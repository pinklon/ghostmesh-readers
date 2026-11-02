import hashlib
import json
import unittest
from unittest.mock import MagicMock, patch

from scripts.check_public_search_freshness import needs_refresh


def sources():
    catalog = b"current public catalog"
    digest = hashlib.sha256(catalog).hexdigest()
    records = [
        {"id": f"artifact:work-{i}", "title": f"Work {i}",
         "canonicalUrl": f"https://shareplane.malott.ai/artifacts/work-{i}/",
         "publiclyAccessible": True}
        for i in range(114)
    ]
    corpus = {"schemaVersion": "shareplane.reader-public-works-snapshot.v1",
              "sourceCatalogSha256": digest, "records": records,
              "publicWorkCount": 114, "verifiedPublicRouteCount": 114}
    return catalog, json.dumps(corpus).encode(), digest


class FreshnessTests(unittest.TestCase):
    def compare(self, deployed):
        catalog, corpus, _ = sources()
        response = MagicMock()
        response.__enter__.return_value.read.return_value = json.dumps(deployed).encode()
        with patch("scripts.check_public_search_freshness.fetch_shareplane_bytes",
                   side_effect=[catalog, corpus]), patch(
                       "urllib.request.urlopen",
                       return_value=response):
            return needs_refresh("https://shareplane.malott.ai/corpus.json",
                                 "https://shareplane.malott.ai/catalog.js",
                                 "https://youtube.shareplane.malott.ai/readers/unified-search-index.json")

    def test_current_does_not_request_deploy(self):
        _, _, digest = sources()
        self.assertFalse(self.compare({
            "schema": "ghostmesh-unified-search-v1",
            "sources": {"SharePlane": {"sourceCatalogSha256": digest, "count": 114}}}))

    def test_new_or_missing_source_requests_deploy(self):
        self.assertTrue(self.compare({
            "schema": "ghostmesh-unified-search-v1",
            "sources": {"SharePlane": {"sourceCatalogSha256": "0" * 64, "count": 114}}}))
        self.assertTrue(self.compare({"schema": "not-yet-unified"}))

    def test_rejects_unqualified_corpus(self):
        catalog, corpus, _ = sources()
        data = json.loads(corpus)
        data["records"][0]["publiclyAccessible"] = False
        with patch("scripts.check_public_search_freshness.fetch_shareplane_bytes",
                   side_effect=[catalog, json.dumps(data).encode()]):
            with self.assertRaisesRegex(ValueError, "qualification"):
                needs_refresh("https://shareplane.malott.ai/corpus.json",
                              "https://shareplane.malott.ai/catalog.js",
                              "https://youtube.shareplane.malott.ai/readers/unified-search-index.json")


if __name__ == "__main__":
    unittest.main()
