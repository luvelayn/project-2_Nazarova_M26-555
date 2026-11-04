import shlex

import prompt

from .constants import DB_META_PATH
from .core import create_table, drop_table
from .utils import load_metadata, save_metadata


def print_help():
    """Prints the help message for the current mode."""

    print("\n***Процесс работы с таблицей***")
    print("Функции:")
    print("<command> create_table <имя_таблицы> <столбец1:тип> .. - создать таблицу")
    print("<command> list_tables - показать список всех таблиц")
    print("<command> drop_table <имя_таблицы> - удалить таблицу")

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

        input = prompt.string("Введите команду: ")

        try:
            tokens = shlex.split(input)
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
                    print(f"Не удалось сохранить метаданные: {e}")
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
                    drop_table(metadata, table_name)
                    save_metadata(DB_META_PATH, metadata)
                except ValueError as e:
                    print(f"Ошибка: {e}")
                except OSError as e:
                    print(f"Не удалось сохранить метаданные: {e}")
                else:
                    print(f'Таблица "{table_name}" успешно удалена.')

            case _:
                print(f"Функции {command} нет. Попробуйте снова.")
