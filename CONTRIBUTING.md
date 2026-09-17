# Contributing

This is a solo project. This file exists so the project's own conventions
don't have to be re-derived from memory later.

## Development setup

- Python 3.12, managed via pyenv (not system Python, not the newest release)
- Dependency/setup instructions will be added here once the project has installable dependencies

## Branching model

Trunk-based — no long-lived `dev` branch. Short-lived feature branches off `main`,
merged back via pull request.

**Branch naming:** `<type>/<short-description>`

Examples:
- `chore/repo-setup`
- `feat/silver-deidentify`
- `fix/gold-schema-drift`

Types in use: `feat`, `fix`, `chore`.

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
