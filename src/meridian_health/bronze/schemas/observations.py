# One Pandera schema per table
import pandera.pandas as pa


class ObservationsSchema(pa.DataFrameModel):
    # TODO: Add fields — no Id column, and no reliable natural key either.
    # PATIENT + ENCOUNTER + CODE + DATE repeats for ~250 rows; can't be
    # treated as unique the way it can for ConditionsSchema.

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Convert columns to declared types, failures -> validation errors
        # (structural schema enforcement - business rules enforced in Silver)
        coerce = True
        # Reject any column not declared in this schema
        # (catch schema drift and unexpected / extra columns)
        strict = True
