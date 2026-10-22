"""Small, public-only Scout and subscription projections. No private scanner input."""
from datetime import date, datetime, timezone
from email.utils import format_datetime
from html import escape
from urllib.parse import urlsplit
import json
import re

DIMENSIONS = ('ghostmeshFit', 'everydayUse', 'evidenceStrength', 'adoptionEffort')
RATINGS = {'high', 'mixed', 'low', 'unknown'}
METHODS = {'metadata-reviewed', 'source-inspected', 'executed', 'independently-measured'}
KINDS = {'new-reader', 'material-reader-update', 'new-scout-review', 'material-scout-update'}
SCOUT_PUBLIC_HOST = 'https://youtube.shareplane.malott.ai'
PRIVATE = re.compile(r'/Users/|/srv/ghostmesh/|/private/var/|gh[pousr]_[A-Za-z0-9]{20,}|(?:X-Amz-Signature|access_token|client_secret)=', re.I)
INVALID_XML = re.compile('[\x00-\x08\x0b\x0c\x0e-\x1f\ud800-\udfff\ufffe\uffff]')


def _text(value, label):
    if not isinstance(value, str) or not value.strip() or PRIVATE.search(value) or INVALID_XML.search(value):
        raise ValueError(f'{label}: missing or private text')
    return value.strip()


def _url(value, label, host=None):
    value = _text(value, label)
    parsed = urlsplit(value)
    if parsed.scheme != 'https' or not parsed.netloc or parsed.username or parsed.password:
        raise ValueError(f'{label}: HTTPS URL required')
    if host and (parsed.scheme + '://' + parsed.netloc) != host:
        raise ValueError(f'{label}: URL outside public site')
    return value


def _day(value, label):
    if not isinstance(value, str) or not re.fullmatch(r'\d{4}-\d{2}-\d{2}', value):
        raise ValueError(f'{label}: date must be YYYY-MM-DD')
    if date.fromisoformat(value) > datetime.now(timezone.utc).date():
        raise ValueError(f'{label}: future date')
    return value


def validate_scout(source):
    if set(source) != {'schema', 'reviews'} or source['schema'] != 'ghostmesh-public-scout-v1' or not isinstance(source['reviews'], list):
        raise ValueError('Scout public source schema')
    seen = set()
    for review in source['reviews']:
        required = {'id', 'title', 'sourceUrl', 'reviewedOn', 'method', 'confidence', 'identity', 'scope', 'summary', 'unknowns', 'ratings', 'sourceType', 'topic', 'audience', 'recommendation', 'discovery', 'selectionRationale', 'priorReviews'}
        if not isinstance(review, dict) or set(review) != required:
            raise ValueError('Scout review fields')
        ident = _text(review['id'], 'Scout ID')
        if not re.fullmatch(r'[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Scout review ID duplicate or invalid')
        seen.add(ident)
        _text(review['title'], 'Scout title')
        _text(review['identity'], 'Scout identity')
        _text(review['scope'], 'Scout review scope')
        _text(review['summary'], 'Scout summary')
        for field in ('topic', 'audience', 'selectionRationale'):
            _text(review[field], 'Scout ' + field)
        if review['sourceType'] != 'repository' or review['recommendation'] not in {'adapt', 'experiment', 'watch'} or not re.fullmatch(r'[a-z]+(?:-[a-z]+)*', review['topic']):
            raise ValueError('Scout classification')
        discovery = review['discovery']
        if not isinstance(discovery, dict) or set(discovery) != {'route', 'evidenceUrl', 'retainedHistoryUrl', 'firstRetainedObservation', 'originalDiscovery'} or discovery['route'] != 'explicit-research-priority' or discovery['originalDiscovery'] != 'not-recorded':
            raise ValueError('Scout discovery provenance')
        _url(discovery['evidenceUrl'], 'Scout priority record', SCOUT_PUBLIC_HOST)
        _url(discovery['retainedHistoryUrl'], 'Scout retained history', SCOUT_PUBLIC_HOST)
        stamp = datetime.fromisoformat(_text(discovery['firstRetainedObservation'], 'Scout retained observation'))
        if stamp.tzinfo is None or stamp > datetime.now(timezone.utc):
            raise ValueError('Scout retained observation timestamp')
        if not isinstance(review['priorReviews'], list):
            raise ValueError('Scout review history')
        for prior in review['priorReviews']:
            if not isinstance(prior, dict) or set(prior) != {'reviewedOn', 'recommendation', 'summary', 'url'} or prior['recommendation'] not in {'adapt', 'experiment', 'watch'}:
                raise ValueError('Scout prior review fields')
            _day(prior['reviewedOn'], 'Scout prior review date')
            _text(prior['summary'], 'Scout prior review summary')
            _url(prior['url'], 'Scout prior review URL')
        _url(review['sourceUrl'], 'Scout source')
        _day(review['reviewedOn'], 'Scout review date')
        if review['method'] not in METHODS or review['confidence'] not in {'high', 'medium', 'low'}:
            raise ValueError('Scout method or confidence')
        if not isinstance(review['unknowns'], str):
            raise ValueError('Scout unknowns must be explicit text')
        _text(review['unknowns'], 'Scout unknowns')
        ratings = review['ratings']
        if not isinstance(ratings, dict) or set(ratings) != set(DIMENSIONS):
            raise ValueError('Scout needs four ratings')
        for dimension in DIMENSIONS:
            rating = ratings[dimension]
            if not isinstance(rating, dict) or set(rating) != {'value', 'rationale', 'evidenceUrls'} or rating['value'] not in RATINGS:
                raise ValueError(f'Scout {dimension}: rating fields')
            _text(rating['rationale'], f'Scout {dimension} rationale')
            if not isinstance(rating['evidenceUrls'], list) or not rating['evidenceUrls']:
                raise ValueError(f'Scout {dimension}: source links required')
            for url in rating['evidenceUrls']:
                _url(url, f'Scout {dimension} evidence')
    return source


def validate_events(source, catalog, scout):
    if set(source) != {'schema', 'events'} or source['schema'] != 'ghostmesh-public-release-events-v1' or not isinstance(source['events'], list):
        raise ValueError('Public release event schema')
    host = catalog['host']
    readers = {r['id']: r for r in catalog['readers']}
    reviews = {r['id']: r for r in scout['reviews']}
    seen = set()
    first_releases = set()
    for event in source['events']:
        required = {'id', 'kind', 'subjectId', 'url', 'title', 'summary', 'publicDate'}
        if not isinstance(event, dict) or not required <= set(event) or set(event) - (required | {'releasedAt'}):
            raise ValueError('Public release event fields')
        ident = _text(event['id'], 'Release event ID')
        if not re.fullmatch(r'(?:reader|scout):[a-z0-9][a-z0-9-]*:[a-z0-9][a-z0-9-]*', ident) or ident in seen:
            raise ValueError('Duplicate or invalid release event ID')
        seen.add(ident)
        kind = event['kind']
        if kind not in KINDS:
            raise ValueError('Release event kind')
        subject = _text(event['subjectId'], 'Release subject')
        prefix = 'reader' if kind in {'new-reader', 'material-reader-update'} else 'scout'
        identity = subject if prefix == 'reader' else 'scout:' + subject
        if not ident.startswith(identity + ':'):
            raise ValueError('Release event ID does not bind subject')
        if prefix == 'reader':
            if subject not in readers or event['url'] != host + '/' + readers[subject]['slug'] + '/':
                raise ValueError('Release event Reader identity')
        elif subject not in reviews or event['url'] != host + '/scout/reviews/' + subject + '/':
            raise ValueError('Release event Scout identity')
        if kind in {'new-reader', 'new-scout-review'}:
            if identity in first_releases:
                raise ValueError('Duplicate first public release for subject')
            first_releases.add(identity)
        _url(event['url'], 'Release URL', host)
        _text(event['title'], 'Release title')
        _text(event['summary'], 'Release summary')
        _day(event['publicDate'], 'Release public date')
        if 'releasedAt' in event:
            raw = _text(event['releasedAt'], 'Release timestamp')
            stamp = datetime.fromisoformat(raw.replace('Z', '+00:00'))
            if stamp.tzinfo is None or stamp.date().isoformat() != event['publicDate']:
                raise ValueError('Release timestamp must be timezone-aware and match public date')
            if stamp > datetime.now(timezone.utc):
                raise ValueError('Release timestamp is in the future')
    return source


def _report_inline(value):
    """Render only the bold text and HTTPS links used by the authored report."""
    pattern = re.compile(r'\*\*([^*]+)\*\*|\[([^\]]+)\]\((https://[^)\s]+)\)')
    out = []
    end = 0
    for match in pattern.finditer(value):
        out.append(escape(value[end:match.start()]))
        if match.group(1) is not None:
            out.append('<strong>' + escape(match.group(1)) + '</strong>')
        else:
            out.append('<a href="' + escape(_url(match.group(3), 'Report source'), quote=True) + '">' + escape(match.group(2)) + '</a>')
        end = match.end()
    out.append(escape(value[end:]))
    return ''.join(out)


def scout_report_html(raw):
    """Render the reviewed, public Markdown without a dependency or raw HTML."""
    _text(raw, 'Scout report')
    blocks = [block.strip() for block in raw.split('\n\n') if block.strip()]
    if not blocks or not blocks[0].startswith('# '):
        raise ValueError('Scout report title required')
    rendered = []
    headings = []
    for block in blocks:
        if '\n' in block:
            raise ValueError('Scout report blocks must be paragraphs')
        if block.startswith('# '):
            rendered.append('<h2 id="first-scout-title">' + escape(block[2:]) + '</h2>')
        elif block.startswith('## '):
            title = block[3:]
            ident = 'report-' + re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            headings.append((ident, title))
            rendered.append('<h3 id="' + ident + '">' + escape(title) + '</h3>')
        else:
            kind = (' class="gm-scout-report-meta"' if block.startswith('GhostMesh Scout |')
                    else ' class="gm-scout-report-call"' if block.startswith('**Recommendation:')
                    else ' class="gm-scout-report-identity"' if block.startswith('**What it is.')
                    else ' class="gm-scout-report-scope"' if block.startswith('**What we inspected.') else '')
            rendered.append('<p' + kind + '>' + _report_inline(block) + '</p>')
    toc = ''.join('<a href="#' + ident + '">' + escape(title) + '</a>' for ident, title in headings)
    return ('<section class="gm-scout-report" aria-labelledby="first-scout-title">'
            '<div class="gm-scout-report-layout"><aside class="gm-scout-report-rail" aria-label="In this report">'
            '<p class="gm-kicker">FIRST LOOK / THREE PROJECTS</p><nav aria-label="Report sections">' + toc +
            '</nav><p>Read the source. Test the recommendation. Keep unknowns visible.</p></aside>'
            '<article class="gm-scout-report-copy">' + ''.join(rendered) + '</article></div></section>')


def scout_body(scout, report_html=''):
    intro = ('<section class="gm-scout-intro"><div class="gm-scout-intro-copy"><p class="gm-kicker">GhostMesh / Scout</p>'
             '<h1>Watch what might be useful. Keep the evidence in view.</h1>'
             '<p class="gm-scout-lede">Scout discovers tools and ideas, then records a first-pass review for GhostMesh and for everyday users. A discovery is not an adoption decision or a product test.</p>'
             '<p class="gm-scout-method">Ratings are editorial judgments linked to public sources. “Source inspected” means the source was read, not run. Execution and independent measurement are named only when actually done.</p></div>'
             '<aside class="gm-scout-follow" aria-labelledby="follow-scout-title"><div class="gm-scout-follow-top">'
             '<svg viewBox="0 0 24 24" width="24" height="24" fill="none" stroke="currentColor" stroke-width="2" aria-hidden="true"><circle cx="5" cy="19" r="2"/><path d="M3 11a10 10 0 0 1 10 10M3 3a18 18 0 0 1 18 18"/></svg>'
             '<p class="gm-kicker">One public feed / no account</p></div><h2 id="follow-scout-title">Follow Scout.</h2>'
             '<p>New Readers, meaningful Reader updates and published Scout reviews, together in one RSS feed.</p>'
             '<a class="gm-scout-subscribe" href="/feed.xml">Get the RSS feed <span aria-hidden="true">↗</span></a></aside></section>')
    if not scout['reviews']:
        if report_html:
            raise ValueError('A Scout report requires reviewed cards')
        return intro + '<section class="gm-scout-empty" aria-labelledby="scout-findings"><h2 id="scout-findings">Public reviews are being prepared.</h2><p>No Scout candidate review has been approved for this page yet. The private discovery watchlist is not a set of completed evaluations.</p></section>'
    names = {'ghostmeshFit': 'GhostMesh fit', 'everydayUse': 'Everyday usefulness', 'evidenceStrength': 'Evidence strength', 'adoptionEffort': 'Adoption effort'}
    cards = []
    for review in sorted(scout['reviews'], key=lambda r: r['reviewedOn'], reverse=True):
        ratings = []
        for key in DIMENSIONS:
            item = review['ratings'][key]
            links = ' '.join(f'<a href="{escape(url, quote=True)}">Source {i + 1} ↗</a>' for i, url in enumerate(item['evidenceUrls']))
            ratings.append(f'<div><dt>{names[key]}</dt><dd><strong>{escape(item["value"])}</strong> {escape(item["rationale"])} <span>{links}</span></dd></div>')
        recommendation = review['summary'].split('. ', 1)[0] + '.'
        analysis = 'report-' + re.sub(r'[^a-z0-9]+', '-', review['title'].lower()).strip('-')
        analysis_link = f'<a class="gm-scout-analysis-link" href="#{analysis}">Read the analysis ↑</a>' if f'id="{analysis}"' in report_html else ''
        cards.append(f'<article id="{escape(review["id"])}" class="gm-scout-card"><p class="gm-kicker">Reviewed {escape(review["reviewedOn"])} · {escape(review["method"].replace("-", " "))} · confidence {escape(review["confidence"])}</p><h3><a href="{escape(review["sourceUrl"], quote=True)}">{escape(review["title"])}</a></h3><p class="gm-scout-identity">{escape(review["identity"])}</p><p class="gm-scout-scope"><strong>Review boundary</strong> {escape(review["scope"])}</p><p class="gm-scout-recommendation">{escape(recommendation)}</p>{analysis_link}<details><summary>Ratings, rationale and limits</summary><dl>{"".join(ratings)}</dl><p><strong>Still unknown:</strong> {escape(review["unknowns"])}</p></details></article>')
    return intro + report_html + '<section class="gm-scout-reviews" aria-labelledby="scout-findings"><p class="gm-kicker">ASSESSMENT RECORD</p><h2 id="scout-findings">Source-linked scorecards</h2><p class="gm-scout-card-intro">The argument lives in the report above. These records keep the source links, review boundary, ratings and unresolved questions together.</p>' + ''.join(cards) + '</section>'


def feed_xml(events, host):
    items = []
    for event in sorted(events['events'], key=lambda item: (item.get('releasedAt', item['publicDate']), item['id']), reverse=True):
        item = '<item><title>' + escape(event['title']) + '</title><link>' + escape(event['url']) + '</link>'
        item += '<guid isPermaLink="false">urn:ghostmesh-readers:release:' + escape(event['id']) + '</guid>'
        item += '<description>' + escape(event['summary']) + '</description><dc:date>' + event['publicDate'] + '</dc:date>'
        if 'releasedAt' in event:
            stamp = datetime.fromisoformat(event['releasedAt'].replace('Z', '+00:00'))
            item += '<pubDate>' + format_datetime(stamp) + '</pubDate>'
        items.append(item + '</item>')
    return ('<?xml version="1.0" encoding="UTF-8"?>\n'
            '<rss version="2.0" xmlns:dc="http://purl.org/dc/elements/1.1/"><channel>'
            '<title>GhostMesh Readers and Scout</title><link>' + escape(host) + '/</link>'
            '<description>New Readers, substantive Reader revisions and published Scout reviews.</description>'
            '<language>en</language>' + ''.join(items) + '</channel></rss>\n')
