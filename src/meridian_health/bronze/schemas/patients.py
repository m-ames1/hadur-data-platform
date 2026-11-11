# One Pandera schema per table
import pandera.pandas as pa
from pandera.typing import Series


class PatientsSchema(pa.DataFrameModel):
    Id: Series[str]
    BIRTHDATE: Series[str]
    DEATHDATE: Series[str] = pa.Field(nullable=True)
    SSN: Series[str]
    DRIVERS: Series[str] = pa.Field(nullable=True)
    PASSPORT: Series[str] = pa.Field(nullable=True)
    PREFIX: Series[str] = pa.Field(nullable=True)
    FIRST: Series[str]
    MIDDLE: Series[str] = pa.Field(nullable=True)
    LAST: Series[str]
    SUFFIX: Series[str] = pa.Field(nullable=True)
    MAIDEN: Series[str] = pa.Field(nullable=True)
    MARITAL: Series[str] = pa.Field(nullable=True)
    RACE: Series[str] = pa.Field(nullable=True)
    ETHNICITY: Series[str] = pa.Field(nullable=True)
    GENDER: Series[str]
    BIRTHPLACE: Series[str]
    ADDRESS: Series[str] = pa.Field(nullable=True)
    CITY: Series[str] = pa.Field(nullable=True)
    STATE: Series[str] = pa.Field(nullable=True)
    COUNTY: Series[str]
    FIPS: Series[str] = pa.Field(nullable=True)
    ZIP: Series[str] = pa.Field(nullable=True)
    LAT: Series[str]
    LON: Series[str]
    HEALTHCARE_EXPENSES: Series[str]
    HEALTHCARE_COVERAGE: Series[str]
    INCOME: Series[str] = pa.Field(nullable=True)

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Reject any column not declared in this schema
        # (catch schema drift and unexpected / extra columns)
        strict = True
