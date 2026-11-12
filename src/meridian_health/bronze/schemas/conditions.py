# One Pandera schema per table
import pandera.pandas as pa
from pandera.typing import Series


class ConditionsSchema(pa.DataFrameModel):
    # There is no Id column
    # Unique only by a composite key (PATIENT + ENCOUNTER + CODE + date)
    START: Series[str]
    STOP: Series[str] = pa.Field(nullable=True)
    PATIENT: Series[str]
    ENCOUNTER: Series[str]
    SYSTEM: Series[str]
    CODE: Series[str]
    DESCRIPTION: Series[str] = pa.Field(nullable=True)

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Reject any column not declared in this schema
        # (catch schema drift / extra columns)
        strict = True
