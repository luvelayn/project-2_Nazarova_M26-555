import re
from pathlib import Path

DB_META_PATH = Path(__file__).resolve().parents[2] / "data" / "db_meta.json"
VALID_TYPES = {"int", "str", "bool"}
VALID_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
