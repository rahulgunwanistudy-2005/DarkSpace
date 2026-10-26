---
doc: prd
status: approved
---

# DarkSpace — Product Requirements

A working instrument for hackathon builders to inspect model convergence, place their own kernel, and explore shared defaults through questions answered in their own words.

Source: `scope.md > The Unique Kernel`, `Who It's For`, and `The Core Loop`.

Rahul approved this product definition on October 26, 2026. Technical choices and the frozen evaluation protocol belong in `4-spec`. Approval records intended behavior, not completed implementation or evaluation.

## The Core Journey

Source: `scope.md > What "Working" Looks Like`.

1. Open directly on the retrospective backtest reveal. In the first 10–15 seconds, see a previous event's brief and forecast cards matching real anonymized projects, with measured event coverage and control coverage beside one another.
2. By 30 seconds, reach this hackathon's forecast map and see its densest constellations named. The historical real-project dots leave the map; a corner label offers an optional replay. The current map is explicitly labeled as forecasts, not real entries.
3. By 60 seconds, enter an idea in one sentence, see it placed, inspect crowding and shared defaults with their actual frequencies, and read the first question about knowledge the builder brings that a model would not.
4. Open a default as a question or use the start button. Answer in the builder's own words, rewrite the one-line idea, and re-place it. Watch the point travel along a visible trail and compare before/after percentiles; the next question then opens. Each common default is asked once, up to five questions; the builder may skip or stop at any time.
5. End with the point's complete trail and one hand-off file containing nearby crowded clusters, defaults avoided and their frequencies, exact answers, and the idea and percentile before/after. Direct the builder to take the file to `2-scope`: it is a better starting point, not a finished scope.

Before input, a sample idea is already placed. No account, installation, or visitor setup is required.

## Screens and Layout

Source: the learner's layout answer; `scope.md > The Core Loop` and `What "Working" Looks Like`.

- **One continuous surface:** no tabs. The reveal's cards become historical points; those real-project points then fade, pull away to one side, and shrink into a corner summary as the current forecast becomes the active map. The user experiences a state change rather than a page change.
- **Current map:** fills the screen edge to edge with the forecast for Build With AI: Basics only, named dense constellations, and black empty space. Its title reads: “Forecast for this hackathon. These are not real entries.” Forecast ideas are soft, hollow rings. There are no solid project dots on this map; the only solid point is the builder's green idea. Hover shows an anonymized card.
- **Historical replay:** the corner label reads `Last event: {real_project_count} real projects, {matched_count} matched by the forecast`, using actual run counts. Clicking it restores the historical proof in a distinct color with its own event label. It is off by default. Replaying the same proof means showing the historical real projects with that event's own forecast; it must not overlay them on the current event's forecast or imply cross-event matches.
- **Idea line:** a single-line command bar docked at the bottom, prefilled with the sample idea. Submit a one-sentence kernel with Enter.
- **Placement:** the kernel drops in as a green point, the camera eases into its neighborhood, and the destination cluster lights up with its name. A panel slides in from the right, occupying about a third of the width.
- **Panel:** a large density percentile at the top; shared defaults below, each with its measured frequency, ordered most common first. The same panel hosts the interview and before/after comparison.
- **Phone:** the map occupies the top half, the panel becomes a bottom sheet, and the idea line remains pinned above the sheet.
- **Methods:** a small link in the corner. This is the only separate page; all other navigation changes the map or panel state.

There is no marketing landing page.

## Look and Feel

Source: the learner's design answer on October 26, 2026; `scope.md > Inspiration & Identity`.

- **Feeling:** “a quiet instrument in a dark room.” Precise, calm, and a bit cold, like a scope or star chart where the only light is the data.
- **Ground and space:** near-black base, generous negative space and spacing, clear hierarchy. Empty regions stay black. Dense clusters glow faintly.
- **Signal:** one vivid green accent for matched projects, the builder's kernel, and the coverage number. Darker greens provide secondary emphasis.
- **Supporting text:** neutral grey and visually subdued. Subdued styling must still meet the contrast requirements in `CLAUDE.md`.
- **Possible secondary marker:** burgundy may be used sparingly for crowded regions; this is optional, not a second dominant accent.
- **Data as proof:** metrics establish credibility through real results. Every displayed number traces to a run artifact. The example “72% of this cluster: auto-generated quiz” is not a measured result.
- **Type:** clear hierarchy is established; a font has not been selected. Follow the display-face exclusions in `CLAUDE.md` when choosing it in the technical plan.
- **Excluded structure:** no hero with a CTA, feature cards, or pricing-style sections. “It opens straight on the backtest reveal, because this is a product and not a pitch.”

The design must also respect reduced motion, keyboard access, and WCAG AA contrast as required by `CLAUDE.md`.

## Features and Behavior

### Backtest Reveal

Source: `scope.md > What "Working" Looks Like` and `The POC Boundary`.

- Show the previous event's brief, anonymized real projects, and matching forecast cards.
- Reveal actual matches and update the coverage counter from those matches.
- Keep control coverage beside event coverage so the gap is visible.
- Show the measured results even if the gap is weak, absent, or reversed.
- Disclose that this is a retrospective backtest generated using models released before the event; forecasts generated now must not be represented as historically timestamped predictions.
- The backtest ships precomputed with the repository. No invented numbers may replace unavailable evaluation artifacts.
- On transition to the current hackathon, remove all past-event real-project points from the active map and retain a clickable corner summary. Its real-project count and match count must agree with the reveal and source artifact. “123” in the learner's example is conditional on the eventual corpus actually containing 123 eligible projects.
- The optional historical replay repeats the same real-versus-forecast proof with solid dots for real projects, hollow rings for forecasts, a distinct replay color, and the historical event clearly labeled. It must not represent past projects as current submissions.

### Forecast Map and Kernel Placement

Source: `scope.md > The Core Loop` and `What "Working" Looks Like`.

- Map actual multi-model samples for the current hackathon brief.
- The default map contains only this event's forecast and the builder's kernel. Display the explicit forecast-only title. Never collect this hackathon's gallery or imply the forecast knows its real entries.
- Name dense constellations and display a placed sample idea before the builder types.
- Accept a one-sentence idea and show its placement, crowding, and the shared defaults that explain that placement, each with a measured frequency.
- On Enter, place the kernel in green, ease into its neighborhood, highlight the cluster name, and open the right panel. Display the density percentile prominently and sort defaults by descending frequency.
- Hovering a point shows an anonymized card. Provide keyboard access to the same information under `CLAUDE.md`'s accessibility requirement.
- Describe the map as sampled-model convergence. It does not establish what real entrants will build.
- Point shape reinforces source identity: real projects are solid dots, forecast ideas are soft hollow rings, and the builder's kernel is green and solid. Preserve this distinction in the historical replay as well as the current-event state.

### Placement Progress, Recovery, and Demo Mode

- During placement, show the actual active step and an elapsed-time timer. The learner's examples are reading the idea, finding nearby ideas, and measuring crowding; display a step only when the real operation is running. A spinner alone is insufficient.
- Keep the map interactive for panning and hover while work runs. Keep the builder's sentence untouched in the command bar and provide Cancel.
- On failure, state the actual cause in plain words and explain an available action. Distinguish an unavailable model, timeout, and input too short to place rather than showing a raw status code as the explanation. Input validation thresholds belong in the technical plan.
- Preserve the builder's sentence on failure and cancellation. Let them fix it and press Enter again.
- Next to the failure message, offer Try again, Edit my idea, and Use a sample idea when the live part is unavailable. Do not silently replace the builder's sentence.
- The deployed demo works without a backend. When live placement is off, say so directly and offer saved sample ideas. The learner's example message is: “live placing is off in this demo, here are saved sample ideas”. Do not imply arbitrary input has been placed in this mode.
- Require an explicit sample choice. Mark every sample result “sample” on screen and keep it distinct from a result for the builder's own idea. Preserve access to their original sentence.
- If only part of placement succeeds, show what is available, identify what is missing, and count the missing or failed parts. For example, neighbors may be available while defaults are not. Missing defaults or density must not be invented or presented as successful output.

### Defaults Interview

Source: `scope.md > The Core Loop` and `The POC Boundary`.

- Ask about the shared defaults around the builder's idea and the knowledge they bring.
- Preserve the builder's own answers and authorship.
- Clicking a default or pressing the start button turns that default row into a question with a text box. Ask one question at a time.
- After an answer, make the bottom idea line editable. The builder rewrites the idea in their own words and re-places it; do not generate the rewrite for them.
- Show the point's journey to the new position as a visible trail, and show before/after percentiles in the panel. Open the next question after re-placement.
- Ask each common default once, with “common” meaning more than half the cluster exhibits it. Keep the existing most-common-first ordering and cap the session at five questions, the upper end of the learner's requested four-to-five limit. The cap takes precedence if more defaults qualify; do not keep extending the session with new defaults after re-placement.
- Each question can be answered or explicitly skipped. The builder can stop at any time. A skipped question must not become a generated answer or be counted as an avoided default.
- Finish when the selected common defaults have each been answered or skipped, the cap is reached, or the builder stops. Never finish because a percentile is “high enough.”
- Measure the actual change even if density does not improve. If the idea barely moves or remains equally/more crowded, state that plainly. Do not present a high percentile as the user's goal or a successful completion condition.
- Completion leaves the full start-to-finish point trail visible as the final scene, with the hand-off available and a direction to bring it into `2-scope`. No score, badge, or claim that the idea is finished.
- Follow the established calm, precise voice and plain language. Questions stay grounded in shared defaults and the builder's knowledge, without suggested answers; do not reward a higher percentile with congratulatory copy.

### Hand-off Contents

The learner's final deliverable is one hand-off file, available after completion or stopping early. It contains:

- Crowded clusters near the idea.
- Defaults actually avoided, with their measured frequencies. Do not equate answering or skipping a question with avoiding its default.
- The builder's answers exactly as typed, without paraphrasing or rewriting. Distinguish skipped questions from answers.
- The builder's idea before and after, with the measured percentile before and after.

Use actual successful placement results; never invent a final measurement for an unplaced rewrite. The hand-off informs the builder's `2-scope` brain dump and must not author the scope for them.

### Navigation and Keyboard Controls

- The map is always home; only the panel changes during placement and the interview.
- Esc closes the panel and returns to the plain map.
- `/` focuses the idea line.
- Arrow keys navigate the defaults.
- The corner Methods link opens the only separate page. Returning from it must preserve the current work rather than restart the interview; ordinary return navigation is a small implementation assumption for review.

### Methods and Limitations

Source: `scope.md > What "Working" Looks Like`, `CLAUDE.md > Scientific honesty (non-negotiable)` and `Data and ethics`, and the session's truth gate.

- Explain the actual run's method and limitations in plain language, with event identity and retrospective timing clear.
- Show the same coverage and control figures as the reveal, with their run provenance. Identify the actual models here, while keeping model names anonymized as A/B/C/D on the main surface as required by `CLAUDE.md`.
- Describe the actual frozen evaluation, judge checks, and known failures from its artifacts; do not imply validation that has not occurred. The exact protocol will be decided in `4-spec`.
- Explain that the current map is a forecast from sampled models, and that density movement is not a measure of idea quality or winning probability.
- State whether personal placement is available on the device or the visitor is using saved samples. Describe local-only saving and its limits consistently with the main surface.

### Local Recovery, Privacy, and Forgetting

- No accounts, server-side personal history, or cloud sync. Personal idea text and interview answers stay on the user's device; do not send them to hosted inference, Colab, Kaggle, analytics, logs, or other remote services. Public forecast generation may use authorized cloud compute without receiving personal ideas or answers.
- Remember only the idea sentence, interview answers including half-typed drafts, current question/progress, and last placement in the user's browser on their own device. Save the placement's forecast-run identity with it. Keep enough associated local state to recover the current interview without changing the recorded answers or measurements.
- On return, offer “continue where you left off” so the visitor does not need to retype their work. This return-state exception takes precedence over replaying the first-visit reveal.
- Provide a small “forget this idea” button that clears all locally saved personal state in one click. Do not clear unrelated browser data. An exported hand-off is a separate file owned by the user; the browser reset does not remove it.
- Compare the saved placement's run identity with the active forecast before displaying its numbers as current. If the forecast has changed, preserve the text and answers, withhold the old percentile as a current result, and say: “this was placed on an older forecast, place again”. Offer one-click re-placement, subject to actual on-device placement availability and the explicit demo-mode fallback above. Never silently recompute or relabel an old measurement.
- If storage is blocked, unavailable, or cleared, the product still works and starts fresh without an error. A private session must not require durable storage or promise that it will survive closing the session.
- Say plainly that work is saved on this device only and clearing browser data removes it. The downloaded hand-off, initiated by the user, is the durable record; do not imply browser recovery is a backup.

### Companion Skill and Hand-off

Source: `scope.md > The Core Loop`, `The POC Boundary`, and `Companion Eligibility and Fallback`.

- Run after `1-start` and before `2-scope`, reading the learner profile's starting idea.
- Place the idea, show shared defaults, and interview in the terminal using open questions one at a time with no suggested answers.
- Write one hand-off outside `devpost/`, listing nearby crowded clusters, defaults avoided, and the builder's own answers; tell the builder to bring it into their `2-scope` brain dump.
- Follow the same bounded, user-controlled interview and hand-off contents above. The hand-off includes existing before/after placement measurements; the skill does not introduce its own scoring system.
- Never write anything in `devpost/` or edit Skill Pack files. Do not include backtest execution, map UI, or scoring in the skill.
- Implementation is provisionally authorized. If organizers reject the integration, remove the skill and retain a manual hand-off step.

## States and Boundaries

- **First use:** actual backtest reveal on entry and a sample idea already placed when the map is reached; no blank initial experience.
- **Event transition:** past real-project points leave the map and become the corner summary. The current event's forecast-only title is visible; historical replay is off by default.
- **Skipped or stopped interview:** preserve actual answers and placement history, mark skips distinctly, and allow the hand-off without requiring all five questions.
- **Completion:** show the point's full trail and hand-off; explain honestly if little movement occurred. Percentile is a result, not the goal.
- **Placement in progress:** real active step, elapsed timer, Cancel, interactive map, and unchanged input.
- **Placement canceled or failed:** retain the sentence; state the specific problem and recovery actions. A cancellation or failure is not a successful new placement.
- **Live placement off:** explicit demo-mode disclosure and saved sample options. An explicit sample selection produces visibly labeled sample results; never claim they are the builder's placement.
- **Partial placement:** retain valid results, disclose and count missing components, and never fabricate replacements.
- **Unavailable evaluation artifacts:** never substitute fabricated backtest numbers. The approved scope requires reporting an unsupported or weak reveal before building UI around it.
- **Return visit with saved work:** offer to continue with the saved sentence, exact answers and drafts, question progress, and the last placement from its identified forecast run.
- **Forecast changed since saving:** preserve authored content, identify the older forecast, and offer re-placement. Do not present the saved percentile as current.
- **Storage unavailable or cleared:** start fresh without breaking the product or raising an error.
- **Forget this idea:** clear all of this idea's locally saved work in one click; leave unrelated site data and user-downloaded files alone.

## Product Decisions

- Direct entry to proof rather than a marketing page — the learner wants a product experience.
- Green carries the signal while black and grey preserve focus and empty space — the map's empty regions are central to the name.
- A sample idea appears before input — the builder should immediately understand the interaction.
- The skill remains thin while the web demo remains the product — the learner wants to limit what the skill can break.
- Keep the reveal, map, placement, defaults, and interview on one continuous surface with no tabs — the learner wants a change in state rather than a perceived page change.
- Use a right panel on desktop and bottom sheet on phones, with a persistently accessible idea line.
- The builder rewrites and re-places after each answer; a visible trail and before/after percentile make the measured movement inspectable.
- Separate past-event evidence from the current-event forecast, with explicit event labels and solid-versus-hollow point shapes — the learner wants to prevent any suggestion that the forecast already knows this event's real entries.
- End by common-default coverage, a five-question cap, or the builder's choice to stop — a percentile target would encourage gaming rather than adding the builder's own knowledge.
- Preserve exact answers and supply one hand-off rather than a score or badge — the builder still does the scoping.
- Show real progress and preserve input across waiting, cancellation, failure, and explicit sample fallback — the learner wants control without losing their words.
- Disclose unavailable live placement and label samples — passing saved results off as the builder's idea would misrepresent the demo.
- Surface and count partial failures rather than hiding incomplete output.
- Persist only the current work on the user's own device, with one-click forgetting — there is no account or server identity to remember.
- Tie saved measurements to their exact forecast run and require explicit re-placement after a forecast update — every displayed number must retain its provenance.
- Treat the user-downloaded hand-off as the durable output; browser data can disappear and is not a backup.

## What We're Building

The retrospective backtest reveal, current-event forecast map, placement and defaults interview, and provisional terminal companion within the approved scope. All displayed measurements must come from actual artifacts.

## Deferred From the POC

Using Devpost's own gallery remains conditional on data access. An alternative authorized event is allowed. No candidate dataset or hardware probe establishes evaluation success.

## Non-Goals

- Accounts or a visitor setup flow.
- Marketing landing-page, feature-card, or pricing-section structure.
- Generated user answers or automated scope authorship.
- Backtest execution, map UI, or scoring inside the companion skill.
- Claims of real-entrant prediction beyond the evidence of an actual evaluation.
- Collecting the Build With AI: Basics gallery or presenting past-event projects as this event's entries.
- Interview completion thresholds based on density percentile, badges, or claims that a high percentile makes an idea better.
- Silently substituting sample placements for the builder's own idea, simulating backend progress, or inventing missing results.
- Uploading personal ideas or answers to remote inference or other services, server-side personal history, accounts, or cloud sync.
- Presenting saved percentiles from an older forecast as current, or promising durable recovery from private/blocked/cleared storage.

## Acceptance Criteria

These formalize the learner's examples and decisions above; they are requirements, not a claim that verification has run.

- The opening reveal shows real artifact-backed matches and coverage/control, identifies retrospective timing, and uses actual corpus counts.
- The transition removes historical projects from the current map; the forecast-only title, hollow rings, and opt-in separately labeled historical replay preserve event identity.
- A sample idea is already placed. Enter on an available personal-placement path produces the builder's green point, neighborhood, percentile, and frequency-sorted defaults; unavailable live placement is disclosed instead.
- The desktop panel, phone bottom sheet, persistent idea line, hover/keyboard access, Esc, `/`, and default navigation behave as specified.
- Each majority-shared default is asked once, up to five questions; answer, skip, and stop are available, and completion never depends on reaching a percentile target.
- Answer/rewrite/re-place preserves the builder's words and shows the actual trail and measured before/after result, including no improvement.
- Placement shows actual active steps and elapsed time; Cancel preserves input. Specific errors offer recovery. Partial results disclose and count missing components.
- Explicit sample selection is required for fallback; all sample results remain visibly labeled and are never represented as placements of the visitor's own sentence.
- The hand-off contains the specified clusters, frequencies, exact answers, and before/after idea and measured percentile. It can be obtained after stopping early and points to `2-scope` without writing the scope.
- Recovery restores authored content and progress locally. “Forget this idea” clears it; unavailable storage starts fresh without an error.
- A changed forecast invalidates presentation of the stored placement as current, without erasing authored content; explicit re-placement is offered.
- Personal ideas and answers do not leave the device. Methods states the actual run, models, limitations, sample/live mode, and local-only saving truthfully.

## Open Questions

No unanswered interview question remains for this draft's core journey. Ordinary return navigation from Methods is labeled above as an implementation assumption for review.

`4-spec` must resolve how personal placement stays on-device, what supported-device limits it has, and how unavailable on-device placement uses the disclosed sample fallback. Do not retain a remote personal-placement design from the kit if it conflicts with the local-only requirement. Exact fonts, thresholds, model revisions, sample budgets, and the frozen evaluation protocol also belong there.

Organizer confirmation and authorized evaluation data remain external conditions tracked in the scope. Their absence must not be concealed by the product. These conditions are not evidence of a successful evaluation or a completed build.
