#!/usr/bin/env bash
set -euo pipefail

echo "Setting up hadur-data-platform..."

if ! command -v uv &> /dev/null; then
    echo "uv not found. Install it: https://docs.astral.sh/uv/getting-started/installation/" >&2
    exit 1
fi

uv sync
echo "Python dependencies installed (uv sync)."

uv run pre-commit install
echo "Pre-commit hooks installed."

if ! command -v duckdb &> /dev/null; then
    echo "duckdb not found. Install it: https://duckdb.org/docs/installation" >&2
    exit 1
fi

duckdb hadur.duckdb -init setup/schema.sql
echo "hadur.duckdb built from setup/schema.sql."

echo "Setup complete."
