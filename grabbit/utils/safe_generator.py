import functools
from typing import Callable, Type, Tuple

def safe_generator(
    exceptions: Tuple[Type[BaseException], ...],
    handler: Callable[[BaseException], None] = lambda e: None
):
    """
    A decorator for generator functions that catches specified exceptions
    on each `yield` and calls the handler, then continues.
    """
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            gen = func(*args, **kwargs)
            while True:
                try:
                    yield next(gen)
                except StopIteration:
                    return
                except exceptions as e:
                    handler(e)
                    continue
        return wrapper
    return decorator
