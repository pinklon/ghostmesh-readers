"""Public, owner-approved Scout research register and deterministic catalog."""
from datetime import date
from html import escape
from pathlib import Path
import re

TYPES = {'investigation', 'essay', 'experiment', 'counterexample', 'method', 'journal'}
HOST = 'https://youtube.shareplane.malott.ai'
LEGACY_PUBLIC_BY_IDS = {
    'essay:the-signal-is-not-the-finding', 'essay:follow-the-work',
    'essay:five-ideas-outside-the-filter',
    'essay:a-faster-review-button-is-not-a-better-decision',
    'essay:the-plateau-that-lied', 'essay:latent-states-are-not-an-agent-api',
}


def publication_label(item, events):
    """Keep an evidenced public-by bound distinct from a first-release date."""
    event = events.get(item['releaseEventId']) if item['releaseEventId'] else None
    public_date = event['publicDate'] if event else item['publicByOn']
    day = date.fromisoformat(public_date)
    readable = f'{day.strftime("%B")} {day.day}, {day.year}'
    prefix = 'Published' if event else 'Public by'
    result = f'{prefix} <time datetime="{public_date}">{readable}</time>'
    if not event:
        result += ' · First-publication day unverified · <a href="' + escape(item['publicByEvidenceUrl'], quote=True) + '">Release record ↗</a>'
    if item['reviewedOn']:
        reviewed = date.fromisoformat(item['reviewedOn'])
        result += f' · Reviewed <time datetime="{item["reviewedOn"]}">{reviewed.strftime("%B")} {reviewed.day}, {reviewed.year}</time>'
    return result


def validate_research(source, scout, events, root):
    if source.get('schema') != 'ghostmesh-scout-research-v1' or not isinstance(source.get('records'), list):
        raise ValueError('Scout research schema')
    ids, urls = set(), set()
    reviews = {r['id']: r for r in scout['reviews']}
    release_events = {e['id']: e for e in events['events']}
    for item in source['records']:
        required = {'id', 'slug', 'type', 'status', 'title', 'url', 'sourcePath', 'provenance',
                    'evidenceLimits', 'summary', 'topics', 'reviewedOn', 'releaseEventId', 'relatedIds'}
        legacy = item.get('id') in LEGACY_PUBLIC_BY_IDS
        expected_fields = required | ({'publicByOn', 'publicByEvidenceUrl'} if legacy else set())
        if set(item) != expected_fields or item['type'] not in TYPES or item['status'] != 'published':
            raise ValueError('Invalid Scout research record fields/status')
        ident, slug, url = item['id'], item['slug'], item['url']
        if (not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9:]+(?:-[a-z0-9]+)*', ident)
                or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug)
                or ident in ids or url in urls):
            raise ValueError('Duplicate or invalid Scout research identity')
        ids.add(ident); urls.add(url)
        expected = ('/scout/reviews/' + slug + '/' if item['type'] == 'investigation' else
                    '/scout/research-journal/' if item['type'] == 'journal' else '/scout/essays/' + slug + '/')
        if url != expected or not url.endswith('/'):
            raise ValueError('Scout research canonical URL')
        path = item['sourcePath']
        if (not isinstance(path, str) or path.startswith('/') or '..' in Path(path).parts
                or '\\' in path or not path.startswith(('site/scout/essays/', 'content/scout/reviews/', 'site/scout/research-journal/'))
                or not (root/path).is_file()):
            raise ValueError('Scout research source path')
        if item['type'] == 'journal' and path != 'site/scout/research-journal/index.html':
            raise ValueError('Scout journal source path')
        for key in ('title', 'provenance', 'evidenceLimits', 'summary'):
            value = item[key]
            if not isinstance(value, str) or not value.strip() or '—' in value or any(x in value for x in ('/Users/', '/home/', 'token=', 'Bearer ')):
                raise ValueError('Scout research public-safe text: ' + key)
        if not isinstance(item['topics'], list) or not item['topics'] or not all(re.fullmatch(r'[a-z0-9-]+', v) for v in item['topics']):
            raise ValueError('Scout research topics')
        reviewed = item['reviewedOn']
        if reviewed is not None:
            try: date.fromisoformat(reviewed)
            except (ValueError, TypeError): raise ValueError('Scout research reviewed date')
        if legacy:
            if item['releaseEventId'] is not None or item['publicByOn'] != '2026-10-23' or item['publicByEvidenceUrl'] != 'https://github.com/pinklon/ghostmesh-readers/pull/72':
                raise ValueError('Scout legacy public-by evidence')
        elif item['releaseEventId'] is None:
            raise ValueError('Scout first-publication event required')
        if item['type'] == 'investigation':
            if slug not in reviews or reviewed != reviews[slug]['reviewedOn'] or item['title'] != reviews[slug]['title']:
                raise ValueError('Scout research review mismatch')
            event = release_events.get(item['releaseEventId'])
            if not event or event['kind'] != 'new-scout-review' or event['subjectId'] != slug or event['url'] != HOST + url:
                raise ValueError('Scout research release event mismatch')
        elif item['releaseEventId'] is not None:
            event = release_events.get(item['releaseEventId'])
            if not event or event['kind'] != 'new-scout-research' or event['subjectId'] != slug or event['url'] != HOST + url:
                raise ValueError('Scout research release event mismatch')
        if not isinstance(item['relatedIds'], list) or len(set(item['relatedIds'])) != len(item['relatedIds']):
            raise ValueError('Scout research relationships')
    for item in source['records']:
        if any(target not in ids or target == item['id'] for target in item['relatedIds']):
            raise ValueError('Scout research relationship target')
    if {r['id'] for r in source['records'] if r['type'] == 'investigation'} != set(reviews):
        raise ValueError('Scout research review inventory incomplete')
    return source


def research_graph(source):
    """Project only reviewed public Research Library identities and approved links."""
    records = sorted(source['records'], key=lambda item: item['id'])
    if any(item['status'] != 'published' for item in records):
        raise ValueError('Nonpublic Scout research graph record')
    by_id = {item['id']: item for item in records}
    return {
        'schema': 'ghostmesh-scout-research-relationships-v1',
        'scope': 'Public Scout research reading routes; links are editorial, not corroboration.',
        'authority': 'scout-research-curated-editorial',
        'visibility': 'public',
        'recordCount': len(records),
        'relationshipCount': sum(len(item['relatedIds']) for item in records),
        'nodes': [{'id': 'scout:' + item['id'], 'sourceId': item['id'],
                   'type': item['type'], 'title': item['title'],
                   'url': HOST + item['url']} for item in records],
        'edges': [{'from': 'scout:' + item['id'], 'to': 'scout:' + target,
                   'type': 'approved related work',
                   'fromUrl': HOST + item['url'], 'toUrl': HOST + by_id[target]['url']}
                  for item in records for target in item['relatedIds']],
    }


def research_page(source, events):
    records = sorted(source['records'], key=lambda r: (r['type'] != 'investigation', r['title'].lower()))
    release_events = {event['id']: event for event in events['events']}
    types = sorted({r['type'] for r in records})
    topics = sorted({tag for r in records for tag in r['topics']})
    options = lambda values: ''.join('<option value="' + escape(x, quote=True) + '">' + escape(x.replace('-', ' ').title()) + '</option>' for x in values)
    cards = []
    for item in records:
        searchable = ' '.join([item['title'], item['summary'], item['provenance'], ' '.join(item['topics'])])
        related = ''.join('<li><a href="' + escape(next(r['url'] for r in records if r['id'] == rid), quote=True) + '">' + escape(next(r['title'] for r in records if r['id'] == rid)) + '</a></li>' for rid in item['relatedIds'])
        cards.append('<article class="gm-scout-archive-card" data-research-card data-type="' + escape(item['type']) + '" data-topic="' + escape(' '.join(item['topics'])) + '" data-search="' + escape(searchable, quote=True) + '"><p class="gm-kicker">' + escape(item['type'].title()) + ' / ' + escape(', '.join(item['topics'])) + '</p><h2><a href="' + escape(item['url'], quote=True) + '">' + escape(item['title']) + '</a></h2><p>' + escape(item['summary']) + '</p><p><strong>Evidence boundary:</strong> ' + escape(item['evidenceLimits']) + '</p><p class="gm-scout-date">' + publication_label(item, release_events) + '</p>' + ('<details><summary>Approved related work</summary><ul>' + related + '</ul></details>' if related else '') + '</article>')
    from scout_pages import nav
    return (nav() +
            '<section class="gm-scout-archive"><header><p class="gm-kicker">GhostMesh / Scout / Public research</p><h1>The work behind the signal.</h1><p>One public record for reviewed source investigations and original essays. Read the evidence, challenge the interpretation and keep the unknowns visible. Private collection, tentative leads and internal experiments are not published here.</p></header>'
            '<form id="scout-research-filters" class="gm-scout-filters" role="search"><label>Search research<input id="research-query" type="search" placeholder="An idea, source or method"></label><label>Type<select id="research-type"><option value="">All types</option>' + options(types) + '</select></label><label>Topic<select id="research-topic"><option value="">All topics</option>' + options(topics) + '</select></label><button type="reset">Clear filters</button></form>'
            '<p id="research-count" role="status" aria-live="polite">' + str(len(cards)) + ' public works.</p><p><a href="/scout/research/relationships.json">Download approved Scout research relationships JSON ↗</a></p><div id="research-results">' + ''.join(cards) + '</div></section><script src="/assets/scout-research.js" defer></script>')
