import json
from itertools import pairwise
from pathlib import Path

import pytest

from darkspace.corpus import (
    AGENT,
    GALLERY,
    HOST,
    FetchError,
    Pacer,
    Response,
    crawl,
    parse_gallery,
    register_fingerprints,
)


def entry(
    slug: str, title: str = "Made-up moon canopy", tagline: str = "A fictional workshop sample."
) -> str:
    url = "https://" + "devpost.com" + "/software/" + slug
    return f'<div class="software-entry gallery-entry"><a href="{url}"><img src="decorative.invalid"><h5 class="software-entry-name">{title}</h5><p class="tagline">{tagline}</p></a></div>'


def test_parser_keeps_missing_text_and_returns_pagination_without_fetching_projects() -> None:
    html = entry("fixture-one") + entry("fixture-two", tagline="") + '<a href="?page=2">Next</a>'
    cards, next_url, starts = parse_gallery(html, GALLERY)
    assert len(cards) == 2 and starts == 2
    assert cards[1].tagline == ""
    assert next_url == GALLERY + "?page=2"


def test_rate_limit_applies_to_robots_pages_and_each_redirect(tmp_path: Path) -> None:
    now = [0.0]
    calls = []

    def sleep(seconds: float) -> None:
        now[0] += seconds

    def transport(url: str) -> Response:
        calls.append((url, now[0]))
        if url.endswith("robots.txt"):
            return Response(
                status=200, headers={}, body=b"User-agent: *\nAllow: /\nCrawl-delay: 5\n"
            )
        if url == GALLERY:
            return Response(status=302, headers={"location": "/project-gallery?page=1"}, body=b"")
        if url.endswith("page=1"):
            return Response(
                status=200,
                headers={},
                body=(entry("fixture-one") + '<a href="?page=2">Next</a>').encode(),
            )
        return Response(
            status=200,
            headers={},
            body=(entry("fixture-one") + entry("fixture-two", tagline="")).encode(),
        )

    result = crawl(transport, Pacer(lambda: now[0], sleep), tmp_path / "crawl")
    assert result["records"] == 2 and result["duplicates"] == 1 and result["missing_text"] == 1
    assert result["requests"] == 4 and result["event_completeness_verified"] is False
    assert all(later[1] - earlier[1] >= 5 for earlier, later in pairwise(calls))
    assert all(url.startswith("https://" + HOST) for url, _ in calls)
    assert AGENT.startswith("DarkSpace")


def test_robots_denial_fetches_no_gallery_and_keeps_failure_provenance(tmp_path: Path) -> None:
    urls = []

    def transport(url: str) -> Response:
        urls.append(url)
        return Response(status=200, headers={}, body=b"User-agent: *\nDisallow: /project-gallery\n")

    target = tmp_path / "denied"
    with pytest.raises(FetchError, match="robots.txt forbids"):
        crawl(transport, Pacer(lambda: 0, lambda seconds: None), target)
    assert len(urls) == 1
    manifest = json.loads((target / "provenance.json").read_text())
    assert manifest["records"] == 0 and manifest["html_pagination_exhausted"] is False


@pytest.mark.parametrize("kind", ["offhost", "empty", "limit", "http"])
def test_failures_are_counted_and_partial_data_is_never_claimed_complete(
    tmp_path: Path, kind: str
) -> None:
    calls = []

    def transport(url: str) -> Response:
        calls.append(url)
        if url.endswith("robots.txt"):
            return Response(status=200, headers={}, body=b"User-agent: *\nAllow: /\n")
        if kind == "offhost":
            return Response(
                status=302, headers={"location": "https://example.invalid/private"}, body=b""
            )
        if kind == "empty":
            return Response(status=200, headers={}, body=b"<h1>No readable gallery</h1>")
        if kind == "http":
            return Response(status=503, headers={}, body=b"unavailable")
        return Response(
            status=200,
            headers={},
            body=(entry("fixture-one") + '<a href="?page=2">Next</a>').encode(),
        )

    target = tmp_path / kind
    with pytest.raises(FetchError):
        crawl(transport, Pacer(lambda: 0, lambda seconds: None), target, max_pages=1)
    manifest = json.loads((target / "provenance.json").read_text())
    assert len(manifest["requests"]) == 2 and manifest["html_pagination_exhausted"] is False
    assert len(calls) == 2


def test_local_fingerprints_cover_partial_snapshots_without_copying_text(tmp_path: Path) -> None:
    from darkspace.safety import Fingerprint, text_issue

    target = tmp_path / "partial"
    target.mkdir()
    phrase = "A fictional meteor cupboard shares tiny umbrella handles."
    (target / "corpus.json").write_text(
        json.dumps(
            {
                "records": [
                    {"title": "Made-up sample", "tagline": phrase, "source_url": "metadata-only"}
                ]
            }
        )
    )
    register_fingerprints(tmp_path, target)
    raw = (tmp_path / "data-safety/fingerprints.json").read_text()
    assert phrase not in raw
    known = tuple(Fingerprint(**row) for row in json.loads(raw))
    assert text_issue(phrase, known) is not None
