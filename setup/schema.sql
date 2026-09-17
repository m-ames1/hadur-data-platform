-- =============================================================================
-- Hadur Data Platform — DuckDB schema definitions
--
-- Run from the project root:
--     duckdb hadur.duckdb -init setup/schema.sql
--
-- Creates one view per raw source table, over the CSVs landed under
-- data/raw/<date>/csv/. This is a read-only local querying setup — it does not
-- copy or transform any data, only exposes what's already on disk as SQL.
--
-- Why the raw views are built the way they are:
--
--   all_varchar=true   reads every column as text, so nothing is silently
--                       coerced or reinterpreted. Mirrors how a staging
--                       layer should behave — land raw, cast deliberately
--                       downstream, and let cast failures surface as findings
--                       instead of being hidden by inference.
--
--   filename=true       adds a `filename` column recording which dated batch
--                       each row came from, since the glob below reads across
--                       every batch under data/raw/*/csv/ at once.
--
--   union_by_name=true  aligns columns by name rather than position across
--                       batches, so a provider schema change in a later batch
--                       doesn't silently misalign into the wrong columns.
--
-- Bronze/Silver/Gold views are added here once each stage's ingestion code
-- exists and has actually written data to query — not before.
-- =============================================================================


INSTALL delta;
LOAD delta;

-- Raw data
CREATE OR REPLACE VIEW raw_allergies AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/allergies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_careplans AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/careplans.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_claims_transactions AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/claims_transactions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_claims AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/claims.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_conditions AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/conditions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_devices AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/devices.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_encounters AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/encounters.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_imaging_studies AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/imaging_studies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_immunizations AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/immunizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_medications AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/medications.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_observations AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/observations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_organizations AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/organizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_patients AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/patients.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_payer_transitions AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/payer_transitions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_payers AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/payers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_procedures AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/procedures.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_providers AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/providers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_supplies AS
    SELECT *
    FROM read_csv_auto('data/raw/*/csv/supplies.csv', all_varchar=true, filename=true, union_by_name=true);
