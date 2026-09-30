# 0006. Make Bronze writes idempotent per batch

- **Status:** Accepted
- **Date:** 2026-09-30 (recorded retroactively; implemented in #12)

## Context

Pipeline runs get repeated: a retry after a failure, or a deliberate re-run
of a batch. Bronze accumulates batches over time. The two obvious write modes
both fail here:

- **Append** duplicates every row of a batch that's run twice.
- **Full overwrite** replaces the batch, but also erases every other batch
  in the table.

## Decision

Bronze tables are partitioned by `_batch_date`, and each write overwrites
only the partition for the batch being written:

```python
write_deltalake(
    table_or_uri=bronze_table_path,
    data=df,
    partition_by=["_batch_date"],
    mode="overwrite",
    predicate=f"_batch_date = '{batch_date.isoformat()}'",
)
```

## Consequences

- Running a batch any number of times leaves the same result, and other
  batches are untouched. Retries are safe.
- Every row must carry `_batch_date`. `add_metadata_columns` stamps it,
  alongside `_source_file` and `_ingested_at`.
- The batch is the unit of correction: fixing one row means re-running its
  whole batch.
