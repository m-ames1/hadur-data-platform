# One Pandera schema per table
import pandera.pandas as pa


class PatientsSchema(pa.DataFrameModel):
    # TODO: Add the 28 real columns; this is a structural placeholder only.

    class Config:  # pyright: ignore[reportIncompatibleVariableOverride]
        # Convert columns to declared types, failures -> validation errors
        # (structural schema enforcement - business rules enforced in Silver)
        coerce = True
        # Reject any column not declared in this schema
        # (catch schema drift and unexpected / extra columns)
        strict = True
