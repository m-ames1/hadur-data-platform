import os
from pathlib import Path

# Paths
DATA_ROOT = Path(os.environ.get("HADUR_DATA_ROOT", "data"))
LANDING_ZONE = DATA_ROOT / "landing_zone"
BRONZE_ZONE = DATA_ROOT / "bronze"

# Table names
ENCOUNTERS = "encounters"
