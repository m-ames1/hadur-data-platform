# 0010. Quarantine failing rows in Bronze

- **Status:** Accepted
- **Date:** 2026-11-10 (implemented in #35)

## Context

With validation in the write path (ADR 0009), some rows will fail. Failing the
whole batch for one bad row blocks every good row behind it; dropping bad rows
silently loses data with no record of why.

## Decision

`apply_quarantine_process` validates lazily, collecting every failure in one
pass, then splits by failure type:

- **Row-level failures** (e.g. a null in a required column): failing rows are
  written to `<table>_quarantine`, one row per failed check to
  `<table>_quarantine_failure_cases`, and passing rows to `<table>`.
- **Table-level failures** (missing, extra or renamed column): the batch can't
  be split by row, so the run fails before anything is written.

Quarantine tables are sibling Delta tables in the same Bronze schema
(`bronze.<provider>.<table>_quarantine`). They carry the same provenance
columns as Bronze and are written through `write_to_bronze`, so they share its
batch-scoped overwrite (ADR 0006). Both are written on every validated run —
empty when nothing fails — so a re-run clears that batch's stale quarantine
rows and the table schemas stay stable.

## Consequences

- Good rows load even when some rows fail; every rejected row is kept with its
  reasons.
- Schema drift stops the run loudly rather than producing a partial load.
- The three writes aren't atomic. A failure part-way leaves the tables out of
  step until the batch is re-run, which restores consistency.
- Quarantined rows can't yet be joined to their failure cases; a source line
  number provenance column is planned for that.
- Quarantined rows aren't re-validated on later runs yet.
