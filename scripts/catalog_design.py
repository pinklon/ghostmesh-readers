"""Reader archive presentation, grounded in the published catalog records.

This module changes navigation and editorial compression, not claim disposition.
Each short call below paraphrases a Reader's existing whyItMatters,
ghostMeshTakeaway, and evidenceReview/falsification text. The Reader itself is
the authority for the full argument and claim-level limits.
"""
from html import escape
import re


def _e(value):
    return escape(str(value), quote=True)


def paper_cover(source):
    """Original typographic art; never a captured or redistributed paper page."""
    if source.get('kind') != 'paper' or not re.fullmatch(r'arxiv:\d{4}\.\d{4,5}v\d+', source.get('identity', '')):
        raise ValueError('Paper cover requires a version-pinned arXiv identity')
    return ('<div class="gm-paper-cover" role="img" '
            'aria-label="Original Reader illustration of the paper\'s two selected cases, LLM personas and TabPFN distribution shift; not a page from the paper">'
            f'<span class="gm-paper-cover-id">ARXIV / {_e(source["identity"].removeprefix("arxiv:"))}</span>'
            '<div class="gm-paper-cover-cases"><span><small>01 / MODEL BEHAVIOR</small><strong>LLM<br>personas</strong></span>'
            '<span><small>02 / MODEL SHIFT</small><strong>TabPFN<br>distribution</strong></span></div>'
            '<span class="gm-paper-cover-footer">TWO CASES <b>↘</b> TWO RESEARCH QUESTIONS</span></div>')


# Reader-specific route labels and calls. These are recommendations to read or
# test, not verification labels. Keep the source-grounding checks below when
# adding a Reader; never infer a call from its category or claim count.
CALLS = {
    'ask-for-the-outcome-keep-the-boundary': ('Watch selectively', 'Try the frames on one low-risk task. The top-one-percent label is not measured evidence.'),
    'make-good-work-inspectable': ('Watch the failure story', 'Judge the result by inspectable application behavior, not commit volume.'),
    'a-challenge-is-not-a-verdict': ('Try on a consequential choice', 'Use an AI objection as a candidate for checking, never as a verdict.'),
    'the-score-is-not-the-system': ('Study the environment', 'Keep reward signals, permission and persistent state separate in the evaluation.'),
    'the-inbox-was-a-boundary': ('Study the incident boundary', 'Treat a retrieved page as evidence, never as permission for credential actions.'),
    'the-agent-a-company-owns': ('Investigate before adopting', 'Test permission, replay, memory isolation and portability with synthetic cases.'),
    'autonomy-needs-an-interface': ('Run a bounded comparison', 'Make the accountable owner and permission scope visible at each agent handoff.'),
    'when-software-becomes-legible': ('Investigate one fixture', 'Compare reconstructed rules with known source and observed behavior.'),
    'when-agents-become-the-customer': ('Test service boundaries', 'Keep billing principal, caller identity and service authorization explicit.'),
    'the-scan-never-reached-the-login': ('Study a stalled run', 'Separate a proposed scan, a tool call, a completed run and a verified finding.'),
    'the-key-was-the-boundary': ('Watch the incident scope', 'Contain exposed credentials at their issuer; attacker attribution remains unresolved.'),
    'the-microscope-is-not-a-soul': ('Investigate the boundary', 'Keep mechanisms, welfare hypotheses and operational authority separate.'),
    'the-funnel-is-not-the-frontier': ('Use as a prompt, not a ranking', 'Compare bounded tasks instead of ranking people with an unmeasured population estimate.'),
    'the-fleet-does-not-prove-the-forecast': ('Study the cases', 'Separate reported fleet behavior and lab results from the predicted agent internet.'),
    'a-scenario-is-not-a-singularity': ('Watch the bounded evidence', 'Treat the physics score as a calculation result and the $44.4 trillion scenario as conditional.'),
    'the-test-must-name-its-target': ('Use for evaluation design', 'Test grounded use and changed premises before assigning a broad understanding label.'),
    'the-parallel-result-is-not-the-product': ('Study before migrating', 'Reproduce quality, latency and cost on your own workload before changing the product stack.'),
    'the-experiment-ran-did-the-research-advance': ('Study the evaluation', 'Separate completed engineering from research judgment; two selected cases cannot set a universal ceiling.'),
}


def _poster(reader):
    source = reader['source']
    if source.get('kind') == 'paper':
        return paper_cover(source)
    platform = source.get('platform', 'YouTube')
    aspect = source.get('mediaAspect')
    if platform not in {'YouTube', 'Instagram'} or aspect not in {'16:9', '9:16', '1:1', 'unknown'}:
        raise ValueError('Unsupported catalog source shape')
    if aspect == 'unknown':
        return '<div class="gm-archive-source-unknown">Source shape unverified. Open the Reader for the original link.</div>'
    source_id = source.get('videoId') if platform == 'YouTube' else source.get('shortcode')
    pattern = r'[A-Za-z0-9_-]{11}' if platform == 'YouTube' else r'[A-Za-z0-9_-]+'
    if not isinstance(source_id, str) or not re.fullmatch(pattern, source_id):
        raise ValueError('Unsafe catalog source ID')
    preview = (f'<img src="https://i.ytimg.com/vi/{_e(source_id)}/hqdefault.jpg" loading="lazy" decoding="async" referrerpolicy="no-referrer" alt="">'
               if platform == 'YouTube' else '<span class="gm-home-source-fallback">Original Instagram Reel<br>Source image unavailable</span>')
    return (f'<div class="gm-library-frame gm-archive-source-frame" data-home-player data-source-platform="{_e(platform)}" '
            f'data-source-id="{_e(source_id)}" data-gm-aspect="{_e(aspect)}">'
            f'{preview}<button type="button" data-home-play hidden>Play original here</button></div>')


def card(reader, number=None):
    """One complete, linkable archive entry; caller controls order and heading context."""
    slug = reader['slug']
    if slug not in CALLS:
        raise ValueError(f'Reader requires a source-grounded archive call: {slug}')
    if not reader.get('whyItMatters') or not reader.get('ghostMeshTakeaway'):
        raise ValueError(f'Reader lacks source guidance: {slug}')
    call_label, call = CALLS[slug]
    unverified = sum(claim['status'] == 'unverified' for claim in reader['claims'])
    total = len(reader['claims'])
    paper = reader['source'].get('kind') == 'paper'
    platform = 'paper' if paper else reader['source'].get('platform', 'YouTube')
    number = number if number is not None else reader['editorialOrder'] + 1
    search_text = ' '.join([reader['title'], reader['overview'], reader['category'], *reader['tags'], call_label, call])
    tags = ''.join(f'<span>{_e(tag)}</span>' for tag in reader['tags'])
    return (
        f'<article class="gm-card gm-archive-entry gm-library-card" data-category="{_e(reader["category"])}" '
        f'data-tags="{_e(" ".join(reader["tags"]))}" data-search="{_e(search_text)}" '
        f'data-date="{_e(reader["published"])}" data-rank="{_e(reader.get("rank", reader["editorialOrder"]))}">'
        f'<div class="gm-archive-index" aria-hidden="true">{int(number):02d}</div>'
        '<div class="gm-library-copy gm-archive-copy">'
        f'<p class="gm-archive-meta">{_e(reader["category"])} <span aria-hidden="true">/</span> {_e(reader["published"])}</p>'
        f'<h3><a href="/{_e(slug)}/">{_e(reader["title"])}</a></h3>'
        f'<p class="gm-archive-audience">{_e(reader["whyItMatters"])}</p>'
        '<div class="gm-archive-judgment">'
        f'<span class="gm-archive-call-label">{_e(call_label)}</span><p>{_e(call)}</p></div>'
        f'<p class="gm-archive-evidence">Mapped evidence: <strong>{_e(reader["evidenceState"])}</strong> '
        f'<span aria-hidden="true">·</span> {unverified} of {total} mapped claims unverified. '
        'These labels are claim-level, not an article-wide verification score.</p>'
        f'<p class="gm-archive-tags" aria-label="Topics">{tags}</p>'
        '<div class="gm-library-actions gm-archive-actions">'
        f'<a href="/{_e(slug)}/">Read the deconstruction <span aria-hidden="true">↗</span></a>'
        f'<a href="{_e(reader["source"]["url"])}">Original {_e(platform)} source <span aria-hidden="true">↗</span></a>'
        '</div></div>'
        f'<div class="gm-archive-visual"><span>{"Original source / direct link" if paper else "Original source / opt-in player"}</span>{_poster(reader)}</div>'
        '</article>'
    )


def _topic_links(categories, current=None):
    links = ['<a href="/readers/"' + (' aria-current="page"' if current is None else '') + '>All Readers</a>']
    for index, category in enumerate(categories):
        links.append(f'<a href="/readers/categories/{index}/"' +
                     (' aria-current="page"' if category == current else '') +
                     f'>{_e(category)}</a>')
    return '<nav class="gm-archive-topics" aria-label="Browse by category">' + ''.join(links) + '</nav>'


def _filters(readers, categories):
    tags = sorted({tag for reader in readers for tag in reader['tags']})
    return (
        '<form class="gm-filters gm-archive-filters" role="search">'
        '<label class="gm-search-field" for="search">Find a Reader'
        '<input type="search" id="search" autocomplete="off" placeholder="Try an idea, question or source"></label>'
        '<div class="gm-filter-row">'
        '<label for="category">Category<select id="category"><option value="">All</option>' +
        ''.join(f'<option>{_e(category)}</option>' for category in categories) + '</select></label>'
        '<label for="tag">Topic<select id="tag"><option value="">All</option>' +
        ''.join(f'<option>{_e(tag)}</option>' for tag in tags) + '</select></label>'
        '<label for="sort">Order<select id="sort"><option value="recent">Latest first</option>'
        '<option value="relevance">Editorial order</option><option value="title">Title A–Z</option></select></label>'
        '<button class="gm-reset" type="reset">Clear</button></div></form>'
    )


def archive(readers, categories):
    """Body for /readers/, including no-JS paths and existing catalog.js hooks."""
    entries = ''.join(card(reader, index) for index, reader in enumerate(readers, 1))
    return (
        '<div class="gm-archive">'
        '<header class="gm-archive-hero"><p class="gm-kicker">GhostMesh / complete Reader archive</p>'
        '<h1>Choose a question worth examining.</h1>'
        f'<p>{len(readers)} public deconstructions. Each pairs a source with an editorial call, a claim register and explicit limits. Start with a topic or search the article text.</p>'
        '</header>'
        + _topic_links(categories) +
        '<div class="gm-archive-tools">' + _filters(readers, categories) +
        '<div class="gm-result-bar"><p id="result-count" role="status" aria-live="polite">' +
        str(len(readers)) + ' Readers</p><p>Search covers this published Reader library only. Article text is included when JavaScript is available.</p></div></div>'
        '<noscript><p class="gm-archive-noscript">Search and sorting require JavaScript. All Readers appear below, and the category links above work without it.</p></noscript>'
        '<section aria-label="Reader results"><div class="gm-archive-list" id="catalog-results">' + entries + '</div></section>'
        '</div><script src="/assets/catalog.js" defer></script><script src="/assets/home-player.js" defer></script>'
    )


def category(readers, categories, selected):
    """Body for a static category page; every entry remains accessible without JS."""
    chosen = [reader for reader in readers if reader['category'] == selected]
    return (
        '<div class="gm-archive gm-archive-category">'
        f'<header class="gm-archive-hero"><p class="gm-kicker">GhostMesh / Reader category</p><h1>{_e(selected)}</h1>'
        f'<p>{len(chosen)} public Reader' + ('s' if len(chosen) != 1 else '') +
        ' in this category. Open any deconstruction to see its source and claim-level limits.</p></header>'
        + _topic_links(categories, selected) +
        '<section aria-label="Category Readers"><div class="gm-archive-list">' +
        (''.join(card(reader, index) for index, reader in enumerate(chosen, 1)) or '<p>No Reader is currently classified here.</p>') +
        '</div></section></div><script src="/assets/home-player.js" defer></script>'
    )
