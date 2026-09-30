# 0003. Use pandas for v1 transforms, reserve PySpark for v2

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #12)

## Context

Version 1 processes one provider's batch on a single machine. Today the
pipelines run as scripts directly on the host; once the Airflow DAG is
built, they run as tasks inside the local Airflow containers. Either way
it's one machine, and distributed engines like PySpark bring a JVM and
cluster overhead that only pays off at volumes v1 doesn't have.

## Decision

v1 transforms use pandas. PySpark is reserved for Version 2 on Databricks,
where it is exercised at production scale.

## Consequences

- No JVM or Spark runtime is needed to develop or run v1.
- Every transform must fit in one machine's memory, which holds at
  single-provider Synthea volumes.
- v2's transforms are rewritten in PySpark rather than ported, as part of
  the planned re-platform. The era tags described in `CONTRIBUTING.md` mark
  that boundary.
