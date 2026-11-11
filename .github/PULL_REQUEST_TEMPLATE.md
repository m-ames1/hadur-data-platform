## Summary

<!-- What this PR does and why. -->

## Checklist

**Release**

- [ ] Version bumped in `pyproject.toml` **and** `CHANGELOG.md` entry written — or N/A (no capability change)
- [ ] Branch, commits and PR title carry conventional prefixes; PR title type matches branch type

**Dependencies**

- [ ] `uv lock` — lockfile regenerated after any `pyproject.toml` change, including the version bump
- [ ] `uv export --no-dev --format requirements.txt --output-file requirements.txt` — regenerated (if runtime deps changed)

**Quality**

- [ ] `uv run pytest --cov=src --cov-report=term-missing` — all tests pass, no unexpected skips, new code covered

**Docs**

- [ ] Docs updated if behavior, layout or conventions changed
- [ ] ADR added in `docs/adr/` if this PR changes the system's shape

## Known limitations

<!-- Anything deliberately incomplete, mirroring the CHANGELOG. Write "None" if none. -->

## After merge

Tag the release, if this PR bumped the version: `git tag -a vX.Y.Z -m "..."` && `git push origin vX.Y.Z`