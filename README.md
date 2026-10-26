# Dark Space

See where sampled models converge before committing to a hackathon idea. Place your own sentence privately, examine shared defaults, and carry your own answers into scoping.

## Current status

The technical approach is selected. The placement/interview core and shared on-device embedding path are implemented, and the frozen public sampler is verified. Actual current-event sampling is running on the authorized Colab GPU. The web app and validated historical backtest are not complete. No entrant-prediction claim has been demonstrated. Synthetic fixtures below verify arithmetic and state handling only.

## Run the verified core

Requires Node 24.19 or later.

```sh
npm ci
npm test
npm run check:core
npm run fixture
```

The last command writes `darkspace-output/FIXTURE-HANDOFF.md`, clearly marked synthetic. It contains declared fixture sentences, not your personal idea or any model forecast. Personal outputs are excluded from Git.

Verify the real private embedding path separately:

```sh
npm run assets:placement
npm run verify:embedding
```

The first command downloads approximately 46 MB of pinned model/runtime assets if they are absent. Assets are checked by hash. The verification uses a declared synthetic sentence; it proves engineering behavior, not semantic accuracy. The installed tokenizer uses a patched image dependency even though this application processes text only.

## Public sampling

```sh
uv sync --locked --python 3.12
uv run pytest -q
uv run ruff check darkspace tests scripts
uv run mypy --strict darkspace
uv run darkspace sample --config configs/current-event.json
```

Sampling needs the four pinned models in a loopback Ollama runtime. `configs/freeze-current.json` checks exact public prompts, configuration and source inputs before any call. Public setup scripts are in `scripts/colab_bootstrap.py` and `scripts/colab_pull.py`; use the authorized notebook for public data only. The browser and terminal private path never send personal inputs there. Cache-only reruns make zero new model calls. The sampler counts invalid output, repair attempts and provider failures instead of silently replacing draws.

## Approach and evidence

The planned static app reads precomputed public forecast/evaluation artifacts. Personal placement runs on-device; browser and terminal share one WASM embedding/placement contract. No personal inference server, accounts or analytics.

- [Approved scope](devpost/scope.md)
- [Approved product behavior](devpost/prd.md)
- [Selected technical specification](devpost/spec.md)
- [Build progress](devpost/checklist.md)
- [Architecture comparison and measured probe](devpost/research/architecture-decision.md)
- [Historical dataset access and exposure ledger](devpost/research/dataset-screening.md)

The model probe measured engineering feasibility on eight synthetic desktop sentences. It does not establish semantic placement accuracy, phone performance, judge reliability or historical coverage. Those have separate gates in the spec. No Devpost gallery is collected without permission, and the current event's gallery is never collected.
