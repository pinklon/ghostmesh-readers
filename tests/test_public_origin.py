import hashlib
import json
from pathlib import Path
import shutil
import tempfile
import unittest
from xml.etree import ElementTree as ET

from scripts.build_unified_search_index import build
from scripts.knowledge_contract import build_claim_register, validate_contract
from scripts.project_public_origin import OLD, NEW, RECEIPT, project, project_html

ROOT = Path(__file__).resolve().parents[1]


class PublicOriginTests(unittest.TestCase):
    def test_only_url_attributes_are_projected(self):
        original = f'<link rel="canonical" href="{OLD}/reader/"><a href="{OLD}/reader/#claim">Exact prose</a>'.encode()
        self.assertEqual(project_html(original), original.replace(OLD.encode(), NEW.encode()))
        for raw in (f'<p>{OLD}/reader/</p>', f'<script>let x="{OLD}"</script>',
                    f'<a href="{OLD}.example/reader/">bad</a>',
                    f'<img alt="{OLD}">'):
            with self.subTest(raw=raw), self.assertRaises(ValueError):
                project_html(raw.encode())

    def test_real_public_projection_preserves_source_and_rebinds_knowledge(self):
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary)
            output = repo / "site"
            shutil.copytree(ROOT / "site", output)
            catalog = json.loads((ROOT / "site/catalog.json").read_text())
            readers = json.loads((ROOT / "site/readers/search-index.json").read_text())
            shareplane = {
                "schemaVersion": "shareplane.reader-public-works-snapshot.v1",
                "sourceCatalogSha256": "a" * 64, "publicWorkCount": 1,
                "verifiedPublicRouteCount": 1,
                "records": [{"id": "work:fixture", "title": "Synthetic test work",
                             "canonicalUrl": "https://shareplane.malott.ai/artifacts/fixture/",
                             "publiclyAccessible": True, "text": "Fixture text"}],
            }
            index = build(readers, shareplane, reader_catalog=catalog)
            (output / "readers/unified-search-index.json").write_text(json.dumps(index))
            before = {p.relative_to(output).as_posix(): p.read_bytes()
                      for p in output.rglob("*") if p.is_file()}
            receipt = project(output)
            after = {p.relative_to(output).as_posix(): p.read_bytes()
                     for p in output.rglob("*") if p.is_file()}
            self.assertEqual(set(after) - set(before), {RECEIPT})
            self.assertEqual(set(x["path"] for x in receipt["files"]),
                             {p for p in before if before[p] != after[p]})
            for entry in receipt["files"]:
                path = entry["path"]
                self.assertEqual(entry["sourceSha256"], hashlib.sha256(before[path]).hexdigest())
                self.assertEqual(entry["projectedSha256"], hashlib.sha256(after[path]).hexdigest())
                if path.endswith(".html"):
                    self.assertEqual(after[path], before[path].replace(OLD.encode(), NEW.encode()))
            self.assertTrue(all(before[p] == after[p] for p in before if p.endswith("/receipt.json")))
            new_catalog = json.loads(after["catalog.json"])
            self.assertEqual(new_catalog, dict(catalog, host=NEW))
            new_index = json.loads(after["readers/unified-search-index.json"])
            for prior, current in zip(index["records"], new_index["records"]):
                expected = dict(prior)
                if prior["source"] == "Readers":
                    expected["url"] = prior["url"].replace(OLD, NEW)
                self.assertEqual(current, expected)
            old_guids = [e.text for e in ET.fromstring(before["feed.xml"]).iter("guid")]
            new_guids = [e.text for e in ET.fromstring(after["feed.xml"]).iter("guid")]
            self.assertEqual(old_guids, new_guids)
            self.assertEqual(before["knowledge/v0.1/contract.schema.json"],
                             after["knowledge/v0.1/contract.schema.json"])
            old_ld = json.loads(before["knowledge/v0.1/readers.jsonld"])
            new_ld = json.loads(after["knowledge/v0.1/readers.jsonld"])
            self.assertEqual(old_ld["@context"], new_ld["@context"])

            # Validate published graph and all 672 claim bindings against the
            # actual projected page bytes using the established contract.
            (repo / "content").mkdir()
            source_catalog = json.loads((ROOT / "content/catalog.json").read_text())
            source_catalog["host"] = NEW
            (repo / "content/catalog.json").write_text(json.dumps(source_catalog))
            graph = json.loads(after["knowledge/v0.1/readers.json"])
            schema = json.loads(after["knowledge/v0.1/contract.schema.json"])
            validate_contract(graph, schema, repo)
            self.assertEqual(build_claim_register(source_catalog, graph, repo),
                             json.loads(after["knowledge/v0.1/claim-register.json"]))
            manifest = json.loads(after["knowledge/v0.1/publication-manifest.json"])
            prior_manifest = json.loads(before["knowledge/v0.1/publication-manifest.json"])
            self.assertEqual(manifest["sourceSha256"], prior_manifest["sourceSha256"])
            self.assertEqual(manifest["schemaSha256"], prior_manifest["schemaSha256"])
            for item in manifest["outputs"]:
                data = after[item["path"].removeprefix("site/")]
                self.assertEqual(item["sha256"], hashlib.sha256(data).hexdigest())
                self.assertEqual(item["bytes"], len(data))
            with self.assertRaises(ValueError):
                project(output)


if __name__ == "__main__":
    unittest.main()
