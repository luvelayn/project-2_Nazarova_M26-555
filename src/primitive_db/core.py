from .constants import DB_META_PATH, VALID_NAME_PATTERN, VALID_TYPES
from .utils import save_metadata


def _validate_name(name: str, entity: str) -> None:
    if not VALID_NAME_PATTERN.fullmatch(name):
        raise ValueError(
            f"Некорректное имя {entity}: {name}. "
            "Допустимы только латинские буквы, цифры и нижнее подчеркивание."
        )


def _parse_columns(columns: list[str]) -> dict[str, str]:
    columns_parsed = {"ID": "int"}

    for column in columns:
        key, separator, val = column.partition(":")

        if not separator or not key or not val:
            raise ValueError(f"Некорректное описание столбца: {column}.")

        if key == "ID":
            continue

        _validate_name(key, "столбца")

        if val not in VALID_TYPES:
            raise TypeError(
                f"Некорректный тип для столбца {key}: {val}. "
                "Возможные типы: int, str, bool."
            )

        if key in columns_parsed:
            raise ValueError("Названия столбцов не могут повторяться.")

        columns_parsed[key] = val

    return columns_parsed


def create_table(
    metadata: dict[str, dict[str, str]], table_name: str, columns: list[str]
) -> dict[str, dict[str, str]]:

    _validate_name(table_name, "таблицы")

    if table_name in metadata:
        raise ValueError(f"Таблица с именем {table_name} уже существует.")

    metadata[table_name] = _parse_columns(columns)

    save_metadata(DB_META_PATH, metadata)

    return metadata


def drop_table(
    metadata: dict[str, dict[str, str]], table_name: str
) -> dict[str, dict[str, str]]:

    if table_name not in metadata:
        raise ValueError(f"Таблица {table_name} не существует.")

    metadata.pop(table_name)
    save_metadata(DB_META_PATH, metadata)

    return metadata
