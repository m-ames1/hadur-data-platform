-- =============================================================================
-- Hadur Data Platform — Bronze catalog views
--
-- Run from the project root, after at least one pipeline has written output:
--     duckdb hadur.duckdb -init setup/schema_bronze.sql -no-stdin
--
-- Separate from schema_landing.sql by necessity. These views are defined over
-- Delta tables, and DuckDB binds the path when the view is created, not when
-- it is queried — so delta_scan on a table that hasn't been written yet fails
-- with InvalidTableLocationError and aborts the whole script. The landing
-- catalog has no such dependency, so it builds at setup time and this does not.
--
-- The bronze catalog itself is created by schema_landing.sql, so setup/attach.sql
-- works before this file has ever run. Until then bronze.meridian_health is an
-- empty schema and its tables report as missing, which is accurate.
-- =============================================================================

INSTALL delta;
LOAD delta;

ATTACH IF NOT EXISTS 'catalog/bronze.duckdb' AS bronze;
CREATE SCHEMA IF NOT EXISTS bronze.meridian_health;

CREATE OR REPLACE VIEW bronze.meridian_health.encounters AS
    SELECT *
    FROM delta_scan('data/bronze/meridian_health/encounters/');

CREATE OR REPLACE VIEW bronze.meridian_health.patients AS
    SELECT *
    FROM delta_scan('data/bronze/meridian_health/patients/');

CREATE OR REPLACE VIEW bronze.meridian_health.conditions AS
    SELECT *
    FROM delta_scan('data/bronze/meridian_health/conditions/');

CREATE OR REPLACE VIEW bronze.meridian_health.observations AS
    SELECT *
    FROM delta_scan('data/bronze/meridian_health/observations/');
