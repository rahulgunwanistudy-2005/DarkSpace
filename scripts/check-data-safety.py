"""Read the Git index and history without printing prohibited text."""

import argparse
import json
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from darkspace.safety import Fingerprint, file_issue, text_issue


def git(*arguments: str) -> bytes:
    return subprocess.check_output(["git", *arguments])


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--staged", action="store_true")
    parser.add_argument("--tracked", action="store_true")
    parser.add_argument("--history", action="store_true")
    args = parser.parse_args()
    policy = json.loads(Path("configs/data-safety.json").read_text())
    known = tuple(Fingerprint(**row) for row in policy["gallery_fingerprints"])
    local_policy = Path(".darkspace-local/data-safety/fingerprints.json")
    if local_policy.exists():
        known += tuple(Fingerprint(**row) for row in json.loads(local_policy.read_text()))
    paths = set(git("ls-files", "-z").decode().split("\0")) if args.tracked else set()
    if args.staged or not (args.history or args.tracked):
        paths.update(
            git("diff", "--cached", "--name-only", "--diff-filter=ACMR", "-z").decode().split("\0")
        )
    problems = []
    checked = 0
    for path in sorted(paths - {""}):
        try:
            payload = git("show", ":" + path)
        except subprocess.CalledProcessError:
            continue
        checked += 1
        issue = file_issue(path, payload, known, policy["reviewed_media"])
        if issue:
            problems.append({"path": path, "reason": issue})
    commits = []
    blobs = 0
    if args.history:
        commits = git("log", "--all", "--format=%H").decode().splitlines()
        for line in (
            git("cat-file", "--batch-all-objects", "--batch-check=%(objectname) %(objecttype)")
            .decode()
            .splitlines()
        ):
            oid, kind = line.split()
            if kind != "blob":
                continue
            blobs += 1
            payload = git("cat-file", "blob", oid)
            issue = text_issue(payload.decode("utf-8", errors="replace"), known)
            if issue:
                problems.append({"blob": oid, "reason": issue})
    result = {
        "tracked_or_staged_files_checked": checked,
        "history_commits_checked": len(commits),
        "history_blobs_checked": blobs,
        "violations": problems,
    }
    print(json.dumps(result, indent=2))
    if problems:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
