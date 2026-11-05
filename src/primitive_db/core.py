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


def insert(metadata, table_name, table_data, values):
    """Validate values against the schema, append a row, and return the table."""
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')

    columns = [
        (column, dtype)
        for column, dtype in metadata[table_name].items()
        if column != "ID"
    ]

    values_num = len(values)
    columns_num = len(columns)
    if values_num != columns_num:
        raise ValueError(f"Ожидается значений: {columns_num}. Передано: {values_num}.")

    max_id = max((raw["ID"] for raw in table_data), default=-1)
    new_raw = {"ID": max_id + 1}

    for (column, dtype), value in zip(columns, values):
        vtype = type(value).__name__
        if vtype != dtype:
            raise TypeError(
                f"Ожидаемый тип для поля {column}: {dtype}. Переданный тип: {vtype}."
            )
        new_raw[column] = value

    table_data.append(new_raw)
    return table_data


def _clause_item(clause, name):
    if not isinstance(clause, dict):
        raise TypeError(f"{name} должен быть словарём.")
    if len(clause) != 1:
        raise ValueError(f"{name} должен содержать ровно одну пару ключ:значение.")
    (item,) = clause.items()
    return item


def _matches(row, column, value):
    return column in row and row[column] == value


def select(table_data, where_clause=None):
    """Return rows matching one condition, or the input list if it is omitted."""
    if where_clause is None:
        return table_data

    column, value = _clause_item(where_clause, "where_clause")
    return [row for row in table_data if _matches(row, column, value)]


def update(table_data, set_clause, where_clause):
    """Update one field in matching rows in place and return the full table."""
    target_column, new_value = _clause_item(set_clause, "set_clause")
    filter_column, filter_value = _clause_item(where_clause, "where_clause")

    for row in table_data:
        if _matches(row, filter_column, filter_value):
            row[target_column] = new_value

    return table_data


def delete(table_data, where_clause):
    """Return a new list excluding rows that match one condition."""
    column, value = _clause_item(where_clause, "where_clause")
    return [row for row in table_data if not _matches(row, column, value)]
