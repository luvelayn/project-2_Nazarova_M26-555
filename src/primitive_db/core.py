from .constants import VALID_NAME_PATTERN, VALID_TYPES


def _validate_name(name):
    if not VALID_NAME_PATTERN.fullmatch(name):
        raise ValueError(
            f"Некорректное имя: {name}. "
            "Допустимы только латинские буквы, цифры и нижнее подчеркивание."
        )


def _parse_columns(columns):
    """Validate column descriptions and return a schema with ID first."""

    if not columns:
        raise ValueError("Ожидается хотя бы один столбец в формате имя:тип.")

    columns_parsed = {}
    for column in columns:
        name, separator, dtype = column.partition(":")
        if not name or not separator or not dtype or ":" in dtype:
            raise ValueError(
                f"Некорректное значение: {column}. Ожидаемый формат: имя:тип"
            )
        _validate_name(name)

        if dtype not in VALID_TYPES:
            raise TypeError(
                f'Некорректный тип для столбца "{name}": {dtype}. '
                "Возможные типы: int, str, bool."
            )
        if name == "ID" and dtype != "int":
            raise TypeError(
                f'Некорректный тип для столбца "ID": {dtype}. Возможный тип: int.'
            )
        if name in columns_parsed:
            raise ValueError("Названия столбцов не могут повторяться.")

        columns_parsed[name] = dtype

    return {"ID": "int", **columns_parsed}


def create_table(metadata, table_name, columns):
    """Validate a table schema and add it to metadata."""

    _validate_name(table_name)

    if table_name in metadata:
        raise ValueError(f'Таблица с именем "{table_name}" уже существует.')

    metadata[table_name] = _parse_columns(columns)
    return metadata


def drop_table(metadata, table_name):
    """Remove an existing table from metadata."""

    _validate_name(table_name)

    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    metadata.pop(table_name)
    return metadata
