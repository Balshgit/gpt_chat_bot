import httpx
import pytest
from faker import Faker
from fastapi.responses import ORJSONResponse
from httpx import ASGITransport, AsyncClient, Response
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Session
from starlette import status

from api.exceptions import BaseAPIException
from core.bot.app import BotApplication
from main import Application as AppApplication
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


async def test_server_error_handler_returns_500_without_traceback_when_debug_disabled(
    test_settings: AppSettings,
    bot_app: BotApplication,
) -> None:
    settings = test_settings.model_copy(update={"DEBUG": False})
    fastapi_app = AppApplication(settings=settings, bot_app=bot_app).fastapi_app

    route = "/server-error"

    @fastapi_app.get(route, response_model=None, status_code=status.HTTP_500_INTERNAL_SERVER_ERROR)
    async def controller() -> ORJSONResponse:
        result = 1 / 0
        return ORJSONResponse(content=result, status_code=status.HTTP_200_OK)

    async with AsyncClient(
        transport=ASGITransport(app=fastapi_app, raise_app_exceptions=False),  # type: ignore[arg-type]
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        response = await client.get(route)
    assert response.status_code == 500
    data = response.json()
    assert data == {"error": {"title": "Something went wrong!", "type": "InternalServerError"}, "status": 500}
    replaced_oauth_route = next(
        filter(lambda r: r.path == route, fastapi_app.routes)  # type: ignore[arg-type, attr-defined]
    )
    fastapi_app.routes.remove(replaced_oauth_route)
