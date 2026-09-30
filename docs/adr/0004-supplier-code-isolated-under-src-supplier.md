# 0004. Isolate provider-specific code under `src/<provider>/`

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #12)

## Context

v1 onboards one provider, Meridian Health, and more are planned. Each
provider brings its own table scope, data quirks, and schemas. If that logic
mixes with shared code, adding a second provider means untangling the first.

## Decision

Provider-specific code lives in its own package under `src/`. Meridian
Health's is `src/meridian_health/`, which defines
`PROVIDER = "meridian_health"` and holds that provider's pipelines and
schemas. Provider-agnostic code (paths in `src/config.py`, the ingestion path
in `src/bronze_ingestion.py`) takes the provider as a parameter and never
hardcodes one. All providers share one repository.

## Consequences

- Adding a provider means a new package under `src/`, a landing directory at
  `data/landing_zone/<provider>/<batch_date>/`, and a schema in each layer's
  DuckDB catalog (see [0005](0005-duckdb-catalog-per-layer-schema-per-provider.md)).
- Shared code has to stay generic. Provider-specific behavior can't be
  special-cased inside it.
- One repository means one CI pipeline and one version number across all
  providers.
