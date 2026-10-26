#!/usr/bin/env python3
"""Fail closed on the source scope of a standing-policy Scout release PR."""
import argparse
import json
from pathlib import Path
import subprocess

from scout_research import ROUTINE_POLICY, validate_routine_source_report

ROOT = Path(__file__).resolve().parents[1]
REGISTER = 'content/scout-research.json'
LEDGER = 'content/public-release-events.json'
PROJECTED = {
    'site/scout/index.html', 'site/scout/research/index.html',
    'site/scout/research/relationships.json', 'site/feed.xml', 'site/sitemap.xml',
}


def check_delta(old_records, records, old_events, events, changed):
    """Require one additive, source-bound report and one stable first-release event."""
    prior = {r['id']: r for r in old_records}
    current = {r['id']: r for r in records}
    if len(prior) != len(old_records) or len(current) != len(records):
        raise ValueError('Duplicate research ID')
    if any(current.get(key) != value for key, value in prior.items()):
        raise ValueError('Previously published research changed')
    added = [r for key, r in current.items() if key not in prior]
    if len(added) != 1 or added[0].get('standingRelease') != ROUTINE_POLICY or added[0].get('type') != 'source-report':
        raise ValueError('Standing release requires one new routine source report')
    item = added[0]
    slug = item['slug']
    expected_event_id = f'scout:{slug}:first-public-release'
    before = {e['id']: e for e in old_events}
    after = {e['id']: e for e in events}
    if (len(before) != len(old_events) or len(after) != len(events)
            or any(after.get(key) != value for key, value in before.items())):
        raise ValueError('Existing release events changed')
    new_events = [e for key, e in after.items() if key not in before]
    if (len(new_events) != 1 or new_events[0]['id'] != expected_event_id
            or new_events[0]['kind'] != 'new-scout-research'
            or item['releaseEventId'] != expected_event_id):
        raise ValueError('Standing release requires one first-publication event')
    required = {REGISTER, LEDGER, item['sourcePath'],
                f'content/scout/release-reviews/{slug}.json'}
    if not required <= changed or changed - required - PROJECTED:
        raise ValueError('Standing release changed paths outside one report and projections')
    return item


def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT, text=True).strip()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--base', required=True, help='Current main commit, verified against the PR base')
    parser.add_argument('--if-present', action='store_true', help='Skip PRs with no new standing-policy report')
    args = parser.parse_args()
    base = git('rev-parse', '--verify', args.base + '^{commit}')
    if subprocess.run(['git', 'merge-base', '--is-ancestor', base, 'HEAD'], cwd=ROOT).returncode:
        raise ValueError('Standing release base is not an ancestor')
    old_records = json.loads(git('show', f'{base}:{REGISTER}'))['records']
    records = json.loads((ROOT / REGISTER).read_text())['records']
    old_ids = {item['id'] for item in old_records}
    if args.if_present and not any(item.get('standingRelease') == ROUTINE_POLICY and item['id'] not in old_ids for item in records):
        print('SKIP standing Scout release scope: no new routine report')
        return
    if git('status', '--porcelain'):
        raise ValueError('Standing release checkout is dirty')
    changed = set(git('diff', '--name-only', base, 'HEAD').splitlines())
    old_events = json.loads(git('show', f'{base}:{LEDGER}'))['events']
    events = json.loads((ROOT / LEDGER).read_text())['events']
    item = check_delta(old_records, records, old_events, events, changed)
    validate_routine_source_report(item, ROOT)
    print(f'PASS standing Scout release scope: {item["id"]} at {git("rev-parse", "HEAD")}')


if __name__ == '__main__':
    main()
