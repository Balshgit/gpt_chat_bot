import asyncio
from asyncio import AbstractEventLoop
from unittest import mock

import pytest
import telegram
from assertpy import assert_that
from faker import Faker
from httpx import AsyncClient
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from constants import BotStagesEnum
from core.bot import BotApplication, BotQueue
from main import Application
from settings.config import AppSettings
from tests.integration.bot.conftest import mocked_ask_question_api
from tests.integration.bot.networking import MockedRequest
from tests.integration.factories.bot import (
    BotCallBackQueryFactory,
    BotMessageFactory,
    BotUpdateFactory,
    CallBackFactory,
)

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.enable_socket,
]


faker = Faker()


async def test_bot_updates(rest_client: AsyncClient) -> None:
    response = await rest_client.get("/api/healthcheck")
    assert response.status_code == 200


async def test_bot_webhook_endpoint(
    rest_client: AsyncClient,
    main_application: Application,
) -> None:
    bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/help"))
    response = await rest_client.post(url="/api/123456789:AABBCCDDEEFFaabbccddeeff-1234567890", json=bot_update)
    assert response.status_code == 202
    update = await main_application.fastapi_app.state._state["queue"].queue.get()
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

    bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/help"))

    mocked_request = MockedRequest(bot_update)
    await bot_queue.put_updates_on_queue(mocked_request)  # type: ignore
    await asyncio.sleep(1)
    assert bot_queue.queue.empty()


async def test_help_command(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message:
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/help"))

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert_that(mocked_send_message.call_args.kwargs).is_equal_to(
            {
                "text": "Help!",
                "api_kwargs": {"text": "Список основных команд:"},
                "chat_id": bot_update["message"]["chat"]["id"],
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=(
                        (
                            InlineKeyboardButton(callback_data="about_me", text="Обо мне"),
                            InlineKeyboardButton(callback_data="website", text="Веб версия"),
                        ),
                        (
                            InlineKeyboardButton(callback_data="help", text="Помощь"),
                            InlineKeyboardButton(callback_data="about_bot", text="О боте"),
                        ),
                    )
                ),
            },
            include=["text", "api_kwargs", "chat_id", "reply_markup"],
        )


async def test_about_me_callback_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text:
        bot_update = BotCallBackQueryFactory(
            message=BotMessageFactory.create_instance(text="Список основных команд:"),
            callback_query=CallBackFactory(data=BotStagesEnum.about_me),
        )

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == ("Автор бота: *Дмитрий Афанасьев*\n\nTg nickname: *Balshtg*",)
        assert mocked_reply_text.call_args.kwargs == {"parse_mode": "MarkdownV2"}


async def test_about_bot_callback_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text:
        bot_update = BotCallBackQueryFactory(
            message=BotMessageFactory.create_instance(text="Список основных команд:"),
            callback_query=CallBackFactory(data=BotStagesEnum.about_bot),
        )

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == (
            "Бот использует бесплатную модель Chat-GPT3.5 для ответов на вопросы. Принимает запросы на разных языках. "
            "\n\nБот так же умеет переводить голосовые сообщения в текст. Просто пришлите голосовуху и получите поток "
            "сознания без запятых в виде текста",
        )
        assert mocked_reply_text.call_args.kwargs == {"parse_mode": "Markdown"}


async def test_website_callback_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text:
        bot_update = BotCallBackQueryFactory(
            message=BotMessageFactory.create_instance(text="Список основных команд:"),
            callback_query=CallBackFactory(data=BotStagesEnum.website),
        )

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == ("Веб версия: http://localhost/chat/",)


async def test_ask_question_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message, mocked_ask_question_api(host=test_settings.GPT_BASE_HOST):
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="Привет!"))
        bot_update["message"].pop("entities")

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
        assert_that(mocked_send_message.call_args.kwargs).is_equal_to(
            {
                "text": "Привет! Как я могу помочь вам сегодня?",
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )
