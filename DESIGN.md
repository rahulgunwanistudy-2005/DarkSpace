# DarkSpace visual theme

The theme-pass verification below predates the organizer data-boundary migration. The current public build uses labelled sample data; real runs and recordings stay local. Current migration evidence is recorded in `devpost/research/data-boundary-audit.md` and the checklist.

Reference: [AI Agent SaaS Landing Page Design by Ridoy Rock](https://dribbble.com/shots/27146559-AI-Agent-SaaS-Landing-Page-Design), inspected in the browser on 26 October 2026, including its full landing-page artwork. Firecrawl capture was unavailable because the connected account had no credits.

## Reference evidence

The artwork combines black sections, subdued green mountain scenery, white serif display headings, compact sans-serif interface text, lime action buttons with inset icon tiles, rounded navigation, and quiet hairline panel borders. Dribbble publishes palette values including #030302, #457B23, #565A55, #73BA43, #9EF839, and #D8D9D8. The precise fonts and CSS dimensions are unavailable from the flattened artwork.

## Implementation choices

- Ground #030302; raised surface #0d100b; border #292e23; primary text #e8ebe3; secondary text #a2aa98; lime #c8fa83. The surface and lime variants are visual interpretations of the artwork, not extracted CSS.
- Georgia for editorial headings and the primary measurement; existing locally bundled IBM Plex Sans for controls and content, Plex Mono for provenance and timing. No external font requests.
- Rounded navigation and input controls, 18–22px panel corners, thin olive borders, restrained shadows, and generous left-aligned spacing. These dimensions are implementation estimates.
- Desktop: top navigation, forecast introduction, wide map and right results panel, persistent idea input. Mobile: map above the results, with a fixed accessible idea input. Methods uses the same navigation and editorial typography.
- The original locally stored generated mountain photograph interprets the reference's atmosphere; it is decorative scenery, not a data visualization. Actual map points, labels, and measurements remain provided by existing artifacts. No third-party logos or image requests.

## Scope and review

Retain all placement, interview, persistence, worker, loading, error, sample, and export behavior. Do not add marketing sections, invented metrics, accounts, or fake controls. Preserve explicit fixture and pending-evidence notices. Check desktop and mobile views, panel and map controls, keyboard operation, reduced motion, and production build. The reference supplies no mobile or interaction specification; responsive behavior is adapted for DarkSpace.

## Local image asset

Built-in image generation produced `web/static/images/mountain-valley.webp` (optimized WebP). Final prompt: “A wide cinematic photograph of a remote, steep, moss-green mountain valley with dark rock cliffs on the left, layered distant mountains, low fog and overcast grey olive sky; uncluttered center for an overlaid data visualization; natural moss and grass texture, muted olive, charcoal and sage mist, low contrast, deep lower shadows. No people, buildings, signage, text, logos, UI, data points or watermarks.” The image is decorative and contains no evidence or application data.

## Verification

- Frontend check: 0 errors, 0 warnings; production build passes.
- Existing core suite: 11 tests pass; core TypeScript check passes.
- Browser review: 1440×900 desktop, 390×844 phone, and 768×1024 tablet. Map browse, zoom, panel close/reopen, sample selection, Methods navigation, and horizontal-overflow checks pass.
- Real local model workflow passes on desktop and phone using explicitly synthetic fixture data: placement, answer, rewrite, re-placement, exact draft recovery, early stop, and hand-off download. No external requests or page errors occurred.
- Existing reactive forecast state could not be copied into a Worker message. The only application-script adjustment converts it with `$state.snapshot(run)` at that frontend boundary. Worker, engine, measurement, interview rules, and storage/export logic are unchanged.
- No production forecast artifact is installed in this checkout. Normal entry retains the actual unavailable-data disclosure; the preview's explicit `?fixture=engineering` mode is labeled synthetic and remains disabled in production.
- No commits created.
