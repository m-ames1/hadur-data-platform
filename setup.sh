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

# Seed the landing zone from the committed sample batch on a fresh clone.
# Real batches are gitignored, so an existing data/landing_zone belongs to the
# developer and is never overwritten.
shopt -s nullglob
landing_batches=(data/landing_zone/*/*/)
shopt -u nullglob

if (( ${#landing_batches[@]} == 0 )); then
    mkdir -p data
    cp -R sample_data/landing_zone data/
    echo "Landing zone seeded from sample_data/ (10-patient sample batch)."
else
    echo "Existing landing-zone data found; left untouched."
fi

mkdir -p catalog

if duckdb hadur.duckdb -init setup/schema_landing.sql -no-stdin; then
    echo "Landing catalog built under catalog/."
else
    rm -f catalog/landing.duckdb catalog/bronze.duckdb
    echo "Catalog build failed; removed the partial catalogs." >&2
    exit 1
fi

echo
echo "Setup complete. Next:"
echo "  uv run python -m src.meridian_health.bronze.pipelines.encounters"
echo "  duckdb hadur.duckdb -init setup/schema_bronze.sql -no-stdin"
echo "  duckdb hadur.duckdb -init setup/attach.sql"
