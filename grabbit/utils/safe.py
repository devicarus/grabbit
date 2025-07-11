from typing import Callable, TypeVar, Type, Tuple

from grabbit.logger import logger

T = TypeVar("T")


def safe(getter: Callable[[], T], default: T = None, exceptions: Tuple[Type[BaseException], ...] = (Exception, )) -> T:
    try:
        return getter()
    except exceptions as e:
        logger.debug("Failed safe call, falling back: %s", e)
        return default
