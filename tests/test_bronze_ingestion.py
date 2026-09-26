from datetime import date

from src.bronze_ingestion import build_bronze_table_path, build_landing_file_path

# Both read HADUR_DATA_ROOT at runtime - hardcoding "data/..." here would assume it's unset
from src.config import BRONZE_ZONE, LANDING_ZONE

PROVIDER = "test_provider"
BATCH_DATE = date(2027, 2, 1)
TABLE_NAME = "test_table_name"
NON_DEFAULT_EXT = ".txt"


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
