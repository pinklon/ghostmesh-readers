"""Public, owner-approved Scout research register and deterministic catalog."""
from datetime import date, datetime, timezone
from html import escape
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit
import hashlib
import ipaddress
import json
import re

TYPES = {'investigation', 'essay', 'experiment', 'counterexample', 'method', 'journal', 'source-report'}
HOST = 'https://youtube.shareplane.malott.ai'
ROUTINE_POLICY = 'routine-source-report-v1'
VOID_TAGS = {'area', 'base', 'br', 'col', 'embed', 'hr', 'img', 'input', 'link',
             'meta', 'param', 'source', 'track', 'wbr'}
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


class SourceReportSurface(HTMLParser):
    """Collect only visible article copy, source links and dated observations."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.stack = []
        self.words = []
        self.links = set()
        self.dates = set()
        self.marked_article = False

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        parent_visible = self.stack[-1]['visible'] if self.stack else True
        parent_inside = self.stack[-1]['inside'] if self.stack else False
        marker = tag == 'article' and attrs.get('data-scout-source-report') == 'v1'
        style = attrs.get('style', '').replace(' ', '').lower()
        visible = (parent_visible and 'hidden' not in attrs
                   and attrs.get('aria-hidden') != 'true'
                   and not any(rule in style for rule in ('display:none', 'visibility:hidden', 'opacity:0'))
                   and tag not in {'script', 'style', 'noscript', 'template'})
        inside = parent_inside or marker
        if marker and visible:
            self.marked_article = True
        if tag not in VOID_TAGS:
            self.stack.append({'tag': tag, 'visible': visible, 'inside': inside,
                               'href': attrs.get('href'), 'date': attrs.get('datetime'),
                               'text': ''})

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index]['tag'] == tag:
                for element in self.stack[index:]:
                    if element['inside'] and element['visible'] and element['text'].strip():
                        if element['tag'] == 'a' and element['href']:
                            self.links.add(element['href'])
                        if element['tag'] == 'time' and element['date']:
                            self.dates.add(element['date'])
                del self.stack[index:]
                return

    def handle_data(self, data):
        if self.stack and self.stack[-1]['visible'] and self.stack[-1]['inside']:
            self.words.append(data)
            for element in self.stack:
                if element['visible'] and element['inside']:
                    element['text'] += data


def validate_routine_source_report(item, root):
    """Bind the narrow standing policy to exact public copy and independent review."""
    if item['type'] != 'source-report' or item['standingRelease'] != ROUTINE_POLICY:
        raise ValueError('Scout standing release class')
    if item['relatedIds']:
        raise ValueError('Routine source report cannot infer relationships')
    slug = item['slug']
    if item['id'] != f'report:{slug}':
        raise ValueError('Routine source report identity')
    source_path = f'site/scout/essays/{slug}/index.html'
    if item['sourcePath'] != source_path:
        raise ValueError('Routine source report path')
    raw = (root/source_path).read_bytes()
    review_path = root/f'content/scout/release-reviews/{slug}.json'
    if not review_path.is_file():
        raise ValueError('Routine source report independent review missing')
    review = json.loads(review_path.read_text())
    fields = {'schema', 'policy', 'researchId', 'sourceUrl', 'observedOn', 'reviewedOn',
              'sourceMethod', 'sourceSha256', 'reviewerTask', 'publisherTask', 'decision',
              'sourceReportedOnly', 'noNewRecommendation', 'noExecutionOrEntitlementClaim',
              'publicSafe', 'title', 'summary', 'evidenceLimits', 'topics'}
    if (not isinstance(review, dict) or set(review) != fields
            or review['schema'] != 'ghostmesh-scout-source-report-review-v1'
            or review['policy'] != ROUTINE_POLICY or review['researchId'] != item['id']
            or review['decision'] != 'accept'
            or review['sourceMethod'] not in {'official-release-note', 'official-docs', 'primary-repository'}
            or review['sourceSha256'] != hashlib.sha256(raw).hexdigest()
            or review['reviewedOn'] != item['reviewedOn']
            or any(review[key] != item[key] for key in ('title', 'summary', 'evidenceLimits', 'topics'))
            or any(review[field] is not True for field in ('sourceReportedOnly',
                'noNewRecommendation', 'noExecutionOrEntitlementClaim', 'publicSafe'))):
        raise ValueError('Routine source report review binding')
    if (not isinstance(review['reviewerTask'], str) or not review['reviewerTask'].strip()
            or not isinstance(review['publisherTask'], str) or not review['publisherTask'].strip()
            or review['reviewerTask'] == review['publisherTask']):
        raise ValueError('Routine source report reviewer independence')
    try:
        observed = date.fromisoformat(review['observedOn'])
        reviewed = date.fromisoformat(review['reviewedOn'])
    except (TypeError, ValueError):
        raise ValueError('Routine source report evidence dates')
    if observed > reviewed or reviewed > datetime.now(timezone.utc).date():
        raise ValueError('Routine source report evidence dates')
    if item['releaseEventId'] != f'scout:{slug}:first-public-release':
        raise ValueError('Routine source report release identity')
    url = review['sourceUrl']
    if not isinstance(url, str):
        raise ValueError('Routine source report primary URL')
    parsed = urlsplit(url)
    try:
        private_ip = not ipaddress.ip_address(parsed.hostname).is_global
    except (TypeError, ValueError):
        private_ip = False
    if (parsed.scheme != 'https' or not parsed.hostname or parsed.username or parsed.password
            or parsed.hostname == 'localhost' or private_ip
            or '/private/' in parsed.path or any(x in url.lower() for x in ('token=', 'signature=', 'secret='))):
        raise ValueError('Routine source report primary URL')
    page = raw.decode('utf-8')
    surface = SourceReportSurface()
    surface.feed(page)
    if (not surface.marked_article
            or url not in surface.links
            or f'<link rel="canonical" href="{HOST}{item["url"]}">' not in page
            or 'Source-reported; not independently tested' not in ' '.join(surface.words)
            or review['observedOn'] not in surface.dates
            or 'noindex' in page.lower() or item['provenance'] != url):
        raise ValueError('Routine source report public wrapper')
    return review


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
        routine = item.get('type') == 'source-report'
        expected_fields = required | ({'publicByOn', 'publicByEvidenceUrl'} if legacy else set()) | ({'standingRelease'} if routine else set())
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
        if routine:
            validate_routine_source_report(item, root)
            event = release_events[item['releaseEventId']]
            if date.fromisoformat(event['publicDate']) < date.fromisoformat(item['reviewedOn']):
                raise ValueError('Routine source report release before review')
            if event['title'] != item['title'] or event['summary'] != item['summary']:
                raise ValueError('Routine source report event copy differs from reviewed record')
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
