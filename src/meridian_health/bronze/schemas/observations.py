# One Pandera schema per table
import pandera.pandas as pa
from pandera.typing import Series


class ObservationsSchema(pa.DataFrameModel):
    # TODO: Add fields — no Id column, and no reliable natural key either.
    # PATIENT + ENCOUNTER + CODE + DATE repeats for ~250 rows; can't be
    # treated as unique the way it can for ConditionsSchema.
    DATE: Series[str]
    PATIENT: Series[str]
    ENCOUNTER: Series[str] = pa.Field(nullable=True)
    CATEGORY: Series[str] = pa.Field(nullable=True)
    CODE: Series[str]
    DESCRIPTION: Series[str]
    VALUE: Series[str] = pa.Field(nullable=True)
    UNITS: Series[str] = pa.Field(nullable=True)
    TYPE: Series[str]

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Reject any column not declared in this schema
        # (catch schema drift and unexpected / extra columns)
        strict = True
