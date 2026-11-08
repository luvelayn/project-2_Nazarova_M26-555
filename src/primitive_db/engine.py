import json
import shlex

import prompt
from prettytable import PrettyTable

from .constants import (
    COLUMN_TYPE_SEPARATOR,
    COMMAND_PROMPT,
    COMMAND_USAGE,
    DB_META_PATH,
    HELP_LINES,
    ID_COLUMN,
    MESSAGES,
    MIN_CREATE_TABLE_ARGS,
    SCHEMA_DISPLAY_SEPARATOR,
)
from .core import (
    create_table,
    delete,
    drop_table,
    insert,
    prepare_table,
    select,
    update,
)
from .decorators import create_cacher
from .parser import (
    parse_columns,
    parse_delete,
    parse_insert,
    parse_select,
    parse_update,
)
from .utils import (
    delete_table_data,
    load_metadata,
    load_table_data,
    save_metadata,
    save_table_data,
)


def print_help():
    """Print supported commands."""
    print("\n".join(HELP_LINES))


def _parse_command(user_input):
    """Check command syntax and return its name and parsed arguments."""
    try:
        tokens = shlex.split(user_input)
    except ValueError:
        raise ValueError(MESSAGES["invalid_quotes"]) from None

    if not tokens:
        return None, ()
    command, *args = tokens

    match command:
        case "exit" | "help" | "list_tables":
            if args:
                raise ValueError(
                    MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE[command])
                )
            return command, ()
        case "info" | "drop_table":
            if len(args) != 1:
                raise ValueError(
                    MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE[command])
                )
            return command, (args[0],)
        case "create_table":
            if len(args) < MIN_CREATE_TABLE_ARGS:
                raise ValueError(
                    MESSAGES["expected_syntax"].format(usage=COMMAND_USAGE[command])
                )
            return command, (args[0], parse_columns(args[1:]))
        case "insert":
            return command, parse_insert(user_input)
        case "select":
            return command, parse_select(user_input)
        case "update":
            return command, parse_update(user_input)
        case "delete":
            return command, parse_delete(user_input)
        case _:
            raise ValueError(MESSAGES["unknown_command"].format(command=command))


def run():
    """Read commands, call database operations and display their results."""
    cache_result = create_cacher()
    print_help()

    while True:
        try:
            metadata = load_metadata(DB_META_PATH)
        except (OSError, ValueError) as error:
            print(MESSAGES["metadata_error"].format(error=error))
            break

        try:
            user_input = prompt.string(COMMAND_PROMPT)
        except (KeyboardInterrupt, EOFError):
            print("\n" + MESSAGES["exit"])
            break

        try:
            command, args = _parse_command(user_input)
        except ValueError as error:
            print(error)
            continue

        if command is None:
            continue

        try:
            match command:
                case "exit":
                    print(MESSAGES["exit"])
                    break

                case "help":
                    print_help()

                case "list_tables":
                    if not metadata:
                        print(MESSAGES["no_tables"])
                    for table_name in metadata:
                        print(MESSAGES["table_item"].format(table_name=table_name))

                case "create_table":
                    table_name, columns = args
                    updated_metadata = create_table(metadata, table_name, columns)
                    if updated_metadata is None:
                        continue
                    save_table_data(table_name, [])
                    save_metadata(DB_META_PATH, updated_metadata)
                    columns_description = SCHEMA_DISPLAY_SEPARATOR.join(
                        f"{name}{COLUMN_TYPE_SEPARATOR}{dtype}"
                        for name, dtype in updated_metadata[table_name].items()
                    )
                    print(
                        MESSAGES["table_created"].format(
                            table_name=table_name, columns=columns_description
                        )
                    )

                case "drop_table":
                    (table_name,) = args
                    if prepare_table(metadata, table_name) is None:
                        continue
                    updated_metadata = drop_table(metadata, table_name)
                    if updated_metadata is None:
                        continue
                    cache_result = create_cacher()
                    save_metadata(DB_META_PATH, updated_metadata)
                    try:
                        delete_table_data(table_name)
                    except OSError as error:
                        print(
                            MESSAGES["drop_file_error"].format(
                                table_name=table_name, error=error
                            )
                        )
                    else:
                        print(MESSAGES["table_dropped"].format(table_name=table_name))

                case "insert":
                    table_name, values = args
                    if prepare_table(metadata, table_name) is None:
                        continue
                    table_data = load_table_data(table_name)
                    table_data = insert(metadata, table_name, table_data, values)
                    if table_data is None:
                        continue
                    cache_result = create_cacher()
                    save_table_data(table_name, table_data)
                    new_id = table_data[-1][ID_COLUMN]
                    print(
                        MESSAGES["inserted"].format(
                            row_id=new_id, table_name=table_name
                        )
                    )

                case "select":
                    table_name, where_clause = args
                    schema = prepare_table(metadata, table_name, where_clause)
                    if schema is None:
                        continue
                    condition = (
                        None if where_clause is None else tuple(where_clause.items())
                    )
                    cache_key = (table_name, condition)
                    selected_data = cache_result(
                        cache_key,
                        lambda: select(load_table_data(table_name), where_clause),
                    )
                    if selected_data is None:
                        cache_result = create_cacher()
                        continue
                    columns = list(schema)
                    output = PrettyTable()
                    output.field_names = columns
                    output.add_rows(
                        [[row[column] for column in columns] for row in selected_data]
                    )
                    print(output)

                case "update":
                    table_name, set_clause, where_clause = args
                    schema = prepare_table(
                        metadata, table_name, set_clause, where_clause
                    )
                    if schema is None:
                        continue
                    table_data = load_table_data(table_name)
                    matching_rows = select(table_data, where_clause)
                    if matching_rows is None:
                        continue
                    if not matching_rows:
                        print(MESSAGES["no_matches"])
                        continue
                    updated_ids = [row[ID_COLUMN] for row in matching_rows]
                    table_data = update(table_data, set_clause, where_clause)
                    if table_data is None:
                        continue
                    cache_result = create_cacher()
                    save_table_data(table_name, table_data)
                    for row_id in updated_ids:
                        print(
                            MESSAGES["updated"].format(
                                row_id=row_id, table_name=table_name
                            )
                        )

                case "delete":
                    table_name, where_clause = args
                    schema = prepare_table(metadata, table_name, where_clause)
                    if schema is None:
                        continue
                    table_data = load_table_data(table_name)
                    matching_rows = select(table_data, where_clause)
                    if matching_rows is None:
                        continue
                    if not matching_rows:
                        print(MESSAGES["no_matches"])
                        continue
                    deleted_ids = [row[ID_COLUMN] for row in matching_rows]
                    table_data = delete(table_data, where_clause)
                    if table_data is None:
                        continue
                    cache_result = create_cacher()
                    save_table_data(table_name, table_data)
                    for row_id in deleted_ids:
                        print(
                            MESSAGES["deleted"].format(
                                row_id=row_id, table_name=table_name
                            )
                        )

                case "info":
                    (table_name,) = args
                    schema = prepare_table(metadata, table_name)
                    if schema is None:
                        continue
                    table_data = load_table_data(table_name)
                    columns_description = SCHEMA_DISPLAY_SEPARATOR.join(
                        f"{name}{COLUMN_TYPE_SEPARATOR}{dtype}"
                        for name, dtype in schema.items()
                    )
                    print(MESSAGES["table_name"].format(table_name=table_name))
                    print(MESSAGES["table_columns"].format(columns=columns_description))
                    print(MESSAGES["row_count"].format(count=len(table_data)))

        except (OSError, json.JSONDecodeError) as error:
            print(MESSAGES["file_error"].format(error=error))
