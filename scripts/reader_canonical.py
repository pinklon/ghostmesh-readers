"""Forward-only Reader presentation contract.

Reader #55 is the complete production reference for Reader #56 onward.
Reader #53 remains the original visual baseline for #54 and #55.
Earlier Readers remain immutable; checks cover structure, not editorial truth
or rendered mobile acceptance. No parallel rendering or release pipeline.
"""

from html.parser import HTMLParser

REFERENCE_SLUG = "replacing-cowork-is-a-test-not-a-title"
START_DATE = "2026-11-11"
FORWARD_EDITORIAL_ORDER = 53  # Reader #54 and later use the shared visual baseline.
CONNECTIONS_EDITORIAL_ORDER = 53  # Graph-backed routes or visible reviewed zeros.


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.classes = set()
        self.class_counts = {}
        self.stylesheets = set()
        self.hrefs = set()
        self.unstyled_tables = 0
        self.ancestors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get("class") or "").split())
        self.ids.add(attrs.get("id"))
        if attrs.get("href"):
            self.hrefs.add(attrs["href"])
        self.classes.update(classes)
        for name in classes:
            self.class_counts[name] = self.class_counts.get(name, 0) + 1
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.add(attrs.get("href"))
        if tag == "table":
            wrapped = any("table-wrap" in parent for parent in self.ancestors)
            if not wrapped:
                self.unstyled_tables += 1
        if tag not in {"area", "base", "br", "col", "embed", "hr", "img", "input",
                       "link", "meta", "param", "source", "track", "wbr"}:
            self.ancestors.append(classes)

    def handle_endtag(self, tag):
        if self.ancestors:
            self.ancestors.pop()


def errors(reader, html):
    """Return structural regressions; independent browser QA remains required."""
    if reader["slug"] != REFERENCE_SLUG and reader["published"] < START_DATE:
        return []
    parsed = Structure()
    parsed.feed(html)
    required_ids = {"at-a-glance", "external-evidence"}
    required_classes = {"gm-evidence", "gm-evidence-intro", "gm-evidence-body",
                        "gm-claim-list", "gm-source-scope", "gm-source-list",
                        "gm-publication-status"}
    if reader.get("relationships"):
        required_ids.add("related-thinking")
        required_classes.update({"gm-related", "gm-cards"})
    if reader.get("sharePlaneRelationships"):
        required_classes.update({"gm-work-routes", "gm-work-grid"})
    missing = []
    if reader.get("editorialOrder", 0) >= CONNECTIONS_EDITORIAL_ORDER:
        required_ids.update({"related-thinking", "shareplane-thinking"})
        required_classes.update({"gm-related", "gm-work-routes"})
        relationships = reader.get("relationships", [])
        work = reader.get("sharePlaneRelationships", [])
        # A reviewed zero is valid, but never silently absent or masked by
        # authored 'proposed' links that are not admitted into the catalog.
        if parsed.class_counts.get("gm-related-copy", 0) != len(relationships):
            missing.append("catalog-matched Reader connection card count")
        if parsed.class_counts.get("gm-work-kind", 0) != len(work):
            missing.append("catalog-matched SharePlane Work connection count")
        expected_zeros = int(not relationships) + int(not work)
        if parsed.class_counts.get("gm-route-empty", 0) != expected_zeros:
            missing.append("explicit reviewed-zero connection disposition")
        for edge in relationships:
            if "/" + edge["target"].removeprefix("reader:") + "/" not in parsed.hrefs:
                missing.append("admitted Reader edge missing from rendered links")
        for edge in work:
            if edge["url"] not in parsed.hrefs:
                missing.append("admitted SharePlane Work edge missing from rendered links")
    missing += [f"id={name}" for name in sorted(required_ids - parsed.ids)]
    missing += [f"class={name}" for name in sorted(required_classes - parsed.classes)]
    if "/assets/reader-refresh.css" not in parsed.stylesheets:
        missing.append("shared Reader presentation stylesheet")
    if reader["source"].get("platform") == "YouTube" and reader["source"].get("creatorChapters"):
        if "chapters" not in parsed.ids and "chapters" not in parsed.classes:
            missing.append("source chapter navigator")
    if reader.get("editorialOrder", 0) >= FORWARD_EDITORIAL_ORDER:
        required_classes = {"gm-brief", "gm-brief-point", "gm-brief-index"}
        missing += [f"class={name}" for name in sorted(required_classes - parsed.classes)]
        if parsed.class_counts.get("gm-brief-point", 0) != 3:
            missing.append("exactly three styled brief moves")
        if parsed.unstyled_tables:
            missing.append("unstyled table (use a responsive wrapper or labeled decision rows)")
    return [f"{reader['slug']}: canonical presentation missing {item}" for item in missing]
