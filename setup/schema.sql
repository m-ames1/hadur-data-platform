-- =============================================================================
-- Hadur Data Platform — DuckDB schema definitions
--
-- Run from the project root:
--     duckdb hadur.duckdb -init setup/schema.sql
--
-- Creates one view per raw source table for the purely raw data, over the CSVs landed under
-- data/landing_zone/all/raw/<date>/csv/. This is a read-only local querying setup — it does not
-- copy or transform any data, only exposes what's already on disk as SQL.
-- 
-- Provider views will be created per provider specific raw source table, over the CSVs landed under
-- data/landing_zone/<provider_name>/*/.csv
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
--                       every batch under data/landing_zone/all/raw/*/csv/ at once.
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

-- All raw data
CREATE OR REPLACE VIEW raw_allergies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/allergies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_careplans AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/careplans.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_claims_transactions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/claims_transactions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_claims AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/claims.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_conditions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/conditions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_devices AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/devices.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_encounters AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/encounters.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_imaging_studies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/imaging_studies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_immunizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/immunizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_medications AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/medications.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_observations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/observations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_organizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/organizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_patients AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/patients.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_payer_transitions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/payer_transitions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_payers AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/payers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_procedures AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/procedures.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_providers AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/providers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW raw_supplies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/supplies.csv', all_varchar=true, filename=true, union_by_name=true);


-- Meridian Health raw data
CREATE OR REPLACE VIEW meridian_health_raw_allergies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/allergies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_careplans AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/careplans.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_conditions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/conditions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_devices AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/devices.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_encounters AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/encounters.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_imaging_studies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/imaging_studies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_immunizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/immunizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_medications AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/medications.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_observations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/observations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_organizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/organizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_patients AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/patients.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_procedures AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/procedures.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_providers AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/providers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW meridian_health_raw_supplies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/supplies.csv', all_varchar=true, filename=true, union_by_name=true);
