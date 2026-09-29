# Contributing

This is a solo project. This file exists so the project's own conventions
don't have to be re-derived from memory later.

## Development setup

- Python 3.12, managed via [`uv`](https://docs.astral.sh/uv/) — `uv` installs and pins the
  interpreter itself, no separate pyenv/venv setup required
- Clone the repo, then run:
  ```bash
  ./setup.sh
  ```
  This installs dependencies (`uv sync`), wires up the pre-commit git hook, and builds
  the local DuckDB catalogs under `catalog/` from `setup/schema.sql` — requires `uv` and
  `duckdb` to already be installed
- To run those steps individually instead (or if `setup.sh` fails partway through):
  ```bash
  uv sync
  uv run pre-commit install
  mkdir -p catalog
  duckdb hadur.duckdb -init setup/schema.sql -no-stdin
  ```
- Run any project command through `uv run <command>` (e.g. `uv run pytest`) instead of
  activating the virtualenv manually — `uv run` uses `.venv` automatically

## Dependency workflow

Dependencies are only ever changed via `uv add <package>` / `uv remove <package>`
(or `uv add --dev <package>` for dev-only tools) — never by hand-editing the
`dependencies` list in `pyproject.toml`. Those commands update `pyproject.toml`
and `uv.lock` together, atomically, so the two can't drift apart.

`requirements.txt` is a separate export artifact, used only to install
`src/meridian_health` into the Airflow image (see `Dockerfile`). It is never
updated by `uv add`/`uv remove` — it's regenerated automatically by a
pre-commit hook, described below.

## Automated checks

Pre-commit hooks run on every `git commit`, in order, and stop at the first
failure (`fail_fast: true`):

1. `ruff` — lints, auto-fixes what it can
2. `ruff-format` — auto-formats
3. `uv-lock` — verifies `uv.lock` matches `pyproject.toml` (check only)
4. `uv-export` — regenerates `requirements.txt` from `uv.lock`, only if step 3 passed

If `uv-lock` fails, the commit is blocked and `requirements.txt` is left
untouched — that's a signal something drifted outside the normal `uv add`
workflow and needs investigating, not something to fix by re-running export.

If `uv-export` regenerates `requirements.txt` with real changes, pre-commit
reports that step as failed even though nothing is wrong — `git add
requirements.txt` and commit again to pick up the regenerated file.

There's no pre-commit hook for tests; running the full suite on every commit
would be too slow. Run `uv run pytest --cov=src --cov-report=term-missing`
yourself before pushing — CI is the only enforced backstop if that's skipped.

CI (`.github/workflows/ci.yml`) re-verifies the same lockfile/lint/format
checks independently, as a backstop for hooks that were skipped or bypassed
locally, and is the only place tests actually run automatically:

1. Sync dependencies (`uv sync --locked`) — fails if the lockfile is out of sync
2. Verify `requirements.txt` is in sync with `uv.lock`
3. `ruff check .`
4. `ruff format --check`
5. `uv run pytest`

## Local querying

Tables are addressed as `<layer>.<provider>.<table>` — e.g. `bronze.meridian_health.encounters`.
Each medallion layer is a separate DuckDB catalog file under `catalog/`, and each provider is a
schema inside it. A single DuckDB file offers only `schema.table`, so the layer has to be a
catalog to get three levels.

`ATTACH` is per-connection session state and is never persisted, so every session runs the
attach script:

```bash
duckdb hadur.duckdb -init setup/attach.sql
```

Run it from the project root — the views store relative paths and resolve them against the
process working directory.

When onboarding a provider, add a schema to the relevant layer catalog in `setup/schema.sql`
rather than a new view-name prefix. Layer catalogs are gitignored build artifacts, reproducible
at any time from `setup/schema.sql`.

## Branching model

Trunk-based — no long-lived `dev` branch. Short-lived feature branches off `main`,
merged back via pull request.

**Branch naming:** `<type>/<short-description>`

Examples:
- `chore/repo-setup`
- `feat/silver-deidentify`
- `fix/gold-schema-drift`

Types in use: `feat`, `fix`, `chore`, `docs`, `refactor`.

## Commit messages

Loosely follow [Conventional Commits](https://www.conventionalcommits.org/):
`type: short description`, e.g. `chore: add CONTRIBUTING.md`.

## Versioning

- SemVer (`MAJOR.MINOR.PATCH`), tracked in `pyproject.toml`'s `version` field
- Stays in `0.x` through v1 — no stable public contract yet
- **MINOR** bumps once per completed feature (a self-contained capability — e.g. dirty-data cleaning, de-identification, privacy-cleaning, the reference-table join), not batched by medallion stage. Each feature-sized PR gets its own bump and CHANGELOG entry; a medallion stage (Bronze/Silver/Gold) being "done" is just wherever its last feature bump landed, not a bump trigger on its own.
- Releases get an annotated git tag: `git tag -a vX.Y.Z -m "..."`, pushed explicitly with `git push origin vX.Y.Z`
- Era tags mark full re-platforms, separately from SemVer: `airflow-platform-v1` is applied once v1 is feature-complete (one provider onboarded, data flowing end-to-end through Gold)

## Pull requests

- All changes land on `main` through a PR — direct pushes are blocked by branch protection, enforced even for the repo owner
- PRs require conversation resolution and linear history (squash or rebase merge only, no merge commits)
- No PR merges without tests included in the same PR
