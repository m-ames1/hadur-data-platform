## Summary

<!-- What this PR does and why. -->

## Checklist

**Dependencies**

- [ ] `uv lock` — lockfile regenerated (if `pyproject.toml` changed)
- [ ] `uv export --no-dev --format requirements.txt --output-file requirements.txt` — regenerated (if runtime deps changed)

*Temporary — these become CI checks once a workflow exists, and drop off this list.*

**Quality**

- [ ] `uv run pytest --cov=src --cov-report=term-missing` — all tests pass, no unexpected skips, new code covered

*Temporary — these become CI checks once a workflow exists, and drop off this list.*

**Release**

- [ ] Version bumped in `pyproject.toml` **and** `CHANGELOG.md` entry written — or N/A (no capability change)
- [ ] Branch, commits and PR title carry conventional prefixes; PR title type matches branch type

**Docs**

- [ ] Docs updated if behavior, layout or conventions changed

## Known limitations

<!-- Anything deliberately incomplete, mirroring the CHANGELOG. Write "None" if none. -->

## After merge

Tag the release, if this PR bumped the version:

`git tag -a vX.Y.Z -m "..."` && `git push origin vX.Y.Z`
