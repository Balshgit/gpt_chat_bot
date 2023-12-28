import os
from datetime import datetime, timedelta
from functools import cache, wraps
from inspect import cleandoc
from typing import Any, Callable

from constants import MOSCOW_TZ


def timed_lru_cache(
    microseconds: int = 0,
    milliseconds: int = 0,
    seconds: int = 0,
    minutes: int = 0,
    hours: int = 0,
) -> Any:
    def _wrapper(func: Any) -> Callable[[Any], Any]:
        update_delta = timedelta(
            microseconds=microseconds, milliseconds=milliseconds, seconds=seconds, minutes=minutes, hours=hours
        )
        next_update = datetime.now(tz=MOSCOW_TZ) + update_delta

        cached_func = cache(func)

        @wraps(func)
        def _wrapped(*args: Any, **kwargs: Any) -> Callable[[Any], Any]:
            nonlocal next_update
            now = datetime.now(tz=MOSCOW_TZ)
            if now >= next_update:
                cached_func.cache_clear()
                next_update = now + update_delta
            return cached_func(*args, **kwargs)

        return _wrapped

    return _wrapper


def clean_doc(cls: Any) -> str | None:
    if cls.__doc__ is None:
        return None
    return cleandoc(cls.__doc__)


def build_uri(uri_parts: list[str]) -> str:
    parts = [part.strip("/") for part in uri_parts]
    uri = str(os.path.join(*parts)).strip("/")
    return f"/{uri}"
