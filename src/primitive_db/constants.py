import os

# Storage format and paths.
DB_DATA_PATH = "data"
DB_META_PATH = os.path.join(DB_DATA_PATH, "meta", "db_meta.json")
TABLE_FILE_EXTENSION = ".json"
FILE_ENCODING = "utf-8"
JSON_INDENT = 4

# Schema rules and supported value literals.
VALID_TYPES = {"int": int, "str": str, "bool": bool}
VALID_TYPE_NAMES = ", ".join(VALID_TYPES)
ID_COLUMN = "ID"
ID_TYPE = "int"
FIRST_ID = 1
NAME_EXTRA_CHARACTERS = "_"
BOOLEAN_LITERALS = {"true": True, "false": False}

# Command grammar. Token counts include the command name itself.
COLUMN_TYPE_SEPARATOR = ":"
VALUE_SEPARATOR = ","
ASSIGNMENT_OPERATOR = "="
OPEN_PAREN = "("
CLOSE_PAREN = ")"
STRING_QUOTE = '"'
COMMAND_PUNCTUATION = OPEN_PAREN + CLOSE_PAREN + VALUE_SEPARATOR + ASSIGNMENT_OPERATOR
TOKEN_DELIMITERS = COMMAND_PUNCTUATION + STRING_QUOTE
CLAUSE_TOKEN_COUNT = 3
VALUE_TOKEN_STEP = 2  # Values and separators alternate: value, comma, value.
INSERT_MIN_TOKEN_COUNT = 6
SELECT_ALL_TOKEN_COUNT = 3
SELECT_WHERE_TOKEN_COUNT = 7
UPDATE_TOKEN_COUNT = 10
DELETE_TOKEN_COUNT = 7
MIN_CREATE_TABLE_ARGS = 2  # Table name and at least one column description.

COMMAND_USAGE = {
    "exit": "exit",
    "help": "help",
    "list_tables": "list_tables",
    "info": "info <имя_таблицы>",
    "drop_table": "drop_table <имя_таблицы>",
    "create_table": "create_table <имя_таблицы> <столбец:тип> ...",
    "insert": "insert into <имя_таблицы> values (<значение1>, ...)",
    "select": "select from <имя_таблицы> [where <столбец> = <значение>]",
    "update": (
        "update <имя_таблицы> set <столбец> = <значение> where <столбец> = <значение>"
    ),
    "delete": "delete from <имя_таблицы> where <столбец> = <значение>",
}

# Terminal prompts and formatting.
COMMAND_PROMPT = "\nВведите команду: "
CONFIRMATION_YES = "y"
CONFIRMATION_NO = "n"
ACTION_NAMES = {"drop_table": "удаление таблицы", "delete": "удаление записей"}
SCHEMA_DISPLAY_SEPARATOR = ", "

MESSAGES = {
    "invalid_name": (
        "Некорректное имя: {name}. "
        "Допустимы только латинские буквы, цифры и нижнее подчеркивание."
    ),
    "unsupported_type": (
        'Некорректный тип для столбца "{column}": {dtype}. '
        "Возможные типы: {valid_types}."
    ),
    "id_type": f'Столбец "{ID_COLUMN}" должен иметь тип {ID_TYPE}.',
    "duplicate_columns": "Имена столбцов не могут повторяться.",
    "missing_table": 'Таблица "{table_name}" не существует.',
    "existing_table": 'Таблица "{table_name}" уже существует.',
    "wrong_type": (
        'Ожидаемый тип для столбца "{column}": {dtype}. Переданный тип: {actual_type}.'
    ),
    "value_count": "Ожидается значений: {expected}. Передано: {actual}.",
    "missing_column": 'Не существует столбца с именем "{column}".',
    "id_update": f'Изменять столбец "{ID_COLUMN}" запрещено.',
    "invalid_value": "Некорректное значение: {value}. Попробуйте снова.",
    "invalid_quotes": "Некорректная строка в кавычках.",
    "invalid_quoted_string": "Некорректная строка в двойных кавычках.",
    "invalid_value_list": "Значения должны быть разделены запятыми.",
    "invalid_clause": f"Ожидается условие: столбец {ASSIGNMENT_OPERATOR} значение.",
    "expected_syntax": "Ожидается: {usage}",
    "unknown_command": "Функции {command} нет. Попробуйте снова.",
    "error": "Ошибка: {error}",
    "file_error": "Ошибка работы с файлами: {error}",
    "metadata_error": "Не удалось загрузить метаданные: {error}",
    "exit": "Выход из программы.",
    "no_tables": "Таблиц пока нет.",
    "table_item": "- {table_name}",
    "table_created": (
        'Таблица "{table_name}" успешно создана со столбцами: {columns}.'
    ),
    "table_dropped": 'Таблица "{table_name}" успешно удалена.',
    "drop_file_error": (
        'Таблица "{table_name}" удалена из метаданных, '
        "но файл данных удалить не удалось: {error}"
    ),
    "inserted": 'Запись с ID={row_id} успешно добавлена в таблицу "{table_name}".',
    "updated": 'Запись с ID={row_id} в таблице "{table_name}" успешно обновлена.',
    "deleted": 'Запись с ID={row_id} успешно удалена из таблицы "{table_name}".',
    "no_matches": "Подходящие записи не найдены.",
    "table_name": "Таблица: {table_name}",
    "table_columns": "Столбцы: {columns}",
    "row_count": "Количество записей: {count}",
    "missing_data_file": (
        "Ошибка: Файл данных не найден. Возможно, база данных не инициализирована."
    ),
    "missing_key": "Ошибка: Таблица или столбец {key} не найден.",
    "unexpected_error": "Произошла непредвиденная ошибка: {error}",
    "cancelled": "Операция отменена.",
    "confirm_action": (
        'Вы уверены, что хотите выполнить "{action_name}"? [{yes}/{no}]: '
    ),
    "elapsed_time": ("Функция {function_name} выполнилась за {duration:.3f} секунд."),
}

HELP_LINES = (
    "Функции:",
    "<command> create_table <имя_таблицы> <столбец1:тип> ... - создать таблицу",
    "<command> list_tables - показать список всех таблиц",
    "<command> drop_table <имя_таблицы> - удалить таблицу",
    "<command> insert into <имя_таблицы> values (<значение1>, <значение2>, ...) "
    "- создать запись",
    "<command> select from <имя_таблицы> where <столбец> = <значение> "
    "- прочитать записи по условию",
    "<command> select from <имя_таблицы> - прочитать все записи",
    "<command> update <имя_таблицы> set <столбец1> = <новое_значение1> "
    "where <столбец_условия> = <значение_условия> - обновить запись",
    "<command> delete from <имя_таблицы> where <столбец> = <значение> - удалить запись",
    "<command> info <имя_таблицы> - вывести информацию о таблице",
    "<command> exit - выход из программы",
    "<command> help - справочная информация",
)
