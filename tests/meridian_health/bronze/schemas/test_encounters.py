import pandas as pd
import pandera.pandas as pa
import pytest
from pandas.testing import assert_frame_equal

from src.meridian_health.bronze.schemas.encounters import EncountersSchema

SCHEMA_ERRORS = (pa.errors.SchemaError, pa.errors.SchemaErrors)


# Encounters schema input data
# All columns populated
full_encounter_row = {
    "Id": "enc-2",
    "START": "2026-09-01T09:00:00Z",
    "STOP": "2026-09-01T10:00:00Z",
    "PATIENT": "patient-2",
    "ORGANIZATION": "org-2",
    "PROVIDER": "provider-2",
    "PAYER": "payer-2",
    "ENCOUNTERCLASS": "ambulatory",
    "CODE": "185345009",
    "DESCRIPTION": "Encounter for symptom",
    "BASE_ENCOUNTER_COST": "136.80",
    "TOTAL_CLAIM_COST": "136.80",
    "PAYER_COVERAGE": "0.00",
    "REASONCODE": "10509002",
    "REASONDESCRIPTION": "Acute bronchitis (disorder)",
}

# All nullable columns containing Nulls
minimum_viable_encounter_row = {
    "Id": "enc-1",
    "START": "2026-09-01T09:00:00Z",
    "STOP": "2026-09-01T10:00:00Z",
    "PATIENT": "patient-1",
    "ORGANIZATION": "org-1",
    "PROVIDER": "provider-1",
    "PAYER": "payer-1",
    "ENCOUNTERCLASS": "ambulatory",
    "CODE": "185347001",
    "DESCRIPTION": None,
    "BASE_ENCOUNTER_COST": "136.80",
    "TOTAL_CLAIM_COST": None,
    "PAYER_COVERAGE": "0.00",
    "REASONCODE": None,
    "REASONDESCRIPTION": None,
}

valid_encounters_df = pd.DataFrame(data=[full_encounter_row, minimum_viable_encounter_row])


# Encounters schema tests
def test_encounters_schema_valid_rows_pass():
    result_df = EncountersSchema.validate(valid_encounters_df)

    assert_frame_equal(result_df, valid_encounters_df)


def test_encounters_schema_rejects_null_required_column():
    # Immutable operation preferred over in-place mutations
    null_required_col_df = valid_encounters_df.assign(PATIENT=None)

    with pytest.raises(SCHEMA_ERRORS):
        EncountersSchema.validate(null_required_col_df)


def test_encounters_schema_rejects_extra_column():
    extra_col_df = valid_encounters_df.assign(EXTRA_COL="unexpected")

    with pytest.raises(SCHEMA_ERRORS):
        EncountersSchema.validate(extra_col_df)


def test_encounters_schema_rejects_missing_column():
    missing_col_df = valid_encounters_df.drop(columns="PATIENT")

    with pytest.raises(SCHEMA_ERRORS):
        EncountersSchema.validate(missing_col_df)
