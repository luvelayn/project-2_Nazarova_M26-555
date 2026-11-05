import json
import os

from .constants import DB_DATA_PATH


def load_metadata(filepath):
    try:
        with open(filepath, encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}


def save_metadata(filepath, data):
    directory = os.path.dirname(filepath)
    if directory:
        os.makedirs(directory, exist_ok=True)
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def load_table_data(table_name):
    filepath = os.path.join(DB_DATA_PATH, f"{table_name}.json")
    with open(filepath, encoding="utf-8") as f:
        return json.load(f)


def table_data_path(table_name):
    return os.path.join(DB_DATA_PATH, f"{table_name}.json")


def save_table_data(table_name, data):
    filepath = os.path.join(DB_DATA_PATH, f"{table_name}.json")
    with open(filepath, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=4)


def delete_table_data(table_name):
    try:
        os.remove(table_data_path(table_name))
    except FileNotFoundError:
        pass
