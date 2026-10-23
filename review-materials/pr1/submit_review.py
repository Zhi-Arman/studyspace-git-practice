#!/usr/bin/env python3
"""Validate and optionally submit the pinned PR1 review as like577 only."""

import argparse
import json
from pathlib import Path, PurePosixPath
import re
import subprocess
import sys
import tempfile

DIRECTORY = Path(__file__).resolve().parent
ROOT = DIRECTORY.parents[1]
REPOSITORY = "Zhi-Arman/studyspace-git-practice"
NUMBER = 7
REVIEWER = "like577"


def command(args, cwd=None, stdin=None):
    result = subprocess.run(args, cwd=cwd, input=stdin, text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError(result.stderr.strip() or f"command failed: {args[0]}")
    return result.stdout


def api(path, method=None, payload=None):
    args = ["gh", "api", path]
    if method:
        args += ["--method", method]
    if payload is not None:
        args += ["--input", "-"]
    value = command(args, stdin=json.dumps(payload) if payload is not None else None)
    return json.loads(value) if value.strip() else None


def api_list(path):
    pages = json.loads(command(["gh", "api", "--paginate", "--slurp", path]))
    return [entry for page in pages for entry in page]


def added_lines(patch):
    """Only new-side added lines are eligible for this review packet."""
    line = None
    eligible = set()
    for value in patch.splitlines():
        match = re.match(r"@@ -\d+(?:,\d+)? \+(\d+)(?:,\d+)? @@", value)
        if match:
            line = int(match.group(1))
        elif line is not None and value.startswith("+"):
            eligible.add(line)
            line += 1
        elif line is not None and value.startswith(" "):
            line += 1
    return eligible


def validate_payload(payload, manifest, files):
    assert payload["commit_id"] == manifest["head_sha"], "packet head mismatch"
    assert payload["event"] == "COMMENT", "only a nonblocking COMMENT is allowed"
    comments = payload["comments"]
    assert len(comments) >= 8, "need at least eight inline comments"
    assert len({entry["section"] for entry in manifest["comments"]}) >= 5
    assert len(manifest["comments"]) == len(comments)
    assert len({entry["marker"] for entry in manifest["comments"]}) == len(comments)
    assert sum("```suggestion\n" in c["body"] for c in comments) >= 2
    assert sum("[question]" in c["body"] and "?" in c["body"] for c in comments) >= 1
    by_path = {file["filename"]: added_lines(file.get("patch", "")) for file in files}
    for entry, comment in zip(manifest["comments"], comments):
        assert entry["marker"] in comment["body"], "missing unique marker"
        assert (comment["path"], comment["line"]) == (entry["path"], entry["line"])
        assert comment["side"] == "RIGHT"
        assert comment["line"] in by_path.get(comment["path"], set()), "stale/non-added line"
        for label in ("Location:", "Observation:", "Impact:", "Proposal:", "Label:"):
            assert label in comment["body"], f"missing comment field {label}"


def verify_actor(login, pull, expected_sha):
    if login != REVIEWER:
        raise RuntimeError(f"Expected reviewer {REVIEWER}; current account is {login}. No review submitted.")
    if pull["user"]["login"] == login:
        raise RuntimeError("Reviewer must differ from the PR author")
    if pull["head"]["sha"] != expected_sha:
        raise RuntimeError("PR head changed; re-review and regenerate line anchors before submitting")
    if pull["state"] != "open":
        raise RuntimeError("PR is no longer open")


def snapshot_and_test(sha, destination):
    exists = subprocess.run(["git", "cat-file", "-e", f"{sha}^{{commit}}"], cwd=ROOT,
                            capture_output=True).returncode == 0
    if not exists:
        command(["git", "fetch", "origin", sha], cwd=ROOT)
    paths = command(["git", "ls-tree", "-r", "--name-only", sha, "classroom-git"], cwd=ROOT).splitlines()
    # Deliberately inspect test source before implementation source.
    ordered = sorted(paths, key=lambda path: ("/tests/" not in path, path))
    for name in ordered:
        parsed = PurePosixPath(name)
        if parsed.is_absolute() or ".." in parsed.parts:
            raise RuntimeError("unsafe path in pinned tree")
        content = command(["git", "show", f"{sha}:{name}"], cwd=ROOT)
        target = destination.joinpath(*parsed.parts)
        target.parent.mkdir(parents=True, exist_ok=True)
        target.write_text(content, encoding="utf-8")
    result = subprocess.run([sys.executable, "-m", "unittest", "discover", "-s", "tests", "-v"],
                            cwd=destination / "classroom-git", text=True, capture_output=True)
    if result.returncode:
        raise RuntimeError("Pinned tests failed; no review submitted:\n" + result.stdout + result.stderr)
    if not re.search(r"Ran 7 tests\b", result.stderr):
        raise RuntimeError("Unexpected pinned test count; regenerate review packet")
    return {"read_order": ordered, "test_output": result.stdout + result.stderr}


def existing_markers(comments, head):
    return {marker for comment in comments
            if comment["user"]["login"] == REVIEWER and comment["commit_id"] == head
            for marker in re.findall(r"PR1-R\d{2}", comment["body"])}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--submit", action="store_true", help="post COMMENT as like577 after validation")
    args = parser.parse_args()
    payload = json.loads((DIRECTORY / "review-payload.json").read_text(encoding="utf-8"))
    manifest = json.loads((DIRECTORY / "review-manifest.json").read_text(encoding="utf-8"))
    login = api("user")["login"]
    pull = api(f"repos/{REPOSITORY}/pulls/{NUMBER}")
    verify_actor(login, pull, payload["commit_id"])
    files = api_list(f"repos/{REPOSITORY}/pulls/{NUMBER}/files?per_page=100")
    validate_payload(payload, manifest, files)
    commits = api_list(f"repos/{REPOSITORY}/pulls/{NUMBER}/commits?per_page=100")
    if [commit["sha"] for commit in commits] != [payload["commit_id"]]:
        raise RuntimeError("Commit composition changed; regenerate review packet")
    checks = api(f"repos/{REPOSITORY}/commits/{payload['commit_id']}/check-runs?per_page=100")
    statuses = api(f"repos/{REPOSITORY}/commits/{payload['commit_id']}/status?per_page=100")
    if checks["total_count"] or statuses["statuses"]:
        raise RuntimeError("CI evidence changed from no checks; inspect and update the packet before posting")
    with tempfile.TemporaryDirectory(prefix="pr1-review-") as directory:
        evidence = snapshot_and_test(payload["commit_id"], Path(directory))
    print(json.dumps({"reviewer": login, "head": payload["commit_id"],
                      "inline_comments": len(payload["comments"]),
                      "sections": sorted({c["section"] for c in manifest["comments"]}),
                      "ci": "NO_CHECKS_CONFIGURED", **evidence}, ensure_ascii=False, indent=2))
    if not args.submit:
        print("CHECKED; no review submitted. Inspect the payload, then run with --submit.")
        return
    # Recheck identity and head immediately before the external write.
    verify_actor(api("user")["login"], api(f"repos/{REPOSITORY}/pulls/{NUMBER}"), payload["commit_id"])
    prior = api_list(f"repos/{REPOSITORY}/pulls/{NUMBER}/comments?per_page=100")
    done = existing_markers(prior, payload["commit_id"])
    remaining = [c for c in payload["comments"] if not any(
        entry["marker"] in done and entry["marker"] in c["body"] for entry in manifest["comments"])]
    if not remaining:
        print("All packet comments already exist as like577 on this head; no duplicate review posted.")
        return
    outgoing = dict(payload, comments=remaining)
    try:
        review = api(f"repos/{REPOSITORY}/pulls/{NUMBER}/reviews", method="POST", payload=outgoing)
    except RuntimeError:
        print("Submission result uncertain. Inspect existing reviews or rerun; markers prevent duplicate comments.",
              file=sys.stderr)
        raise
    actual = api_list(f"repos/{REPOSITORY}/pulls/{NUMBER}/comments?per_page=100")
    expected = {entry["marker"] for entry in manifest["comments"]}
    if not expected <= existing_markers(actual, payload["commit_id"]):
        raise RuntimeError("Review returned but not all comments are visible; inspect GitHub before claiming completion")
    print(json.dumps({"review_url": review["html_url"], "reviewer": review["user"]["login"],
                      "state": review["state"], "verified_packet_comments": len(expected)}, indent=2))


if __name__ == "__main__":
    try:
        main()
    except (AssertionError, RuntimeError) as error:
        sys.exit(str(error))
