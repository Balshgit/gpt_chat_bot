import time
from typing import Callable

from core.utils import timed_lru_cache


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
