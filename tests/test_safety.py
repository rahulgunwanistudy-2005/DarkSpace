import json
import subprocess
from pathlib import Path

from darkspace.safety import file_issue, fingerprints, text_issue


def test_gallery_wording_and_urls_are_blocked_without_storing_the_words_in_policy() -> None:
    invented = "A fictional moon garden lends crystal watering cans at midnight."
    known = fingerprints(invented)
    assert text_issue("prefix " + invented + " suffix", known) is not None
    assert text_issue("Unrelated application source.", known) is None
    assert (
        text_issue("https://" + "devpost.com" + "/software/" + "fictional-test-only", ())
        is not None
    )
    assert file_issue("innocent.json", invented.encode(), known, {}) is not None
    assert file_issue("renamed.sqlite", b"database", (), {}) is not None
    assert file_issue("renamed.sqlite3-wal", b"database", (), {}) is not None
    assert file_issue("cache.db-shm", b"database", (), {}) is not None
    assert file_issue(".darkspace-local/run.json", b"{}", (), {}) is not None
    assert file_issue("web/static/data/current.json", b'{"bundleKind":"local"}', (), {}) is not None
    assert (
        file_issue(
            "web/static/data/current.json",
            b'{"bundleKind":"fixture","dataLabel":"sample data"}',
            (),
            {},
        )
        is None
    )


def test_git_index_guard_rejects_staged_gallery_wording_in_an_isolated_repository(
    tmp_path: Path,
) -> None:
    project = Path.cwd()
    subprocess.run(["git", "init", "-q", str(tmp_path)], check=True)
    (tmp_path / "configs").mkdir()
    phrase = "An invented comet cupboard lends miniature telescopes during eclipses."
    policy = {
        "gallery_fingerprints": [
            {"words": row.words, "sha256": row.sha256} for row in fingerprints(phrase)
        ],
        "reviewed_media": {},
    }
    (tmp_path / "configs/data-safety.json").write_text(json.dumps(policy))
    (tmp_path / "renamed.md").write_text(phrase)
    subprocess.run(["git", "add", "renamed.md"], cwd=tmp_path, check=True)
    result = subprocess.run(
        ["python3", str(project / "scripts/check-data-safety.py"), "--staged", "--tracked"],
        cwd=tmp_path,
        check=False,
        capture_output=True,
        text=True,
    )
    assert result.returncode == 1
    assert "known gallery wording fingerprint" in result.stdout
    assert phrase not in result.stdout


def test_gallery_fingerprints_also_cover_non_latin_text() -> None:
    phrase = "एक काल्पनिक चाँद कार्यशाला अपनी छोटी छतरियाँ साझा करती है"
    assert text_issue("prefix " + phrase + " suffix", fingerprints(phrase)) is not None
