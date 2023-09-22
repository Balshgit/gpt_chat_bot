import sys
from datetime import datetime, timedelta
from functools import lru_cache, wraps
from typing import Any

from loguru import logger as loguru_logger

logger = loguru_logger

logger.remove()
logger.add(
    sink=sys.stdout,
    colorize=True,
    level='DEBUG',
    format="<cyan>{time:DD.MM.YYYY HH:mm:ss}</cyan> | <level>{level}</level> | <magenta>{message}</magenta>",
)


def timed_cache(**timedelta_kwargs: Any) -> Any:
    def _wrapper(func: Any) -> Any:
        update_delta = timedelta(**timedelta_kwargs)
        next_update = datetime.utcnow() + update_delta
        # Apply @lru_cache to f with no cache size limit
        cached_func = lru_cache(None)(func)

        @wraps(func)
        def _wrapped(*args: Any, **kwargs: Any) -> Any:
            nonlocal next_update
            now = datetime.utcnow()
            if now >= next_update:
                cached_func.cache_clear()
                next_update = now + update_delta
            return cached_func(*args, **kwargs)

        return _wrapped

    return _wrapper
