# 0002. Store medallion layers as Delta tables via delta-rs

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #12)

## Context

Each medallion layer needs durable storage that supports writing a batch
atomically and safely replacing a batch when a run is repeated. The options
considered:

- **Bare Parquet files.** Simple and open, but no transactions. A failed
  write can leave partial files behind, and replacing a batch means deleting
  files by hand.
- **A SQL database or warehouse.** Transactional, but adds a server to run
  and moves storage away from open files on disk.
- **Delta Lake tables.** Parquet files plus a transaction log, giving atomic
  writes and scoped overwrites on plain files.

## Decision

Every layer is stored as Delta tables, written from pandas with the
`deltalake` package (delta-rs, the Rust implementation, with no Spark or JVM
required). Each table lives at `data/<layer>/<provider>/<table>/`, for
example `data/bronze/meridian_health/encounters/`.

## Consequences

- Writes are atomic, and a batch can be replaced without touching the rest
  of the table (see [0006](0006-idempotent-bronze-writes-by-batch-date.md)).
- DuckDB reads the tables through its `delta` extension for local querying
  (see [0005](0005-duckdb-catalog-per-layer-schema-per-provider.md)).
- DuckDB binds a Delta path when a view is created, so Bronze views can only
  be built after a pipeline has written that table. This is why
  `setup/schema_bronze.sql` runs separately from setup.
- The storage format carries over to v2 on Databricks, which is Delta-native.
