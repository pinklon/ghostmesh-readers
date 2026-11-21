#!/usr/bin/env python3
"""Fail closed for confidential Reader 71 PR previews, without touching production.

Netlify PR #205 may contain owner-review manuscript source in a private GitHub
repository. The ordinary public Netlify deploy preview must not serve it.
"""
from pathlib import Path
import os, shutil, sys
root=Path(__file__).resolve().parents[1]
site=root/"site"
context=os.getenv("CONTEXT","")
review=os.getenv("REVIEW_ID","")
# A no-op on other PRs and on production, which remains on main.
if context != "deploy-preview":
    print("Reader 71 preview guard: not deploy-preview")
    sys.exit(0)
if review != "205":
    if (site/"__drafts"/"reader-71").exists() and not review:
        sys.exit("Reader 71 preview guard: missing REVIEW_ID, refuse publication")
    print("Reader 71 preview guard: different PR")
    sys.exit(0)
if os.getenv("NETLIFY") != "true":
    sys.exit("Reader 71 preview guard: refusing destructive operation off Netlify")
# This only changes Netlify's transient build checkout. Git and local files are unaffected.
shutil.rmtree(site)
site.mkdir()
(site/"index.html").write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="robots" content="noindex,nofollow">'
    '<title>Owner review held</title></head>'
    '<body><h1>Owner review held</h1>'
    '<p>This Reader is under private editorial review. No draft content is publicly accessible from this preview.</p>'
    '</body></html>\n'
)
(site/"404.html").write_text(
    '<!doctype html><html lang="en"><head><meta charset="utf-8">'
    '<meta name="robots" content="noindex,nofollow"><title>Not found</title></head>'
    '<body><h1>Not found</h1></body></html>\n'
)
(site/"_headers").write_text("/*\n  X-Robots-Tag: noindex, nofollow\n  Cache-Control: no-store\n")
print("Reader 71 preview guard: PR205 public deploy output suppressed")
