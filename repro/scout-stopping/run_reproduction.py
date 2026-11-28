#!/usr/bin/env python3
"""Reproduce Scout's three pinned synthetic benchmarks without external services.

Usage: python3 -B repro/scout-stopping/run_reproduction.py --out /path/to/new-directory
The destination must not exist. All outputs are synthetic and public-safe.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import platform
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent
PINNED = ROOT / "pinned"
sys.path.insert(0, str(PINNED))

import scout_speculative_search_pilot as search  # noqa: E402
import scout_heldout_stop_stress as stopping  # noqa: E402
import scout_three_way_extra_work as probe  # noqa: E402

SOURCE_BLOBS = {
    "scout_speculative_search_pilot.py": "265d75d392b79e986c2afe957982f275ea833f91",
    "scout_heldout_stop_stress.py": "c807e3b5d92efe7800d22d533b92c6608bb8a046",
    "scout_three_way_extra_work.py": "2753367dcedf3d3b17f3f9151a3c2e1d7766c3a9",
}
HISTORICAL_COMMIT = "d46047390869ff372aa6239053ef882bd1b60a65"


def git_blob(data: bytes) -> str:
    return hashlib.sha1(b"blob " + str(len(data)).encode() + b"\0" + data).hexdigest()


def validate_sources() -> None:
    for name, expected in SOURCE_BLOBS.items():
        actual = git_blob((PINNED / name).read_bytes())
        if actual != expected:
            raise AssertionError(f"Pinned source mismatch: {name}: {actual} != {expected}")


def reports() -> dict[str, dict]:
    return {
        "search": search.benchmark(),
        "stopping": stopping.benchmark(),
        "probe": probe.benchmark(),
    }


def validate(data: dict[str, dict]) -> None:
    s, h, p = data["search"], data["stopping"], data["probe"]
    assert (len(s["rows"]), len(h["rows"]), len(p["rows"])) == (432, 240, 240)
    assert [s["strategies"][x]["mean_best_score"] for x in ("random", "success_only", "failure_aware")] == [.964286, .891314, .956680]
    assert [s["strategies"][x]["exact_matches"] for x in ("random", "success_only", "failure_aware")] == [20, 40, 75]
    assert [s["strategies"][x]["duplicate_evaluations"] for x in ("random", "success_only", "failure_aware")] == [132, 513, 0]
    late = next(r for r in h["summary"] if r["regime"] == "late_breakthrough" and r["rule"] == "stop_on_plateau")
    assert (late["premature_stops"], late["mean_missed_gain"], late["mean_saved_cost"], late["mean_net_vs_continue"]) == (20, .129851, .033550, -.096300)
    expected = {"late_breakthrough": (-.099211, -.119110), "false_plateau": (.008640, -.011048), "steady_progress": (-.089656, -.008000), "flat_noise": (.030262, .010170)}
    for regime, (stopped, probed) in expected.items():
        for action, value in (("stop", stopped), ("probe_then_decide", probed)):
            row = next(r for r in p["summary"] if r["regime"] == regime and r["action"] == action)
            assert row["mean_utility_delta_vs_continue"] == value, (regime, action)


def serialize(data: dict) -> bytes:
    return (json.dumps(data, indent=2, ensure_ascii=True, sort_keys=True) + "\n").encode("utf-8")


def run(destination: Path) -> dict:
    if destination.exists():
        raise FileExistsError(f"Refusing to overwrite existing directory: {destination}")
    validate_sources()
    data = reports()
    validate(data)
    payloads = {f"{name}.json": serialize(report) for name, report in data.items()}
    manifest = {
        "schema": "scout-stopping-reproduction-v1",
        "historical_source_commit": HISTORICAL_COMMIT,
        "python_version": platform.python_version(),
        "source_git_blobs": SOURCE_BLOBS,
        "synthetic_rows": {name: len(report["rows"]) for name, report in data.items()},
        "outputs_sha256": {name: hashlib.sha256(payload).hexdigest() for name, payload in payloads.items()},
        "evidence_status": "same-source deterministic replay; not independent replication",
        "original_raw_archive_hashes": "UNKNOWN",
        "model_dispatch_authorized": False,
        "production_adoption_authorized": False,
    }
    payloads["manifest.json"] = serialize(manifest)
    destination.mkdir(parents=True, exist_ok=False)
    for name, payload in payloads.items():
        (destination / name).write_bytes(payload)
    return manifest


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", required=True, type=Path)
    args = parser.parse_args()
    try:
        manifest = run(args.out)
    except (AssertionError, FileExistsError) as exc:
        parser.exit(1, f"FAIL: {exc}\n")
    print(json.dumps({"status": "PASS", "directory": str(args.out), **manifest}, indent=2))


if __name__ == "__main__":
    main()
