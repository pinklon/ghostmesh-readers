"""Forward-only Reader presentation contract.

Reader #53 is the production visual reference for Reader #54 onward.
Earlier Readers remain immutable; checks cover structure, not editorial truth
or rendered mobile acceptance. No parallel rendering or release pipeline.
"""

from html.parser import HTMLParser

REFERENCE_SLUG = "the-small-fix-is-a-boundary"
START_DATE = "2026-11-11"
FORWARD_EDITORIAL_ORDER = 53  # Reader #54; Reader #53 is editorialOrder 52.


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.classes = set()
        self.class_counts = {}
        self.stylesheets = set()
        self.unstyled_tables = 0
        self.ancestors = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        classes = set((attrs.get("class") or "").split())
        self.ids.add(attrs.get("id"))
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
    missing = [f"id={name}" for name in sorted(required_ids - parsed.ids)]
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
