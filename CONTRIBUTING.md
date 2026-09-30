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
  This installs dependencies (`uv sync`), wires up the pre-commit git hook, seeds
  `data/landing_zone/` from the committed sample batch if no landing data exists yet, and
  builds the landing catalog under `catalog/` from `setup/schema_landing.sql` — requires `uv`
  and `duckdb` to already be installed
- To run those steps individually instead (or if `setup.sh` fails partway through):
  ```bash
  uv sync
  uv run pre-commit install
  mkdir -p data && cp -R sample_data/landing_zone data/   # fresh clone only
  mkdir -p catalog
  duckdb hadur.duckdb -init setup/schema_landing.sql -no-stdin
  ```
- Bronze views are built separately, after at least one pipeline has written output:
  ```bash
  duckdb hadur.duckdb -init setup/schema_bronze.sql -no-stdin
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

Dependabot security updates are enabled. Dependabot PRs bump `uv.lock` but
don't regenerate `requirements.txt`, so the `dependabot-requirements-sync`
workflow does it on the PR branch (see below). Review and merge them like any
other PR.

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

CI runs as three GitHub Actions workflows on every pull request:

| Workflow | Job | Required to merge | What it does |
|---|---|---|---|
| `ci.yml` | `test` | Yes | Re-verifies the lockfile, `requirements.txt` sync, lint, and format, then runs the tests |
| `pr-title-lint.yml` | `lint-pr-title` | Yes | Checks the PR title against the convention below. Skipped on Dependabot PRs |
| `dependabot-requirements-sync.yml` | `sync-requirements` | No | On Dependabot PRs only, regenerates `requirements.txt` and pushes it to the PR branch |

Required checks are enforced by the `main-protection` ruleset. A skipped
required check counts as passing, which is why `lint-pr-title` can be required
while skipping Dependabot's PRs, whose titles don't follow the convention.

`ci.yml` runs these steps, as a backstop for hooks that were skipped or
bypassed locally, and is the only place tests actually run automatically:

1. Sync dependencies (`uv sync --locked`) — fails if the lockfile is out of sync
2. Verify `requirements.txt` is in sync with `uv.lock`
3. `ruff check .`
4. `ruff format --check`
5. `uv run pytest`

`ci.yml` also runs on every push to `main`, which re-tests the squash commit
that actually landed. A failure there doesn't undo the merge — fix forward
with a new PR.

`dependabot-requirements-sync.yml` pushes with a fine-grained personal access
token stored as the `DEPENDABOT_SYNC_TOKEN` secret, because GitHub makes the
default token read-only on Dependabot-triggered runs. The token expires; when
it does, this workflow fails and the token needs regenerating.

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

When onboarding a provider, add a schema to the relevant layer catalog — in
`setup/schema_landing.sql` for landing, `setup/schema_bronze.sql` for Bronze — rather than a
new view-name prefix. Layer catalogs are gitignored build artifacts, reproducible at any time
from those scripts.

## Branching model

Trunk-based — no long-lived `dev` branch. Short-lived feature branches off `main`,
merged back via pull request.

**Branch naming:** `<type>/<short-description>`

Examples:
- `chore/repo-setup`
- `feat/silver-deidentify`
- `fix/gold-schema-drift`

Types in use: `feat`, `fix`, `chore`, `docs`, `refactor`.

## Commit messages and PR titles

PRs are squash-merged, so the PR title becomes the single commit that lands
on `main`. PR titles are enforced by the `lint-pr-title` check:

- Format: `type: Description`, following [Conventional Commits](https://www.conventionalcommits.org/)
- `type` is one of the types above, and matches the branch type
- The description starts with a capital letter
- Example: `chore: Add DuckDB dependency`

Commits inside a PR follow the same title format by convention, with a body of
bullet points, one per change. They aren't checked, because squash merging
discards them.

## Versioning

- SemVer (`MAJOR.MINOR.PATCH`), tracked in `pyproject.toml`'s `version` field
- Stays in `0.x` through v1 — no stable public contract yet
- **MINOR** bumps once per completed feature (a self-contained capability — e.g. dirty-data cleaning, de-identification, privacy-cleaning, the reference-table join), not batched by medallion stage. Each feature-sized PR gets its own bump and CHANGELOG entry; a medallion stage (Bronze/Silver/Gold) being "done" is just wherever its last feature bump landed, not a bump trigger on its own.
- Releases get an annotated git tag: `git tag -a vX.Y.Z -m "..."`, pushed explicitly with `git push origin vX.Y.Z`
- Era tags mark full re-platforms, separately from SemVer: `airflow-platform-v1` is applied once v1 is feature-complete (one provider onboarded, data flowing end-to-end through Gold)

## Pull requests

- All changes land on `main` through a PR — direct pushes are blocked by the `main-protection` ruleset, enforced even for the repo owner
- PRs require conversation resolution and linear history (squash merge only)
- `test` and `lint-pr-title` must pass before merge — enforced as required status checks
- No PR merges without tests included in the same PR
- Required approvals: 0, since this is a solo project. If contributors join, raise required approvals to 1 in the `main-protection` ruleset

## Architecture decisions

Decisions about the system's shape are recorded in [`docs/adr/`](docs/adr/). A PR that makes
one adds its ADR in the same PR. See [`docs/adr/README.md`](docs/adr/README.md) for the rules.

## Not configured, on purpose

- **Continuous deployment.** There's no deployed service, published package, or built
  artifact to ship yet. Revisit once there's a persistent deployment target, such as a
  long-running Airflow instance, to trigger a build against.
- **Signed commits.** Solo project, so there's no one else's identity to distinguish commits
  from. Revisit if this repo takes outside contributors.
