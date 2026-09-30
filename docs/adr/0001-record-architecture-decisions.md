# 0001. Record architecture decisions

- **Status:** Accepted
- **Date:** 2026-09-30

## Context

Decisions about how this system is built get made in pull requests and
design discussions, and the reasoning is then lost. Months later the code
shows what was built, but not why, or what was considered and rejected.

## Decision

Record each significant decision about the system's shape as an Architecture
Decision Record in `docs/adr/`, following the rules in [README.md](README.md).
An ADR is written in the same PR that implements its decision, and only for
decisions that are already built.

## Consequences

- The reasoning behind the architecture lives next to the code and is
  versioned with it.
- ADRs 0002–0008 were recorded retroactively, for decisions implemented
  before this folder existed. Each cites the PR that implemented it.
- Workflow rules stay in `CONTRIBUTING.md`, so each rule has one home.
- Writing an ADR becomes part of the definition of done for any PR that
  changes the system's shape.
