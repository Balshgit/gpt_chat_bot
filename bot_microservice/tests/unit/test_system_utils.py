import time
from typing import Callable

import pytest
from fastapi.responses import ORJSONResponse
from httpx import ASGITransport, AsyncClient
from starlette import status

from core.bot.app import BotApplication
from core.bot.handlers import bot_event_handlers
from core.utils import timed_lru_cache
from main import Application as AppApplication
from settings.config import AppSettings

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.enable_socket,
]


class TestTimedLruCache:
    call_count: int = 0

    def sum_two_numbers(self, first: int, second: int) -> int:
        self.call_count += 1
        return first + second

    def test_timed_lru_cache_cached_for_1_second(self) -> None:
        self.call_count = 0

        tested_func = timed_lru_cache(seconds=1)(self.sum_two_numbers)

        self._call_function_many_times(call_times=2, func=tested_func, first=2, second=40, result=42)
        time.sleep(0.5)
        self._call_function_many_times(call_times=4, func=tested_func, first=2, second=40, result=42)
        time.sleep(1)
        self._call_function_many_times(call_times=3, func=tested_func, first=2, second=40, result=42)
        assert tested_func(2, 2) == 4
        assert self.call_count == 3

    def test_timed_lru_cache_cached_for_long_time(self) -> None:
        self.call_count = 0

        tested_func = timed_lru_cache(minutes=5)(self.sum_two_numbers)

        self._call_function_many_times(call_times=3, func=tested_func, first=2, second=40, result=42)
        time.sleep(0.2)
        self._call_function_many_times(call_times=4, func=tested_func, first=2, second=40, result=42)
        time.sleep(0.2)
        self._call_function_many_times(call_times=2, func=tested_func, first=2, second=40, result=42)
        assert tested_func(2, 2) == 4
        assert self.call_count == 2

    def test_timed_lru_cache_cached_for_short_time(self) -> None:
        self.call_count = 0

        tested_func = timed_lru_cache(milliseconds=200)(self.sum_two_numbers)

        self._call_function_many_times(call_times=2, func=tested_func, first=2, second=40, result=42)
        time.sleep(0.3)
        self._call_function_many_times(call_times=5, func=tested_func, first=2, second=40, result=42)
        time.sleep(0.3)
        self._call_function_many_times(call_times=7, func=tested_func, first=2, second=40, result=42)
        time.sleep(0.3)
        self._call_function_many_times(call_times=3, func=tested_func, first=2, second=40, result=42)
        assert tested_func(2, 2) == 4
        assert self.call_count == 5

    @staticmethod
    def _call_function_many_times(
        call_times: int, func: Callable[[int, int], int], first: int, second: int, result: int
    ) -> None:
        for _ in range(call_times):
            assert func(first, second) == result


async def test_server_error_handler_returns_500_without_traceback_when_debug_disabled(
    test_settings: AppSettings,
) -> None:
    bot_app = BotApplication(
        settings=test_settings,
        handlers=bot_event_handlers.handlers,
    )
    settings = test_settings.model_copy(update={"DEBUG": False})
    fastapi_app = AppApplication(settings=settings, bot_app=bot_app).fastapi_app

    @fastapi_app.get("/server-error", response_model=None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    async def controller() -> ORJSONResponse:
        result = 1 / 0
        return ORJSONResponse(content=result, status_code=status.HTTP_200_OK)

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app, raise_app_exceptions=False),  # type: ignore[arg-type]
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        response = await client.get("/server-error")
    assert response.status_code == 500
