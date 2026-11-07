import json
import os

from .constants import DB_DATA_PATH


def _load_json(filepath, default):
    """Read JSON, returning the default if the file does not exist."""
    try:
        with open(filepath, encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        return default


def _save_json(filepath, data):
    """Create the parent directory and write data as JSON."""
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as file:
        json.dump(data, file, ensure_ascii=False, indent=4)


def load_metadata(filepath):
    """Load table schemas or return an empty metadata dictionary."""
    return _load_json(filepath, {})


def save_metadata(filepath, data):
    """Save table schemas to a JSON file."""
    _save_json(filepath, data)


def table_data_path(table_name):
    """Return the JSON file path for a table."""
    return os.path.join(DB_DATA_PATH, f"{table_name}.json")


def load_table_data(table_name):
    """Load table rows or return an empty list if the file is missing."""
    return _load_json(table_data_path(table_name), [])


def save_table_data(table_name, data):
    """Save table rows to a JSON file."""
    _save_json(table_data_path(table_name), data)


def delete_table_data(table_name):
    """Delete the table file if it exists."""
    try:
        os.remove(table_data_path(table_name))
    except FileNotFoundError:
        pass
