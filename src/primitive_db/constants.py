import os
import re

DB_META_PATH = os.path.join("data", "db_meta.json")
VALID_TYPES = {"int", "str", "bool"}
VALID_NAME_PATTERN = re.compile(r"^[a-zA-Z0-9_]+$")
