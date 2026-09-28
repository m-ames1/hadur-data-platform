# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.1.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added

### Changed

### Deprecated

### Removed

### Fixed

### Security

## [0.5.0] - 2026-09-28

### Added

- A committed 10-patient sample batch under `sample_data/`, so the
  repository runs end to end on clone without generating data first —
  437 encounters, 216 conditions, 2,731 observations, roughly 3 MB.
- `scripts/build_sample_batch.py`, which carves that sample from a full
  Synthea export. The cohort is selected by patient and cascaded through
  every table, so foreign keys resolve and the sample supports the same
  joins as a full batch. Output is deterministic, so re-running it
  produces no spurious diffs.

### Changed

- `setup.sh` seeds `data/landing_zone/` from `sample_data/` when no
  landing-zone data is present, and leaves existing data untouched.
- README Quick Start rewritten around the sample batch.

### Known limitations

- The Meridian Health slice is still an unfiltered copy of the full
  Synthea export rather than an organization-filtered slice. The sampler
  mirrors that and will need updating once the filter lands.
- `claims`, `claims_transactions` and `payer_transitions` are row-capped
  at 2,000 rows in the sample. They are out of scope for every layer and
  exist only so the `landing.synthea` views resolve.
- Schema validation still isn't wired into the write path across any
  table. Quarantine handling remains unimplemented.
- The Airflow DAG is still absent; pipelines run as standalone scripts.

## [0.4.1] - 2026-09-28

### Removed

- `setup/schema.sql`, split into `setup/schema_landing.sql` (landing
  views plus both catalog attachments) and `setup/schema_bronze.sql`
  (Bronze views). The two have different preconditions: landing views
  need only raw CSVs, while Bronze views bind to Delta paths at
  `CREATE VIEW` time and cannot exist before the first pipeline run.

### Fixed

- `setup/attach.sql` no longer fails on a fresh clone. It attaches
  `catalog/bronze.duckdb` READ_ONLY, which cannot create a missing file,
  so the entire session aborted — including landing queries — before any
  Bronze data existed. `schema_landing.sql` now creates that catalog
  with an empty schema at setup time.
- `setup.sh` no longer reports a genuine SQL failure as "no landing-zone
  data found"; the two cases are distinguished before DuckDB runs.
- `setup.sh` removes partially-built catalogs on a failed build, rather
  than leaving an empty one that `attach.sql` would silently open.

## [0.4.0] - 2026-09-28

### Added

- Bronze ingestion for the Meridian Health `observations` table, via
  `observations_pipeline.py`, using the same shared
  `run_bronze_pipeline()` path as the other three tables.
- An `ObservationsSchema` placeholder in `schemas.py` — fields-less,
  same pattern as the other stubs, so the pending schema work is
  visible rather than absent.
- A skipped test stub for the pending `ObservationsSchema` tests in
  `test_schemas.py`.

### Known limitations

- `ObservationsSchema` has no columns declared yet — validation isn't
  enforced for observations, same as the other three tables.
- `observations` has no `Id` column and, unlike `conditions`, no
  reliable natural key at all — its composite key
  (`PATIENT` + `ENCOUNTER` + `CODE` + `DATE`) repeats for roughly 250
  rows. Dedup logic here can't assume any column combination is
  unique — Silver-layer work, not part of this release.
- Schema validation still isn't wired into the write path at all
  across any table. Quarantine handling remains unimplemented.
- All four tables planned for this first onboarding batch are now
  ingested (`encounters`, `patients`, `conditions`, `observations`) —
  the next table onboarded starts a new batch.

## [0.3.0] - 2026-09-27

### Added

- Bronze ingestion for the Meridian Health `conditions` table, via
  `conditions_pipeline.py`, using the same shared `run_bronze_pipeline()`
  path as `encounters` and `patients`.
- A `ConditionsSchema` placeholder in `schemas.py` — fields-less, same as
  `PatientsSchema`, so the pending schema work is visible rather than
  absent.
- A skipped test stub for the pending `ConditionsSchema` tests in
  `test_schemas.py`.

### Known limitations

- `ConditionsSchema` has no columns declared yet — validation isn't
  enforced for conditions, same as encounters and patients.
- `conditions` has no `Id` column; it's unique only by a composite key
  (`PATIENT` + `ENCOUNTER` + `CODE` + date). Dedup on that key isn't
  implemented yet — that's Silver-layer work, not part of this release.
- Schema validation still isn't wired into the write path at all across
  any table. Quarantine handling remains unimplemented.
- Only 3 of 14 planned Meridian Health tables are now ingested
  (`encounters`, `patients`, `conditions`).

## [0.2.0] - 2026-09-27

### Added

- Bronze ingestion for the Meridian Health `patients` table, using the same
  generalized `run_bronze_pipeline()` path as `encounters`.
- `run_bronze_pipeline()` generalized to accept `provider` and `table_name`
  parameters instead of being hardcoded to `encounters`, so the same
  read -> add-metadata -> write mechanics work for any table.
- A `PatientsSchema` placeholder in `schemas.py` — declared with no fields
  yet, so it rejects any real data outright until built out. Marks the
  pending schema work as acknowledged rather than absent.
- Skipped test stubs for the pending `PatientsSchema` tests and for a
  `run_bronze_pipeline()` integration test, so both are visible in the test
  suite rather than silently missing.

### Changed

- DuckDB tables are now addressed as `<layer>.<provider>.<table>` (e.g.
  `bronze.meridian_health.encounters`) instead of flat prefixed view names
  (`meridian_health_bronze_encounters`). Each medallion layer is a separate
  catalog file under `catalog/`, with one schema per provider. Sessions attach
  the layer catalogs via `duckdb hadur.duckdb -init setup/attach.sql`.

### Known limitations

- `PatientsSchema` has no columns declared yet — validation isn't enforced
  for patients, same as `encounters`.
- Schema validation still isn't wired into the write path at all; both
  tables write unvalidated rows to Bronze. Quarantine handling remains
  unimplemented.
- `encounters`' own pipeline file hasn't been updated to use the new shared
  `run_bronze_pipeline()` yet — that refactor ships as its own release
  immediately after this one.
- Only 2 of the 14 planned Meridian Health tables are now ingested
  (`encounters`, `patients`).

## [0.1.0] - 2026-09-27

### Added

- Bronze ingestion for the Meridian Health `encounters` table: reads the dated
  landing-zone CSV, stamps provenance columns, and writes a Delta table
  partitioned by `_batch_date`. Re-running a batch overwrites only that batch's
  partition, so retries do not duplicate rows.
- Reusable ingestion helpers (`build_landing_file_path`, `add_metadata_columns`,
  `build_bronze_table_path`, `write_to_bronze`) intended to be shared by every
  supplier pipeline, not just Meridian Health.
- Provenance columns stamped onto every Bronze row: `_source_file`,
  `_ingested_at` (UTC) and `_batch_date`.
- Data-zone path configuration, with the data root overridable via the
  `HADUR_DATA_ROOT` environment variable.
- A Pandera schema definition for the Bronze `encounters` table, configured to
  coerce declared types and reject undeclared columns. Not yet applied during
  ingestion — see Known limitations.
- DuckDB views over the Synthea raw extracts, the Meridian Health raw subset, and
  the Bronze `encounters` Delta table, for ad-hoc querying during development.
- A custom Airflow image that installs the project and its runtime dependencies.
- pytest with coverage reporting, plus unit tests for the path builders, the
  provenance-column transformation and the `encounters` schema.
- Background documentation for the Meridian Health supplier.

### Changed

- Raw Synthea extracts now live under the landing zone at
  `data/landing_zone/all/raw/<date>/csv/`, moved from `data/raw/<date>/csv/`, with
  the DuckDB raw views repointed. Existing local data must be moved to match.
- Docker Compose now builds the project's own Airflow image instead of pulling the
  stock `apache/airflow` image. Run `docker compose build` before starting the
  stack.

### Known limitations

- The `encounters` schema is defined but not yet applied — the pipeline writes
  unvalidated rows.
- Quarantine handling for rejected rows is not implemented.
- Batch-level idempotency in `write_to_bronze` is implemented but not yet covered
  by tests.
- The Airflow DAG is a stub; the pipeline runs as a script during development.
  Scheduled execution ships as its own later release — onboarding a provider and
  automating that provider are deliberately separate units of work.
- Only `encounters` of the 14 planned Meridian Health tables is ingested.
