import time

import prompt

from .constants import CONFIRMATION_NO, CONFIRMATION_YES, MESSAGES


def handle_db_errors(func):
    """Display database errors and return None if the operation fails."""

    def wrapper(*args, **kwargs):
        """Call the function and handle errors."""
        try:
            return func(*args, **kwargs)
        except FileNotFoundError:
            print(MESSAGES["missing_data_file"])
        except KeyError as error:
            print(MESSAGES["missing_key"].format(key=error))
        except (ValueError, TypeError) as error:
            print(MESSAGES["error"].format(error=error))
        except Exception as error:
            print(MESSAGES["unexpected_error"].format(error=error))
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
                    MESSAGES["confirm_action"].format(
                        action_name=action_name,
                        yes=CONFIRMATION_YES,
                        no=CONFIRMATION_NO,
                    )
                )
            except (KeyboardInterrupt, EOFError):
                answer = ""

            if answer.strip() != CONFIRMATION_YES:
                print(MESSAGES["cancelled"])
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
        print(
            MESSAGES["elapsed_time"].format(
                function_name=func.__name__, duration=duration
            )
        )
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
