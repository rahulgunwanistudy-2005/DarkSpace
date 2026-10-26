# CLAUDE.md: standing rules for Dark Space

Copy this file into the project root right after `1-start` finishes. It must not be there before: 1-start's folder check stops if the folder already has another project in it.

## Precedence
1. The Devpost Learn Skill Pack's SKILL.md files govern process: interviews, approvals, authorship, slice commits, and the ban on writing submission copy. Where anything below conflicts with them on process, the SKILL.md wins.
2. This file governs the quality bar and engineering standards.
3. `devpost/scope.md`, `prd.md` and `spec.md`, once approved, govern what gets built. Do not build anything they do not contain. Changes go through the Skill Pack's revision flow.

## Authorship
- I (Rahul) supply the ideas and decisions. Never answer an interview question for me. Never pre-fill a planning doc from background notes. Never draft my Devpost copy, video narration or Discord posts.
- When I ask for a recommendation, give one, with its main reason and trade-off. `kit/02-TECH-BLUEPRINT.md` is the default technical recommendation, not a decision already made.

## Engineering bar
- Python 3.12 with uv; `ruff` and `mypy --strict` on the engine package. TypeScript strict on the frontend.
- Every pipeline stage is a pure function over typed inputs (pydantic models), with I/O at the edges. The CLI and the API call the same functions.
- Determinism: fixed seeds and a content-addressed cache. Rerunning the same config is free and produces byte-identical artifacts.
- Every slice ends with mechanical verification I can rerun: a command, a test, or an observed output. Paste the actual output, never "should work."
- No dead code, no TODOs left in committed code, no commented-out blocks.
- Fail loudly. A dropped sample, a parse failure or a judge refusal is counted and surfaced, never silently swallowed.

## Scientific honesty (non-negotiable)
- Match rules, K, thresholds and the judge prompt are written into spec.md and frozen before the backtest touches the precursor gallery. Tune only on the dev event.
- Report the numbers we get. Never round up, cherry-pick, or hide the control result. If the result is weak, stop and tell me before building UI around it.
- Every number shown in the UI traces to an artifact file in `data/runs/<run_id>/`.

## Design bar
- Use the `frontend-design` skill for every UI slice, on top of the Look and Feel I approve in prd.md.
- Banned unless prd.md explicitly asks for them:
  - Inter, Roboto or system-font stacks as the display face.
  - Purple or blue hero gradients.
  - Three-card feature grids.
  - Default shadcn or MUI look.
  - Glassmorphism.
  - Emoji as icons.
  - "Get Started" CTAs.
  - Lorem ipsum.
- Screenshot loop after every UI slice: render with Playwright at 1440x900 and 390x844 and look at both screenshots. Check them against prd.md's Look and Feel and the banned list, fix what fails, then commit.
- Respect `prefers-reduced-motion`. Contrast meets WCAG AA. Every interactive element is keyboard reachable.

## Data and ethics
- Real gallery projects appear in the UI and video as anonymised cards ("Project 47: PRD interview tool"). No entrant names, no avatars, no screenshots of their work.
- No third-party logos or brand marks in the UI. Models are labelled "Model A/B/C/D" in the UI; their real identities go in the methods page and README.
- Collect public pages at one request every 3 seconds or slower, keep source URLs and fetch dates, and honour robots.txt.

## Secrets
- `.env` and `.env.*` are ignored; commit only `.env.example` with placeholders. `devpost/learner-profile.md` stays out of git.
- Before any push, scan tracked files and history for keys and tokens.
