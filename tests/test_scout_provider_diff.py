import copy
import json
import sys
from pathlib import Path
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from scout_provider_diff import compare, unknown_baseline, SCHEMA
from scout_provider_watch import parse_html


def snapshot(entries, status="observed", when="2026-10-22T00:00:00Z"):
    return {"schema": SCHEMA, "observed_at": when, "observations": [
        {"id": "openai-news", "provider": "OpenAI", "status": status, "entries": entries}]}


class ProviderDiffTests(unittest.TestCase):
    def test_first_snapshot_is_unknown_not_six_new_launches(self):
        result = unknown_baseline(snapshot([{"title": "Decisions GA",
                                             "url": "https://openai.com/index/decisions-api/"}]))
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["source_health"], [{"id": "openai-news", "status": "UNKNOWN",
                                                    "reason": "no-prior-main-snapshot"}])
        self.assertEqual(result["publication_status"], "NOT_APPROVED")

    def test_new_entry_and_duplicate_url(self):
        baseline = {"title": "Earlier release", "url": "https://openai.com/index/earlier-release/"}
        first = snapshot([baseline])
        second = snapshot([baseline, {"title": "Agents API", "url": "https://openai.com/index/devday-2026-recap/"},
                           {"title": "Agents API repost", "url": "https://openai.com/index/devday-2026-recap"}])
        result = compare(first, second)
        self.assertEqual(len(result["candidates"]), 1)
        self.assertEqual(result["candidates"][0]["kind"], "new-source-entry")
        self.assertEqual(result["publication_status"], "NOT_APPROVED")

    def test_unknown_source_is_not_zero_releases(self):
        result = compare(snapshot([{"title": "Decisions", "url": "https://openai.com/index/decisions-api/"}]),
                         snapshot([], status="unknown"))
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["source_health"][0]["status"], "UNKNOWN")

    def test_one_unsupported_entry_does_not_make_a_source_comparable(self):
        good = {"title": "Earlier release", "url": "https://example.com/earlier"}
        result = compare(snapshot([good]), snapshot([good, {"level": "h2", "text": "New heading"}]))
        self.assertEqual(result["candidates"], [])
        self.assertEqual(result["source_health"][0]["status"], "UNKNOWN")

    def test_changed_title_requires_review(self):
        old = snapshot([{"title": "Preview", "url": "https://example.com/release"}])
        new = snapshot([{"title": "Generally available", "url": "https://example.com/release"}])
        result = compare(old, new)
        self.assertEqual(result["candidates"][0]["kind"], "changed-entry-title")
        self.assertEqual(result["candidates"][0]["editorial_status"], "NOT_APPROVED")

    def test_different_dates_do_not_reannounce(self):
        old = snapshot([{"title": "Decisions GA", "url": "https://openai.com/index/decisions-api/"}])
        new = snapshot([{"title": "Decisions GA", "url": "https://openai.com/index/decisions-api/"}],
                       when="2026-10-23T00:00:00Z")
        self.assertEqual(compare(old, new)["candidates"], [])

    def test_missing_source_and_bad_schema(self):
        self.assertEqual(compare(snapshot([{"title": "Earlier", "url": "https://example.com/earlier"}]),
                                 {"schema": SCHEMA, "observations": []})["source_health"][0]["status"], "UNKNOWN")
        with self.assertRaises(ValueError):
            compare({"schema": "bad", "observations": []}, snapshot([]))

    def test_all_six_sources_keep_html_changes_separate_from_rss_releases(self):
        registry = json.loads((Path(__file__).resolve().parents[1] /
                               'content/scout/provider-sources.json').read_text())['sources']
        self.assertEqual(len(registry), 6)
        self.assertEqual(sum(source['format'] == 'html' for source in registry), 4)
        observations = []
        for source in registry:
            entries = (parse_html(b'<h2>Earlier heading</h2>') if source['format'] == 'html'
                       else [{"title": "Earlier release", "url": source['url']}])
            observations.append({"id": source['id'], "provider": source['provider'],
                                 "source_url": source['url'], "status": "observed", "entries": entries})
        previous = {"schema": SCHEMA, "observations": observations}
        unchanged = compare(previous, previous)
        self.assertEqual(unchanged['candidates'], [])
        health = {item['id']: item['status'] for item in unchanged['source_health']}
        self.assertEqual({health[source['id']] for source in registry if source['format'] == 'html'}, {'heading-only'})
        self.assertEqual({health[source['id']] for source in registry if source['format'] == 'rss'}, {'comparable'})

        for source in registry:
            with self.subTest(source=source['id']):
                changed = copy.deepcopy(previous)
                target = next(item for item in changed['observations'] if item['id'] == source['id'])
                target['entries'] = (parse_html(b'<h2>Changed heading</h2>') if source['format'] == 'html'
                                     else [{"title": "Changed release", "url": source['url']}])
                result = compare(previous, changed)
                changed_health = next(item for item in result['source_health'] if item['id'] == source['id'])
                if source['format'] == 'html':
                    self.assertEqual(changed_health['status'], 'heading-only')
                    self.assertEqual([(item['source_id'], item['kind'], item['editorial_status'])
                                      for item in result['candidates']],
                                     [(source['id'], 'source-heading-window-change', 'NOT_APPROVED')])
                    self.assertNotIn('title', result['candidates'][0])
                else:
                    self.assertEqual(changed_health['status'], 'comparable')
                    self.assertEqual([(item['source_id'], item['kind']) for item in result['candidates']],
                                     [(source['id'], 'changed-entry-title')])

                target['entries'] = []
                empty = compare(previous, changed)
                self.assertEqual(empty['candidates'], [])
                self.assertEqual(next(item for item in empty['source_health'] if item['id'] == source['id'])['status'],
                                 'UNKNOWN')

        mixed = copy.deepcopy(previous)
        google = next(item for item in mixed['observations'] if item['id'] == 'google-gemini')
        google['entries'] = parse_html(b'<h2>New Gemini release</h2>')
        openai = next(item for item in mixed['observations'] if item['id'] == 'openai-news')
        openai['entries'][0]['title'] = 'New OpenAI release'
        result = compare(previous, mixed)
        self.assertEqual([(item['source_id'], item['kind']) for item in result['candidates']],
                         [('google-gemini', 'source-heading-window-change'),
                          ('openai-news', 'changed-entry-title')])
        self.assertEqual(next(item for item in result['source_health'] if item['id'] == 'google-gemini')['status'],
                         'heading-only')

    def test_heading_reorder_is_not_misreported_as_new_feature(self):
        old = snapshot([{"level": "h2", "text": "October 22"},
                        {"level": "h2", "text": "October 21"}])
        new = snapshot([{"level": "h2", "text": "October 21"},
                        {"level": "h2", "text": "October 22"}])
        old['observations'][0]['source_url'] = 'https://example.com/releases'
        new['observations'][0]['source_url'] = 'https://example.com/releases'
        candidate = compare(old, new)['candidates'][0]
        self.assertEqual(candidate['kind'], 'source-heading-window-change')
        self.assertEqual(candidate['added_headings'], [])
        self.assertEqual(candidate['removed_headings'], [])
        self.assertNotIn('release_status', candidate)


if __name__ == "__main__":
    unittest.main()
