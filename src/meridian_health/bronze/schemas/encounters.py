# One Pandera schema per table
import pandera.pandas as pa
from pandera.typing import Series


class EncountersSchema(pa.DataFrameModel):
    Id: Series[str]
    START: Series[str]
    STOP: Series[str]
    PATIENT: Series[str]
    ORGANIZATION: Series[str]
    PROVIDER: Series[str]
    PAYER: Series[str]
    ENCOUNTERCLASS: Series[str]
    CODE: Series[str]
    DESCRIPTION: Series[str] = pa.Field(nullable=True)
    BASE_ENCOUNTER_COST: Series[str]
    TOTAL_CLAIM_COST: Series[str] = pa.Field(nullable=True)
    PAYER_COVERAGE: Series[str]
    REASONCODE: Series[str] = pa.Field(nullable=True)
    REASONDESCRIPTION: Series[str] = pa.Field(nullable=True)

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Reject any column not declared in this schema
        # (catch schema drift / extra columns)
        strict = True
