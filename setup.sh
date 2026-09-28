#!/usr/bin/env bash
set -euo pipefail

echo "Setting up hadur-data-platform..."

for tool in uv duckdb; do
    if ! command -v "$tool" &> /dev/null; then
        echo "$tool not found. See README.md for installation links." >&2
        exit 1
    fi
done

uv sync
echo "Python dependencies installed (uv sync)."

uv run pre-commit install
echo "Pre-commit hooks installed."

# schema_landing.sql defines views over CSV globs and binds those paths at
# CREATE VIEW time, so it aborts on the first missing path. Check for data
# before invoking it, to keep "no data yet" distinct from a real SQL error.
shopt -s nullglob
landing_batches=(data/landing_zone/*/*/)
shopt -u nullglob

if (( ${#landing_batches[@]} == 0 )); then
    echo "No landing-zone data found — skipping catalog build."
    echo "Place a Synthea batch under data/landing_zone/<provider>/<batch_date>/,"
    echo "then re-run ./setup.sh."
else
    mkdir -p catalog
    if duckdb hadur.duckdb -init setup/schema_landing.sql -no-stdin; then
        echo "Landing catalog built under catalog/."
    else
        rm -f catalog/landing.duckdb catalog/bronze.duckdb
        echo "Catalog build failed; removed the partial catalogs." >&2
        exit 1
    fi
fi

echo "Setup complete."
