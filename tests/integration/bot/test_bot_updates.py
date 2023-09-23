import asyncio
import time
from asyncio import AbstractEventLoop
from typing import Any

import pytest
from assertpy import assert_that
from bot_microservice.core.bot import BotApplication, BotQueue
from bot_microservice.main import Application
from faker import Faker
from httpx import AsyncClient

from tests.integration.bot.networking import MockedRequest
from tests.integration.factories.bot import (
    BotChatFactory,
    BotEntitleFactory,
    BotUserFactory,
)

pytestmark = [
    pytest.mark.asyncio,
]


faker = Faker()


async def test_bot_updates(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/healthcheck")
    assert response.status_code == 200


async def test_bot_webhook_endpoint(
    rest_client: AsyncClient,
    main_application: Application,
) -> None:
    bot_update = create_bot_update()
    response = await rest_client.post(url="/api/123456789:AABBCCDDEEFFaabbccddeeff-1234567890", json=bot_update)
    assert response.status_code == 202
    update = await main_application.state._state["queue"].queue.get()  # type: ignore[attr-defined]
    update = update.to_dict()
    assert update["update_id"] == bot_update["update_id"]
    assert_that(update["message"]).is_equal_to(
        bot_update["message"], include=["from", "entities", "message_id", "text"]
    )


async def test_bot_queue(
    bot: BotApplication,
    event_loop: AbstractEventLoop,
) -> None:
    bot_queue = BotQueue(bot_app=bot)
    event_loop.create_task(bot_queue.get_updates_from_queue())
    bot_update = create_bot_update()
    mocked_request = MockedRequest(bot_update)
    await bot_queue.put_updates_on_queue(mocked_request)  # type: ignore
    await asyncio.sleep(1)
    assert bot_queue.queue.empty()


def create_bot_update() -> dict[str, Any]:
    bot_update: dict[str, Any] = {}
    bot_update["update_id"] = faker.random_int(min=10**8, max=10**9 - 1)
    bot_update["message"] = {
        "message_id": faker.random_int(min=10**8, max=10**9 - 1),
        "from": BotUserFactory()._asdict(),
        "chat": BotChatFactory()._asdict(),
        "date": time.time(),
        "text": "/chatid",
        "entities": [BotEntitleFactory()],
    }
    return bot_update
