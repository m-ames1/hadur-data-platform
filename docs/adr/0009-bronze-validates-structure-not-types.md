# 0009. Bronze validates structure, not types

- **Status:** Accepted
- **Date:** 2026-11-10 (implemented in #35)

## Context

Bronze is the first persisted copy of provider data. Validating there catches
broken deliveries early, but every check Bronze applies also changes what
Bronze stores: a value that fails is no longer kept as delivered. Typing in
particular is lossy — read as numbers, ZIP `02134` becomes `2134.0` and codes
lose leading zeros — and a value that won't cast (`"not a number"` in a cost
column) is a cleaning question, not a delivery error.

## Decision

Bronze keeps provider data exactly as delivered, plus `_`-prefixed provenance
columns. Each table's Pandera schema is the provider's **data contract**:

- Landing files are read with every column as a string (`dtype=str`).
- Every schema field is `Series[str]`; there is no `coerce`.
- `strict = True`: the columns must match exactly — no missing, extra or
  renamed columns.
- Required columns and nullable columns are enforced per the data contract
  with the data supplier

Typing, format checks and cleaning belong to Silver.

## Consequences

- Bronze is a faithful copy of the source; nothing is lost to type inference.
- Validation never changes data. Schema tests assert that a valid frame comes
  back unchanged.
- Bad values reach Silver, which must cast deliberately and handle failures.
- Changing a Bronze column's type requires rebuilding the table: batch-scoped
  overwrites (ADR 0006) replace rows, not a Delta table's schema.
