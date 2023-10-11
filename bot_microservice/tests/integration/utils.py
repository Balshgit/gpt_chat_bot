from contextlib import contextmanager
from typing import Any, Iterator

import respx
from httpx import Response

from settings.config import settings


@contextmanager
def mocked_ask_question_api(
    host: str, return_value: Response | None = None, side_effect: Any | None = None
) -> Iterator[respx.MockRouter]:
    with respx.mock(
        assert_all_mocked=True,
        assert_all_called=True,
        base_url=host,
    ) as respx_mock:
        ask_question_route = respx_mock.post(url=settings.chatgpt_backend_url, name="ask_question")
        ask_question_route.return_value = return_value
        ask_question_route.side_effect = side_effect
        yield respx_mock
