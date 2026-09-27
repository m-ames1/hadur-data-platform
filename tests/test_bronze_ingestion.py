from datetime import date, datetime, timezone
from pathlib import Path

import pandas as pd
import pytest
from freezegun import freeze_time
from pandas.testing import assert_frame_equal

from src.bronze_ingestion import (
    add_metadata_columns,
    build_bronze_table_path,
    build_landing_file_path,
)

# Both read HADUR_DATA_ROOT at runtime - hardcoding "data/..." here would assume it's unset
from src.config import BRONZE_ZONE, LANDING_ZONE

PROVIDER = "test_provider"
BATCH_DATE = date(2027, 2, 1)
TABLE_NAME = "test_table_name"
NON_DEFAULT_EXT = ".txt"
SOURCE_FILE_PATH = Path("test/path/test_table_name.csv")
INGESTED_AT = datetime(2027, 2, 5, 12, 0, 0, tzinfo=timezone.utc)


def test_build_landing_file_path_default_extension():
    landing_zone_file_path = build_landing_file_path(
        provider=PROVIDER, batch_date=BATCH_DATE, table_name=TABLE_NAME
    )
    assert (
        landing_zone_file_path
        == LANDING_ZONE / "test_provider" / "2027-02-01" / "test_table_name.csv"
    )


def test_build_landing_file_path_custom_extension():
    landing_zone_file_path = build_landing_file_path(
        provider=PROVIDER, batch_date=BATCH_DATE, table_name=TABLE_NAME, ext=NON_DEFAULT_EXT
    )
    assert (
        landing_zone_file_path
        == LANDING_ZONE / "test_provider" / "2027-02-01" / "test_table_name.txt"
    )


def test_build_bronze_table_path():
    bronze_table_path = build_bronze_table_path(provider=PROVIDER, table_name=TABLE_NAME)
    assert bronze_table_path == BRONZE_ZONE / "test_provider" / "test_table_name"


@freeze_time(INGESTED_AT)
def test_add_metadata_columns():
    input_data = {"col1": ["abc"], "col2": ["def"]}
    input_df = pd.DataFrame(input_data)

    expected_data = {
        "col1": ["abc"],
        "col2": ["def"],
        "_source_file": [str(SOURCE_FILE_PATH)],
        "_ingested_at": [INGESTED_AT],
        "_batch_date": [pd.Timestamp(BATCH_DATE)],
    }
    expected_df = pd.DataFrame(expected_data)

    actual_df = add_metadata_columns(
        df=input_df, source_file=SOURCE_FILE_PATH, batch_date=BATCH_DATE
    )

    assert_frame_equal(actual_df, expected_df)


# TODO: Add write_to_bronze() unit test
@pytest.mark.skip(reason="not implemented")
def test_write_to_bronze():
    pass
