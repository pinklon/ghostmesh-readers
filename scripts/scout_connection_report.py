"""Offline, read-only Markdown rendering of reviewed Scout Connection Thesis fixtures.

The output is a research report, not publication or outreach authority.
"""
from __future__ import annotations

import json
from pathlib import Path
from scout_connection_thesis import validate


def render(records: list[dict]) -> str:
    if not isinstance(records, list):
        raise ValueError("candidates must be an array")
    ids = set()
    for item in records:
        problems = validate(item)
        if problems:
            raise ValueError(f"invalid candidate: {problems}")
        if item["id"] in ids:
            raise ValueError("duplicate candidate id")
        ids.add(item["id"])

    lines = [
        "# Scout Connection Thesis | Research review",
        "",
        "> Offline descriptive rendering of authored source-linked fixtures.",
        "> Not independent evaluation, accuracy evidence, introduction approval, or public copy.",
        "",
        f"Candidates: {len(records)} | Outreach authorized: no | Publication authorized: no",
        "",
    ]
    for item in records:
        lines.extend([
            f"## {item['id']}",
            "",
            f"Primary source: {item['source_url']}",
            "",
            f"**Contribution:** {item['original_contribution']}",
            "",
            f"**GhostMesh gap:** {item['ghostmesh_gap']}",
            "",
            f"**Connection thesis:** {item['connection_thesis']}",
            "",
            f"**Counterargument:** {item['strongest_objection']}",
            "",
            f"**Joint experiment:** {item['proposed_experiment']}",
            "",
            f"**Evidence status:** {item['evidence']}",
            "",
            f"**Editorial recommendation:** {item['recommendation']} (research only)",
            "",
        ])
    lines.extend([
        "## Unresolved",
        "",
        "- The candidate set is topic-selected, not randomized.",
        "- Maintainer collaboration interest and independent implementation quality are UNKNOWN.",
        "- No independent ratings, outcome measurement, or controlled comparison are recorded.",
        "- No automated contact, scheduling, production ranking, or publishing is performed.",
        "",
    ])
    return "\n".join(lines)


def main() -> None:
    root = Path(__file__).resolve().parents[1]
    payload = json.loads((root / "research" / "scout-connection-fixtures.json").read_text(encoding="utf-8"))
    print(render(payload["candidates"]), end="")


if __name__ == "__main__":
    main()
