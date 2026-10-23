"""Deterministic, offline extraction of public HTML research evidence."""
from __future__ import annotations
from html.parser import HTMLParser
import re

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.depth = 0
        self.skip = 0
        self.capture = []
        self.abstract = []
        self.in_abstract = 0
        self.in_main = 0

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == "meta":
            key = a.get("name") or a.get("property")
            if key in {"citation_title", "citation_abstract", "description", "og:description"}:
                self.meta[key] = a.get("content", "")
        if tag in {"script", "style", "nav", "footer", "header"}:
            self.skip += 1
        if tag == "main":
            self.in_main += 1
        if tag in {"blockquote", "div", "section"} and "abstract" in a.get("class", "").split():
            self.in_abstract += 1
        self.capture.append((tag, bool(self.in_abstract), bool(self.in_main)))

    def handle_endtag(self, tag):
        if self.capture:
            # Pop through the matching open tag, including malformed nesting.
            pos = next((i for i in range(len(self.capture)-1, -1, -1)
                        if self.capture[i][0] == tag), None)
            if pos is not None:
                if any(t in {"script", "style", "nav", "footer", "header"} for t, _, _ in self.capture[pos:]):
                    self.skip = max(0, self.skip - sum(t in {"script", "style", "nav", "footer", "header"} for t, _, _ in self.capture[pos:]))
                if any(t == "main" for t, _, _ in self.capture[pos:]):
                    self.in_main = max(0, self.in_main - sum(t == "main" for t, _, _ in self.capture[pos:]))
                self.in_abstract = max(0, self.in_abstract - sum(a for _, a, _ in self.capture[pos:] if a) )
                self.capture = self.capture[:pos]

    def handle_data(self, data):
        if self.skip:
            return
        clean = " ".join(data.split())
        if not clean:
            return
        if self.in_abstract:
            self.abstract.append(clean)
        elif self.in_main:
            self.depth += 1
            self.capture_text.append(clean) if hasattr(self, "capture_text") else setattr(self, "capture_text", [clean])

def extract(html: str) -> dict:
    parser = Extractor()
    parser.feed(html)
    title = parser.meta.get("citation_title", "")
    abstract = parser.meta.get("citation_abstract") or " ".join(parser.abstract)
    description = parser.meta.get("description") or parser.meta.get("og:description") or ""
    main = " ".join(getattr(parser, "capture_text", []))
    body = abstract or description or main
    body = re.sub(r"\\s+", " ", body).strip()
    if not body:
        return {"title": title, "excerpt": None, "extraction_status": "INSUFFICIENT"}
    return {"title": title, "excerpt": body[:4000], "extraction_status": "EXTRACTED_UNVERIFIED"}
