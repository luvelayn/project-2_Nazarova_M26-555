import json
import shlex

import prompt
from prettytable import PrettyTable

from .constants import DB_META_PATH
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
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")
    print(
        "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
        "- создать запись"
    )
    print(
        "<command> select from <имя_таблицы> where <столбец> = <значение> "
        "- прочитать записи по условию"
    )
    print("<command> select from <имя_таблицы> - прочитать все записи")
    print(
        "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
        "where <столбец_условия> = <значение_условия> - обновить запись"
    )
    print(
        "<command> delete from <имя_таблицы> where <столбец> = <значение> "
        "- удалить запись"
    )
    print("<command> info <имя_таблицы> - вывести информацию о таблице")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация")


def _parse_command(user_input):
    """Check command syntax and return its name and parsed arguments."""
    try:
        tokens = shlex.split(user_input)
    except ValueError:
        raise ValueError("Некорректная строка в кавычках.") from None

    if not tokens:
        return None, ()
    command, *args = tokens

    match command:
        case "exit" | "help" | "list_tables":
            if args:
                raise ValueError(f"Ожидается: {command}")
            return command, ()
        case "info" | "drop_table":
            if len(args) != 1:
                raise ValueError(f"Ожидается: {command} <имя_таблицы>")
            return command, (args[0],)
        case "create_table":
            if len(args) < 2:
                raise ValueError(
                    "Ожидается: create_table <имя_таблицы> <столбец:тип> ..."
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
            raise ValueError(f"Функции {command} нет. Попробуйте снова.")


def run():
    """Read commands, call database operations and display their results."""
    cache_result = create_cacher()
    print_help()

    while True:
        try:
            metadata = load_metadata(DB_META_PATH)
        except (OSError, ValueError) as error:
            print(f"Не удалось загрузить метаданные: {error}")
            break

        try:
            user_input = prompt.string("\nВведите команду: ")
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
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
                    print("Выход из программы.")
                    break

                case "help":
                    print_help()

                case "list_tables":
                    if not metadata:
                        print("Таблиц пока нет.")
                    for table_name in metadata:
                        print(f"- {table_name}")

                case "create_table":
                    table_name, columns = args
                    updated_metadata = create_table(metadata, table_name, columns)
                    if updated_metadata is None:
                        continue
                    save_table_data(table_name, [])
                    save_metadata(DB_META_PATH, updated_metadata)
                    columns_description = ", ".join(
                        f"{name}:{dtype}"
                        for name, dtype in updated_metadata[table_name].items()
                    )
                    print(
                        f'Таблица "{table_name}" успешно создана '
                        f"со столбцами: {columns_description}."
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
                            f'Таблица "{table_name}" удалена из метаданных, '
                            f"но файл данных удалить не удалось: {error}"
                        )
                    else:
                        print(f'Таблица "{table_name}" успешно удалена.')

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
                    new_id = table_data[-1]["ID"]
                    print(
                        f"Запись с ID={new_id} успешно добавлена "
                        f'в таблицу "{table_name}".'
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
                        print("Подходящие записи не найдены.")
                        continue
                    updated_ids = [row["ID"] for row in matching_rows]
                    table_data = update(table_data, set_clause, where_clause)
                    if table_data is None:
                        continue
                    cache_result = create_cacher()
                    save_table_data(table_name, table_data)
                    for row_id in updated_ids:
                        print(
                            f'Запись с ID={row_id} в таблице "{table_name}" '
                            "успешно обновлена."
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
                        print("Подходящие записи не найдены.")
                        continue
                    deleted_ids = [row["ID"] for row in matching_rows]
                    table_data = delete(table_data, where_clause)
                    if table_data is None:
                        continue
                    cache_result = create_cacher()
                    save_table_data(table_name, table_data)
                    for row_id in deleted_ids:
                        print(
                            f"Запись с ID={row_id} успешно удалена "
                            f'из таблицы "{table_name}".'
                        )

                case "info":
                    (table_name,) = args
                    schema = prepare_table(metadata, table_name)
                    if schema is None:
                        continue
                    table_data = load_table_data(table_name)
                    columns_description = ", ".join(
                        f"{name}:{dtype}" for name, dtype in schema.items()
                    )
                    print(f"Таблица: {table_name}")
                    print(f"Столбцы: {columns_description}")
                    print(f"Количество записей: {len(table_data)}")

        except (OSError, json.JSONDecodeError) as error:
            print(f"Ошибка работы с файлами: {error}")
