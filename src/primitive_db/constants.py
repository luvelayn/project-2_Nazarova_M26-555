import os
import re

DB_DATA_PATH = "data"
DB_META_PATH = os.path.join(DB_DATA_PATH, "meta", "db_meta.json")
VALID_TYPES = {"int", "str", "bool"}
VALID_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
