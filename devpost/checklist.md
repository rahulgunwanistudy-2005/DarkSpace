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

## Organizer Ruling — Ordered Migration

This user-authorized migration is the active build order before resuming the remaining original slices. Rahul directed applying the already-stated permissions without a repeated interview. Earlier unchecked boxes are retained honestly; they are not silently marked complete. Scope, PRD and spec carry the exact supplied ruling and its revision basis.

- [x] **6. Remove gallery material from publication paths and install a safety gate**
  Becomes usable: The source tree and Git history exclude the real development corpus; staged/tracked checks block recurrence.
  Why now: Data handling must be safe before another bundle or commit.
  PRD ref: `prd.md > Organizer Ruling — Data Boundary Revision`.
  Spec ref: `spec.md > Data Boundary Implementation`.
  Build: Audit, local quarantine, announced history cleanup, ignore rules, nonverbatim fingerprints and pre-commit/history checks.
  Verify (mechanical): Full Git object scan, isolated staging rejection tests, strict types/lint and original artifact hashes unchanged.
  Learner check: Inspect the audit and exact commit mapping; no entrant wording is copied into the report.
  Commit: `fix: keep gallery material out of source and history`

- [x] **7. Build separate fixture and local recording exports**
  Becomes usable: The public app and tests consume made-up gallery/forecasts labelled sample data; local recording output stays ignored.
  Why now: Public behavior must obey the ruling before real-data collection tools are exposed.
  PRD ref: `prd.md > Organizer Ruling — Data Boundary Revision`, `Backtest Reveal`.
  Spec ref: `spec.md > Data Boundary Implementation`.
  Build: `data/fixtures/`, `configs/fixture.yaml`, deterministic fixture pipeline, explicit export modes and aggregate-only summary. Preserve actual run bytes.
  Verify (mechanical): Fixture run, byte-identical repeat, public/local export rejection tests, core/web checks and build.
  Learner check: Every public card says sample data; the local recording build identifies its different provenance.
  Commit: `feat: separate fixture demo and local recording bundles`

- [ ] **8. Fetch the permitted corpus locally with provenance**
  Becomes usable: `darkspace corpus fetch` collects the permitted gallery locally, respecting robots and the minimum request interval.
  Why now: A safe local destination and export boundary exist first.
  PRD ref: `prd.md > Organizer Ruling — Data Boundary Revision`.
  Spec ref: `spec.md > Data Boundary Implementation`.
  Build: Restricted host/redirect handling, rate limiter, robots check, pagination, provenance and counted failures. README reproduction instructions.
  Verify (mechanical): Deterministic transport tests for robots denial, redirects, interval, parse failures, duplicates and local path boundaries; no live entrant collection is required for these tests.
  Learner check: Follow the documented local command; collected wording never appears in Git or the public build.
  Commit: `feat: add local-only authorized gallery fetch`

- [ ] **9. Verify the full fixture journey and publication boundary**
  Becomes usable: A checked public fixture build, preserved local recording route, CI and refreshed app map.
  Why now: Completes the migration using actual mechanical and browser evidence.
  PRD ref: `prd.md > Acceptance Criteria`, `Organizer Ruling — Data Boundary Revision`.
  Spec ref: `spec.md > Verification and Build Order`, `Data Boundary Implementation`.
  Build: Fixture CI, smoke checks, final safety/history scan and truthful documentation. Companion implementation remains unchanged.
  Verify (mechanical): Python/core/web checks, production build, Playwright smoke through Cua, desktop/phone screenshots, companion protected-path tests and pre-push scan.
  Learner check: Inspect sample labels and the downloaded hand-off; no real backtest accuracy is implied.
  Commit: `test: verify fixture-only demo and local data boundary`

- Migration slice 6 verified and committed as `254ccdf`: 2 safety tests passed, strict types/lint passed, 64 tracked/staged files had zero violations, and the sanitized full-object history scan found zero violations across 125 blobs. The pre-commit hook is active. Original corpus is absent from reachable history and its former blob is no longer present.

- Migration slice 7 verified and committed as `2cca881`: 8 made-up projects, 16 forecasts and 16 controls; fixture coverage/control both 6/8, lift 0, CI [-50, 50] retained. Both production builds passed. 14 Node tests, 12 Python tests, strict engine types and Svelte checks passed. Browser inspection confirmed all eight sample card labels and private placement. The companion workflow/output protection remains; only its source resolution follows the local bundle boundary.
