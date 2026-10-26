# Dark Space

See where sampled models converge before committing to a hackathon idea. Place your own sentence privately, examine shared defaults, and carry your own answers into scoping.

## Current status

The technical approach is selected and the first placement/interview core is implemented. The web app, real public forecast and validated historical backtest are not complete. No entrant-prediction claim has been demonstrated. Synthetic fixtures below verify arithmetic and state handling only.

## Run the verified core

Requires Node 24.19 or later.

```sh
npm ci
npm test
npm run check:core
npm run fixture
```

The last command writes `darkspace-output/FIXTURE-HANDOFF.md`, clearly marked synthetic. It contains declared fixture sentences, not your personal idea or any model forecast. Personal outputs are excluded from Git.

## Approach and evidence

The planned static app reads precomputed public forecast/evaluation artifacts. Personal placement runs on-device; browser and terminal share one WASM embedding/placement contract. No personal inference server, accounts or analytics.

- [Approved scope](devpost/scope.md)
- [Approved product behavior](devpost/prd.md)
- [Selected technical specification](devpost/spec.md)
- [Build progress](devpost/checklist.md)
- [Architecture comparison and measured probe](devpost/research/architecture-decision.md)
- [Historical dataset access and exposure ledger](devpost/research/dataset-screening.md)

The model probe measured engineering feasibility on eight synthetic desktop sentences. It does not establish semantic placement accuracy, phone performance, judge reliability or historical coverage. Those have separate gates in the spec. No Devpost gallery is collected without permission, and the current event's gallery is never collected.
