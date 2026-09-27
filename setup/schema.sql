-- =============================================================================
-- Hadur Data Platform — DuckDB catalog definitions
--
-- Run from the project root:
--     duckdb hadur.duckdb -init setup/schema.sql -no-stdin
--
-- Layout: one catalog (.duckdb file) per medallion layer under catalog/, one
-- schema per provider inside it, so every table addresses as
-- <layer>.<provider>.<table> — e.g. bronze.meridian_health.encounters.
-- A single DuckDB file offers only two naming levels (schema.table), so the
-- layer has to be a catalog to get three. Mirrors how Unity Catalog and
-- Snowflake medallion warehouses are addressed, and means promoting a table
-- between layers changes one word of a query rather than the whole name.
--
-- Attached READ-WRITE here because this script creates the catalogs. Every
-- other entry point attaches them READ_ONLY — see setup/attach.sql.
--
-- Creates one view per source table. This is a read-only local querying
-- setup — it does not copy or transform any data, only exposes what is
-- already on disk as SQL, so the views never go stale against the files.
--
-- Note: the landing.synthea schema reads from data/landing_zone/all/, not a
-- directory named synthea. `all` is a DuckDB reserved word and would need
-- quoting in every query, so the schema takes the name of what produced the
-- data instead of the directory it sits in.
--
-- Why the raw views are built the way they are:
--
--   all_varchar=true    reads every column as text, so nothing is silently
--                       coerced or reinterpreted. Mirrors how a staging
--                       layer should behave — land raw, cast deliberately
--                       downstream, and let cast failures surface as findings
--                       instead of being hidden by inference.
--
--   filename=true       adds a `filename` column recording which dated batch
--                       each row came from, since the globs below read across
--                       every batch at once.
--
--   union_by_name=true  aligns columns by name rather than position across
--                       batches, so a provider schema change in a later batch
--                       doesn't silently misalign into the wrong columns.
--
-- Silver/Gold catalogs are added here once each stage's ingestion code exists
-- and has actually written data to query — not before.
-- =============================================================================

INSTALL delta;
LOAD delta;

ATTACH IF NOT EXISTS 'catalog/landing.duckdb' AS landing;
ATTACH IF NOT EXISTS 'catalog/bronze.duckdb'  AS bronze;

CREATE SCHEMA IF NOT EXISTS landing.synthea;
CREATE SCHEMA IF NOT EXISTS landing.meridian_health;
CREATE SCHEMA IF NOT EXISTS bronze.meridian_health;


-- =============================================================================
-- landing.synthea — full Synthea output, all providers, before the split
-- =============================================================================

CREATE OR REPLACE VIEW landing.synthea.allergies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/allergies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.careplans AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/careplans.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.claims_transactions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/claims_transactions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.claims AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/claims.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.conditions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/conditions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.devices AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/devices.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.encounters AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/encounters.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.imaging_studies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/imaging_studies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.immunizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/immunizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.medications AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/medications.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.observations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/observations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.organizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/organizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.patients AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/patients.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.payer_transitions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/payer_transitions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.payers AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/payers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.procedures AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/procedures.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.providers AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/providers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.synthea.supplies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/all/raw/*/csv/supplies.csv', all_varchar=true, filename=true, union_by_name=true);


-- =============================================================================
-- landing.meridian_health — Meridian Health's slice of the landing zone
-- =============================================================================

CREATE OR REPLACE VIEW landing.meridian_health.allergies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/allergies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.careplans AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/careplans.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.conditions AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/conditions.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.devices AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/devices.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.encounters AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/encounters.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.imaging_studies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/imaging_studies.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.immunizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/immunizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.medications AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/medications.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.observations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/observations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.organizations AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/organizations.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.patients AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/patients.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.procedures AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/procedures.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.providers AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/providers.csv', all_varchar=true, filename=true, union_by_name=true);

CREATE OR REPLACE VIEW landing.meridian_health.supplies AS
    SELECT *
    FROM read_csv_auto('data/landing_zone/meridian_health/*/supplies.csv', all_varchar=true, filename=true, union_by_name=true);


-- =============================================================================
-- bronze.meridian_health
-- =============================================================================

CREATE OR REPLACE VIEW bronze.meridian_health.encounters AS
    SELECT *
    FROM delta_scan('data/bronze/meridian_health/encounters/');
