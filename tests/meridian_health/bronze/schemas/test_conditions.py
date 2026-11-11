import pandas as pd
import pandera.pandas as pa
import pytest
from pandas.testing import assert_frame_equal

from src.meridian_health.bronze.schemas.conditions import ConditionsSchema

SCHEMA_ERRORS = (pa.errors.SchemaError, pa.errors.SchemaErrors)


# Conditions schema input data
# All columns populated
full_condition_row = {
    "START": "2026-09-01",
    "STOP": "2026-09-15",
    "PATIENT": "patient-2",
    "ENCOUNTER": "enc-2",
    "SYSTEM": "SNOMED-CT",
    "CODE": "10509002",
    "DESCRIPTION": "Acute bronchitis (disorder)",
}

# All nullable columns containing Nulls
minimum_viable_condition_row = {
    "START": "2026-09-01",
    "STOP": None,
    "PATIENT": "patient-1",
    "ENCOUNTER": "enc-1",
    "SYSTEM": "SNOMED-CT",
    "CODE": "44054006",
    "DESCRIPTION": None,
}

valid_conditions_df = pd.DataFrame(data=[full_condition_row, minimum_viable_condition_row])


# Conditions schema tests
def test_conditions_schema_valid_rows_pass():
    result_df = ConditionsSchema.validate(valid_conditions_df)

    assert_frame_equal(result_df, valid_conditions_df)


def test_conditions_schema_rejects_null_required_column():
    # Immutable operation preferred over in-place mutations
    null_required_col_df = valid_conditions_df.assign(ENCOUNTER=None)

    with pytest.raises(SCHEMA_ERRORS):
        ConditionsSchema.validate(null_required_col_df)


def test_conditions_schema_rejects_extra_column():
    extra_col_df = valid_conditions_df.assign(EXTRA_COL="unexpected")

    with pytest.raises(SCHEMA_ERRORS):
        ConditionsSchema.validate(extra_col_df)


def test_conditions_schema_rejects_missing_column():
    missing_col_df = valid_conditions_df.drop(columns="ENCOUNTER")

    with pytest.raises(SCHEMA_ERRORS):
        ConditionsSchema.validate(missing_col_df)
