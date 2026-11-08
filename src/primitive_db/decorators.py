import time

import prompt


def handle_db_errors(func):
    """Display database errors and return None if the operation fails."""

    def wrapper(*args, **kwargs):
        """Call the function and handle errors."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(
                "Ошибка: Файл данных не найден. "
                "Возможно, база данных не инициализирована."
            )
        except KeyError as error:
            print(f"Ошибка: Таблица или столбец {error} не найден.")
        except (ValueError, TypeError) as error:
            print(f"Ошибка: {error}")
        except Exception as error:
            print(f"Произошла непредвиденная ошибка: {error}")
        return None

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def confirm_action(action_name):
    """Ask for confirmation before an action; return None if it is cancelled."""

    def decorator(func):
        """Wrap the function with a confirmation prompt."""

        def wrapper(*args, **kwargs):
            """Run the function only after the user enters y."""
            try:
                answer = prompt.string(
                    f'Вы уверены, что хотите выполнить "{action_name}"? [y/n]: '
                )
            except (KeyboardInterrupt, EOFError):
                answer = ""

            if answer.strip() != "y":
                print("Операция отменена.")
                return None
            return func(*args, **kwargs)

        wrapper.__name__ = func.__name__
        wrapper.__doc__ = func.__doc__
        return wrapper

    return decorator


def log_time(func):
    """Display the duration of a successfully completed function call."""

    def wrapper(*args, **kwargs):
        """Measure the function with a monotonic clock and return its result."""
        started = time.monotonic()
        result = func(*args, **kwargs)
        duration = time.monotonic() - started
        print(f"Функция {func.__name__} выполнилась за {duration:.3f} секунд.")
        return result

    wrapper.__name__ = func.__name__
    wrapper.__doc__ = func.__doc__
    return wrapper


def create_cacher():
    """Return a function that caches results in a closure dictionary."""
    cache = {}

    def cache_result(key, value_func):
        """Return the cached result or compute and store it for a new key."""
        if key not in cache:
            cache[key] = value_func()
        return cache[key]

    return cache_result
