import pandas as pd
import pandera.pandas as pa
import pytest
from pandas.testing import assert_frame_equal

from src.meridian_health.bronze.schemas.patients import PatientsSchema

SCHEMA_ERRORS = (pa.errors.SchemaError, pa.errors.SchemaErrors)


# Patients schema input data
# All columns populated
full_patient_row = {
    "Id": "patient-2",
    "BIRTHDATE": "1985-03-14",
    "DEATHDATE": "2025-11-02",
    "SSN": "999-12-3456",
    "DRIVERS": "S99912345",
    "PASSPORT": "X12345678X",
    "PREFIX": "Mrs.",
    "FIRST": "Jane",
    "MIDDLE": "Marie",
    "LAST": "Doe",
    "SUFFIX": "PhD",
    "MAIDEN": "Smith",
    "MARITAL": "M",
    "RACE": "white",
    "ETHNICITY": "nonhispanic",
    "GENDER": "F",
    "BIRTHPLACE": "Boston  Massachusetts  US",
    "ADDRESS": "123 Main St",
    "CITY": "Boston",
    "STATE": "Massachusetts",
    "COUNTY": "Suffolk County",
    "FIPS": "25025",
    "ZIP": "02134",
    "LAT": "42.3601",
    "LON": "-71.0589",
    "HEALTHCARE_EXPENSES": "54321.00",
    "HEALTHCARE_COVERAGE": "12345.00",
    "INCOME": "75000",
}

# All nullable columns containing Nulls
minimum_viable_patient_row = {
    "Id": "patient-1",
    "BIRTHDATE": "1990-06-01",
    "DEATHDATE": None,
    "SSN": "999-65-4321",
    "DRIVERS": None,
    "PASSPORT": None,
    "PREFIX": None,
    "FIRST": "John",
    "MIDDLE": None,
    "LAST": "Doe",
    "SUFFIX": None,
    "MAIDEN": None,
    "MARITAL": None,
    "RACE": None,
    "ETHNICITY": None,
    "GENDER": "M",
    "BIRTHPLACE": "Springfield  Massachusetts  US",
    "ADDRESS": None,
    "CITY": None,
    "STATE": None,
    "COUNTY": "Hampden County",
    "FIPS": None,
    "ZIP": None,
    "LAT": "42.1015",
    "LON": "-72.5898",
    "HEALTHCARE_EXPENSES": "1000.00",
    "HEALTHCARE_COVERAGE": "500.00",
    "INCOME": None,
}

valid_patients_df = pd.DataFrame(data=[full_patient_row, minimum_viable_patient_row])


# Patients schema tests
def test_patients_schema_valid_rows_pass():
    result_df = PatientsSchema.validate(valid_patients_df)

    assert_frame_equal(result_df, valid_patients_df)


def test_patients_schema_rejects_null_required_column():
    # Immutable operation preferred over in-place mutations
    null_required_col_df = valid_patients_df.assign(SSN=None)

    with pytest.raises(SCHEMA_ERRORS):
        PatientsSchema.validate(null_required_col_df)


def test_patients_schema_rejects_extra_column():
    extra_col_df = valid_patients_df.assign(EXTRA_COL="unexpected")

    with pytest.raises(SCHEMA_ERRORS):
        PatientsSchema.validate(extra_col_df)


def test_patients_schema_rejects_missing_column():
    missing_col_df = valid_patients_df.drop(columns="SSN")

    with pytest.raises(SCHEMA_ERRORS):
        PatientsSchema.validate(missing_col_df)
