import json

from .constants import VALID_TYPES


def parse_columns(columns):
    """Parse name:type descriptions into pairs, preserving order."""
    parsed_columns = []
    for column in columns:
        name, separator, dtype = column.partition(":")
        if not name or not separator or not dtype or ":" in dtype:
            raise ValueError(f"Некорректное значение: {column}. Попробуйте снова.")
        parsed_columns.append((name, dtype))

    return parsed_columns


def _split_command(user_input):
    """Split a command into words, quoted strings and punctuation."""
    tokens = []
    text = user_input.strip()
    decoder = json.JSONDecoder()

    while text:
        if text[0] == '"':
            try:
                _, end = decoder.raw_decode(text)
            except json.JSONDecodeError:
                raise ValueError("Некорректная строка в двойных кавычках.")
        elif text[0] in "(),=":
            end = 1
        else:
            end = 0
            while (
                end < len(text) and not text[end].isspace() and text[end] not in '(),="'
            ):
                end += 1

        tokens.append(text[:end])
        text = text[end:].lstrip()

    return tokens


def _parse_value(text):
    """Parse an integer, a quoted string or a case-insensitive boolean."""
    if text.lower() == "true":
        return True
    if text.lower() == "false":
        return False

    error_message = f"Некорректное значение: {text}. Попробуйте снова."
    try:
        value = json.loads(text)
    except json.JSONDecodeError:
        raise ValueError(error_message) from None

    if type(value) not in VALID_TYPES.values():
        raise ValueError(error_message)

    return value


def _parse_values(tokens):
    """Parse comma-separated values inside one pair of parentheses."""
    if not tokens:
        return []
    if len(tokens) % 2 == 0 or any(token != "," for token in tokens[1::2]):
        raise ValueError("Значения должны быть разделены запятыми.")

    return [_parse_value(token) for token in tokens[::2]]


def _parse_clause(tokens):
    """Parse one column = value condition or assignment."""
    if len(tokens) != 3 or tokens[1] != "=":
        raise ValueError("Ожидается условие: столбец = значение.")

    column, _, value = tokens
    return {column: _parse_value(value)}


def parse_insert(user_input):
    """Return the table name and values from an insert command."""
    tokens = _split_command(user_input)
    if (
        len(tokens) < 6
        or tokens[:2] != ["insert", "into"]
        or tokens[3:5] != ["values", "("]
        or tokens[-1] != ")"
    ):
        raise ValueError(
            "Ожидается: insert into <имя_таблицы> values (<значение1>, ...)"
        )

    return tokens[2], _parse_values(tokens[5:-1])


def parse_select(user_input):
    """Return the table name and optional condition from a select command."""
    tokens = _split_command(user_input)
    if len(tokens) == 3 and tokens[:2] == ["select", "from"]:
        return tokens[2], None
    if len(tokens) == 7 and tokens[:2] == ["select", "from"] and tokens[3] == "where":
        return tokens[2], _parse_clause(tokens[4:])

    raise ValueError(
        "Ожидается: select from <имя_таблицы> [where <столбец> = <значение>]"
    )


def parse_update(user_input):
    """Return the table name, assignment, and condition from an update command."""
    tokens = _split_command(user_input)
    if (
        len(tokens) != 10
        or tokens[0] != "update"
        or tokens[2] != "set"
        or tokens[6] != "where"
    ):
        raise ValueError(
            "Ожидается: update <имя_таблицы> set <столбец> = <значение> "
            "where <столбец> = <значение>"
        )

    return tokens[1], _parse_clause(tokens[3:6]), _parse_clause(tokens[7:])


def parse_delete(user_input):
    """Return the table name and condition from a delete command."""
    tokens = _split_command(user_input)
    if len(tokens) != 7 or tokens[:2] != ["delete", "from"] or tokens[3] != "where":
        raise ValueError(
            "Ожидается: delete from <имя_таблицы> where <столбец> = <значение>"
        )

    return tokens[2], _parse_clause(tokens[4:])
