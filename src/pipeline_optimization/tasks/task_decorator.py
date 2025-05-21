import asyncio
import functools
import random


def task(_func=None, failure_rate: float = 0.1, sleep_time: float = 0.25):
    def decorator(func):
        @functools.wraps(func)
        async def wrapper(*args, **kwargs):
            if sleep_time > 0:
                await asyncio.sleep(sleep_time)
            if random.random() < failure_rate:  # noqa: S311
                msg = "Unexpected error occurred"
                raise ValueError(msg)
            return await func(*args, **kwargs)

        return wrapper

    if _func is None:
        return decorator
    return decorator(_func)
