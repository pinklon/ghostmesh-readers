"""Research-only Scout Connection Thesis validation and comparison.

No network, publication, outreach or candidate execution. Standard library only.
"""
from __future__ import annotations
import json
from pathlib import Path

ALLOWED = {"ARCHIVE", "FOLLOW", "INVESTIGATE", "CONSIDER_INTRODUCTION", "NO_CONNECTION_JUSTIFIED"}
REQUIRED = ("id", "source_url", "original_contribution", "evidence", "ghostmesh_gap",
            "connection_thesis", "proposed_experiment", "strongest_objection",
            "recommendation", "outreach_authorized")

def validate(item: dict) -> list[str]:
    errors = []
    if not isinstance(item, dict):
        return ["record must be an object"]
    for field in REQUIRED:
        if field not in item:
            errors.append(f"missing {field}")
    if errors:
        return errors
    for field in REQUIRED:
        if field != "outreach_authorized" and (not isinstance(item[field], str) or not item[field].strip()):
            errors.append(f"{field} must be nonempty text")
    if item["recommendation"] not in ALLOWED:
        errors.append("invalid recommendation")
    if item["outreach_authorized"] is not False:
        errors.append("outreach must remain disabled in research prototype")
    if not isinstance(item["source_url"], str) or not item["source_url"].startswith("https://"):
        errors.append("source_url must be HTTPS")
    if item["recommendation"] == "CONSIDER_INTRODUCTION" and item["proposed_experiment"].strip().lower() in {"none", "unknown", "n/a"}:
        errors.append("introduction requires a specific experiment")
    return errors

def compare(records: list[dict]) -> dict:
    """Produce descriptive counts, never invented success metrics."""
    failures = {str(i): err for i, item in enumerate(records) if (err := validate(item))}
    if failures:
        raise ValueError(f"invalid records: {failures}")
    counts = {decision: sum(item["recommendation"] == decision for item in records)
              for decision in sorted(ALLOWED)}
    return {"schema": "scout-connection-shadow-v0", "candidate_count": len(records),
            "recommendations": counts, "measured_accuracy": None,
            "caveat": "Descriptive shadow output only; no blind A/B result or outreach authorization."}

def main() -> None:
    root = Path(__file__).resolve().parents[1]
    records = json.loads((root / "research" / "scout-connection-fixtures.json").read_text(encoding="utf-8"))
    print(json.dumps(compare(records["candidates"]), indent=2, sort_keys=True))

if __name__ == "__main__":
    main()
