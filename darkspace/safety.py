"""Pure checks for prohibited gallery material; stored fingerprints contain no wording."""

import hashlib
import json
import math
import re
import unicodedata
from dataclasses import dataclass
from pathlib import PurePosixPath


@dataclass(frozen=True)
class Fingerprint:
    words: int
    sha256: str


def words(text: str) -> list[str]:
    return re.findall(r"[^\W_]+", unicodedata.normalize("NFKC", text).casefold())


def fingerprints(text: str, size: int = 8) -> tuple[Fingerprint, ...]:
    tokens = words(text)
    length = min(size, len(tokens))
    if not length:
        return ()
    return tuple(
        Fingerprint(
            length, hashlib.sha256(" ".join(tokens[index : index + length]).encode()).hexdigest()
        )
        for index in range(len(tokens) - length + 1)
    )


def text_issue(text: str, known: tuple[Fingerprint, ...]) -> str | None:
    if re.search(r"https?://(?:www\.)?devpost\.com/software/[a-z0-9]", text, re.IGNORECASE):
        return "entrant project URL"
    if re.search(
        r"https?://github\.com/civictechdc/hackdc2025/[^\s\"]*/projects/", text, re.IGNORECASE
    ):
        return "entrant project source URL"
    tokens = words(text)
    for size in {value.words for value in known}:
        expected = {value.sha256 for value in known if value.words == size}
        for index in range(len(tokens) - size + 1):
            value = hashlib.sha256(" ".join(tokens[index : index + size]).encode()).hexdigest()
            if value in expected:
                return "known gallery wording fingerprint"
    return None


def file_issue(
    path: str, payload: bytes, known: tuple[Fingerprint, ...], allowed_media: dict[str, str]
) -> str | None:
    parts = PurePosixPath(path).parts
    suffix = PurePosixPath(path).suffix.lower()
    if any(
        part in {".darkspace-local", ".cache", "local-bundle", "recordings", "videos"}
        for part in parts
    ):
        return "local-only data path"
    if (
        suffix
        in {".sqlite", ".sqlite3", ".db", ".zip", ".gz", ".zst", ".tar", ".mp4", ".webm", ".mov"}
        or re.search(r"\.(?:sqlite3?|db)-(?:wal|shm|journal)$", path, re.IGNORECASE) is not None
    ):
        return "database, archive or recording must remain local"
    if suffix in {".png", ".jpg", ".jpeg", ".webp", ".gif", ".pdf"}:
        if allowed_media.get(path) != hashlib.sha256(payload).hexdigest():
            return "media requires an explicit reviewed content hash"
        return None
    if path.startswith(("data/raw/", "data/corpora/", "data/cache/", "data/development/")):
        return "real/development corpus path"
    if (
        path.startswith("data/runs/")
        and len(parts) > 2
        and parts[2] != "README.md"
        and not parts[2].startswith("fixture-")
    ):
        return "non-fixture run must remain local"
    text = payload.decode("utf-8", errors="replace")
    issue = text_issue(text, known)
    if issue:
        return issue
    if path == "data/backtest-summary.json":
        try:
            summary = json.loads(text)
            keys = {
                "status",
                "evidence",
                "run_id",
                "coverage",
                "control",
                "lift",
                "ci",
                "curve",
                "drop_counts",
            }
            if (
                set(summary) != keys
                or summary["status"] not in {"not_run", "validated"}
                or summary["evidence"] != "real"
            ):
                return "real backtest summary has non-aggregate fields"
            identity = summary["run_id"]
            if identity is not None and (
                not isinstance(identity, str) or re.fullmatch(r"[a-f0-9]{64}", identity) is None
            ):
                return "real backtest summary run identity is invalid"
            metric_keys = {
                "matched",
                "eligible",
                "rate",
                "lower",
                "upper",
                "difference_pp",
                "ratio",
                "confidence_level",
                "attempts",
                "coverage",
                "control",
                "invalid",
                "unknown",
                "provider_errors",
                "refusals",
                "repair_attempts",
                "repair_failures",
                "unavailable",
                "duplicates",
                "excluded",
            }

            def numeric(value: object) -> bool:
                if value is None:
                    return True
                if isinstance(value, bool):
                    return False
                if isinstance(value, (int, float)):
                    return math.isfinite(value)
                if isinstance(value, list):
                    return all(numeric(item) for item in value)
                if isinstance(value, dict):
                    return all(key in metric_keys and numeric(item) for key, item in value.items())
                return False

            if not all(numeric(summary[key]) for key in keys - {"status", "evidence", "run_id"}):
                return "real backtest summary contains text or per-project fields"
        except (ValueError, TypeError, AttributeError):
            return "invalid aggregate backtest summary"
    if path == "web/static/data/current.json":
        try:
            bundle = json.loads(text)
            if bundle.get("bundleKind") != "fixture" or bundle.get("dataLabel") != "sample data":
                return "public bundle must be explicitly labelled fixture sample data"
        except (ValueError, AttributeError):
            return "invalid public bundle"
    return None
