---
name: dark-space
description: Place an existing learner idea among Dark Space's saved model forecasts and run a local own-words interview between 1-start and 2-scope, producing a hand-off for scoping.
---

# Dark Space companion

Run after `1-start` has created `devpost/learner-profile.md`, before `2-scope`. This informs the learner's scoping; it never scopes for them.

Locate the DarkSpace repository and check that `web/static/data/current.json` exists. Explain that this is a model forecast, not actual hackathon entries or validated entrant prediction. The learner reports organizer approval for this companion. Its local interview and protected hand-off boundary stay in place. It reads the local recording forecast when installed; it does not present the public fixture as a real forecast.

Give the learner this command to run themselves in their local interactive terminal, replacing the two paths with the actual repository and learner project paths:

```sh
cd /path/to/DarkSpace
node packages/core/src/companion.ts /path/to/learner-project
```

The repository requires its declared Node version, installed npm dependencies and verified placement assets (`npm ci`, then `npm run assets:placement`). These setup commands use only public code/model assets. The web demo requires no setup.

The runner reads the starting idea directly from the local profile. Do not read that profile or their answers into a hosted agent's context, pipe this command into captured tool output, or ask them to paste their private words here. Let them interact locally. It shows nearby clusters and measured default frequencies, asks one open question at a time, accepts only their own words, and supports skipping or stopping. No suggested answers, automatic rewrites, quality score, map, or backtest execution.

It writes only `darkspace-output/HANDOFF.md` in the learner project, refuses protected/symlink paths and refuses to overwrite an existing hand-off. It never edits anything in `devpost/`, any installed skill, or the Skill Pack. Tell the learner to bring their hand-off into the `2-scope` brain dump. Do not continue into scoping without their request.
