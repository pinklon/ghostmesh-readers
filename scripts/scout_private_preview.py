"""Build a private, static Scout adjudication preview from verified receipts.

Output must remain local, never copied into a publicly deployed site tree.
"""
from __future__ import annotations
import argparse
from html import escape
import json
from pathlib import Path
from scout_editorial_join import join

# Independent reviewer outcomes, recorded in research/scout-independent-reconciliation-v0.md.
REVIEW = {
    "debate": {
        "reviewer": "INVESTIGATE",
        "final": "INVESTIGATE",
        "critique": "The paper tests diversity of initial answers, not independent source acquisition. Confidence-modulated updates involve learned calibration.",
        "next": "Pilot 30 claims under equal token budgets; compare voting, ordinary debate, and diversity-selected debate.",
    },
    "sensemaking": {
        "reviewer": "FOLLOW",
        "final": "FOLLOW",
        "critique": "Existing GhostMesh provenance must be examined before claiming a missing capability. The paper is conceptual, not a demonstrated system.",
        "next": "Establish existing-view baseline; test whether attribution and dissent views improve 12 fixed review histories.",
    },
    "negative-control": {
        "reviewer": "NO_CONNECTION_JUSTIFIED",
        "final": "NO_CONNECTION_JUSTIFIED",
        "critique": "Useful engineering documentation alone does not establish a distinctive collaboration opportunity.",
        "next": "None. Retain as a negative control.",
    },
}
STYLE = """
:root{color-scheme:dark light;font-family:system-ui,-apple-system,sans-serif}
body{max-width:1080px;margin:0 auto;padding:32px 22px;line-height:1.55;background:#121720;color:#e7ebf0}
h1,h2{letter-spacing:-.025em}h1{font-size:2.1rem}
small,.muted{color:#aeb8c8}
.panel{border:1px solid #384457;border-radius:12px;margin:24px 0;padding:22px;background:#1b2430}
.columns{display:grid;grid-template-columns:repeat(3,minmax(0,1fr));gap:12px}
.cell{background:#111924;border-radius:8px;padding:14px;min-width:0}
.label{font-size:.78rem;text-transform:uppercase;letter-spacing:.09em;color:#bcc9d9}
.verdict{font-weight:700;overflow-wrap:anywhere}
a{color:#b2d7ff}code{overflow-wrap:anywhere}
footer{border-top:1px solid #384457;padding:18px 0;margin-top:32px}
@media(max-width:740px){.columns{grid-template-columns:1fr}}
@media(prefers-color-scheme:light){body{background:#f7f9fc;color:#202a37}.panel{background:white;border-color:#d8dee8}.cell{background:#f0f3f8}.muted,small,.label{color:#465569}a{color:#075ba1}footer{border-color:#d8dee8}}
"""

def render(receipts: Path, editorial_path: Path) -> str:
    # Ensures every retained snapshot and editorial SHA binding is valid before rendering.
    join(receipts, editorial_path)
    data = json.loads(editorial_path.read_text(encoding="utf-8"))
    if {c["id"] for c in data["cases"]} != set(REVIEW):
        raise ValueError("Preview requires exact reviewed case set")
    manifest = json.loads((receipts / "manifest.json").read_text(encoding="utf-8"))
    sources = {x["id"]: x["source_url"] for x in manifest["results"]}
    chunks = [
        "<!doctype html><html lang='en'><head><meta charset='utf-8'>",
        "<meta name='viewport' content='width=device-width,initial-scale=1'>",
        "<meta name='robots' content='noindex,nofollow,noarchive'>",
        "<title>Scout | Private Evidence Review</title><style>", STYLE, "</style></head><body>",
        "<header><small>GHOSTMESH SCOUT · LOCAL REVIEW ONLY</small>",
        "<h1>Connection Thesis: independent review</h1>",
        "<p class='muted'>Three source-linked cases. Source bytes are hash-checked; author claims and collaboration hypotheses are not independently validated. Reviewer sequence was self-reported.</p>",
        "<p><strong>Research-only.</strong> No publication, outreach, merge, or autonomous recommendation authority.</p></header>"
    ]
    for case in data["cases"]:
        key = case["id"]
        review = REVIEW[key]
        h = lambda x: escape(str(x), quote=True)
        source = sources[key]
        packet = json.loads((receipts / (key + ".json")).read_text(encoding="utf-8"))
        extracted = packet["substantive_text"]
        chunks.extend([
            "<article class='panel'><h2>", h(extracted.get("title") or key), "</h2>",
            "<p><a href='", h(source), "' rel='noopener noreferrer'>Primary source</a> · ",
            "<small>SHA-256 <code>", h(case["snapshot_sha256"]), "</code></small></p>",
            "<div class='columns'>",
            "<section class='cell'><div class='label'>Initial editorial</div><p class='verdict'>", h(case["recommendation"]), "</p>",
            "<p>", h(case["contribution"]), "</p></section>",
            "<section class='cell'><div class='label'>Independent review</div><p class='verdict'>", h(review["reviewer"]), "</p>",
            "<p>", h(review["critique"]), "</p></section>",
            "<section class='cell'><div class='label'>Adjudicated research status</div><p class='verdict'>", h(review["final"]), "</p>",
            "<p>", h(review["next"]), "</p></section></div>",
            "<p><strong>GhostMesh question:</strong> ", h(case["ghostmesh_gap"]), "</p>",
            "<p><strong>Strongest original objection:</strong> ", h(case["counterargument"]), "</p>",
            "<details><summary>Collected source excerpt (unverified claims)</summary><p>", h((extracted.get("excerpt") or "")[:2400]), "</p></details>",
            "</article>"
        ])
    chunks.extend([
        "<footer><strong>Limits:</strong> Two apparent agreements and one disagreement are not discovery accuracy. The negative control's identity was disclosed; the reviewer read public pages rather than retained snapshots. No source implementation was reproduced. ",
        "Independent review receipt: <a href='https://ghostmesh.slack.com/archives/D0C76SEPA3G/p1792722589895059'>Pale Horse Slack thread</a>.",
        "</footer></body></html>"
    ])
    return "".join(chunks)

def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--receipts", required=True, type=Path)
    parser.add_argument("--editorial", required=True, type=Path)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    if args.out.exists():
        raise SystemExit("Refusing to overwrite an existing preview")
    args.out.write_text(render(args.receipts, args.editorial), encoding="utf-8")
    print(args.out)

if __name__ == "__main__":
    main()
