-- =============================================================================
-- Hadur Data Platform — attach the layer catalogs
--
-- Run at the start of every DuckDB session, from the project root:
--     duckdb hadur.duckdb -init setup/attach.sql
--
-- Why this file exists at all:
--
--   ATTACH is per-connection session state. The views inside each layer
--   catalog persist in its .duckdb file, but the aliases that make them
--   reachable as `landing` and `bronze` do not — every new connection has to
--   re-attach. So this runs every session, while setup/schema.sql runs once.
--
--   IF NOT EXISTS   makes the file safe to run twice in one session (an init
--                   script plus a .read from a query file, say) instead of
--                   erroring on a duplicate alias.
--
--   READ_ONLY       these catalogs hold only views over data on disk; Bronze
--                   is written as Delta through delta-rs, never through
--                   DuckDB. It also fails loudly on a missing or mistyped
--                   path instead of silently creating an empty catalog and
--                   returning zero rows, which is the failure mode that
--                   wastes an afternoon.
--
--   Relative paths inside the stored views resolve against the process
--   working directory, so sessions must be launched from the project root.
-- =============================================================================

ATTACH IF NOT EXISTS 'catalog/landing.duckdb' AS landing (READ_ONLY);
ATTACH IF NOT EXISTS 'catalog/bronze.duckdb'  AS bronze (READ_ONLY);
