from typing import Any

import pytest
from httpx import AsyncClient, Response
from telegram._utils.defaultvalue import DEFAULT_NONE
from telegram._utils.types import ODVInput
from telegram.error import RetryAfter, TimedOut
from telegram.request import HTTPXRequest, RequestData


class NonchalantHttpxRequest(HTTPXRequest):
    """This Request class is used in the tests to suppress errors that we don't care about
    in the test suite.
    """

    async def _request_wrapper(
        self,
        url: str,
        method: str,
        request_data: RequestData | None = None,
        read_timeout: ODVInput[float] = DEFAULT_NONE,
        write_timeout: ODVInput[float] = DEFAULT_NONE,
        connect_timeout: ODVInput[float] = DEFAULT_NONE,
        pool_timeout: ODVInput[float] = DEFAULT_NONE,
    ) -> bytes:
        try:
            return await super()._request_wrapper(
                method=method,
                url=url,
                request_data=request_data,
                read_timeout=read_timeout,
                write_timeout=write_timeout,
                connect_timeout=connect_timeout,
                pool_timeout=pool_timeout,
            )
        except RetryAfter as e:
            pytest.xfail(f"Not waiting for flood control: {e}")
        except TimedOut as e:
            pytest.xfail(f"Ignoring TimedOut error: {e}")


async def send_webhook_message(
    ip: str,
    port: int,
    payload_str: str | None,
    url_path: str = "",
    content_len: int | None = -1,
    content_type: str = "application/json",
    get_method: str | None = None,
    secret_token: str | None = None,
) -> Response:
    headers = {
        "content-type": content_type,
    }
    if secret_token:
        headers["X-Telegram-Bot-Api-Secret-Token"] = secret_token

    if not payload_str:
        content_len = None
        payload = None
    else:
        payload = bytes(payload_str, encoding="utf-8")

    if content_len == -1:
        content_len = len(payload) if payload else None

    if content_len is not None:
        headers["content-length"] = str(content_len)

    url = f"http://{ip}:{port}/{url_path}"

    async with AsyncClient() as client:
        return await client.request(
            url=url,
            method=get_method or "POST",
            data=payload,  # type: ignore
            headers=headers,
        )


class MockedRequest:
    def __init__(self, data: dict[str, Any]) -> None:
        self.data = data

    async def json(self) -> dict[str, Any]:
        return self.data
