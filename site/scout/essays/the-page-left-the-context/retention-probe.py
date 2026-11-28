#!/usr/bin/env python3
"""Offline DR Pixel evidence-retention check. No network, model or API calls.

First save these two pinned upstream source files, preserving their bytes:
https://raw.githubusercontent.com/StarTrail-org/DRPixel/14a3a82f5c5266c6c87565a19184d1e16adfb531/eval/drbench/harness.py
https://raw.githubusercontent.com/StarTrail-org/DRPixel/14a3a82f5c5266c6c87565a19184d1e16adfb531/eval/drbench/judge.py

Run:
  python3 retention-probe.py --harness harness.py --judge judge.py

This executes only three selected helper functions from hash-checked sources.
Synthetic image markers stand in for image data. No model correctness is scored.
"""
import argparse
import ast
import hashlib
import json
from pathlib import Path
from types import SimpleNamespace

REVISION = "14a3a82f5c5266c6c87565a19184d1e16adfb531"
EXPECTED = {
    "harness": "cff3bba48cc21e8d35296ba19ef516d6f1c5680451c3392b084856dd8720dfb4",
    "judge": "5937a29a4e315b2bf1c3592ec771411a068d4c146fd6184456b7bab115ed345f",
}

def checked_tree(path, kind):
    raw = Path(path).read_bytes()
    actual = hashlib.sha256(raw).hexdigest()
    if actual != EXPECTED[kind]:
        raise SystemExit("%s source hash mismatch: %s" % (kind, actual))
    return ast.parse(raw.decode("utf-8"))

def functions(tree, names):
    nodes = [n for n in tree.body
             if isinstance(n, ast.FunctionDef) and n.name in names]
    if {n.name for n in nodes} != set(names):
        raise SystemExit("Expected helper function missing")
    return ast.Module(body=nodes, type_ignores=[])

ap = argparse.ArgumentParser(description=__doc__)
ap.add_argument("--harness", required=True)
ap.add_argument("--judge", required=True)
args = ap.parse_args()
h = checked_tree(args.harness, "harness")
j = checked_tree(args.judge, "judge")
cap = next(ast.literal_eval(n.value) for n in h.body
           if isinstance(n, ast.Assign)
           and any(isinstance(t, ast.Name) and t.id == "MAX_IMAGES" for t in n.targets))
ns = {
    "gem": SimpleNamespace(text_part=lambda s: {"_t": "text", "text": s}),
    "PAGE_TOOLS": ("search_page", "search_figure"),
}
exec(compile(functions(h, {"_img_count", "_drop_oldest_images"}), args.harness, "exec"), ns)
exec(compile(functions(j, {"retrieval_hits"}), args.judge, "exec"), ns)

messages, searches = [], []
for turn in range(9):
    parts, hits = [], []
    for rank in range(3):
        marker = turn * 3 + rank
        doc = "gold" if marker == 0 else "distractor-%d" % marker
        parts.append({"_t": "img", "marker": marker})
        hits.append({"doc": doc, "page_idx": 7})
    messages.append({"role": "user", "parts": parts})
    searches.append({"tool": "search_page", "hits": hits})
    over = ns["_img_count"](messages) - cap
    if over > 0:
        ns["_drop_oldest_images"](messages, over)

retained = [p["marker"] for m in messages for p in m["parts"] if p["_t"] == "img"]
hit = ns["retrieval_hits"]({"doc": "gold", "page": 7}, searches, {"search_page": "page"})
assert len(retained) == 24 and 0 not in retained and hit["page_hit"] is True
print(json.dumps({
    "revision": REVISION,
    "source_sha256": EXPECTED,
    "scope": "exact helper functions; synthetic markers; no model, image decoder, network or API",
    "searches": 9,
    "images_retrieved": 27,
    "image_cap": cap,
    "images_retained": len(retained),
    "original_gold_image_retained": 0 in retained,
    "historical_page_hit": hit["page_hit"],
    "performance_conclusion": None,
}, indent=2))
