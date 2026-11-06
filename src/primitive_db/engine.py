import shlex

import prompt

from .constants import DB_META_PATH
from .core import create_table, drop_table
from .utils import delete_table_data, load_metadata, save_metadata


def print_help():
    """Prints the help message."""

    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
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

    print("\nОбщие команды:")
    print("<command> exit - выход из программы")
    print("<command> help - справочная информация\n")


def run():
    print_help()

    while True:
        try:
            metadata = load_metadata(DB_META_PATH)
        except (OSError, ValueError) as e:
            print(f"Не удалось загрузить метаданные: {e}")
            break

        try:
            user_input = prompt.string("Введите команду: ")
        except (KeyboardInterrupt, EOFError):
            print("\nВыход из программы.")
            break

        try:
            tokens = shlex.split(user_input)
        except ValueError:
            print("Некорректный ввод команды. Попробуйте снова.")
            continue

        if not tokens:
            continue

        command, *args = tokens

        if command in {"exit", "help", "list_tables"} and args:
            print(f"Функция {command} не принимает аргументы. Попробуйте снова.")
            continue

        match command:
            case "exit":
                print("Выход из программы.")
                break

            case "help":
                print_help()

            case "list_tables":
                if not metadata:
                    print("Таблиц пока нет.")
                else:
                    for table_name in metadata:
                        print(f"- {table_name}")

            case "create_table":
                if len(args) < 2:
                    print(
                        f"Функция {command} должна принимать как минимум два аргумента."
                        " Попробуйте снова."
                    )
                    continue

                table_name, *columns = args

                try:
                    create_table(metadata, table_name, columns)
                    save_metadata(DB_META_PATH, metadata)
                except (TypeError, ValueError) as e:
                    print(f"Ошибка: {e}")
                except OSError as e:
                    print(f"Не удалось создать таблицу: {e}")
                else:
                    columns_description = ", ".join(
                        f"{name}:{dtype}"
                        for name, dtype in metadata[table_name].items()
                    )

                    print(
                        f'Таблица "{table_name}" успешно создана '
                        f"со столбцами: {columns_description}."
                    )

            case "drop_table":
                if len(args) != 1:
                    print(
                        f"Функция {command} должна принимать один аргумент. "
                        "Попробуйте снова."
                    )
                    continue

                table_name = args[0]

                try:
                    delete_table_data(table_name)
                except OSError as e:
                    print(f"Не удалось удалить таблицу: {e}")
                else:
                    try:
                        drop_table(metadata, table_name)
                        save_metadata(DB_META_PATH, metadata)
                    except ValueError as e:
                        print(f"Ошибка: {e}")
                    except OSError as e:
                        print(
                            f"Не удалось удалить таблицу: {e}. Записи таблицы удалены."
                        )
                    else:
                        print(f'Таблица "{table_name}" успешно удалена.')

            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
