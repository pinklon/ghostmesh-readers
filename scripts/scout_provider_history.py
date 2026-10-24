#!/usr/bin/env python3
"""Locate the last retained successful main-branch Scout observation artifact.

Only Actions metadata is read here. Snapshot bytes stay in Actions artifacts.
"""
import argparse
import json
import os
import re
from urllib.request import Request, urlopen

API = "https://api.github.com"
REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
WORKFLOW = "scout-provider-watch.yml"


def select_artifact(runs, artifacts_for_run, current_run_id):
    """Choose a complete, nonexpired snapshot from an earlier main observation."""
    for run in sorted(runs, key=lambda item: item.get("created_at", ""), reverse=True):
        run_id = run.get("id")
        if (not isinstance(run_id, int) or run_id >= current_run_id
                or run.get("head_branch") != "main"
                or run.get("event") not in {"schedule", "workflow_dispatch"}
                or run.get("conclusion") != "success"):
            continue
        expected = f"scout-provider-observations-{run_id}"
        matches = [item for item in artifacts_for_run(run_id)
                   if item.get("name") == expected and not item.get("expired")
                   and isinstance(item.get("id"), int)]
        if matches:
            return {"run_id": run_id, "artifact_id": matches[0]["id"]}
    return None


def api_json(path, token):
    request = Request(API + path, headers={
        "Accept": "application/vnd.github+json",
        "Authorization": f"Bearer {token}",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "GhostMeshScoutProviderHistory/1.0",
    })
    with urlopen(request, timeout=15) as response:
        body = response.read(1_000_001)
    if len(body) > 1_000_000:
        raise ValueError("Actions metadata response too large")
    return json.loads(body)


def find_previous(repository, token, current_run_id):
    runs = api_json(f"/repos/{repository}/actions/workflows/{WORKFLOW}/runs"
                    "?status=success&branch=main&per_page=100", token)["workflow_runs"]
    return select_artifact(
        runs,
        lambda run_id: api_json(f"/repos/{repository}/actions/runs/{run_id}/artifacts"
                                "?per_page=100", token)["artifacts"],
        current_run_id,
    )


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", required=True, help="GitHub Actions step output path")
    args = parser.parse_args()
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    token = os.environ.get("GITHUB_TOKEN", "")
    run_id = os.environ.get("GITHUB_RUN_ID", "")
    if not REPOSITORY.fullmatch(repository) or not token or not run_id.isdigit():
        raise ValueError("Missing or invalid Actions context")
    selected = find_previous(repository, token, int(run_id))
    with open(args.output, "a", encoding="utf-8") as output:
        output.write(f"artifact_id={selected['artifact_id'] if selected else ''}\n")
        output.write(f"previous_run_id={selected['run_id'] if selected else ''}\n")
    print("Previous main-branch snapshot: found" if selected else
          "Previous main-branch snapshot: unavailable; baseline stays UNKNOWN")


if __name__ == "__main__":
    main()
