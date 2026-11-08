from .constants import VALID_TYPES
from .decorators import confirm_action, handle_db_errors, log_time


def _validate_name(name):
    """Check that a name contains only ASCII letters, digits and underscores."""
    if not name or not name.isascii() or not name.replace("_", "a").isalnum():
        raise ValueError(
            f"Некорректное имя: {name}. "
            "Допустимы только латинские буквы, цифры и нижнее подчеркивание."
        )


def _validate_columns(columns):
    """Validate name/type pairs and return a schema with ID first."""
    schema = {}
    for name, dtype in columns:
        _validate_name(name)

        if dtype not in VALID_TYPES:
            raise TypeError(
                f'Некорректный тип для столбца "{name}": {dtype}. '
                "Возможные типы: int, str, bool."
            )
        if name == "ID" and dtype != "int":
            raise TypeError('Столбец "ID" должен иметь тип int.')
        if name in schema:
            raise ValueError("Имена столбцов не могут повторяться.")

        schema[name] = dtype

    return {"ID": "int", **schema}


@handle_db_errors
def get_table_schema(metadata, table_name):
    """Validate the table name and return its existing schema."""
    _validate_name(table_name)
    if table_name not in metadata:
        raise ValueError(f'Таблица "{table_name}" не существует.')
    return metadata[table_name]


def _validate_value(column, dtype, value):
    """Require value to have exactly the type named by dtype."""
    actual_type = type(value).__name__
    if type(value) is not VALID_TYPES[dtype]:
        raise TypeError(
            f'Ожидаемый тип для столбца "{column}": {dtype}. '
            f"Переданный тип: {actual_type}."
        )


def _clause_item(clause):
    """Extract the single column and value from a clause."""
    (item,) = clause.items()
    return item


@handle_db_errors
def validate_clause(schema, clause):
    """Return True for a valid optional clause or None on a handled error."""
    if clause is None:
        return True

    column, value = _clause_item(clause)
    if column not in schema:
        raise ValueError(f'Не существует столбца с именем "{column}".')
    _validate_value(column, schema[column], value)
    return True


def prepare_table(metadata, table_name, *clauses):
    """Return the table schema after validating the table and supplied clauses.

    Each clause may be None. Return None if a validation error was handled.
    """
    schema = get_table_schema(metadata, table_name)
    if schema is None:
        return None

    for clause in clauses:
        if validate_clause(schema, clause) is None:
            return None

    return schema


@handle_db_errors
def create_table(metadata, table_name, columns):
    """Add a validated schema to metadata in place and return metadata."""
    _validate_name(table_name)
    if table_name in metadata:
        raise ValueError(f'Таблица "{table_name}" уже существует.')

    metadata[table_name] = _validate_columns(columns)
    return metadata


@handle_db_errors
@confirm_action("удаление таблицы")
def drop_table(metadata, table_name):
    """Remove a table schema from metadata in place and return metadata."""
    if get_table_schema(metadata, table_name) is None:
        return None
    metadata.pop(table_name)
    return metadata


@handle_db_errors
@log_time
def insert(metadata, table_name, table_data, values):
    """Return a new list of all rows with a validated row appended."""
    schema = get_table_schema(metadata, table_name)
    if schema is None:
        return None
    columns = [(column, dtype) for column, dtype in schema.items() if column != "ID"]

    if len(values) != len(columns):
        raise ValueError(
            f"Ожидается значений: {len(columns)}. Передано: {len(values)}."
        )

    new_id = max((row["ID"] for row in table_data), default=0) + 1
    new_row = {"ID": new_id}

    for (column, dtype), value in zip(columns, values):
        _validate_value(column, dtype, value)
        new_row[column] = value

    return table_data + [new_row]


def _matches(row, column, value):
    """Return True if the field and value have the same type and are equal."""
    if column not in row:
        raise ValueError(f'Не существует столбца с именем "{column}".')
    return type(row[column]) is type(value) and row[column] == value


@handle_db_errors
@log_time
def select(table_data, where_clause=None):
    """Return a new list containing references to matching rows.

    If where_clause is None, include all rows.
    """
    if where_clause is None:
        return table_data.copy()

    column, value = _clause_item(where_clause)
    return [row for row in table_data if _matches(row, column, value)]


@handle_db_errors
def update(table_data, set_clause, where_clause):
    """Return all rows in a new list, copying and updating matching rows.

    Preserve IDs and leave the input list and row dictionaries unchanged.
    """
    target_column, new_value = _clause_item(set_clause)
    if target_column == "ID":
        raise ValueError('Изменять столбец "ID" запрещено.')

    filter_column, filter_value = _clause_item(where_clause)
    updated_data = []
    for row in table_data:
        if _matches(row, filter_column, filter_value):
            if target_column not in row:
                raise ValueError(f'Не существует столбца с именем "{target_column}".')
            _validate_value(target_column, type(row[target_column]).__name__, new_value)
            row = row.copy()
            row[target_column] = new_value
        updated_data.append(row)

    return updated_data


@handle_db_errors
@confirm_action("удаление записей")
def delete(table_data, where_clause):
    """Return a new list of remaining rows without changing table_data."""
    column, value = _clause_item(where_clause)
    return [row for row in table_data if not _matches(row, column, value)]
