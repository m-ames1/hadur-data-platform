from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
from deltalake import write_deltalake

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
    Write a batch of records to a provider's Bronze Delta table.

    Overwrites only the partition matching ``batch_date``, so re-running
    an ingestion for the same batch replaces that batch's rows instead of
    appending duplicates or overwriting the entire table.

    Parameters
    ----------
    provider : str
        Name of the data provider.
    table_name : str
        Name of the table.
    df : pd.DataFrame
        DataFrame to write, expected to already contain the metadata
        columns added by ``add_metadata_columns``.
    batch_date : date
        Batch date the data belongs to; used as the partition key and
        the overwrite predicate.

    Returns
    -------
    None
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
