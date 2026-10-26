# Dark Space

See where sampled models converge before committing to a hackathon idea. Place your sentence privately, examine shared wording, and bring your own answers into scoping.

## Try the app

Requires Node 24.19 or later. No API key or personal inference server is needed.

```sh
npm ci
npm run prepare:web
npm run build
npm run preview:production
```

Open **http://127.0.0.1:4173/**. The saved forecast and a labeled sample appear immediately. The private model downloads from the same site in the background; first-time assets total about 46 MB. Your sentence and answers stay on your device. The terminal companion needs its local asset copy: `npm run assets:placement`.

For development, use `npm run dev`. Development fixtures are available only with an explicit development query and are excluded from the production build.

## Evidence and limits

The actual public run attempted **384 ideas**, 96 from each of four model families. **383 parsed successfully; one was invalid** after one failed repair. There were no provider errors or embedding failures. Kaggle supplied two free T4 GPUs; the run used the frozen prompts, model digests and Ollama 0.40.11. Public sampling received no learner profile, personal idea or interview answer.

HDBSCAN found **five clusters with 122 members**, leaving **261 unclustered ideas**. All 383 ideas remain on the map and in density calculations. Four saved examples are selected by a fixed rule: the first valid sample from each model, without picking for appealing results.

- [Current forecast report](data/runs/4f6cfb90c4cc38756b04814c159bfbc18ca111c8ebc0530067e872b704505383/REPORT.md)
- [Raw counted samples](data/runs/da833e6b1cf8bf6b9348b22e0f6b0d5663eeeaea6dc3b3b64ffaf679aef3e09e/samples.json)
- [Offline replay receipt](data/runs/da833e6b1cf8bf6b9348b22e0f6b0d5663eeeaea6dc3b3b64ffaf679aef3e09e/offline-replay.json)
- [Literal matching rules](configs/default-codebook-v1.json)

The historical backtest, matched control comparison and LLM-judge validation remain **pending**. No entrant-prediction claim, coverage percentage or GO result has been demonstrated. No current-event gallery is collected. The UI states these limits.

Default frequencies measure **explicit wording**, using the public sentence plus its model-supplied mechanism. “Mentions tracking” does not prove that a working tracker exists. Nonmatching text does not prove a feature is absent. The saved rules replaced an exact-text pass that found no majority defaults; the current forecast is therefore exploratory. These are not human-validated semantic labels or a held-out evaluation.

The sampling models are Llama 3.1 8B Instruct, Qwen 2.5 7B Instruct, Mistral 7B Instruct v0.3, and Gemma 3 4B IT, pinned to the digests and release sources in [the configuration](configs/current-event.json). They appear as Models A–D in the product. Placement uses BGE-small-en-v1.5 under [the exact shared WASM contract](packages/core/src/embedding-contract.json).

## Local companion

The companion is optional, between `1-start` and `2-scope`. Organizer eligibility is unresolved; the same command remains usable manually if skill integration is disallowed.

Run it yourself in an interactive local terminal, so private words are not captured in hosted agent output:

```sh
npm run assets:placement
node packages/core/src/companion.ts /absolute/path/to/your-project
```

It reads that project's `devpost/learner-profile.md` locally, asks one open question at a time, and writes `darkspace-output/HANDOFF.md`. It refuses protected paths, symlinks and overwrite. It never edits `devpost/` or Skill Pack files. Bring the hand-off into your own `2-scope` brain dump.

## Verification

```sh
npm test
npm run check:core
npm run check:web
npm run verify:embedding
uv sync --locked --python 3.12
uv run pytest -q
uv run ruff check darkspace tests scripts
PYTHONPATH=. uv run python scripts/replay-public-run.py data/runs/da833e6b1cf8bf6b9348b22e0f6b0d5663eeeaea6dc3b3b64ffaf679aef3e09e/samples.json
```

Analysis has an isolated lock so scientific dependencies do not change the frozen sampler:

```sh
PYTHONPATH=. uv run --script --locked darkspace/analysis.py --input data/runs/da833e6b1cf8bf6b9348b22e0f6b0d5663eeeaea6dc3b3b64ffaf679aef3e09e/analysis-input.json --output /tmp/darkspace-analysis.json
```

For strict Python checks including scientific libraries:

```sh
uv run --with numpy==2.5.4 --with scikit-learn==1.9.1 --with umap-learn==0.5.12 mypy --strict darkspace
```

Cached replay makes zero new model calls and reproduces the raw artifact bytes. The cache can be reconstructed from preserved raw completions; the original cloud SQLite file was not imported. Analysis reruns were byte-identical on this recorded environment; fresh model generation is not guaranteed identical across hardware.

The synthetic fixture command `npm run fixture` verifies arithmetic and state handling only. It is never evidence of model forecasting quality. Personal hand-offs, profiles, credentials, caches and model assets are excluded from Git.

## Project documents

- [Approved scope](devpost/scope.md)
- [Approved product behavior](devpost/prd.md)
- [Selected technical specification](devpost/spec.md)
- [Build and review progress](devpost/checklist.md)
- [Dataset access and exposure ledger](devpost/research/dataset-screening.md)
- [Architecture comparison](devpost/research/architecture-decision.md)

Civic Tech DC's licensed documentation is development material already exposed during planning, not an untouched historical test. Its source, license and fetch record are saved with [the development corpus](data/development/civic-hack-dc-2025.json). Human labels and authorized historical access cannot be replaced with agent-created verdicts.
