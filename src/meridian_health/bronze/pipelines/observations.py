# Read -> validate -> stamp provenance -> write/quarantine

# %%
from datetime import date

from src.bronze_ingestion import run_bronze_pipeline
from src.config import OBSERVATIONS
from src.meridian_health import PROVIDER

BATCH_DATE = date(2026, 9, 1)

if __name__ == "__main__":
    run_bronze_pipeline(batch_date=BATCH_DATE, provider=PROVIDER, table_name=OBSERVATIONS)
