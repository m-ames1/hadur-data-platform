"""Build a small, referentially-consistent sample batch from a full Synthea export.

Run from the project root:
    uv run python scripts/build_sample_batch.py

Selects a fixed cohort of patients and cascades that selection through every
table, so the sample supports the same joins as the full batch. Output is
deterministic, so re-running never creates spurious diffs.
"""

import sys
from pathlib import Path

import pandas as pd

BATCH_DATE = "2026-09-01"
COHORT_SIZE = 10
SEED = 20260901

# The payer/claims cluster is insurer-owned and out of scope for every layer.
# These tables exist in the sample only so the landing.synthea views resolve,
# so they are row-capped rather than kept whole — claims_transactions is
# otherwise more than half the sample by size.
FINANCIAL_ROW_CAP = 2000
FINANCIAL_TABLES = {"claims", "claims_transactions", "payer_transitions"}

SOURCE = Path("data/landing_zone/all/raw") / BATCH_DATE / "csv"
SAMPLE_ROOT = Path("sample_data/landing_zone")
ALL_OUT = SAMPLE_ROOT / "all/raw" / BATCH_DATE / "csv"
PROVIDER_OUT = SAMPLE_ROOT / "meridian_health" / BATCH_DATE

# Tables Meridian Health delivers: clinical events + patients + filtered
# provider/org reference slices.
PROVIDER_TABLES = [
    "allergies",
    "careplans",
    "conditions",
    "devices",
    "encounters",
    "imaging_studies",
    "immunizations",
    "medications",
    "observations",
    "organizations",
    "patients",
    "procedures",
    "providers",
    "supplies",
]

PATIENT_KEYED = {
    "allergies": "PATIENT",
    "careplans": "PATIENT",
    "claims": "PATIENTID",
    "claims_transactions": "PATIENTID",
    "conditions": "PATIENT",
    "devices": "PATIENT",
    "encounters": "PATIENT",
    "imaging_studies": "PATIENT",
    "immunizations": "PATIENT",
    "medications": "PATIENT",
    "observations": "PATIENT",
    "payer_transitions": "PATIENT",
    "procedures": "PATIENT",
    "supplies": "PATIENT",
}


def read(table: str) -> pd.DataFrame:
    return pd.read_csv(SOURCE / f"{table}.csv", dtype=str, keep_default_na=False)


def write(df: pd.DataFrame, out_dir: Path, table: str) -> None:
    out_dir.mkdir(parents=True, exist_ok=True)
    df.to_csv(out_dir / f"{table}.csv", index=False)


def main() -> int:
    if not SOURCE.is_dir():
        print(f"Source batch not found: {SOURCE}", file=sys.stderr)
        return 1

    patients = read("patients").sort_values("Id").reset_index(drop=True)
    cohort_df = patients.sample(n=COHORT_SIZE, random_state=SEED).sort_values("Id")
    cohort = set(cohort_df["Id"])

    encounters = read("encounters")
    encounters = encounters[encounters["PATIENT"].isin(cohort)].sort_values("Id")

    kept_orgs = set(encounters["ORGANIZATION"])
    kept_providers = set(encounters["PROVIDER"])

    frames: dict[str, pd.DataFrame] = {"patients": cohort_df, "encounters": encounters}

    for table, key in PATIENT_KEYED.items():
        if table in frames:
            continue
        df = read(table)
        df = df[df[key].isin(cohort)]
        if table in FINANCIAL_TABLES:
            df = df.head(FINANCIAL_ROW_CAP)
        frames[table] = df

    orgs = read("organizations")
    frames["organizations"] = orgs[orgs["Id"].isin(kept_orgs)]

    providers = read("providers")
    frames["providers"] = providers[providers["Id"].isin(kept_providers)]

    # Payers is 10 rows; keeping it whole avoids dangling payer references.
    frames["payers"] = read("payers")

    for table, df in frames.items():
        write(df, ALL_OUT, table)

    for table in PROVIDER_TABLES:
        write(frames[table], PROVIDER_OUT, table)

    total = sum(f.stat().st_size for f in SAMPLE_ROOT.rglob("*.csv"))
    print(f"Cohort: {COHORT_SIZE} patients, {len(encounters)} encounters")
    print(f"Total sample size: {total / 1024:.0f} KB")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
