import pandas as pd
import pandera.pandas as pa
import pytest
from pandas.testing import assert_frame_equal

from src.meridian_health.bronze.schemas.observations import ObservationsSchema

SCHEMA_ERRORS = (pa.errors.SchemaError, pa.errors.SchemaErrors)


# Observations schema input data
# All columns populated
full_observation_row = {
    "DATE": "2026-09-01T09:00:00Z",
    "PATIENT": "patient-2",
    "ENCOUNTER": "enc-2",
    "CATEGORY": "vital-signs",
    "CODE": "8302-2",
    "DESCRIPTION": "Body Height",
    "VALUE": "159.4",
    "UNITS": "cm",
    "TYPE": "numeric",
}

# All nullable columns containing Nulls
minimum_viable_observation_row = {
    "DATE": "2026-09-01T09:00:00Z",
    "PATIENT": "patient-1",
    "ENCOUNTER": None,
    "CATEGORY": None,
    "CODE": "72166-2",
    "DESCRIPTION": "Tobacco smoking status",
    "VALUE": None,
    "UNITS": None,
    "TYPE": "text",
}

valid_observations_df = pd.DataFrame(data=[full_observation_row, minimum_viable_observation_row])


# Observations schema tests
def test_observations_schema_valid_rows_pass():
    result_df = ObservationsSchema.validate(valid_observations_df)

    assert_frame_equal(result_df, valid_observations_df)


def test_observations_schema_rejects_null_required_column():
    # Immutable operation preferred over in-place mutations
    null_required_col_df = valid_observations_df.assign(PATIENT=None)

    with pytest.raises(SCHEMA_ERRORS):
        ObservationsSchema.validate(null_required_col_df)


def test_observations_schema_rejects_extra_column():
    extra_col_df = valid_observations_df.assign(EXTRA_COL="unexpected")

    with pytest.raises(SCHEMA_ERRORS):
        ObservationsSchema.validate(extra_col_df)


def test_observations_schema_rejects_missing_column():
    missing_col_df = valid_observations_df.drop(columns="PATIENT")

    with pytest.raises(SCHEMA_ERRORS):
        ObservationsSchema.validate(missing_col_df)
