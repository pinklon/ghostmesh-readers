"""Deterministic offline extraction of substantive text from public HTML."""
from __future__ import annotations
from html.parser import HTMLParser
import re

SKIP = {"script", "style", "nav", "footer", "header"}

class Extractor(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.meta = {}
        self.stack = []
        self.abstract_parts = []
        self.main_parts = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == "meta":
            key = attrs.get("name") or attrs.get("property")
            if key in {"citation_title", "citation_abstract", "description", "og:description"}:
                self.meta[key] = attrs.get("content", "")
        is_abstract = tag in {"blockquote", "div", "section"} and "abstract" in attrs.get("class", "").split()
        self.stack.append((tag, is_abstract))

    def handle_startendtag(self, tag, attrs):
        self.handle_starttag(tag, attrs)
        self.handle_endtag(tag)

    def handle_endtag(self, tag):
        for index in range(len(self.stack) - 1, -1, -1):
            if self.stack[index][0] == tag:
                self.stack = self.stack[:index]
                return

    def handle_data(self, data):
        if any(tag in SKIP for tag, _ in self.stack):
            return
        text = " ".join(data.split())
        if not text:
            return
        if any(is_abstract for _, is_abstract in self.stack):
            self.abstract_parts.append(text)
        elif any(tag == "main" for tag, _ in self.stack):
            self.main_parts.append(text)

def extract(html: str) -> dict:
    parser = Extractor()
    parser.feed(html)
    title = parser.meta.get("citation_title", "")
    abstract = parser.meta.get("citation_abstract") or " ".join(parser.abstract_parts)
    description = parser.meta.get("description") or parser.meta.get("og:description") or ""
    body = abstract or description or " ".join(parser.main_parts)
    body = re.sub(r"\s+", " ", body).strip()
    if not body:
        return {"title": title, "excerpt": None, "extraction_status": "INSUFFICIENT"}
    return {"title": title, "excerpt": body[:4000], "extraction_status": "EXTRACTED_UNVERIFIED"}
