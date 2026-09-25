# One Pandera schema per table
import pandas as pd
import pandera.pandas as pa
from pandera.typing import Series


class EncountersSchema(pa.DataFrameModel):
    Id: Series[str]
    START: Series[pd.Timestamp]
    STOP: Series[pd.Timestamp]
    PATIENT: Series[str]
    ORGANIZATION: Series[str]
    PROVIDER: Series[str]
    PAYER: Series[str]
    ENCOUNTERCLASS: Series[str]
    CODE: Series[str]
    DESCRIPTION: Series[str] = pa.Field(nullable=True)
    BASE_ENCOUNTER_COST: Series[float]
    TOTAL_CLAIM_COST: Series[float] = pa.Field(nullable=True)
    PAYER_COVERAGE: Series[float]
    REASONCODE: Series[str] = pa.Field(nullable=True)
    REASONDESCRIPTION: Series[str] = pa.Field(nullable=True)

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Convert columns to declared types, failures -> validation errors
        # (structural schema enforcement - business rules enforced in Silver)
        coerce = True
        # Reject any column not declared in this schema
        # (catch schema drift and unexpected / extra columns)
        strict = True
