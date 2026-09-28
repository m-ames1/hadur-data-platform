# Hadur Data Platform

![Hadúr forging raw data into a trusted data platform](docs/assets/hadur-data-platform-hero.png)

> **From raw ore to trusted data.**

[![Python 3.12](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![Version](https://img.shields.io/github/v/tag/m-ames1/hadur-data-platform?sort=semver&filter=v*&label=version&color=orange)](CHANGELOG.md)

Hadur Data Platform is a data infrastructure project that transforms messy provider data into clean, validated, customer-ready datasets.

The platform follows the same essential rhythm as a blacksmith's forge:

**ingest → refine → test → shape → deliver**

The project demonstrates a provider-to-customer data platform and the engineering discipline required to build one: a medallion (Bronze/Silver/Gold) lakehouse built on Delta Lake, orchestrated with Airflow, with schema validation, quarantine handling, and HIPAA Safe Harbor de-identification as first-class concerns rather than afterthoughts.

> **No real patient data.** Every record in this project is synthetic, generated with [Synthea](https://github.com/synthetichealth/synthea). "Meridian Health" is a fictional integrated health system. No real PHI exists in this repository or its pipelines at any layer.

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

Airflow is provisioned locally via Docker Compose, but **no DAGs are implemented yet** — pipelines currently run as scripts. Orchestration lands in a later release (see [Current Status](#current-status)).

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

## Development

```bash
uv run pytest              # run the test suite — no data setup required
uv run pytest --cov=src    # with coverage
uv run ruff check .        # lint
uv run ruff format .       # format
```

Pre-commit hooks run Ruff automatically on staged files. See [CONTRIBUTING.md](CONTRIBUTING.md) for branching, commit, and release conventions.

## Repository Layout

```
├── .github/                          # CODEOWNERS + pull request template
├── src/
│   ├── bronze_ingestion.py           # Shared, provider-agnostic Bronze mechanics
│   ├── config.py                     # Path and table-name constants
│   └── meridian_health/
│       └── bronze/
│           ├── pipelines/            # One runnable entry point per table
│           └── schemas/              # One Pandera schema per table
├── tests/                            # Mirrors the src/ structure
│   ├── test_bronze_ingestion.py
│   └── meridian_health/
│       └── bronze/
│           └── schemas/              # Per-table schema tests
├── scripts/
│   └── build_sample_batch.py         # Carves the committed sample from a full export
├── sample_data/
│   └── landing_zone/
│       ├── all/raw/<batch_date>/csv/ # 10-patient carve of all 18 Synthea tables
│       └── meridian_health/<batch_date>/  # Meridian Health's 14-table provider slice
├── setup/
│   ├── schema_landing.sql            # Landing catalog — built at setup time
│   ├── schema_bronze.sql             # Bronze views — built after first ingestion
│   └── attach.sql                    # Read-only ATTACH for query sessions
├── docs/
│   ├── assets/                       # README imagery
│   ├── raw-data/
│   │   ├── schema/                   # Synthea table reference, grouped by domain
│   │   ├── data-quality/             # Batch data-quality manifest format
│   │   └── synthea-quirks/           # Known source-data quirks
│   └── suppliers/                    # Per-provider scope documents
├── Dockerfile                        # Airflow image with the project installed
├── docker-compose.yaml               # Local Airflow stack
├── setup.sh                          # One-shot local environment bootstrap
├── pyproject.toml                    # Project metadata, dependencies, tool config
├── uv.lock                           # Locked dependency graph
├── requirements.txt                  # Pinned export consumed by the Airflow image build
├── .env.example                      # Template for local Airflow secrets
├── CHANGELOG.md
├── CONTRIBUTING.md
└── LICENSE
```

## Why Hadúr?

Hadur Data Platform takes its name from Hadúr, the Hungarian divine blacksmith associated with fire, metallurgy, and the forging of weapons for gods and heroes.

His forge stands in the Copper Forest of the cosmic World Tree. There, raw metal is heated, purified, hammered, and transformed into artifacts of power — including, in legend, the Sword of God (*Isten Kardja*), later discovered by Attila the Hun.

Hadur Data Platform applies that imagery to data engineering. Raw data arrives incomplete, inconsistent, duplicated, and malformed. It has potential, but it is not yet fit for use. The platform supplies the structure, heat, pressure, and quality controls needed to forge it into something trustworthy.

Here, the artifacts are not swords. They are dependable data products.

> **Naming convention:** The platform and repository use the ASCII spelling `Hadur`. The mythological figure is written using the original Hungarian spelling, `Hadúr`.

## The Cosmic Data Forge

Each stage of the mythological forge maps to a stage of the platform:

| # | The forge | The platform |
|---|-----------|--------------|
| 1 | Raw ore drawn from the earth | The provider's raw batch, exactly as delivered |
| 2 | Hadúr's fire | Ingestion — the batch is picked up and stamped with provenance |
| 3 | The copper anvil | Bronze — original values preserved, immutable per batch |
| 4 | Hammer and tongs | Silver transforms — cleaning, conforming, typing |
| 5 | Removing impurities | De-identification — direct identifiers removed at Bronze → Silver, quasi-identifiers generalized at Silver → Gold |
| 6 | Reworking flawed metal | Quarantine — bad records set aside with reasons, re-validated |
| 7 | Testing the blade | Quality gates — schema and expectation checks before publish |
| 8 | Artifacts forged for the gods | Gold — de-identified, per-provider tables |
| 9 | The Golden Rooster watching the realms | Observability — run monitoring and data-quality metrics |
| 10 | The Sword of God | Delivery — Gold tables joined into the final customer-facing data product |

## From Raw Material to Gold

Hadur Data Platform follows the logical stages of the Medallion Architecture, followed by a final delivery step. Every layer is stored as [Delta Lake](https://delta.io/) tables via [`delta-rs`](https://github.com/delta-io/delta-rs). Bronze, Silver, and Gold are all provider-scoped and addressable in DuckDB as `<layer>.<provider>.<table>`. Tables are only joined, and providers only combined, after Gold.

### Bronze — Raw material

Provider data enters the platform with its original values preserved. Columns are read as strings so that source-level defects survive ingestion instead of being masked by type coercion. Three provenance columns (`_source_file`, `_batch_date`, `_ingested_at`) are stamped onto every row. Writes are idempotent per batch, so a retried run replaces its own batch rather than duplicating it.

### Silver — The forge

Transformations clean and refine the raw material into conformed, per-entity tables, still scoped to their provider (`silver.<provider>.<table>`) and deliberately not joined. This is where defects from the batch manifest get resolved, and where **direct identifiers are removed** on the way in from Bronze: a stable hashed pseudonym key replaces the patient identifier, and the remaining direct identifiers are dropped.

Quasi-identifiers such as exact dates and geography are kept in Silver, where they are still analytically useful.

Records that fail validation are quarantined with a reason rather than silently discarded, and are re-validated on subsequent runs.

### Gold — Artifacts of power

Between Silver and Gold, a dedicated privacy-cleaning step applies [HIPAA Safe Harbor](https://www.hhs.gov/hipaa/for-professionals/privacy/special-topics/de-identification/) (45 CFR § 164.514(b)(2)) treatment to **quasi-identifiers**: birth and death dates are reduced to year, ZIP5 is generalized to ZIP3 subject to the ≥20,000 population threshold, and ages over 89 are bucketed.

Gold keeps the same per-entity, per-provider shape as the layers before it (`gold.<provider>.<table>`) and stays unjoined. **Gold never contains PHI.**

### Delivery — The finished blade

After Gold, a delivery step joins the Gold tables into the final customer-facing output: `delivery.encounter_summary`, one row per encounter. Each entity is reduced to encounter grain *before* joining. Every row carries its `source_provider`, so as more providers are onboarded, their output lands in the same delivered table and can still be told apart.

## Two Platform Eras

The project is built in two deliberate eras, each tagged in git (`airflow-platform-v1`, `databricks-platform-v2`). The point of the split is to demonstrate the same data product on two different stacks, and to make the migration itself part of the work rather than a rewrite that discards the original.

| | Version 1 | Version 2 |
|---|---|---|
| **Scale** | Small-scale, local | Production-scale |
| **Orchestration** | Apache Airflow (Docker Compose) | Databricks Lakeflow |
| **Transform engine** | pandas | PySpark |
| **Storage** | Delta Lake via `delta-rs`, local filesystem | Delta Lake, Unity Catalog |
| **Scope** | One provider's full feed + one external reference asset | The same provider re-implemented, then additional providers |

A possible third era on dbt + Snowflake is deliberately deferred with no target date.

## Version 1

### Architecture

A single Airflow DAG moves one provider's batch through Bronze → Silver → Gold → Delivery on a local Docker stack.

```
Synthea batch (CSV)
        │
        ▼
  data/landing_zone/<provider>/<batch_date>/
        │
        ▼
┌───────────────────────────────────────────┐
│ BRONZE   bronze.<provider>.<table>        │
│          raw values preserved             │
│          + provenance columns             │
│          + Pandera validation             │
│          + quarantine (failures set aside)│
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│ SILVER   silver.<provider>.<table>        │
│          conformed per-entity tables      │
│          + defect resolution              │
│          + direct-identifier removal      │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│ GOLD     gold.<provider>.<table>          │
│          de-identified, unjoined, no PHI  │
│          + quasi-identifier generalization│
│            (HIPAA Safe Harbor)            │
└───────────────────────────────────────────┘
        │
        ▼
┌───────────────────────────────────────────┐
│ DELIVERY delivery.encounter_summary       │
│          reduce-then-join, final output   │
└───────────────────────────────────────────┘
        │
        ▼
   DuckDB query layer  (landing/bronze/silver/gold/delivery)
```

Key design decisions:

- **Catalog per layer, schema per provider.** Tables are addressed as `<layer>.<provider>.<table>` in Bronze, Silver, and Gold, so adding a provider adds a schema rather than reshaping the namespace. Tables are only joined, and providers only combined, at delivery. Rationale is documented inline in [`setup/schema_landing.sql`](setup/schema_landing.sql).
- **Two-tier de-identification at two boundaries.** Direct identifiers are removed between Bronze and Silver, and quasi-identifiers are generalized between Silver and Gold. Bronze stays faithful to the raw feed, Silver keeps analytically useful detail, and Gold is PHI-free.
- **Reduce-then-join at delivery.** A naive four-way join of the raw clinical tables expands 6,484 encounters into 133,878 rows. Each entity is reduced to encounter grain first, then joined 1:1.
- **Quarantine never blocks a write.** Failed records are persisted to a per-table backlog with a reason and re-validated on later runs, rather than failing the batch.
- **Orchestration is separate from transformation.** DAGs wire tasks together; all logic lives in importable, independently testable modules under `src/`.

The provider is **Meridian Health**, a fictional integrated health system (IDN). An IDN was chosen specifically because it is the smallest real-world entity type that could plausibly produce the full clinical footprint in scope — inpatient, outpatient, and diagnostic — from a single source. Scope is 14 of Synthea's 18 raw tables; the payer/claims cluster is excluded because it is insurer-owned in practice, not provider-owned. See [`docs/suppliers/meridian_health.md`](docs/suppliers/meridian_health.md).

### Technology Stack

| Concern | Choice | Why |
|---|---|---|
| Language | Python 3.12 (pyenv) | Pinned deliberately; not system Python |
| Packaging / env | `uv` | Fast, lockfile-based, reproducible |
| Orchestration | Apache Airflow 3.3.2 (Docker Compose) | Industry standard; runs locally without cloud cost |
| Airflow metadata | PostgreSQL (container-only) | Airflow's own store — not a delivery database |
| Table format | Delta Lake via `delta-rs` | ACID writes and time travel without a JVM or Spark |
| Transform engine | pandas | Right scale for v1; PySpark is reserved for v2 |
| Columnar interchange | PyArrow | Zero-copy bridge between pandas and Delta |
| Validation | Pandera | Vectorized DataFrame validation reporting all failures at once, not just the first |
| Query layer | DuckDB | Zero-setup SQL over local Delta/CSV |
| Testing | pytest, pytest-cov, freezegun | Deterministic tests over timestamped pipelines |
| Lint / format | Ruff | Single fast tool replacing flake8 + isort + black |
| Hooks | pre-commit | Enforces lint before commits land |
| Source data | Synthea | Realistic synthetic patient records, no PHI risk |

## Version 2

### Architecture

Version 2 migrates the same data product to Databricks at production scale. The medallion shape, the provider-scoped layers, the two-tier de-identification model, and the delivery contract stay fixed. What changes is the execution engine, the orchestrator, and the governance layer.

The era opens with a second hand-coded pass over the *same* Meridian Health feed on the new stack. That deliberate repetition is a skill-verification checkpoint: it isolates "can this be built on Databricks" from "can a new provider be onboarded," and makes the two stacks directly comparable on identical inputs. Additional providers are onboarded only after that pass lands, each getting its own schema in Bronze, Silver, and Gold and joining the shared output at delivery.

### Technology Stack

| Concern | Choice | Why |
|---|---|---|
| Platform | Databricks | Production-scale lakehouse |
| Orchestration | Lakeflow Jobs | Native scheduling and lineage |
| Transform engine | PySpark | Distributed execution at real data volumes |
| Table format | Delta Lake | Same format as v1 — the migration is engine-level, not format-level |
| Governance | Unity Catalog | Centralized access control and lineage across layers |

## Project Principles

1. **Preserve the raw truth.** Source data should remain traceable and reproducible.
2. **Make bad data visible.** Quarantine records with reasons instead of silently dropping them.
3. **Test before publishing.** Customer-facing outputs must pass an explicit quality gate.
4. **Keep transformations testable and portable.**
5. **Separate orchestration from transformation.**
6. **Design for migration.** The project will migrate from a Version 1 tech stack on small-scale data to a Version 2 tech stack on production-scale data.
7. **Document the reasoning.** Architecture and documentation are first-class project artifacts.

## Current Status

**Current release: `0.5.0`** — Version 1, Bronze layer in progress. See [CHANGELOG.md](CHANGELOG.md) for per-release detail, including an explicit *Known limitations* section on every version.

**Shipped**

- [x] Project tooling: `uv`, Ruff, pre-commit, pytest, SemVer + changelog discipline, branch protection, PR template
- [x] Local Airflow stack via Docker Compose
- [x] DuckDB catalogs for landing and Bronze, with schema-per-provider addressing
- [x] Shared, provider-agnostic Bronze ingestion path with provenance stamping
- [x] Batch-level idempotent Delta writes
- [x] Bronze ingestion for 4 of 14 Meridian Health tables — `encounters`, `patients`, `conditions`, `observations`
- [x] Per-table package structure for pipelines and schemas
- [x] Committed sample batch, so the repository runs end to end on clone

**In progress**

- [ ] Pandera schemas — `encounters` is fully declared; `patients`, `conditions`, and `observations` are placeholders
- [ ] Wiring schema validation into the write path
- [ ] Quarantine handling

**Not yet started**

- [ ] Airflow DAG — pipelines currently run as standalone scripts
- [ ] Remaining 10 of 14 Bronze tables
- [ ] Meridian Health organization filtering — the provider slice is currently an unfiltered copy of the full Synthea export
- [ ] Silver layer (`silver.<provider>.<table>`) with direct-identifier removal
- [ ] Privacy cleaning — Silver → Gold quasi-identifier generalization
- [ ] Gold layer (`gold.<provider>.<table>`)
- [ ] Delivery step (`delivery.encounter_summary`)
- [ ] CI workflow (lint + tests on pull request)

## Documentation

| Document | Contents |
|---|---|
| [CHANGELOG.md](CHANGELOG.md) | Per-release history, each with an explicit *Known limitations* section |
| [CONTRIBUTING.md](CONTRIBUTING.md) | Branching model, commit conventions, SemVer policy, catalog conventions |
| [docs/suppliers/meridian_health.md](docs/suppliers/meridian_health.md) | Provider scope and why an IDN was chosen |
| [docs/raw-data/schema/](docs/raw-data/schema/) | Synthea table reference, grouped by domain |
| [docs/raw-data/data-quality/manifest-format.md](docs/raw-data/data-quality/manifest-format.md) | Batch data-quality manifest format |
| [docs/raw-data/synthea-quirks/baseline-quirks.md](docs/raw-data/synthea-quirks/baseline-quirks.md) | Known quirks in the Synthea source data |

## License

[MIT](LICENSE)
