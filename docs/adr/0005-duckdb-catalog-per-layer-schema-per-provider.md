# 0005. One DuckDB catalog per layer, one schema per provider

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #14, split in #21)

## Context

Tables are queried locally through DuckDB, across several layers and,
eventually, several providers. A single DuckDB file only offers two levels of
naming, `schema.table`, so one of the two dimensions has to go somewhere
else. The options considered:

- **Encode it in the view name**, e.g. `bronze_meridian_health_encounters`.
  Works, but the names get long and the structure is only a convention.
- **One catalog per layer, one schema per provider.** Gives real three-level
  names.

## Decision

Each layer is its own DuckDB catalog file under `catalog/`
(`landing.duckdb`, `bronze.duckdb`), and each provider is a schema inside it.
Tables are addressed as `<layer>.<provider>.<table>`:

```sql
SELECT count(*) FROM bronze.meridian_health.encounters;
```

The catalogs hold only views over files on disk. They are built by
`setup/schema_landing.sql` and `setup/schema_bronze.sql`, and attached
read-only in each session by `setup/attach.sql`.

## Consequences

- The address says where a table lives, and a new provider is one
  `CREATE SCHEMA` per layer.
- Querying one layer across providers stays inside one catalog. Querying one
  provider across layers crosses catalogs.
- `ATTACH` isn't persisted, so every session runs `setup/attach.sql`.
- The catalogs are gitignored build artifacts, reproducible from the setup
  scripts, and never go stale, since views read the files at query time.
- Read-only attachment fails loudly on a mistyped path instead of silently
  creating an empty catalog.
