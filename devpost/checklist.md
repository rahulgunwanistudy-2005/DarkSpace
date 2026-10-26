---
doc: checklist
status: approved
mode: fast
approval_basis: "Rahul delegated technical selection and proceeding on 2026-10-26; no hands-on checks are claimed completed."
---

# Dark Space — Build Checklist

Build small working slices, verify each, and save a commit. The unique kernel arrives before visual polish. Public data and human labels gate scientific claims rather than being replaced with fixtures.

## Slices

- [x] **1. Place a sentence against a declared fixture and export its exact-word interview**
  Becomes usable: A local command measures a supplied vector against a tiny synthetic forecast, runs a bounded interview state and exports the actual words with provenance.
  Why now: Proves the measurement and authorship rules before investing in the map; bootstraps the shared package in this slice.
  PRD ref: `prd.md > Forecast Map and Kernel Placement`, `Defaults Interview`, `Hand-off Contents`.
  Spec ref: `spec.md > Shared Private Placement`, `Interview, Recovery and Hand-off`.
  Build: Strict typed contracts, original-space neighbors/percentile, partial results, fixed question queue, exact hand-off, fixture-only CLI. Reject incompatible/invalid data.
  Verify (mechanical): `npm test` and `npm run check:core`; cover known arithmetic, duplicate/tie behavior, invalid vectors/contracts, answer/skip/stop/cap, unplaced drafts, exact raw answers and no claimed avoidance without confirmation.
  Learner check: Open the fixture hand-off; inspect words and provenance. It must clearly say synthetic fixture, not a model forecast.
  Commit: `feat: add deterministic local placement and handoff core`

- [ ] **2. Generate a real public forecast with a frozen, counted pipeline**
  Becomes usable: Public model outputs become a reproducible run with neighbors, measured default frequencies and declared failures.
  Why now: The real kernel must exist before a polished map can imply it works.
  PRD ref: `prd.md > Forecast Map and Kernel Placement`, `Methods and Limitations`.
  Spec ref: `spec.md > Public Run and Cache`, `Public Sampling and Defaults`, `Frozen Evaluation Protocol v1`.
  Build: Python contracts, provider/cache, exact prompts and release guards, public run manifest, actual public compute, shared WASM embedding. Conditional historical source gate and blind development label pack; no automated human labels.
  Verify (mechanical): ruff, mypy strict, pytest; cached rerun with identical hashes and zero new calls; actual sampled counts and failures; embedding parity tolerance; access gates reject absent evidence.
  Learner check: Inspect the actual public run and blind-label development pairs locally before looking at judge verdicts. This is the early hands-on checkpoint.
  Commit: `feat: add reproducible public forecast pipeline`

- [ ] **3. Explore the forecast and place an idea privately**
  Becomes usable: One static map, sample already placed, private worker with real progress, cancel, missing-part reporting and explicit sample fallback.
  Why now: It renders real data rather than building a visual claim around fixtures.
  PRD ref: `prd.md > Forecast Map and Kernel Placement`, `Placement Progress, Recovery, and Demo Mode`, `Navigation and Keyboard Controls`.
  Spec ref: `spec.md > Clustering and Map Layout`, `Shared Private Placement`, `Look and Feel`.
  Build: Static SvelteKit, Canvas map, accessible equivalent, self-hosted worker/assets, desktop panel and phone sheet. Apply frontend-design skill.
  Verify (mechanical): Core tests, Svelte check/build; inspect screenshots at 1440×900 and 390×844; actual placement and cancel; private-text canary absent from all requests; sample identity retained.
  Learner check: Type an idea, pan while placement runs, cancel/retry, inspect neighborhood/default counts and sample labels.
  Commit: `feat: add private forecast map and placement worker`

- [ ] **4. Complete the interview, recover work, and use the thin companion**
  Becomes usable: Answers and drafts survive locally; stale forecasts/forget work; one hand-off downloads; terminal path uses the same measurement core.
  Why now: Completes the user's own-words journey on the actual placement behavior.
  PRD ref: `prd.md > Defaults Interview`, `Hand-off Contents`, `Local Recovery, Privacy, and Forgetting`, `Companion Skill and Hand-off`.
  Spec ref: `spec.md > Interview, Recovery and Hand-off`, `Thin Terminal Companion`.
  Build: Fixed queue, exact drafts, successful trail, optional user-confirmed avoidance, local storage, stale-run checks and protected output paths. Apply skill-creator to the companion and frontend-design to visible changes.
  Verify (mechanical): Answer/skip/stop/cap and unchanged density; reload/blocked storage/stale-run/forget race; exact-string hand-off round trip; no writes inside devpost or Skill Pack; screenshots at both required sizes.
  Learner check: Answer and rewrite, reload midway, finish or stop, inspect the downloaded file and final trail.
  Commit: `feat: add recoverable interview and local companion`

- [ ] **5. Present supported evidence and finish the verified demo**
  Becomes usable: Methods and honest evidence entry; real reveal only when authorized data and human judge gates pass; a recordable production build.
  Why now: Proof animation depends on actual measured results, not desired numbers.
  PRD ref: `prd.md > Backtest Reveal`, `Methods and Limitations`, `Acceptance Criteria`.
  Spec ref: `spec.md > Backtest Reveal and Methods`, `Frozen Evaluation Protocol v1`, `Where It Runs and How Someone Tries It`.
  Build: Real historical evaluation if gates pass; otherwise explicit forecast-first pending status. Methods/provenance, keyboard/reduced-motion checks, CI, README local recording, optional hosting configuration. No submission copy.
  Verify (mechanical): Full agreed checks and production start; reveal counters exactly equal artifacts; events separated; no unsupported statistics; screenshots and final network/header/privacy check; secrets audit before any publication.
  Learner check: Try the complete first-minute experience and awkward inputs; report anything broken or misleading.
  Commit: `feat: finish honest evidence flow and production checks`

## Hands-on Checkpoints

- [ ] Early: inspect the real forecast and supply blind development labels after slice 2. Agent labels do not count.
- [ ] Final: try the integrated app and report observations after slice 5.

## Final Review

- [ ] User tried the running app; observations recorded.
- [ ] Agreed fixes verified and committed.
- [ ] Required checks pass; limitations and remaining external conditions reported.
- [ ] User considers the POC ready for submission preparation.

## Code Tour and App Map

- [ ] Connect the frozen judge check to the user's honest-evaluation learning goal using actual results.
- [ ] Produce `devpost/app-map.html` only once screens and flow exist.
- [ ] Record the actual activity and evidence; no invented learning reflection.

## Revisions

- October 26: Rahul explicitly delegated finding and proceeding with the strongest technical approach. Saved the chosen spec and order under that authorization. Original product requirements remain in scope/PRD; human labels, scientific stop rules and final hands-on review are not waived.
- Slice 1 verified and committed as `0395b68`: 10/10 Node tests passed, strict TypeScript passed, fixture hand-off generated with exact words and explicit synthetic provenance. Node's native TypeScript loader required erasable syntax; enabled that check. The installed Skill Pack has an existing trailing blank line in its checklist template; left it unchanged as required, and scoped whitespace verification to project-authored files.
- Slice 2 is in progress. Public sampling and cache/access gates passed 7 Python tests, ruff and strict mypy; frozen before real generation in commit `206f9a5`. Colab supplied a T4 and all four pinned model digests were verified. The notebook's Python 3.13 kernel required an isolated uv Python 3.12 process; protocol source was unchanged. The shared embedding implementation reproduced eight canonical probe vectors exactly on this host, passed input/token/integrity/close checks, and uses 45,881,134 bytes of model/runtime assets. Real forecast export, clustering/defaults and human validation remain unfinished.
