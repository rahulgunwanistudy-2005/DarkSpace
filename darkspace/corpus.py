"""Local-only permitted gallery collection; parsing is pure and HTTP/disk live at this edge."""

import argparse
import fcntl
import hashlib
import json
import time
import urllib.error
import urllib.request
import urllib.robotparser
from collections.abc import Callable
from datetime import UTC, datetime
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import parse_qs, urljoin, urlsplit, urlunsplit

from pydantic import BaseModel, ConfigDict

from darkspace.safety import fingerprints

HOST = "learn-ai.devpost.com"
GALLERY = f"https://{HOST}/project-gallery"
AGENT = "DarkSpace-local-corpus/1.0"


class FetchError(RuntimeError):
    pass


class Response(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    status: int
    headers: dict[str, str]
    body: bytes


class Card(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)
    source_url: str
    title: str
    tagline: str


def project_url(href: str) -> str | None:
    value = urlsplit(href)
    if (
        value.scheme != "https"
        or value.hostname not in {"devpost.com", "www.devpost.com"}
        or not value.path.startswith("/software/")
    ):
        return None
    return urlunsplit(("https", "devpost.com", value.path.rstrip("/"), "", ""))


class GalleryParser(HTMLParser):
    def __init__(self, base: str) -> None:
        super().__init__(convert_charrefs=True)
        self.base = base
        self.depth = 0
        self.capture: str | None = None
        self.capture_depth = 0
        self.title: list[str] = []
        self.tagline: list[str] = []
        self.url: str | None = None
        self.cards: list[Card] = []
        self.pages: set[str] = set()
        self.card_starts = 0

    def handle_starttag(self, tag: str, attrs: list[tuple[str, str | None]]) -> None:
        attributes = dict(attrs)
        classes = (attributes.get("class") or "").split()
        if tag == "a" and attributes.get("href"):
            href = urljoin(self.base, attributes["href"] or "")
            value = urlsplit(href)
            if (
                value.hostname == HOST
                and value.path.rstrip("/") == "/project-gallery"
                and parse_qs(value.query).get("page")
            ):
                self.pages.add(href)
            if self.depth and (project := project_url(href)):
                self.url = self.url or project
        if self.depth == 0 and "software-entry" in classes:
            self.depth = 1
            self.card_starts += 1
            self.title = []
            self.tagline = []
            self.url = project_url(urljoin(self.base, attributes.get("href") or ""))
            return
        if not self.depth:
            return
        if tag not in {
            "img",
            "br",
            "hr",
            "input",
            "meta",
            "link",
            "source",
            "wbr",
            "area",
            "base",
            "embed",
            "param",
            "track",
            "col",
        }:
            self.depth += 1
        if "software-entry-name" in classes or tag == "h5":
            self.capture = "title"
            self.capture_depth = self.depth
        elif "tagline" in classes or "software-entry-description" in classes:
            self.capture = "tagline"
            self.capture_depth = self.depth

    def handle_endtag(self, tag: str) -> None:
        if not self.depth or tag in {
            "img",
            "br",
            "hr",
            "input",
            "meta",
            "link",
            "source",
            "wbr",
            "area",
            "base",
            "embed",
            "param",
            "track",
            "col",
        }:
            return
        if self.depth == self.capture_depth:
            self.capture = None
        self.depth -= 1
        if not self.depth and self.url:
            self.cards.append(
                Card(
                    source_url=self.url,
                    title=" ".join("".join(self.title).split()),
                    tagline=" ".join("".join(self.tagline).split()),
                )
            )

    def handle_data(self, data: str) -> None:
        if self.capture == "title":
            self.title.append(data)
        elif self.capture == "tagline":
            self.tagline.append(data)


def parse_gallery(html: str, base: str) -> tuple[tuple[Card, ...], str | None, int]:
    parser = GalleryParser(base)
    parser.feed(html)
    current = int(parse_qs(urlsplit(base).query).get("page", ["1"])[0])
    future = sorted(
        (int(parse_qs(urlsplit(url).query)["page"][0]), url)
        for url in parser.pages
        if parse_qs(urlsplit(url).query)["page"][0].isdigit()
        and int(parse_qs(urlsplit(url).query)["page"][0]) > current
    )
    return tuple(parser.cards), future[0][1] if future else None, parser.card_starts


class Pacer:
    def __init__(
        self,
        clock: Callable[[], float],
        sleep: Callable[[float], None],
        interval: float = 3.0,
        previous: float | None = None,
        record: Callable[[float], None] | None = None,
    ) -> None:
        self.clock = clock
        self.sleep = sleep
        self.interval = max(3.0, interval)
        self.previous = previous
        self.record = record

    def wait(self) -> None:
        now = self.clock()
        if self.previous is not None:
            remaining = self.interval - (now - self.previous)
            if remaining > 0:
                self.sleep(min(self.interval, remaining))
        self.previous = self.clock()
        if self.record:
            self.record(self.previous)


class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(
        self,
        req: urllib.request.Request,
        fp: object,
        code: int,
        msg: str,
        headers: object,
        newurl: str,
    ) -> None:
        return None


def http_get(url: str) -> Response:
    opener = urllib.request.build_opener(NoRedirect())
    request = urllib.request.Request(
        url, headers={"User-Agent": AGENT, "Accept": "text/html,text/plain;q=0.9"}
    )
    try:
        with opener.open(request, timeout=30) as response:
            body = response.read(8 * 1024 * 1024 + 1)
            if len(body) > 8 * 1024 * 1024:
                raise FetchError("Response exceeded the local size limit.")
            return Response(
                status=response.status,
                headers={key.lower(): value for key, value in response.headers.items()},
                body=body,
            )
    except urllib.error.HTTPError as error:
        return Response(
            status=error.code,
            headers={key.lower(): value for key, value in error.headers.items()},
            body=error.read(8 * 1024 * 1024),
        )


def crawl(
    transport: Callable[[str], Response], pacer: Pacer, destination: Path, max_pages: int = 100
) -> dict[str, object]:
    destination.mkdir(parents=True, exist_ok=False, mode=0o700)
    ledger: list[dict[str, object]] = []
    records: dict[str, dict[str, object]] = {}
    duplicates = 0
    unparsed_cards = 0
    pages = 0
    policy: urllib.robotparser.RobotFileParser | None = None

    def request(url: str, robots: bool = False) -> tuple[Response, str]:
        nonlocal policy
        for _ in range(6):
            value = urlsplit(url)
            if (
                value.scheme != "https"
                or value.hostname != HOST
                or value.port not in {None, 443}
                or value.username is not None
            ):
                raise FetchError("Redirect or source escaped the permitted host.")
            if not robots and (policy is None or not policy.can_fetch(AGENT, url)):
                raise FetchError("robots.txt forbids this gallery path.")
            pacer.wait()
            row: dict[str, object] = {"url": url, "requested_at": datetime.now(UTC).isoformat()}
            ledger.append(row)
            try:
                response = transport(url)
            except Exception as error:
                row["error"] = type(error).__name__
                raise FetchError("The gallery request failed; its failure was recorded.") from error
            row["status"] = response.status
            row["sha256"] = hashlib.sha256(response.body).hexdigest()
            raw = destination / (str(row["sha256"]) + (".robots.txt" if robots else ".html"))
            raw.write_bytes(response.body)
            if response.status in {301, 302, 303, 307, 308}:
                location = response.headers.get("location")
                if not location:
                    raise FetchError("Redirect had no destination.")
                url = urljoin(url, location)
                continue
            return response, url
        raise FetchError("Too many redirects; collection stopped.")

    exhausted = False
    try:
        robots_url = f"https://{HOST}/robots.txt"
        response, robots_final = request(robots_url, True)
        if response.status != 200:
            raise FetchError("robots.txt could not be verified; no gallery was collected.")
        policy = urllib.robotparser.RobotFileParser(robots_final)
        policy.parse(response.body.decode("utf-8", errors="replace").splitlines())
        delay = policy.crawl_delay(AGENT)
        rate = policy.request_rate(AGENT)
        pacer.interval = max(
            3.0,
            float(delay or 0),
            float(rate.seconds) / rate.requests if rate and rate.requests > 0 else 0.0,
        )
        url: str | None = GALLERY
        visited: set[str] = set()
        while url and pages < max_pages:
            if url in visited:
                raise FetchError("Pagination loop detected.")
            visited.add(url)
            response, source_page = request(url)
            if response.status != 200:
                raise FetchError("A gallery page was unavailable; collection is incomplete.")
            cards, next_url, starts = parse_gallery(
                response.body.decode("utf-8", errors="replace"), source_page
            )
            unparsed_cards += max(0, starts - len(cards))
            if not cards:
                raise FetchError(
                    "No project cards were readable. The gallery may require browser access; no bypass was attempted."
                )
            pages += 1
            for card in cards:
                if card.source_url in records:
                    duplicates += 1
                    continue
                identity = hashlib.sha256(card.source_url.encode()).hexdigest()[:24]
                records[card.source_url] = {
                    "id": identity,
                    **card.model_dump(),
                    "source_page": source_page,
                    "missing_text": not bool(card.title and card.tagline),
                }
            url = next_url
        exhausted = url is None
        if not exhausted:
            raise FetchError("Page limit reached; collection is explicitly incomplete.")
        return {
            "records": len(records),
            "pages": pages,
            "requests": len(ledger),
            "duplicates": duplicates,
            "missing_text": sum(bool(row["missing_text"]) for row in records.values()),
            "unparsed_cards": unparsed_cards,
            "html_pagination_exhausted": True,
            "event_completeness_verified": False,
            "evaluation_eligible": False,
        }
    finally:
        corpus = {
            "source": GALLERY,
            "permission": "Organizer permission reported by Rahul: local collection only, no public redistribution.",
            "records": list(records.values()),
        }
        raw = (json.dumps(corpus, sort_keys=True, ensure_ascii=False) + "\n").encode()
        (destination / "corpus.json").write_bytes(raw)
        manifest = {
            "source": GALLERY,
            "user_agent": AGENT,
            "minimum_interval_seconds": pacer.interval,
            "requests": ledger,
            "corpus_sha256": hashlib.sha256(raw).hexdigest(),
            "records": len(records),
            "duplicates": duplicates,
            "unparsed_cards": unparsed_cards,
            "html_pagination_exhausted": exhausted,
            "event_completeness_verified": False,
            "evaluation_eligible": False,
            "note": "HTML pagination exhaustion does not establish complete event eligibility. Missing text stays in the local corpus as unknown.",
        }
        (destination / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")


def register_fingerprints(root: Path, snapshot: Path) -> None:
    corpus = json.loads((snapshot / "corpus.json").read_text())
    hashed = set()
    for row in corpus["records"]:
        for field in ("title", "tagline", "source_url"):
            for item in fingerprints(row[field]):
                hashed.add((item.words, item.sha256))
    private_policy = root / "data-safety"
    if private_policy.is_symlink():
        raise FetchError("The local fingerprint directory must not be a symlink.")
    private_policy.mkdir(exist_ok=True)
    previous_rows = (
        json.loads((private_policy / "fingerprints.json").read_text())
        if (private_policy / "fingerprints.json").exists()
        else []
    )
    hashed.update((row["words"], row["sha256"]) for row in previous_rows)
    (private_policy / "fingerprints.json").write_text(
        json.dumps([{"words": size, "sha256": digest} for size, digest in sorted(hashed)]) + "\n"
    )


def main(arguments: list[str] | None = None) -> None:
    parser = argparse.ArgumentParser(
        description="Fetch the permitted gallery locally; no entrant wording is printed or uploaded."
    )
    parser.add_argument("--refresh", action="store_true")
    parser.add_argument("--max-pages", type=int, default=100)
    args = parser.parse_args(arguments)
    if args.max_pages < 1:
        raise SystemExit("max-pages must be positive.")
    root = Path(".darkspace-local")
    if root.is_symlink():
        raise SystemExit("The local data root must not be a symlink.")
    root.mkdir(exist_ok=True, mode=0o700)
    base = root / "corpora/learn-ai"
    base.mkdir(parents=True, exist_ok=True, mode=0o700)
    if not base.resolve().is_relative_to(root.resolve()):
        raise SystemExit("Corpus destination escaped local storage.")
    latest = base / "latest.json"
    with (root / "corpus-fetch.lock").open("a+") as lock:
        fcntl.flock(lock, fcntl.LOCK_EX)
        if latest.exists() and not args.refresh:
            previous = json.loads(latest.read_text())
            snapshot = (base / previous["snapshot"]).resolve()
            if not snapshot.is_relative_to(base.resolve()):
                raise SystemExit("Invalid local snapshot path.")
            raw = (snapshot / "corpus.json").read_bytes()
            if hashlib.sha256(raw).hexdigest() != previous["corpus_sha256"]:
                raise SystemExit(
                    "Cached corpus failed integrity verification. Retain it and fetch an explicit new snapshot."
                )
            register_fingerprints(root, snapshot)
            print(
                json.dumps(
                    {
                        "cached": True,
                        "snapshot": str(snapshot),
                        "records": previous["records"],
                        "new_requests": 0,
                    }
                )
            )
            return
        last = root / "last-corpus-request.monotonic"
        previous_time = float(last.read_text()) if last.exists() else None

        def record_request(stamp: float) -> None:
            last.write_text(str(stamp))

        pacer = Pacer(
            time.monotonic,
            time.sleep,
            previous=previous_time,
            record=record_request,
        )
        snapshot = base / datetime.now(UTC).strftime("%Y%m%dT%H%M%S%fZ")
        try:
            result = crawl(http_get, pacer, snapshot, args.max_pages)
        except FetchError as error:
            raise SystemExit(
                str(error) + " Local provenance: " + str(snapshot / "provenance.json")
            ) from error
        finally:
            if (snapshot / "corpus.json").exists():
                register_fingerprints(root, snapshot)
        manifest = json.loads((snapshot / "provenance.json").read_text())
        latest.write_text(
            json.dumps(
                {
                    "snapshot": snapshot.name,
                    "corpus_sha256": manifest["corpus_sha256"],
                    "records": result["records"],
                }
            )
            + "\n"
        )
        print(
            json.dumps(
                {"snapshot": str(snapshot), "corpus_sha256": manifest["corpus_sha256"], **result},
                indent=2,
            )
        )
