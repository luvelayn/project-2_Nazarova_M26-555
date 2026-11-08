import json

from .constants import (
    ASSIGNMENT_OPERATOR,
    BOOLEAN_LITERALS,
    CLAUSE_TOKEN_COUNT,
    CLOSE_PAREN,
    COLUMN_TYPE_SEPARATOR,
    COMMAND_PUNCTUATION,
    COMMAND_USAGE,
    DELETE_TOKEN_COUNT,
    INSERT_MIN_TOKEN_COUNT,
    MESSAGES,
    OPEN_PAREN,
    SELECT_ALL_TOKEN_COUNT,
    SELECT_WHERE_TOKEN_COUNT,
    STRING_QUOTE,
    TOKEN_DELIMITERS,
    UPDATE_TOKEN_COUNT,
    VALID_TYPES,
    VALUE_SEPARATOR,
    VALUE_TOKEN_STEP,
)


def parse_columns(columns):
    """Parse name:type descriptions into pairs, preserving order."""
    parsed_columns = []
    for column in columns:
        name, separator, dtype = column.partition(COLUMN_TYPE_SEPARATOR)
        if not name or not separator or not dtype or COLUMN_TYPE_SEPARATOR in dtype:
            raise ValueError(MESSAGES["invalid_value"].format(value=column))
        parsed_columns.append((name, dtype))

    return parsed_columns


def _split_command(user_input):
    """Split a command into words, quoted strings and punctuation."""
    tokens = []
    text = user_input.strip()
    decoder = json.JSONDecoder()

    while text:
        if text[0] == STRING_QUOTE:
            try:
                _, end = decoder.raw_decode(text)
            except json.JSONDecodeError:
                raise ValueError(MESSAGES["invalid_quoted_string"])
        elif text[0] in COMMAND_PUNCTUATION:
            end = 1
        else:
            end = 0
            while (
                end < len(text)
                and not text[end].isspace()
                and text[end] not in TOKEN_DELIMITERS
            ):
                end += 1

        tokens.append(text[:end])
        text = text[end:].lstrip()

    return tokens


def _parse_value(text):
    """Parse an integer, a quoted string or a case-insensitive boolean."""
    normalized_text = text.lower()
    if normalized_text in BOOLEAN_LITERALS:
        return BOOLEAN_LITERALS[normalized_text]

    error_message = MESSAGES["invalid_value"].format(value=text)
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
    if len(tokens) % VALUE_TOKEN_STEP == 0 or any(
        token != VALUE_SEPARATOR for token in tokens[1::VALUE_TOKEN_STEP]
    ):
        raise ValueError(MESSAGES["invalid_value_list"])

    return [_parse_value(token) for token in tokens[::VALUE_TOKEN_STEP]]


def _parse_clause(tokens):
    """Parse one column = value condition or assignment."""
    if len(tokens) != CLAUSE_TOKEN_COUNT or tokens[1] != ASSIGNMENT_OPERATOR:
        raise ValueError(MESSAGES["invalid_clause"])

    column, _, value = tokens
    return {column: _parse_value(value)}


def parse_insert(user_input):
    """Return the table name and values from an insert command."""
    tokens = _split_command(user_input)
    if (
        len(tokens) < INSERT_MIN_TOKEN_COUNT
        or tokens[:2] != ["insert", "into"]
        or tokens[3:5] != ["values", OPEN_PAREN]
        or tokens[-1] != CLOSE_PAREN
    ):
        raise ValueError(
            MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE["insert"])
        )

    return tokens[2], _parse_values(tokens[5:-1])


def parse_select(user_input):
    """Return the table name and optional condition from a select command."""
    tokens = _split_command(user_input)
    if len(tokens) == SELECT_ALL_TOKEN_COUNT and tokens[:2] == ["select", "from"]:
        return tokens[2], None
    if (
        len(tokens) == SELECT_WHERE_TOKEN_COUNT
        and tokens[:2] == ["select", "from"]
        and tokens[3] == "where"
    ):
        return tokens[2], _parse_clause(tokens[4:])

    raise ValueError(MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE["select"]))


def parse_update(user_input):
    """Return the table name, assignment, and condition from an update command."""
    tokens = _split_command(user_input)
    if (
        len(tokens) != UPDATE_TOKEN_COUNT
        or tokens[0] != "update"
        or tokens[2] != "set"
        or tokens[6] != "where"
    ):
        raise ValueError(
            MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE["update"])
        )

    return tokens[1], _parse_clause(tokens[3:6]), _parse_clause(tokens[7:])


def parse_delete(user_input):
    """Return the table name and condition from a delete command."""
    tokens = _split_command(user_input)
    if (
        len(tokens) != DELETE_TOKEN_COUNT
        or tokens[:2] != ["delete", "from"]
        or tokens[3] != "where"
    ):
        raise ValueError(
            MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE["delete"])
        )

    return tokens[2], _parse_clause(tokens[4:])
