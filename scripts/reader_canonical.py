"""Forward-only canonical Reader presentation contract, approved 2026-11-10.

The Nate Herk Reader is the visual reference. Existing historical Readers are
preserved; future Readers must carry its editorial structure before release.
"""

from html.parser import HTMLParser

REFERENCE_SLUG = "when-every-ai-website-looks-good"
START_DATE = "2026-11-11"


class Structure(HTMLParser):
    def __init__(self):
        super().__init__()
        self.ids = set()
        self.classes = set()
        self.stylesheets = set()

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.ids.add(attrs.get("id"))
        self.classes.update((attrs.get("class") or "").split())
        if tag == "link" and attrs.get("rel") == "stylesheet":
            self.stylesheets.add(attrs.get("href"))


def errors(reader, html):
    """Return requirements missing from the approved visual pattern.

    The contract checks structure, not editorial truth or visual acceptance.
    It intentionally does not require a video player for non-video sources.
    """
    if reader["slug"] != REFERENCE_SLUG and reader["published"] < START_DATE:
        return []
    parsed = Structure()
    parsed.feed(html)
    required_ids = {"at-a-glance", "external-evidence"}
    required_classes = {"gm-evidence", "gm-evidence-intro", "gm-evidence-body",
                        "gm-claim-list", "gm-source-scope", "gm-source-list",
                        "gm-publication-status"}
    # An independently reviewed zero is valid. Do not demand fabricated links.
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
    return [f"{reader['slug']}: canonical presentation missing {item}" for item in missing]
