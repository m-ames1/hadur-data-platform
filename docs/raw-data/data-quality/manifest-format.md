# The data quality manifest

**Scope: the two files delivered alongside each batch's `csv/` data** —
`manifest.jsonl` and `manifest_summary.json` — which catalogue known data
quality issues present in that batch, row by row.

## Layout

```
data/raw/<BATCH_DATE>/
├── csv/                    18 CSVs
├── manifest.jsonl          one JSON record per known data quality issue
└── manifest_summary.json   aggregated counts over the same batch
```

`csv/` holds the 18 tables documented in [../schema/](../schema/). The
manifest files describe issues present in those same CSVs — missing values,
formatting inconsistencies, duplicate rows, broken references, and so on.
Every issue the manifest lists is one already present in the delivered
`csv/` files; the manifest doesn't change the data, it just tells you where
to look.

## `manifest.jsonl`

One JSON object per line, one line per individual known issue. Every
record has `injector`, `tier`, `action`, and `table`; the remaining fields
depend on `action`. Keys are written alphabetically, not in the order
below.

- **`injector`** — the category of issue: one of `missing_values`,
  `typos`, `duplicates`, `formatting`, `type_mismatch`, `date_issues` (tier
  `row`), or `orphan_fk`, `key_format_drift`, `cardinality_break` (tier
  `join`).
- **`tier`** — `"row"` for issues confined to a single row/cell, `"join"`
  for issues that break a foreign-key or cardinality relationship between
  tables.
- **`table`** — which of the 18 tables the issue is in.
- **`action`** — `"edit_cell"` or `"duplicate_row"`, determining which of
  the fields below are present.

### `action: "edit_cell"`

A single cell's value is affected.

- **`row_id`** — identifies the row. For 8 tables with a usable dedicated
  key column (`patients`, `organizations`, `providers`, `payers`,
  `encounters`, `careplans`, `claims`, `claims_transactions`; `Id`/`ID`),
  this is that key's value. For the other 10 tables — the 8 keyless
  clinical event logs, plus `imaging_studies` (whose `Id` isn't unique) and
  `payer_transitions` — it's the row's 0-based line index in the CSV
  instead. See [../schema/overview.md](../schema/overview.md) for why these
  particular tables lack a usable key.
- **`column`** — the affected column.
- **`original`** — the value the column would otherwise have had.
- **`new`** — the value actually present in `csv/` (e.g. `""` for a value
  categorized as `missing_values`).

Example:

```json
{"action": "edit_cell", "column": "MARITAL", "injector": "missing_values", "new": "", "original": "M", "row_id": "d3cb6736-0991-40ed-a220-7c714aba4c37", "table": "patients", "tier": "row"}
```

### `action: "duplicate_row"`

An existing row appears more than once.

- **`source_row_id`** — the original row, identified the same way as
  `edit_cell`'s `row_id`.
- **`new_row_id`** — the identifier of the extra, duplicate row. For keyed
  tables this is often identical to `source_row_id` (the duplicate carries
  the same key value — a realistic exact-duplicate-row pattern); for
  keyless tables it's the duplicate row's own line index.

Example:

```json
{"action": "duplicate_row", "injector": "duplicates", "new_row_id": "7811dc30-8c86-8164-6c33-6b6f464745ef", "source_row_id": "7811dc30-8c86-8164-6c33-6b6f464745ef", "table": "patients", "tier": "row"}
```

## `manifest_summary.json`

A single JSON object aggregating the same batch's manifest into counts —
nothing in it isn't derivable from `manifest.jsonl`, it's just pre-tallied
for a quick look without parsing the full JSONL file.

- **`total_changes`** — total number of manifest records (edits +
  duplications combined) in the batch.
- **`by_injector`** — issue count per category, summed across all tables.
- **`by_table`** — issue count per table, summed across all categories.
- **`detail`** — one `{"injector", "table", "count"}` object per
  category/table pair that had at least one issue — the finest-grained
  breakdown the summary provides (still coarser than `manifest.jsonl`,
  which has one entry per individual issue, not per pair).

All three of `by_injector`, `by_table`, and `detail` are sorted by key for
stable diffs across batches.
