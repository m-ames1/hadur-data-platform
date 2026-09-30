# 0008. Commit a sample batch so the repository runs on clone

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #21 and #22)

## Context

`data/` is gitignored, so a fresh clone had no landing data. `setup.sh`
failed building the landing catalog, and nothing could run until someone
generated a Synthea batch themselves. The options considered:

- **Let `setup.sh` skip the catalog build when there's no data.** The clone
  stops failing, but still can't run anything.
- **Require generating a batch first.** Makes a separate tool a
  prerequisite before the repository does anything at all.
- **Commit a small, real batch.**

## Decision

Commit a 10-patient batch under `sample_data/landing_zone/`, carved from a
full Synthea export by `scripts/build_sample_batch.py`. The cohort is
selected by patient and cascaded through every table, so foreign keys
resolve, and the output is deterministic. `setup.sh` copies it into
`data/landing_zone/` only when no landing data exists.

## Consequences

- The repository runs end to end on clone: 437 encounters, 216 conditions,
  and 2,731 observations.
- About 3 MB of sample data lives in version control.
- A developer's own landing data is never overwritten.
- The sample has to be regenerated if the landing layout changes.
