# One Pandera schema per table
import pandera.pandas as pa


class ConditionsSchema(pa.DataFrameModel):
    # TODO: Add fields — note there is no Id column; unique only by a
    # composite key (PATIENT + ENCOUNTER + CODE + date).

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Convert columns to declared types, failures -> validation errors
        # (structural schema enforcement - business rules enforced in Silver)
        coerce = True
        # Reject any column not declared in this schema
        # (catch schema drift and unexpected / extra columns)
        strict = True
