# 0007. One thin pipeline module per Bronze table, one shared function

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #12, restructured in #16 and #20)

## Context

Bronze ingests 4 of Meridian Health's 14 in-scope tables so far, and the
rest will follow. Every table goes through the same steps: build the landing
path, read the CSV, add provenance columns, and write to Delta. The options
considered:

- **One module looping over a table registry.** Compact, but one table can't
  be run or debugged on its own without extra flags.
- **A fully standalone copy of the logic per table.** Each table is
  independent, but a fix has to be made in every copy, and the copies drift.
- **A thin entry point per table that calls one shared function.**

## Decision

Each table has its own module, `src/meridian_health/bronze/pipelines/<table>.py`,
which sets the batch date and calls one shared function,
`run_bronze_pipeline()` in `src/bronze_ingestion.py`, with its table name.
That function does all the work for every table. Each table has a matching
schema module under `schemas/`, and table names are constants in
`src/config.py`.

## Consequences

- Any table can be run on its own:
  `uv run python -m src.meridian_health.bronze.pipelines.encounters`.
- A change to ingestion is made once and applies to every table.
- Every table is ingested identically. A table that needs different
  handling needs a new parameter or its own function.
- One entry point per table lines up with one Airflow task per table, once
  the DAG is built. Until then, each module hardcodes its batch date.
