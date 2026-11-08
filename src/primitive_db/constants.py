import os

DB_DATA_PATH = "data"
DB_META_PATH = os.path.join(DB_DATA_PATH, "meta", "db_meta.json")
VALID_TYPES = {
    "int": int,
    "str": str,
    "bool": bool,
}
