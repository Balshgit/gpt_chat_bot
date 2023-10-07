import httpx
import pytest
from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session

from api.exceptions import BaseAPIException
from settings.config import AppSettings
from tests.integration.factories.bot import ChatGptModelFactory
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
    dbsession: Session,
    rest_client: AsyncClient,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    with mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text="Привет! Как я могу помочь вам сегодня?"),
    ):
        response = await rest_client.get("/api/bot-healthcheck")
        assert response.status_code == httpx.codes.OK


@pytest.mark.parametrize("text", ["Invalid request model", "return unexpected http status code"])
async def test_bot_healthcheck_invalid_request_model(
    dbsession: AsyncSession, rest_client: AsyncClient, test_settings: AppSettings, text: str
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    with mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text=text),
    ):
        response = await rest_client.get("/api/bot-healthcheck")
        assert response.status_code == httpx.codes.INTERNAL_SERVER_ERROR


async def test_bot_healthcheck_not_ok(
    dbsession: Session,
    rest_client: AsyncClient,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    with mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        side_effect=BaseAPIException(),
    ):
        response = await rest_client.get("/api/bot-healthcheck")
        assert response.status_code == httpx.codes.INTERNAL_SERVER_ERROR
