import httpx
import pytest
from faker import Faker
from httpx import AsyncClient, Response

from settings.config import AppSettings
from tests.integration.utils import mocked_ask_question_api

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.enable_socket,
]


faker = Faker()


async def test_bot_updates(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/healthcheck")
    assert response.status_code == 200


async def test_bot_healthcheck_is_ok(
    rest_client: AsyncClient,
    test_settings: AppSettings,
) -> None:
    with mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text="Привет! Как я могу помочь вам сегодня?"),
    ):
        response = await rest_client.get("/api/bot-healthcheck")
        assert response.status_code == httpx.codes.OK


async def test_bot_healthcheck_invalid_request_model(
    rest_client: AsyncClient,
    test_settings: AppSettings,
) -> None:
    with mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text="Invalid request model"),
    ):
        response = await rest_client.get("/api/bot-healthcheck")
        assert response.status_code == httpx.codes.INTERNAL_SERVER_ERROR


async def test_bot_healthcheck_not_ok(
    rest_client: AsyncClient,
    test_settings: AppSettings,
) -> None:
    with mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        side_effect=Exception(),
    ):
        response = await rest_client.get("/api/bot-healthcheck")
        assert response.status_code == httpx.codes.INTERNAL_SERVER_ERROR
