from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pandera.pandas as pa
from deltalake import write_deltalake
from pandera.errors import SchemaErrors

from src.config import BRONZE_ZONE, LANDING_ZONE


def build_landing_file_path(
    provider: str, batch_date: date, table_name: str, ext: str = ".csv"
) -> Path:
    """
    Build the landing zone file path for a provider's batch table.

    Parameters
    ----------
    provider : str
        Name of the data provider.
    batch_date : date
        Batch date the file was landed under.
    table_name : str
        Name of the table.
    ext : str, optional
        File extension, by default ``".csv"``.

    Returns
    -------
    Path
        Full path to the landing zone file:
        ``LANDING_ZONE / provider / batch_date.isoformat() / f"{table_name}{ext}"``.

    Examples
    --------
    >>> build_landing_file_path("meridian_health", date(2026, 9, 1), "encounters")
    PosixPath('data/landing_zone/meridian_health/2026-09-01/encounters.csv')
    """

    landing_file_path = LANDING_ZONE / provider / batch_date.isoformat() / f"{table_name}{ext}"

    return landing_file_path


def add_metadata_columns(df: pd.DataFrame, source_file: Path, batch_date: date) -> pd.DataFrame:
    """
    Add metadata columns to the Bronze table.

    Parameters
    ----------
    df : pd.DataFrame
        The input DataFrame without the metadata columns.
    source_file : Path
        Full path to the landing zone file.
    batch_date : date
        Batch date the file was landed under.

    Returns
    -------
    pd.DataFrame
        A new DataFrame with three metadata columns added: ``_source_file``,
        ``_ingested_at`` (UTC timestamp of ingestion), and ``_batch_date``.

    Examples
    --------
    >>> bronze_df = add_metadata_columns(
    ...     df=raw_df,
    ...     source_file=landing_zone_path,
    ...     batch_date=batch_date,
    ... )
    >>> bronze_df.columns.tolist()
    [..., '_source_file', '_ingested_at', '_batch_date']
    """

    # Use .assign to ensure a new DataFrame is returned with the
    # columns added, leaving the orginal untouched
    # Follows same process as PySpark .withColumn()
    result_df = df.assign(
        _source_file=str(source_file),
        _ingested_at=datetime.now(timezone.utc),
        _batch_date=pd.Timestamp(batch_date),  # Apply explicit conversion over assumption
    )

    return result_df


def build_bronze_table_path(provider: str, table_name: str) -> Path:
    """
    Build the Bronze zone table path for a provider.

    Parameters
    ----------
    provider : str
        Name of the data provider.
    table_name : str
        Name of the table.

    Returns
    -------
    Path
        Full path to the Bronze table: ``BRONZE_ZONE / provider / table_name``.

    Examples
    --------
    >>> build_bronze_table_path("meridian_health", "encounters")
    PosixPath('data/bronze/meridian_health/encounters')
    """

    bronze_table_path = BRONZE_ZONE / provider / table_name

    return bronze_table_path


def write_to_bronze(provider: str, table_name: str, df: pd.DataFrame, batch_date: date) -> None:
    """
    Write a batch of records to a Delta table in a provider's Bronze zone.

    Used for every Bronze-zone table: the main table and its quarantine
    tables (``{table_name}_quarantine`` and
    ``{table_name}_quarantine_failure_cases``). The caller chooses the
    destination through ``table_name``.

    Overwrites only the partition matching ``batch_date``, so re-running
    an ingestion for the same batch replaces that batch's rows instead of
    appending duplicates or overwriting the entire table.

    Parameters
    ----------
    provider : str
        Name of the data provider.
    table_name : str
        Name of the Bronze-zone table to write to, including any
        quarantine suffix.
    df : pd.DataFrame
        DataFrame to write, expected to already contain the metadata
        columns added by ``add_metadata_columns``.
    batch_date : date
        Batch date the data belongs to; used as the partition key and
        the overwrite predicate.

    Returns
    -------
    None

    Examples
    --------
    >>> write_to_bronze(
    ...     provider="meridian_health",
    ...     table_name="encounters_quarantine",
    ...     df=quarantine_df,
    ...     batch_date=date(2026, 9, 1),
    ... )
    """

    bronze_table_path = build_bronze_table_path(provider=provider, table_name=table_name)

    write_deltalake(
        table_or_uri=bronze_table_path,
        data=df,
        partition_by=["_batch_date"],
        mode="overwrite",
        # Scopes the overwrite to the batch, only overwrites batch being rerun (not entire table)
        # Idempotent on batch level
        predicate=f"_batch_date = '{batch_date.isoformat()}'",
    )


def apply_quarantine_process(
    input_df: pd.DataFrame, schema: type[pa.DataFrameModel]
) -> tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]:
    """
    Validate a raw DataFrame against its Bronze schema and split it into
    passed and quarantined records.

    Validation is lazy, so all failures are collected in a single pass.
    Row-level failures (such as a null in a non-nullable column) are
    moved to quarantine and the remaining rows are returned as passed.
    Table-level failures (a missing, extra or renamed column) affect
    every row, so the rows can't be split and the whole batch fails.

    Parameters
    ----------
    input_df : pd.DataFrame
        Raw landing zone data, read with all columns as strings.
    schema : type[pa.DataFrameModel]
        Pandera schema defining the table's Bronze data contract.

    Returns
    -------
    tuple[pd.DataFrame, pd.DataFrame, pd.DataFrame]
        ``(valid_records_df, quarantined_df, failure_cases_df)``:

        - ``valid_records_df``: rows that passed validation.
        - ``quarantined_df``: rows with at least one failure, with the
          same columns as ``input_df``.
        - ``failure_cases_df``: one row per failed check, with columns
          ``schema_context``, ``column``, ``check``, ``check_number``,
          ``failure_case`` and ``index``.

        When every row passes, ``quarantined_df`` and ``failure_cases_df``
        are empty but keep their columns and dtypes, so the quarantine
        table schemas stay the same from run to run.

    Raises
    ------
    pandera.errors.SchemaErrors
        If any failure is table-level (missing, extra or renamed column).

    Examples
    --------
    >>> passed_df, quarantined_df, failure_cases_df = apply_quarantine_process(
    ...     input_df=raw_df,
    ...     schema=EncountersSchema,
    ... )
    >>> len(passed_df) + len(quarantined_df) == len(raw_df)
    True
    >>> failure_cases_df[["column", "check", "index"]]
        column         check  index
    0  PATIENT  not_nullable      1
    """

    # Define failure_cases_df columns and dtypes
    failure_cases_columns = {
        "schema_context": "str",
        "column": "str",
        "check": "str",
        "check_number": "Int64",
        "failure_case": "str",
        "index": "int64",
    }

    # All records pass validation
    try:
        valid_records_df = schema.validate(input_df, lazy=True)
    # Records fail validation
    except SchemaErrors as e:
        # Create a DataFrame containing all the failures and reasons for failure
        failure_cases_df = e.failure_cases

        ## Table-level failures
        # Handling for problems that cause the entire input dataset to fail validation
        # If something breaks the entire DataFrame (missing entire column), the
        #  failure cases DataFrame would contain a row with index column's value of Nan,
        #  so if there's a single row with NaN in the index column, then we want to fail
        #  the entire batch because the entire batch is impacted
        # Later you could quarantine the entire batch instead as well
        if failure_cases_df["index"].isna().any():
            raise  # table-level failure (missing/extra column): can't split by row, fail the batch
        failure_cases_df = failure_cases_df[list(failure_cases_columns)].astype(
            failure_cases_columns
        )

        ## Row-level failures: split on the failing row indexes
        quarantined_df_index = failure_cases_df["index"].unique()
        quarantined_df = input_df.loc[quarantined_df_index]
        valid_records_df = schema.validate(input_df.drop(index=quarantined_df_index))
    else:
        # Create an empty quarantined_df when no records fail validation
        quarantined_df = input_df.iloc[0:0]
        # Create an empty failure_cases_df when no records fail validation
        failure_cases_df = pd.DataFrame(
            {col: pd.Series(dtype=dtype) for col, dtype in failure_cases_columns.items()}
        )

    return (
        valid_records_df.reset_index(drop=True),
        quarantined_df.reset_index(drop=True),
        failure_cases_df.reset_index(drop=True),
    )


def run_bronze_pipeline(
    batch_date: date, provider: str, table_name: str, schema: type[pa.DataFrameModel]
) -> None:
    """
    Run the Bronze pipeline for a single table: read the landing file,
    validate it against the table's schema, quarantine failing rows, and
    write the rest to the table's Bronze Delta table.

    -> Build landing zone path
    -> Read raw data (all columns as strings)
    -> Validate and split passed/failed rows
    -> Write failed rows and failure reasons to the quarantine tables
    -> Add metadata columns
    -> Write passed rows to the Bronze Delta table

    Every write overwrites only the ``batch_date`` partition, so a failed
    or repeated run can be safely re-run for the same batch.

    Parameters
    ----------
    batch_date : date
        Batch date the file was landed under.
    provider : str
        Name of the data provider.
    table_name : str
        Name of the table.
    schema : type[pa.DataFrameModel]
        Pandera schema defining the table's Bronze data contract.

    Returns
    -------
    None

    Raises
    ------
    pandera.errors.SchemaErrors
        If validation finds a table-level failure. Nothing is written
        for the batch.

    Examples
    --------
    Writes the Bronze table and both quarantine tables:

    >>> run_bronze_pipeline(
    ...     batch_date=date(2026, 9, 1),
    ...     provider="meridian_health",
    ...     table_name="encounters",
    ...     schema=EncountersSchema,
    ... )
    """

    landing_zone_file_path = build_landing_file_path(
        provider=provider, batch_date=batch_date, table_name=table_name
    )

    raw_df = pd.read_csv(filepath_or_buffer=landing_zone_file_path, delimiter=",", dtype=str)

    # Validate and split passed/failed rows
    passed_df, failed_df, failure_cases_df = apply_quarantine_process(
        input_df=raw_df, schema=schema
    )

    # Write to quarantine table
    bronze_failed_df = add_metadata_columns(
        df=failed_df, source_file=landing_zone_file_path, batch_date=batch_date
    )
    write_to_bronze(
        provider=provider,
        table_name=f"{table_name}_quarantine",
        df=bronze_failed_df,
        batch_date=batch_date,
    )

    # Write to quarantine failure reasons table
    bronze_failure_cases_df = add_metadata_columns(
        df=failure_cases_df, source_file=landing_zone_file_path, batch_date=batch_date
    )
    write_to_bronze(
        provider=provider,
        table_name=f"{table_name}_quarantine_failure_cases",
        df=bronze_failure_cases_df,
        batch_date=batch_date,
    )

    bronze_df = add_metadata_columns(
        df=passed_df, source_file=landing_zone_file_path, batch_date=batch_date
    )

    write_to_bronze(provider=provider, table_name=table_name, df=bronze_df, batch_date=batch_date)
