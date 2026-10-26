---
doc: scope
status: approved
---

# DarkSpace

Before a hackathon builder picks an idea, show where sampled models converge, place the builder's kernel, and interview them about shared defaults and less crowded directions.

## The Unique Kernel

Run a hackathon's prompt through several models many times, map the resulting ideas, and use the builder's own answers to explore lower-density regions. The map describes the sampled models; predicting what real entrants build remains an unproven hypothesis until an evaluation supports it.

## Who It's For

A hackathon builder using AI agents who is still choosing an idea and wants to put their own identity into the work.

## The Core Loop

See where sampled models converge, place a kernel, answer questions about its shared defaults, and compare placement as the builder develops the idea in their own words. The precise interaction and stopping point will be defined in the PRD.

“The skill is the front door to Dark Space, and the web demo is still the product.” The companion runs between `1-start` and `2-scope`: it reads the learner profile's starting idea, places it against the forecast, shows the defaults, interviews the builder in the terminal, and writes one hand-off file outside `devpost/`. The builder brings that file into their own `2-scope` brain dump.

## Inspiration & Identity

The learner is concerned that projects become similar when builders use similar agents without putting their own identity into the work. Visual direction has not yet been supplied in the interview; it belongs in the PRD conversation.

## Why This Matters to the Learner

“I want to learn how to evaluate an LLM system honestly”: lock the test before seeing results, include a control prompt, and check an LLM judge against their own labels. They want the numbers to hold up and to recognize when they do not.

## What "Working" Looks Like

The learner defined the following first-minute sequence:

- **First 10–15 seconds:** the previous event's brief appears. Forecast cards land on real, anonymized projects from its gallery. A coverage counter rises as actual matches are revealed, with the control number beside it. “Those numbers come straight from the run, and nothing on screen is made up.”
- **By 30 seconds:** the builder reaches the forecast map for this hackathon, with the densest constellations named.
- **By 60 seconds:** the builder has typed an idea in one sentence and seen it placed in a constellation. They see how crowded the spot is, the defaults that put it there, and each default's measured frequency. They are already reading the first question about what they know that a model would not.
- **Before typing:** a sample idea is already placed. “I shouldn't need an account, a setup step, or a blank screen to get there.”

The requested “72% of this cluster: auto-generated quiz” is an example of the display format, not a measured result or target value.

**Evidence and timing:** this will be a retrospective backtest generated now using frozen model releases that predate the event. The learner's phrase “forecast cards made before that event” is not supported by any timestamped historical forecast artifact; the product must disclose the actual chronology. The map represents sampled models' ideas, not observed entrants or certainty about where entrants will build. The interview can measure movement into lower-density regions while entrant prediction remains unproven beyond whatever an actual backtest supports.

The requested reveal requires an authorized corpus and actual evaluation artifacts. It must show the measured coverage and control even when the gap is weak, absent, or reversed. A favorable gap is not an animation requirement. The forecast-first work can proceed while evaluation access is resolved, but no invented reveal can stand in for missing evidence.

## The POC Boundary

- A map from actual multi-model samples for a hackathon brief.
- Kernel placement and an interview about shared defaults.
- Named dense constellations and measured default frequencies, with a sample idea placed before the builder types.
- Immediate access to the demo without an account, installation, or a setup step for the visitor.
- Measurement of placement in lower-density regions, tied to actual run artifacts.
- A separate evaluation track using another authorized past event with its brief, submissions, and models released before the event. Selection and evaluation rules must be frozen before scoring.
- A thin installable companion skill: terminal placement, shared defaults, open interview questions one at a time without suggested answers, and one hand-off containing nearby crowded clusters, defaults avoided, and the builder's own answers. It reads the learner profile but never writes anything in `devpost/` or edits Skill Pack files. “Dark Space informs my scoping, and I still do the scoping.”
- The backtest ships as precomputed, reproducible artifacts with the repo; the map UI belongs in the web demo. Neither is performed by the companion skill. Precomputed means actual measured outputs, not invented results; those outputs do not exist yet.
- Colab GPUs or Kaggle GPU hours are authorized compute options. A Colab T4 hardware probe succeeded; no forecast or backtest has run.

## Companion Eligibility and Fallback

Organizer confirmation is still required to establish whether the companion fits the event's rules. The learner explicitly said “for now build it,” authorizing provisional implementation within the normal planning/build sequence while eligibility remains unverified. If organizers say no, cut the skill and retain the hand-off file as a manual step. No organizer confirmation has been received or inferred.

## Later

The learner is requesting Devpost data access in parallel. Its backtest reveal can be reconsidered when access is granted and the measured result is available. No Devpost gallery has been collected.

## Explicitly Cut

- Requiring Devpost data access to start the revised work: the learner explicitly authorized an alternative event and a forecast-first POC while they request access.
- Presenting actual-entrant prediction as established in the forecast-first POC: the learner explicitly accepted leaving this unproven.
- Accounts and a visitor setup flow: the learner explicitly requires getting through the first minute without either.
- Backtest execution, map UI, and scoring inside the companion skill: “The skill stays thin so it can't break.” These cuts apply to the skill, not to the web product or separate evaluation track.
- Writing scope or other `devpost/` files, editing Skill Pack files, and generating the builder's interview answers: the companion informs scoping while the builder retains authorship.

## Pending External Conditions

Organizer eligibility and data-access checks remain unresolved. The provisional companion and alternative-data approach above do not imply either external approval has been received.

## Current Evidence

Dataset candidates and limitations are recorded in [dataset-screening.md](research/dataset-screening.md). No measured result or candidate listing constitutes a GO verdict. Rahul approved this scope on October 22, 2026. Approval defines the product boundary; it does not imply a completed evaluation or external permission.
