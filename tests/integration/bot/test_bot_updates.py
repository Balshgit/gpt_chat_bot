import asyncio
import time
from asyncio import AbstractEventLoop
from typing import Any

import pytest
from httpx import AsyncClient

from app.core.bot import BotApplication, BotQueue
from app.main import Application
from tests.integration.bot.networking import MockedRequest

pytestmark = [
    pytest.mark.asyncio,
]


async def test_bot_updates(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/healthcheck")

    assert response.status_code == 200


async def test_bot_webhook_endpoint(
    rest_client: AsyncClient,
) -> None:
    response = await rest_client.post(
        url="/api/123456789:AABBCCDDEEFFaabbccddeeff-1234567890",
        json={
            "update_id": 957250703,
            "message": {
                "message_id": 417070387,
                "from": {
                    "id": 1000,
                    "is_bot": "false",
                    "first_name": "William",
                    "last_name": "Dalton",
                    "username": "bolshakovfortunat",
                    "language_code": "ru",
                },
                "chat": {
                    "id": 1,
                    "first_name": "Gabrielle",
                    "last_name": "Smith",
                    "username": "arefi_2019",
                    "type": "private",
                },
                "date": time.time(),
                "text": "/chatid",
                "entities": [{"type": "bot_command", "offset": 0, "length": 7}],
            },
        },
    )
    assert response.status_code == 202


async def test_bot_queue(
    bot: BotApplication,
    bot_application: Any,
    main_application: Application,
    event_loop: AbstractEventLoop,
) -> None:
    bot.application = bot_application
    bot_queue = BotQueue(bot_app=bot)
    event_loop.create_task(bot_queue.get_updates_from_queue())
    mocked_request = MockedRequest(
        {
            "update_id": 957250703,
            "message": {
                "message_id": 417070387,
                "from": {
                    "id": 1000,
                    "is_bot": "false",
                    "first_name": "William",
                    "last_name": "Dalton",
                    "username": "bolshakovfortunat",
                    "language_code": "ru",
                },
                "chat": {
                    "id": 1,
                    "first_name": "Gabrielle",
                    "last_name": "Smith",
                    "username": "arefi_2019",
                    "type": "private",
                },
                "date": time.time(),
                "text": "/chatid",
                "entities": [{"type": "bot_command", "offset": 0, "length": 7}],
            },
        }
    )
    await bot_queue.put_updates_on_queue(mocked_request)  # type: ignore
    await asyncio.sleep(1)
    assert bot_queue.queue.empty()
