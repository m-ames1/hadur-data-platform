# Hadur Data Platform

![Hadúr forging raw data into a trusted data platform](docs/assets/hadur-data-platform-hero.png)

> **From raw ore to trusted data.**

Hadur Data Platform is a data infrastructure project that transforms messy provider data into clean, validated, customer-ready datasets.

The platform follows the same essential rhythm as a blacksmith's forge:

**ingest → refine → test → shape → deliver**

The project demonstrates a provider-to-customer data platform and the engineering discipline required to build one.

## Quick Start

Requires [`uv`](https://docs.astral.sh/uv/), [`duckdb`](https://duckdb.org/docs/installation), and Docker.

```bash
git clone https://github.com/m-ames1/hadur-data-platform.git
cd hadur-data-platform
./setup.sh
```

`setup.sh` installs dependencies, wires up pre-commit, seeds the landing zone from the committed sample batch, and builds the landing catalog. The repository is runnable immediately — no data generation required.

Run the Bronze pipelines:

```bash
uv run python -m src.meridian_health.bronze.pipelines.encounters
uv run python -m src.meridian_health.bronze.pipelines.patients
uv run python -m src.meridian_health.bronze.pipelines.conditions
uv run python -m src.meridian_health.bronze.pipelines.observations
```

Each reads its landing file, stamps provenance columns, and writes a Delta table to `data/bronze/<provider>/<table>`. Writes are idempotent at the batch level — re-running the same batch date replaces that batch rather than duplicating it.

Build the Bronze catalog views over that output, then query:

```bash
duckdb hadur.duckdb -init setup/schema_bronze.sql -no-stdin
duckdb hadur.duckdb -init setup/attach.sql
```

```sql
SELECT count(*) FROM bronze.meridian_health.encounters;  -- 437
SELECT * FROM landing.meridian_health.patients LIMIT 5;
```

`schema_bronze.sql` is a separate step by necessity: its views are defined over Delta tables, and DuckDB resolves those paths when the view is created rather than when it is queried, so they cannot exist before the first pipeline run.

### About the sample data

`sample_data/` holds a committed 10-patient batch — 437 encounters, 216 conditions, 2,731 observations, roughly 3 MB — carved from a full Synthea export by [`scripts/build_sample_batch.py`](scripts/build_sample_batch.py). The cohort is selected by patient and cascaded through every table, so all foreign keys resolve and the sample supports the same joins as a full batch.

It exists so the repository is runnable on clone. To work with a full batch instead, generate one with Synthea, place it under `data/landing_zone/`, and re-run `./setup.sh` — existing landing-zone data is never overwritten.

### Airflow (infrastructure only)

Airflow is provisioned locally via Docker Compose, but **no DAGs are implemented yet** — pipelines currently run as scripts. Orchestration lands in a later release.

```bash
cp .env.example .env
```

Edit `.env` and fill in:
- `AIRFLOW_UID` — output of `id -u`
- `FERNET_KEY` — generate with:
  ```bash
  docker run --rm apache/airflow:3.3.2-python3.12 python -c "from cryptography.fernet import Fernet; print(Fernet.generate_key().decode())"
  ```

```bash
docker compose up
```

- Airflow UI: [http://localhost:8080](http://localhost:8080)

## Why Hadúr?

Hadur Data Platform takes its name from Hadúr, the Hungarian divine blacksmith associated with fire, metallurgy, and the forging of weapons for gods and heroes.

His forge stands in the Copper Forest of the cosmic World Tree. There, raw metal is heated, purified, hammered, and transformed into artifacts of power — including, in legend, the Sword of God (*Isten Kardja*), later discovered by Attila the Hun.

Hadur Data Platform applies that imagery to data engineering. Raw data arrives incomplete, inconsistent, duplicated, and malformed. It has potential, but it is not yet fit for use. The platform supplies the structure, heat, pressure, and quality controls needed to forge it into something trustworthy.

Here, the artifacts are not swords. They are dependable data products.

> **Naming convention:** The platform and repository use the ASCII spelling `Hadur`. The mythological figure is written using the original Hungarian spelling, `Hadúr`.

## The Cosmic Data Forge

1. Raw ore drawn from the earth
2. Hadúr's fire
3. The copper anvil
4. Hammer and tongs
5. Removing impurities
6. Reworking flawed metal
7. Testing the blade
8. Artifacts forged for the gods
9. The Golden Rooster watching the realms
10. The Sword of God

## From Raw Material to Gold

Hadur Data Platform follows the logical stages of the Medallion Architecture.

### Bronze — Raw material

Provider data enters the platform with its original values preserved.

### Silver — The forge

Transformations clean and refine the raw material.

### Gold — Artifacts of power

Validated data is shaped into its final customer-facing form.

## Two Platform Eras

*Details pending.*

## Version 1

### Architecture

*Details pending.*

### Technology Stack

*Details pending.*

## Version 2

### Architecture

*Details pending.*

### Technology Stack

*Details pending.*

## Project Principles

1. **Preserve the raw truth.** Source data should remain traceable and reproducible.
2. **Make bad data visible.** Quarantine records with reasons instead of silently dropping them.
3. **Test before publishing.** Customer-facing outputs must pass an explicit quality gate.
4. **Keep transformations testable and portable.**
5. **Separate orchestration from transformation.**
6. **Design for migration.** The project will migrate from a Version 1 tech stack on small-scale data to a Version 2 tech stack on production-scale data.
7. **Document the reasoning.** Architecture and documentation are first-class project artifacts.

## Current Status

*Details pending.*
