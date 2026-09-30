# Architecture Decision Records

Each file records one significant decision about how this system is built:
the context, the decision, and its consequences, including what was rejected.
`CHANGELOG.md` says what changed; these say why the system is shaped the way
it is.

## Rules

- Files are numbered sequentially and never renumbered: `NNNN-short-title.md`
- An ADR is written in the same PR that implements the decision. Decisions
  that aren't built yet don't get an ADR yet
- Accepted ADRs are never edited. To change a decision, write a new ADR and
  set the old one's status to `Superseded by NNNN`
- Only decisions about the system's shape belong here. Workflow rules
  (branching, versioning, CI) live in [CONTRIBUTING.md](../../CONTRIBUTING.md)

## Format

Each ADR has a status, a date, and three sections: **Context** (the problem
and the options), **Decision** (what was chosen), and **Consequences** (what
follows from it, good and bad).

## Index

| # | Decision | Status |
|---|---|---|
| [0001](0001-record-architecture-decisions.md) | Record architecture decisions | Accepted |
| [0002](0002-medallion-layers-on-delta-lake.md) | Store medallion layers as Delta tables via delta-rs | Accepted |
| [0003](0003-pandas-for-v1-pyspark-reserved-for-v2.md) | Use pandas for v1 transforms, reserve PySpark for v2 | Accepted |
| [0004](0004-supplier-code-isolated-under-src-supplier.md) | Isolate provider-specific code under `src/<provider>/` | Accepted |
| [0005](0005-duckdb-catalog-per-layer-schema-per-provider.md) | One DuckDB catalog per layer, one schema per provider | Accepted |
| [0006](0006-idempotent-bronze-writes-by-batch-date.md) | Make Bronze writes idempotent per batch | Accepted |
| [0007](0007-one-pipeline-module-per-bronze-table.md) | One thin pipeline module per Bronze table, one shared function | Accepted |
| [0008](0008-committed-sample-batch-for-run-on-clone.md) | Commit a sample batch so the repository runs on clone | Accepted |
