# Alternative dataset screening

Checked 2026-10-21 (Asia/Kolkata). Research notes, not an approved evaluation protocol. No model forecasts, judge labels, coverage scores, or GO verdict exist.

## Authorized direction

The learner authorized both an alternative past-event dataset and a forecast-first POC while they request Devpost data access. This changes the original dependency on a Devpost backtest reveal. Scope, PRD, and spec approval still precede product code.

## Civic Hack DC 2025 — usable development candidate

- Organizer: Civic Tech DC.
- Event: July 26, 2025.
- The organizer archive lists 13 project summaries and problem tracks. It says original problem briefs are archived. These counts describe the archive, not verified eligible evaluation rows.
- The root license covers documentation and creative assets under CC BY 4.0; source code is MIT unless a subfolder says otherwise. Check overrides on any extracted source. Preserve required attribution with the corpus; anonymized display cards do not replace license compliance.
- This is a small, specialized civic-data event, not a representative sample of beginner AI hackathons. It can support development and an explicitly exploratory check; it cannot establish general forecast accuracy.
- The archive was assembled after the event. Establish the pre-event provenance and exact version of the brief before claiming a historical forecast.

Sources:
- [Organizer archive](https://github.com/civictechdc/hackdc2025)
- [License at its July 28, 2025 commit](https://github.com/civictechdc/hackdc2025/blob/a329f71cf3d7f2cc6904c8d210dd51bb65a3d134/LICENSE)

## GovHack 2025 — holdout candidate, not yet approved for collection

- Official event dates: August 29–31, 2025.
- The official rules and FAQ require submitted content other than code/data to carry CC BY licensing. Code/data must permit reuse and redistribution. Verify historical applicability and any record-level notices before extraction; the current rules page has been modified since the event.
- The challenge index identifies Digital Confidence: Tools for Safe Online Participation and lists 21 team entries. This is a candidate subset, not the whole event and not a verified corpus denominator.
- A project can enter up to five challenges. Any corpus needs deduplication; overlapping entries are not independent projects.
- The Hackerspace robots.txt URL returned HTTP 404. This is neither a stated prohibition nor an affirmative access grant. Collection policy and any platform terms remain to be checked before bulk retrieval. A reusable text license alone does not establish permission for every access method.
- No individual GovHack project pages have been fetched. Keep project text out of protocol and prompt tuning if this event is selected for held-out evaluation.

Sources:
- [Event dates](https://govhack.org/)
- [Competition rules](https://govhack.org/hackers/competition-rules/)
- [Competition FAQ](https://govhack.org/hackers/competition-faqs/)
- [Challenge index](https://hackerspace.govhack.org/challenges)
- [Candidate challenge](https://hackerspace.govhack.org/challenges/digital_confidence_tools_for_safe_online_participation)
- [Robots check](https://hackerspace.govhack.org/robots.txt)

## Model cutoff feasibility

The official Qwen2.5 announcement is dated September 18, 2024, before either candidate event. It includes 7B models. This establishes an available model family, not a frozen weight revision. Exact model and quantization digests, release provenance, normalization/judge models, additional families, and all generation settings belong in the approved protocol. Do not substitute a newer fine-tune based only on a family name.

Source: [Qwen2.5 announcement](https://qwenlm.github.io/blog/qwen2.5/).

## Other sources screened

- NASA Space Apps: the retrieved official terms apply to 2026, with an event start of November 14, 2026, which is still in the future on the research date. They do not establish the terms for a completed 2025 event. Do not apply them retroactively.
- Swiss E-Collecting Hackathon: organizer overview for October 31–November 1, 2025, has an original guidelines link and team roster. Team-license scope, pre-event brief version, completeness, and non-English evaluation remain unresolved; not selected.
- Hackwinnerdb: a curator advertises CC BY 4.0 data, but the collection focuses on winners. A winners-only denominator would change the scientific question. Not selected for crowd coverage.

Sources: [NASA current terms](https://www.spaceappschallenge.org/legal/), [Swiss organizer overview](https://github.com/swiss/e-collecting-hackathon), [Hackwinnerdb](https://github.com/notsointresting/hackwinnerdb).

## Exposure log

Discovery is exploratory. Search engines returned some entrant snippets even when the query asked only for metadata. The Civic Hack DC README exposed its project summaries, and the Swiss overview exposed team titles. NASA search returned a 2025 project excerpt. None of these can be described as an untouched holdout for this planning session. GovHack discovery so far exposed briefs and an advertised entry count, not project descriptions. No results-based event selection has occurred because no model scores have been computed.

## Before an evaluation run

Verify licensing and authorized collection, event membership and completeness, and a genuine pre-event brief. Separate development from the test corpus. Freeze model revisions, prompts, sample budgets, controls, matching rule, judge checks, error accounting, metrics, and stopping rules before scoring. Keep generated outputs and real submissions labeled separately. Do not use a small event or a narrow challenge to claim general prediction of hackathon entrants.
