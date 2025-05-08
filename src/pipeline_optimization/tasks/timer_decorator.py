import functools
import time


def timer(_func=None, label: str = "_"):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            start = time.perf_counter()
            result = func(*args, **kwargs)
            stop = time.perf_counter()
            print(f"{label}({args}) took {(stop-start)*1000}ms")
            return result

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
