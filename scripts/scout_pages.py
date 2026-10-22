"""Deterministic public Scout pages from reviewed JSON and Markdown only."""
from html import escape
from pathlib import Path
import re

from scout_feed import DIMENSIONS, _day, _report_inline, _text


def review_url(review):
    return '/scout/reviews/' + review['id'] + '/'


def edition_url(edition):
    return '/scout/editions/' + edition['id'] + '/'


def validate_editions(source, scout):
    if set(source) != {'schema', 'editions'} or source['schema'] != 'ghostmesh-public-scout-editions-v1' or not isinstance(source['editions'], list):
        raise ValueError('Scout edition schema')
    reviews = {review['id'] for review in scout['reviews']}
    seen = set()
    for edition in source['editions']:
        if not isinstance(edition, dict) or set(edition) != {'id', 'title', 'reviewedOn', 'summary', 'reviewIds'}:
            raise ValueError('Scout edition fields')
        ident = _text(edition['id'], 'Scout edition ID')
        if not re.fullmatch(r'\d{4}-\d{2}-\d{2}-[a-z0-9]+(?:-[a-z0-9]+)*', ident) or ident in seen:
            raise ValueError('Scout edition ID')
        seen.add(ident)
        _day(edition['reviewedOn'], 'Scout edition review date')
        if not ident.startswith(edition['reviewedOn'] + '-'):
            raise ValueError('Scout edition date identity')
        _text(edition['title'], 'Scout edition title')
        _text(edition['summary'], 'Scout edition summary')
        ids = edition['reviewIds']
        if not isinstance(ids, list) or not ids or len(ids) > 3 or len(ids) != len(set(ids)) or not set(ids) <= reviews:
            raise ValueError('Scout edition reviews')
    return source


def prose_html(raw, drop_title=False):
    """Render the small reviewed Markdown vocabulary; never admit raw HTML."""
    _text(raw, 'Scout prose')
    blocks = [block.strip() for block in raw.split('\n\n') if block.strip()]
    if not blocks or not blocks[0].startswith('# '):
        raise ValueError('Scout prose title required')
    output = []
    for index, block in enumerate(blocks):
        if '\n' in block:
            raise ValueError('Scout prose blocks must be paragraphs')
        if block.startswith('# '):
            if index or drop_title:
                if index:
                    raise ValueError('Duplicate Scout prose title')
                continue
            output.append('<h1>' + escape(block[2:]) + '</h1>')
        elif block.startswith('## '):
            title = block[3:]
            ident = 'section-' + re.sub(r'[^a-z0-9]+', '-', title.lower()).strip('-')
            output.append('<h2 id="' + ident + '">' + escape(title) + '</h2>')
        else:
            style = (' gm-scout-prose-meta' if block.startswith('GhostMesh Scout |') else
                     ' gm-scout-prose-identity' if block.startswith('**What it is.') else
                     ' gm-scout-prose-scope' if block.startswith('**What we inspected.') else
                     ' gm-scout-prose-call' if block.startswith('**Recommendation:') else '')
            output.append('<p class="gm-scout-prose-paragraph' + style + '">' + _report_inline(block) + '</p>')
    return ''.join(output)


def nav():
    return ('<nav class="gm-scout-local-nav" aria-label="Scout navigation">'
            '<a href="/scout/">Latest</a><a href="/scout/archive/">Review library</a>'
            '<a href="/scout/method/">How Scout works</a></nav>')


def call(review):
    return review['summary'].split('. ', 1)[0] + '.'


def source_label(review):
    return review['method'].replace('-', ' ') + ' · ' + review['sourceType'] + ' · reviewed ' + review['reviewedOn']


def home(scout, edition):
    by_id = {review['id']: review for review in scout['reviews']}
    featured = [by_id[ident] for ident in edition['reviewIds']][:3]
    cards = ''.join('<article class="gm-scout-feature"><p class="gm-kicker">' + escape(source_label(review)) +
        '</p><h3><a href="' + review_url(review) + '">' + escape(review['title']) + '</a></h3>' +
        '<p>' + escape(review['identity']) + '</p><strong>' + escape(call(review)) + '</strong></article>' for review in featured)
    return (nav() + '<section class="gm-scout-home-hero"><div><p class="gm-kicker">GhostMesh / Scout</p>'
        '<h1>Notice the signal. Keep the evidence in view.</h1><p>Scout reviews public tools and ideas through two lenses: what GhostMesh might learn, and what an everyday user could actually use. Each finding names its source, scope and unknowns.</p>'
        '</div><aside><p class="gm-kicker">Follow the public record</p><h2>One feed. No account.</h2><p>New Readers, material updates and published Scout reviews appear in the same RSS feed.</p><a class="gm-scout-subscribe" href="/feed.xml">Get the RSS feed ↗</a></aside></section>'
        '<section class="gm-scout-home-edition"><div class="gm-scout-section-heading"><div><p class="gm-kicker">Current edition / reviewed ' + escape(edition['reviewedOn']) + '</p><h2>' + escape(edition['title']) + '</h2></div><a href="' + edition_url(edition) + '">Read the edition ↗</a></div><p class="gm-scout-edition-lede">' + escape(edition['summary']) + '</p><div class="gm-scout-feature-list">' + cards + '</div></section>'
        '<section class="gm-scout-home-next"><div><p class="gm-kicker">The complete record</p><h2>Find a review after it leaves the front page.</h2><p>Browse by topic, source type or recommendation. Each review keeps a permanent URL and dated reassessment history.</p><a href="/scout/archive/">Browse the review library ↗</a></div><div><p class="gm-kicker">How we work</p><h2>Discovery is a lead, not a verdict.</h2><p>Read how candidates enter view, why an editor brings one forward and what the inspection actually established.</p><a href="/scout/method/">How Scout works ↗</a></div></section>')


def review_page(review, narrative):
    evidence = review['discovery']
    ratings = []
    names = {'ghostmeshFit':'GhostMesh fit','everydayUse':'Everyday usefulness','evidenceStrength':'Evidence strength','adoptionEffort':'Adoption effort'}
    for key in DIMENSIONS:
        rating = review['ratings'][key]
        links = ' '.join('<a href="' + escape(url, quote=True) + '">Source ' + str(i) + ' ↗</a>' for i,url in enumerate(rating['evidenceUrls'],1))
        ratings.append('<div><dt>' + names[key] + '</dt><dd><strong>' + escape(rating['value']) + '</strong><p>' + escape(rating['rationale']) + '</p><span>' + links + '</span></dd></div>')
    prior = review['priorReviews']
    history = ''.join('<li><strong>' + escape(item['reviewedOn']) + ' · ' + escape(item['recommendation']) + '</strong><p>' + escape(item['summary']) + '</p><a href="' + escape(item['url'],quote=True) + '">Earlier public judgment ↗</a></li>' for item in prior)
    if not history:
        history = '<li><strong>' + escape(review['reviewedOn']) + ' · first look</strong><p>No earlier Scout review record.</p></li>'
    return (nav() + '<article class="gm-scout-detail"><header class="gm-scout-detail-hero"><p class="gm-kicker">Scout review / ' + escape(review['topic'].replace('-', ' ')) + '</p><h1>' + escape(review['title']) + '</h1><p class="gm-scout-detail-identity">' + escape(review['identity']) + '</p><a href="' + escape(review['sourceUrl'],quote=True) + '">Open the pinned original source ↗</a></header>'
        '<section class="gm-scout-three-moves" aria-label="Review in three moves"><div><span>01 / What it is</span><p>' + escape(review['identity']) + '</p><small>Intended audience: ' + escape(review['audience']) + '</small></div><div><span>02 / What we checked</span><p>' + escape(review['scope']) + '</p><small>' + escape(source_label(review)) + '</small></div><div><span>03 / Our provisional call</span><p>' + escape(call(review)) + '</p><small>Editorial recommendation, not verified outcome.</small></div></section>'
        '<section class="gm-scout-origin" aria-labelledby="scout-origin-title"><p class="gm-kicker">Origin / selection / inspection</p><h2 id="scout-origin-title">Why this came into view.</h2><div class="gm-scout-origin-grid"><div><h3>Recorded route</h3><p>Explicit research priority in the Scout configuration. The original discovery circumstances were not recorded. First retained observation: ' + escape(evidence['firstRetainedObservation']) + '.</p><a href="' + escape(evidence['evidenceUrl'],quote=True) + '">How priorities are recorded ↗</a></div><div><h3>Why examine it now</h3><p>' + escape(review['selectionRationale']) + '</p><small>Current editorial rationale; not a reconstruction of the original seed decision.</small></div><div><h3>Inspection boundary</h3><p>' + escape(review['scope']) + '</p><small>No installation or independent outcome measurement.</small></div></div></section>'
        '<section class="gm-scout-long-read" aria-label="Full analysis">' + prose_html(narrative,drop_title=True) + '</section>'
        '<section class="gm-scout-evidence" aria-labelledby="scout-evidence-title"><p class="gm-kicker">Assessment record / ' + escape(review['reviewedOn']) + '</p><h2 id="scout-evidence-title">Ratings with their limits.</h2><p>These are editorial judgments. Source links support the rationale; they do not independently prove a product outcome.</p><dl>' + ''.join(ratings) + '</dl><h3>Still unknown</h3><p>' + escape(review['unknowns']) + '</p></section>'
        '<section class="gm-scout-history" aria-labelledby="scout-history-title"><p class="gm-kicker">Dated record</p><h2 id="scout-history-title">Review history</h2><ol>' + history + '</ol></section></article>')


def edition_page(edition, scout, narrative):
    by_id = {review['id']:review for review in scout['reviews']}
    reviews = [by_id[ident] for ident in edition['reviewIds']]
    links = ''.join('<li><span>0' + str(i) + '</span><div><h3><a href="' + review_url(review) + '">' + escape(review['title']) + '</a></h3><p>' + escape(review['identity']) + '</p><strong>' + escape(call(review)) + '</strong></div></li>' for i,review in enumerate(reviews,1))
    return nav() + '<article class="gm-scout-edition"><header><p class="gm-kicker">Scout edition / reviewed ' + escape(edition['reviewedOn']) + '</p><h1>' + escape(edition['title']) + '</h1><p>' + escape(edition['summary']) + '</p></header><div class="gm-scout-edition-copy">' + prose_html(narrative,drop_title=True) + '</div><section aria-labelledby="edition-reviews-title"><p class="gm-kicker">Three source-linked reviews</p><h2 id="edition-reviews-title">Choose the question.</h2><ol class="gm-scout-edition-links">' + links + '</ol></section></article>'


def archive_page(scout):
    topics = sorted({review['topic'] for review in scout['reviews']})
    types = sorted({review['sourceType'] for review in scout['reviews']})
    option = lambda value: '<option value="' + escape(value,quote=True) + '">' + escape(value.replace('-', ' ').title()) + '</option>'
    cards = []
    for review in sorted(scout['reviews'],key=lambda item:(item['reviewedOn'],item['id']),reverse=True):
        searchable = ' '.join(str(review[key]) for key in ('title','identity','topic','audience','summary','selectionRationale'))
        cards.append('<article class="gm-scout-archive-card" data-date="' + escape(review['reviewedOn']) + '" data-title="' + escape(review['title'],quote=True) + '" data-topic="' + escape(review['topic']) + '" data-type="' + escape(review['sourceType']) + '" data-call="' + escape(review['recommendation']) + '" data-search="' + escape(searchable,quote=True) + '"><p class="gm-kicker">' + escape(source_label(review)) + '</p><h2><a href="' + review_url(review) + '">' + escape(review['title']) + '</a></h2><p>' + escape(review['identity']) + '</p><strong>' + escape(call(review)) + '</strong></article>')
    return (nav() + '<section class="gm-scout-archive"><header><p class="gm-kicker">Scout / complete library</p><h1>Every review stays findable.</h1><p>Search and filter the public review record. This library contains approved first-look assessments, not the private discovery watchlist.</p></header>'
        '<form class="gm-scout-filters" role="search" action="/scout/archive/" method="get"><label>Search reviews<input id="scout-query" name="q" type="search" placeholder="A project, problem or source"></label><label>Topic<select id="scout-topic"><option value="">All topics</option>' + ''.join(option(x) for x in topics) + '</select></label><label>Source type<select id="scout-type"><option value="">All source types</option>' + ''.join(option(x) for x in types) + '</select></label><label>Recommendation<select id="scout-call"><option value="">All calls</option>' + ''.join(option(x) for x in ('adapt','experiment','watch')) + '</select></label><label>Order<select id="scout-sort"><option value="recent">Recently reviewed</option><option value="title">Title</option></select></label><button type="reset">Clear filters</button></form>'
        '<p id="scout-count" role="status" aria-live="polite">' + str(len(cards)) + ' public reviews. All entries are listed below.</p><div id="scout-results">' + ''.join(cards) + '</div></section><script src="/assets/scout-archive.js" defer></script>')


def method_page(raw):
    return nav() + '<article class="gm-scout-method"><div class="gm-scout-method-prose">' + prose_html(raw) + '</div><p class="gm-scout-method-next"><a href="/scout/archive/">Browse the public reviews ↗</a></p></article>'
