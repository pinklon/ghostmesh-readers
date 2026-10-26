"""Render the approved Claude PDF Scout draft as a local preview page."""

from html import escape
from pathlib import Path
import subprocess
import argparse
from datetime import date

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / "content/scout/publication-drafts/11-reviewing-visual-claims-in-claude-pdf-answers.md"
TARGET = ROOT / "site/scout/essays/reviewing-visual-claims-in-claude-pdf-answers/index.html"
TITLE = "Reviewing visual claims in Claude PDF answers"
SUMMARY = "A proposed claim-level review method for distinguishing cited text, inspected visual evidence and unresolved support in PDF answers."
URL = "https://youtube.shareplane.malott.ai/scout/essays/reviewing-visual-claims-in-claude-pdf-answers/"

parser = argparse.ArgumentParser()
parser.add_argument("--release-date", type=date.fromisoformat)
args = parser.parse_args()
if args.release_date:
    date_label = f'Published <time datetime="{args.release_date.isoformat()}">{args.release_date.strftime("%B %-d, %Y")}</time> · Reviewed <time datetime="2026-10-26">October 26, 2026</time>'
    robots = ""
    state = "Research method"
    footer = "Original analysis"
else:
    date_label = 'Reviewed <time datetime="2026-10-26">October 26, 2026</time> · Not yet published'
    robots = '<meta name="robots" content="noindex,nofollow">'
    state = "Editorial candidate · Research method"
    footer = "Editorial candidate"

body = subprocess.check_output(
    ["pandoc", "--from=gfm", "--to=html5", "--wrap=none"],
    input=SOURCE.read_bytes(),
).decode("utf-8")
html = f'''<!doctype html><html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">{robots}<link rel="canonical" href="{URL}"><meta name="description" content="{escape(SUMMARY, quote=True)}"><title>{escape(TITLE)} | GhostMesh Scout Essays</title><link rel="icon" href="/favicon.svg"><link rel="stylesheet" href="/assets/scout-essays.css"></head><body><header class="bar"><a class="brand" href="/">GHOST<em>MESH</em> / READERS</a><nav aria-label="Main"><a href="/scout/">Scout</a><a href="/scout/essays/">Scout Essays</a><a href="/readers/">Readers</a><a href="/map/">Knowledge Map</a></nav></header><section class="hero"><p class="eyebrow">GhostMesh / Scout / {state}</p><h1>{escape(TITLE)}</h1><p class="lede">{escape(SUMMARY)}</p><p class="publication-meta">{date_label}</p></section><main id="main"><article class="article">{body}</article></main><footer><p>GhostMesh Scout · {footer} · The research workspace is private.</p><p><a href="/scout/">Scout reviews</a> · <a href="/scout/essays/">Essay series</a> · <a href="/">Readers home</a></p></footer></body></html>'''
TARGET.parent.mkdir(parents=True, exist_ok=True)
TARGET.write_text(html, encoding="utf-8")
