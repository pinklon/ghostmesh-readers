"""Public, owner-approved Scout research register and deterministic catalog."""
from datetime import date
from html import escape
from pathlib import Path
import re

TYPES = {'investigation', 'essay', 'experiment', 'counterexample', 'method'}
HOST = 'https://youtube.shareplane.malott.ai'


def validate_research(source, scout, events, root):
    if source.get('schema') != 'ghostmesh-scout-research-v1' or not isinstance(source.get('records'), list):
        raise ValueError('Scout research schema')
    ids, urls = set(), set()
    reviews = {r['id']: r for r in scout['reviews']}
    release_events = {e['id']: e for e in events['events']}
    for item in source['records']:
        required = {'id', 'slug', 'type', 'status', 'title', 'url', 'sourcePath', 'provenance',
                    'evidenceLimits', 'summary', 'topics', 'reviewedOn', 'releaseEventId', 'relatedIds'}
        if set(item) != required or item['type'] not in TYPES or item['status'] != 'published':
            raise ValueError('Invalid Scout research record fields/status')
        ident, slug, url = item['id'], item['slug'], item['url']
        if (not isinstance(ident, str) or not re.fullmatch(r'[a-z0-9:]+(?:-[a-z0-9]+)*', ident)
                or not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', slug)
                or ident in ids or url in urls):
            raise ValueError('Duplicate or invalid Scout research identity')
        ids.add(ident); urls.add(url)
        expected = '/scout/reviews/' + slug + '/' if item['type'] == 'investigation' else '/scout/essays/' + slug + '/'
        if url != expected or not url.endswith('/'):
            raise ValueError('Scout research canonical URL')
        path = item['sourcePath']
        if (not isinstance(path, str) or path.startswith('/') or '..' in Path(path).parts
                or '\\' in path or not path.startswith(('site/scout/essays/', 'content/scout/reviews/'))
                or not (root/path).is_file()):
            raise ValueError('Scout research source path')
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
        if item['type'] == 'investigation':
            if slug not in reviews or reviewed != reviews[slug]['reviewedOn'] or item['title'] != reviews[slug]['title']:
                raise ValueError('Scout research review mismatch')
            event = release_events.get(item['releaseEventId'])
            if not event or event['subjectId'] != slug or event['url'] != HOST + url:
                raise ValueError('Scout research release event mismatch')
        elif item['releaseEventId'] is not None and item['releaseEventId'] not in release_events:
            raise ValueError('Scout research unknown release event')
        if not isinstance(item['relatedIds'], list) or len(set(item['relatedIds'])) != len(item['relatedIds']):
            raise ValueError('Scout research relationships')
    for item in source['records']:
        if any(target not in ids or target == item['id'] for target in item['relatedIds']):
            raise ValueError('Scout research relationship target')
    if {r['id'] for r in source['records'] if r['type'] == 'investigation'} != set(reviews):
        raise ValueError('Scout research review inventory incomplete')
    return source


def research_page(source):
    records = sorted(source['records'], key=lambda r: (r['type'] != 'investigation', r['title'].lower()))
    types = sorted({r['type'] for r in records})
    topics = sorted({tag for r in records for tag in r['topics']})
    options = lambda values: ''.join('<option value="' + escape(x, quote=True) + '">' + escape(x.replace('-', ' ').title()) + '</option>' for x in values)
    cards = []
    for item in records:
        searchable = ' '.join([item['title'], item['summary'], item['provenance'], ' '.join(item['topics'])])
        related = ''.join('<li><a href="' + escape(next(r['url'] for r in records if r['id'] == rid), quote=True) + '">' + escape(next(r['title'] for r in records if r['id'] == rid)) + '</a></li>' for rid in item['relatedIds'])
        cards.append('<article class="gm-scout-archive-card" data-research-card data-type="' + escape(item['type']) + '" data-topic="' + escape(' '.join(item['topics'])) + '" data-search="' + escape(searchable, quote=True) + '"><p class="gm-kicker">' + escape(item['type'].title()) + ' / ' + escape(', '.join(item['topics'])) + '</p><h2><a href="' + escape(item['url'], quote=True) + '">' + escape(item['title']) + '</a></h2><p>' + escape(item['summary']) + '</p><p><strong>Evidence boundary:</strong> ' + escape(item['evidenceLimits']) + '</p>' + ('<p>Reviewed ' + escape(item['reviewedOn']) + '</p>' if item['reviewedOn'] else '<p>Historical essay / release date not asserted</p>') + ('<details><summary>Approved related work</summary><ul>' + related + '</ul></details>' if related else '') + '</article>')
    return ('<nav class="gm-scout-local-nav" aria-label="Scout navigation"><a href="/scout/">Latest</a><a href="/scout/research/">Research Library</a><a href="/scout/method/">How Scout works</a></nav>'
            '<section class="gm-scout-archive"><header><p class="gm-kicker">GhostMesh / Scout / Public research</p><h1>The work behind the signal.</h1><p>One public record for reviewed source investigations and original essays. Read the evidence, challenge the interpretation and keep the unknowns visible. Private collection, tentative leads and internal experiments are not published here.</p></header>'
            '<form id="scout-research-filters" class="gm-scout-filters" role="search"><label>Search research<input id="research-query" type="search" placeholder="An idea, source or method"></label><label>Type<select id="research-type"><option value="">All types</option>' + options(types) + '</select></label><label>Topic<select id="research-topic"><option value="">All topics</option>' + options(topics) + '</select></label><button type="reset">Clear filters</button></form>'
            '<p id="research-count" role="status" aria-live="polite">' + str(len(cards)) + ' public works.</p><div id="research-results">' + ''.join(cards) + '</div></section><script src="/assets/scout-research.js" defer></script>')
