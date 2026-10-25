"""Human-readable, source-bound paths through the published Reader graph.

The catalog owns every directed edge. This projection never adds an edge or
deduces agreement from a shared topic. It needs no client-side script.
"""

from collections import Counter
from html import escape
import re


def _e(value):
    return escape(str(value), quote=True)


def _reason(edge):
    """Make routine topic links scannable without changing their meaning."""
    reason = edge["reason"]
    match = re.fullmatch(
        r"Both editorial briefs examine (.+)\. This is a topic-level reading route, "
        r"not independent corroboration or agreement\.", reason
    )
    if match:
        topics = [topic.strip() for topic in match.group(1).split(",")]
        phrasing = (topics[0] if len(topics) == 1 else
                    " and ".join(topics) if len(topics) == 2 else
                    ", ".join(topics[:-1]) + ", and " + topics[-1])
        return "Read alongside for " + phrasing + "."
    return reason


def relationship_graph(readers, byid, host):
    """Project catalog routes and explicit review outcomes without graph admission."""
    ordered = sorted(readers, key=lambda reader: reader["editorialOrder"])
    return {
        "schema": "ghostmesh-reader-relationship-map-v1",
        "scope": "Local public editorial reading routes; no independent corroboration or cross-site graph admission.",
        "authority": "catalog-curated-editorial",
        "visibility": "public",
        "readerCount": len(ordered),
        "assessmentCount": sum(bool(reader.get("relationshipReview")) for reader in ordered),
        "relationshipCount": sum(len(reader["relationships"]) for reader in ordered),
        "nodes": [{"id": reader["id"], "slug": reader["slug"], "title": reader["title"],
                   "url": f'{host}/{reader["slug"]}/', "review": reader["relationshipReview"]}
                  for reader in ordered],
        "edges": [{"from": reader["id"], "to": edge["target"], "type": edge["type"],
                   "reason": edge["reason"], "provenance": edge["provenance"],
                   "basis": edge["basis"], "direction": edge["direction"]}
                  for reader in ordered for edge in reader["relationships"]],
    }


def relationship_map(readers, byid):
    """Return the complete HTML body for /map/.

    ``readers`` and ``byid`` have already passed catalog validation in
    generate_site. All data-derived text is escaped here as a second boundary.
    """
    ordered = sorted(readers, key=lambda reader: reader["editorialOrder"])
    if len({reader["id"] for reader in ordered}) != len(ordered):
        raise ValueError("Duplicate Reader identity in map")
    if set(byid) != {reader["id"] for reader in ordered}:
        raise ValueError("Map Reader identity mismatch")
    edge_count = sum(len(reader["relationships"]) for reader in ordered)
    kinds = Counter(edge["type"] for reader in ordered for edge in reader["relationships"])

    # These are navigation prompts, not inferred edges. A prompt opens one
    # existing Reader's complete, source-declared relationship list below.
    prompts = [
        ("Where does an agent's authority stop?", "the-inbox-was-a-boundary", "The Inbox Was a Boundary"),
        ("What makes AI work inspectable?", "make-good-work-inspectable", "Make Good Work Inspectable"),
        ("What does a score actually establish?", "the-score-is-not-the-system", "The score is not the system"),
        ("Who owns a company agent?", "the-agent-a-company-owns", "The Agent a Company Owns"),
    ]
    slug_to_index = {reader["slug"]: index for index, reader in enumerate(ordered, 1)}
    if not all(slug in slug_to_index for _, slug, _ in prompts):
        raise ValueError("Map reading route points to an absent Reader")
    prompt_links = "".join(
        f'<li><a href="#map-reader-{slug_to_index[slug]:02d}">'
        f'<span class="gm-question-no">{number:02d} / QUESTION</span>'
        f'<strong>{_e(question)}</strong><span class="gm-question-destination">'
        f'Start with {_e(title)} <span aria-hidden="true">↘</span></span></a></li>'
        for number, (question, slug, title) in enumerate(prompts, 1)
    )

    index_links = "".join(
        f'<li><a href="#map-reader-{index:02d}"><span>{index:02d}</span>'
        f'<span>{_e(reader["title"])}</span></a></li>'
        for index, reader in enumerate(ordered, 1)
    )
    entries = []
    for index, reader in enumerate(ordered, 1):
        edges = []
        for edge in reader["relationships"]:
            target = byid[edge["target"]]
            edges.append(
                '<li class="gm-atlas-link">'
                f'<span class="gm-atlas-type">{_e(edge["type"])}</span>'
                f'<div><a href="/{_e(target["slug"])}/">{_e(target["title"])}</a>'
                f'<p>{_e(_reason(edge))}</p></div></li>'
            )
        entries.append(
            f'<section class="gm-atlas-entry" id="map-reader-{index:02d}" '
            f'aria-labelledby="map-reader-title-{index:02d}">'
            '<div class="gm-atlas-source">'
            f'<span class="gm-atlas-number">{index:02d}</span>'
            f'<div><span class="gm-atlas-category">{_e(reader["category"])}</span>'
            f'<h3 id="map-reader-title-{index:02d}"><a href="/{_e(reader["slug"])}/">'
            f'{_e(reader["title"])}</a></h3>'
            f'<p>{_e(reader["overview"])}</p></div></div>'
            f'<div class="gm-atlas-out"><p class="gm-atlas-out-label">'
            f'{len(edges)} published connection{"s" if len(edges) != 1 else ""}</p>'
            f'<ul>{"".join(edges)}</ul></div></section>'
        )
    kind_text = ", ".join(f"{count} {_e(kind)}" for kind, count in sorted(kinds.items()))
    return (
        '<header class="gm-atlas-hero">'
        f'<p class="gm-kicker">GHOSTMESH / {len(ordered)} READERS / {edge_count} DIRECTED CONNECTIONS</p>'
        '<h1>Follow the question.<br><em>Then follow the evidence.</em></h1>'
        '<p>These routes connect named public Readers by their declared editorial reasons. '
        'A shared topic is a way to read onward, not independent corroboration or agreement.</p>'
        '<div class="gm-atlas-hero-actions"><a href="#map-questions">Choose a question ↓</a>'
        '<a href="#map-all">Browse every connection ↓</a>'
        '<a href="/map/relationships.json">Download reviewed routes JSON ↗</a></div></header>'
        '<section class="gm-question-section" id="map-questions" aria-labelledby="map-questions-title">'
        '<div class="gm-question-head"><p class="gm-kicker">A way in</p>'
        '<h2 id="map-questions-title">What are you trying to understand?</h2>'
        '<p>Start at a relevant Reader, then move through its stated connections. '
        'The complete article holds its claims, citations and uncertainty.</p></div>'
        f'<ol class="gm-question-list">{prompt_links}</ol></section>'
        '<section class="gm-atlas" id="map-all" aria-labelledby="map-all-title">'
        '<div class="gm-atlas-heading"><div><p class="gm-kicker">The complete map</p>'
        '<h2 id="map-all-title">Every published connection.</h2></div>'
        f'<p>{edge_count} directed routes from {len(ordered)} Readers. The arrow of each route '
        'starts at the Reader on the left and opens the named Reader on the right. '
        'Each explanation is drawn from that route’s published reason.</p></div>'
        '<div class="gm-atlas-layout"><nav class="gm-atlas-index" aria-label="Jump to a Reader">'
        '<p>JUMP TO A READER</p>'
        f'<ol>{index_links}</ol></nav><div class="gm-atlas-entries">{"".join(entries)}</div></div></section>'
        '<aside class="gm-atlas-limit" aria-labelledby="map-limit-title">'
        '<div><p class="gm-kicker">Read the boundary</p>'
        '<h2 id="map-limit-title">A connection is an editorial route.</h2></div>'
        '<div><p>Topic links do not establish that either Reader’s claims are true. '
        'Open the Reader for the dated evidence, counterevidence and explicit unknowns. '
        f'The current published types are {_e(kind_text)}.</p>'
        '<p>SharePlane essays and other sites require their own reviewed identity and link '
        'decision before appearing here. No cross-site edge is included.</p>'
        '<p>Scout research uses its own approved public relationships. '
        '<a href="/scout/research/">Explore the Scout Research Library</a> or '
        '<a href="/scout/research/relationships.json">inspect its relationship JSON</a>. '
        'These are separate from the Reader routes counted above.</p>'
        '<a href="/knowledge/">Inspect the public knowledge records ↗</a></div></aside>'
    )
