# Dark Space

Place an idea, examine shared defaults, answer in your own words, and carry one hand-off into scoping.

## Public demo: sample data only

The committed/deployed demo uses a small gallery and forecasts made up from scratch. Every card says **sample data**. These fixtures demonstrate the pipeline and interaction; they do not validate prediction of real entrants.

Requires Node 24.19 or later:

```sh
npm ci
npm run prepare:web
npm run build
npm run preview:production
```

Open **http://127.0.0.1:4173/**. No account, API key or personal inference server is needed. The local model/runtime assets total about 46 MB and come from the same site. Your idea and answers remain on your device.

The public build refuses a local recording bundle. The public browser build also rejects a local bundle at runtime.

## Reproduce the fixture result

Requires Python 3.12 and uv:

```sh
uv sync --locked --python 3.12
uv run darkspace fixtures --config configs/fixture.yaml
node scripts/export-bundle.mjs fixture data/runs/fixture-d14769c6fc4b987ec90459e808ac6c0bb3539e68e933019bc007fab5395e0c9b/bundle.json
```

`configs/fixture.yaml` uses YAML 1.2's JSON-compatible syntax. Inputs are in `data/fixtures/`; the recorded run and manifests are under `data/runs/fixture-…/`. Shared-WASM vectors are precomputed for the made-up forecast sentences; `node scripts/embed-fixtures.mjs` regenerates them.

Actual fixture arithmetic: **6/8 forecast matches, 6/8 control matches, zero lift**. The paired bootstrap interval is **−50 to +50 percentage points**, using seed 42 and 10,000 resamples. Matching compares authored audience/problem/mechanism tags and is used only for fixtures. This is not an LLM-judge result. The zero gap is not tuned away.

## Fetch the permitted gallery locally

Run this on your own machine, from the repository:

```sh
uv run darkspace corpus fetch
```

It requests `learn-ai.devpost.com/robots.txt` first, respects its rules and crawl delay, and waits at least three seconds between all requests, including redirects. It fetches gallery pages only; it does not fetch entrant project pages, avatars or screenshots. Off-host redirects, robots denial, unreadable pages and HTTP failures stop collection with local provenance retained.

Snapshots, raw responses, project URLs, titles/taglines and failure ledgers remain under `.darkspace-local/corpora/learn-ai/`. Repeating the command reuses the verified snapshot with zero requests. `--refresh` creates a new snapshot; `--max-pages N` sets an explicit cap, which is reported as incomplete if pagination remains. Duplicate projects are counted; missing text stays unknown rather than being discarded. Exhausting visible HTML pagination does not establish complete event eligibility.

The fetcher adds hash-only local fingerprints to the staging guard, including partial snapshots. It never prints entrant wording or uploads it to hosted models. These controls are tested with made-up HTTP responses; no live gallery collection was performed during the migration.

The real corpus is not shipped. There is currently no validated real backtest number to reproduce: `data/backtest-summary.json` remains `not_run`. A real evaluation still needs its frozen event/brief/model provenance, retained local corpus and cache, and human judge-validation gates. The fixture matcher must never be used to manufacture a real result.

For the original retained model-sampling run, offline replay verifies its exact existing bytes with zero model calls:

```sh
PYTHONPATH=. uv run python scripts/replay-public-run.py .darkspace-local/runs/da833e6b1cf8bf6b9348b22e0f6b0d5663eeeaea6dc3b3b64ffaf679aef3e09e/samples.json
```

That command requires the retained local artifact and archived protocol; it does not imply fresh model generation will be byte-identical on other hardware. No original real result was recomputed or changed by this migration.

## Real data and local recording

The real corpus is **not in the repository**. Collected titles/taglines, entrant URLs, caches, per-project matches, raw run artifacts, screenshots and recording bundles belong in ignored `.darkspace-local/` paths. Only text-free aggregate backtest results may be committed.

`data/backtest-summary.json` currently says **not run**, with null metrics. No validated real coverage, control, lift, confidence interval or judge-reliability result exists in this checkout. Permission to collect data does not validate an evaluation. Fixture results never replace real results.

The earlier actual model forecast was preserved locally: 384 attempts, 383 valid ideas, one invalid result, no provider or embedding failures. Its original bytes, frozen protocol and offline replay receipt remain local. Those counts are sampling results, not entrant coverage.

Explicit export/build commands for a locally generated forecast:

```sh
node scripts/export-bundle.mjs local .darkspace-local/runs/RUN_ID/forecast.json
npm run build:local
npm run preview:local
```

Open **http://127.0.0.1:4174/** for recording. Output is `.darkspace-local/site/`, which is ignored and must never be deployed. Local gallery cards require anonymised display summaries; the exporter does not copy original titles/taglines into display cards. A local forecast without a validated backtest keeps that backtest pending.

The organizer has not approved public deployment of gallery-derived summaries. Until that changes, the public demo remains fixtures only.

## Companion

The organizer approved the installable companion. Its one-question-at-a-time interview and protected hand-off are retained. The loader prefers the locally installed real forecast, so the public fixture is not passed off as a real crowd forecast.

Run it yourself in a local interactive terminal:

```sh
npm run assets:placement
node packages/core/src/companion.ts /absolute/path/to/your-project
```

It reads the learner profile locally and writes only `darkspace-output/HANDOFF.md`, refusing protected paths, symlinks and overwrite. It does not write in `devpost/` or edit Skill Pack files. Bring the hand-off into your own `2-scope` brain dump.

## Safety and checks

```sh
git config core.hooksPath .githooks
python3 scripts/check-data-safety.py --tracked --staged
python3 scripts/check-data-safety.py --history
npm test
npm run check:core
npm run check:web
uv run pytest -q
uv run ruff check darkspace tests scripts
```

The hook blocks real-data paths, SQLite files, archives, recordings, unreviewed media, entrant project URLs and known gallery wording fingerprints. Fingerprints store hashes, not wording. Repeat the full history scan immediately before the first push. No push was performed during the cleanup.

The original real development corpus was removed from history after the user was notified. [The audit](devpost/research/data-boundary-audit.md) records exact paths and commit mapping without reproducing entrant wording.

## Planning and provenance

- [Scope](devpost/scope.md)
- [Product behavior](devpost/prd.md)
- [Technical specification](devpost/spec.md)
- [Verified build slices](devpost/checklist.md)
- [Offline app map](devpost/app-map.html)

The actual model-generation path uses four pinned families, recorded in `configs/current-event.json`. Personal placement shares one BGE-small q8 WASM contract across browser and terminal. No current Build With AI: Basics gallery is collected, and no fixture or retrospective generation is presented as a historically timestamped forecast.

New sampling under the updated data policy uses `configs/freeze-local-policy.json`; the original freeze is retained for replay of the archived run. Neither access permission nor a sampling run substitutes for the separate real backtest gates.
