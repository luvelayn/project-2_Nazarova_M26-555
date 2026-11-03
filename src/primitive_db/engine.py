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
        command = prompt.string("Введите команду: ")
        metadata = load_metadata(DB_META_PATH)

        match command:
            case "exit":
                break
            case "create_table":
                table_name, *columns = shlex.split(input())
                try:
                    create_table(metadata, table_name, columns)
                except (TypeError, ValueError) as e:
                    print(f"Ошибка: {e}")
                else:
                    save_metadata(DB_META_PATH, metadata)
                    print(
                        f'Таблица "{table_name}" успешно создана со столбцами: '
                        f"{', '.join(columns)}."
                    )
            case "list_tables":
                for table_name in metadata.keys():
                    print(f"- {table_name}")
            case "drop_table":
                table_name = input().strip()
                try:
                    drop_table(metadata, table_name)
                except ValueError as e:
                    print(f"Ошибка: {e}")
                else:
                    save_metadata(DB_META_PATH, metadata)
                    print(f'Таблица "{table_name}" успешно удалена.')
            case "help":
                print_help()
            case _:
                print("Неизвестная команда.\n")
                print_help()
