# Data boundary audit — October 27, 2026

Audit preceded changes. No real gallery wording is reproduced here.

## Findings

- `data/development/civic-hack-dc-2025.json` contained 13 entrant descriptions and 13 project URLs from the licensed development archive. It was introduced in `d556c261e65c16b1b7a1d4296574181fd49c38c8`.
- `data/development/literal-codebook-v1-assignments.json` held derived project identifiers and was untracked.
- No collected learn-ai.devpost.com corpus or Devpost software URLs were found.
- Three reachable commits and 67 unique reachable blobs were inspected. The full object scan covered 144 blobs, including 77 additional stored blobs; no additional corpus wording was found.
- The reconstructed completion cache contained 385 public-sampling rows, with zero known entrant-text matches. The type-check cache also had no matches.
- Four screenshots were reviewed: one synthetic interface fixture and three generated-forecast views. None showed real gallery entrants. No recordings or archives were found. No per-project match artifact existed.
- No real coverage, control, lift or CI artifact existed. The 383 valid model ideas were a forecast count, not coverage. Original run bytes and protocol were preserved locally.

## Local cleanup

The user was told before the rewrite. Commit `d556c261e65c16b1b7a1d4296574181fd49c38c8` became `f5d5ed4d6fb6fbfa868b526eda35f9c9b857e61a`; the preceding two commits were unchanged. Application snapshot trees were sanitized too. No push was performed. A recovery copy exists outside the repository, and the local cleanup receipt records its path.

The corpus and derived identifiers are quarantined under ignored `.darkspace-local/corpora/`. Original generated runs, protocol bytes and screenshots are also local. The public deployment will use only the made-up fixture bundle. Hash-only fingerprints support recurrence checks without storing entrant wording in this report or policy.

The remote advertised no published refs at audit time. The final pre-push history check is required again immediately before any publication.
