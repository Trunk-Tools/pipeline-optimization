import functools
import random


def task(_func=None, failure_rate: float = 0.1):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            if random.random() < failure_rate:  # noqa: S311
                msg = "Unexpected error occurred"
                raise ValueError(msg)
            return func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
