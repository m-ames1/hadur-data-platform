# Read -> validate -> stamp provenance -> write/quarantine
# %%
from datetime import date

import pandas as pd

from src.bronze_ingestion import add_metadata_columns, build_landing_file_path, write_to_bronze
from src.config import ENCOUNTERS
from src.meridian_health import PROVIDER


# %%
def run_bronze_pipeline(batch_date: date) -> None:
    """
    # TODO: Sturcutre will need to be adjusted when DAG is ready and
    # remaining tables are added to the pipeline.
    # TODO: Update docstring.
    # TODO: Quarantine process pending.

    Runs the Bronze pipeline for the initial encounters table
    and calling run_bronze_pipeline() below simulates the behavior
    of the DAG once it is up and running.

    -> Build landing zone path
    -> Read raw data
    -> Add metadata columns
    -> Write to Bronze delta table
    """

    landing_zone_file_path = build_landing_file_path(
        provider=PROVIDER, batch_date=batch_date, table_name=ENCOUNTERS
    )

    raw_df = pd.read_csv(filepath_or_buffer=landing_zone_file_path, delimiter=",")

    bronze_df = add_metadata_columns(
        df=raw_df, source_file=landing_zone_file_path, batch_date=batch_date
    )

    write_to_bronze(provider=PROVIDER, table_name=ENCOUNTERS, df=bronze_df, batch_date=batch_date)


# %%
run_bronze_pipeline(batch_date=date(2026, 9, 1))
