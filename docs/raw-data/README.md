# Documentation for `data/raw/`

Reference documentation for this repo's bronze-layer input data
(`data/raw/<BATCH_DATE>/`) — the 18-CSV schema, known data quality issues,
and table relationships.

## Contents

- **`schema/`** — the 18-CSV schema, by domain cluster. Describes column
  meaning, foreign keys, and shared coding vocabularies (SNOMED CT, LOINC,
  RxNorm, CVX, DICOM, UDI). Start with
  [schema/overview.md](schema/overview.md).
- **`data-quality/manifest-format.md`** — the format of `manifest.jsonl`
  and `manifest_summary.json`, the two files delivered alongside each
  batch's `csv/` data: how to read exactly which rows/cells have a known
  data quality issue.
- **`synthea-quirks/baseline-quirks.md`** — data quality quirks in the
  dataset that are *not* captured in the manifest, plus which apparent
  gaps are actually legitimate (not defects). Needed to correctly
  distinguish "catalogued in the manifest," "a known quirk outside it,"
  and "expected/intentional" when working with the data.
