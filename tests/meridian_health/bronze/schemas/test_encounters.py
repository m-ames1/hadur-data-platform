import pandas as pd
import pandera.pandas as pa
import pytest
from pandas.testing import assert_frame_equal

from src.meridian_health.bronze.schemas.encounters import EncountersSchema

SCHEMA_ERRORS = (pa.errors.SchemaError, pa.errors.SchemaErrors)

# Encounters schema input data
valid_encounter_row = {
    "Id": ["enc-1"],
    "START": ["2026-09-01"],
    "STOP": ["2026-09-01"],
    "PATIENT": ["patient-1"],
    "ORGANIZATION": ["org-1"],
    "PROVIDER": ["provider-1"],
    "PAYER": ["payer-1"],
    "ENCOUNTERCLASS": ["ambulatory"],
    "CODE": ["185347001"],
    "DESCRIPTION": ["Encounter for check up"],
    "BASE_ENCOUNTER_COST": ["136.80"],
    "TOTAL_CLAIM_COST": ["136.80"],
    "PAYER_COVERAGE": ["0.0"],
    "REASONCODE": [None],
    "REASONDESCRIPTION": [None],
}

valid_encounters_df = pd.DataFrame(valid_encounter_row)


# Encounters schema tests
def test_encounters_schema_valid_row_passes():
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
