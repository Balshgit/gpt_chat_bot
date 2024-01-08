import asyncio
import datetime
from unittest import mock

import httpx
import pytest
import telegram
from assertpy import assert_that
from faker import Faker
from httpx import AsyncClient, Response
from sqlalchemy.orm import Session
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update

from constants import BotStagesEnum
from core.auth.models.users import User, UserQuestionCount
from core.bot.app import BotApplication, BotQueue
from main import Application
from settings.config import AppSettings
from tests.integration.bot.networking import MockedRequest
from tests.integration.factories.bot import (
    BotCallBackQueryFactory,
    BotMessageFactory,
    BotUpdateFactory,
    CallBackFactory,
    ChatGptModelFactory,
)
from tests.integration.factories.user import UserFactory, UserQuestionCountFactory
from tests.integration.utils import mocked_ask_question_api

pytestmark = [
    pytest.mark.asyncio,
    pytest.mark.enable_socket,
]


faker = Faker()


async def test_bot_webhook_endpoint(
    rest_client: AsyncClient,
    main_application: Application,
) -> None:
    bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/help"))
    response = await rest_client.post(url="/api/CDDEEFFaabbccdd", json=bot_update)
    assert response.status_code == 202
    update = await main_application.bot_queue.queue.get()
    update = update.to_dict()
    assert update["update_id"] == bot_update["update_id"]
    assert_that(update["message"]).is_equal_to(
        bot_update["message"], include=["from", "entities", "message_id", "text"]
    )


async def test_bot_queue(
    bot: BotApplication,
) -> None:
    bot_queue = BotQueue(bot_app=bot)
    asyncio.create_task(bot_queue.get_updates_from_queue())

    bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/help"))

    mocked_request = MockedRequest(bot_update)
    await bot_queue.put_updates_on_queue(mocked_request)  # type: ignore
    await asyncio.sleep(1)
    assert bot_queue.queue.empty()


async def test_no_update_message(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message:
        bot_update = BotUpdateFactory(message=None)

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_send_message.called is False


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
                            InlineKeyboardButton(callback_data="github", text="GitHub"),
                            InlineKeyboardButton(callback_data="about_bot", text="О боте"),
                        ),
                    )
                ),
            },
            include=["text", "api_kwargs", "chat_id", "reply_markup"],
        )


async def test_help_command_user_is_banned(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    message = BotMessageFactory.create_instance(text="/help")
    user = message["from"]
    UserFactory(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        username=user["username"],
        is_active=False,
        ban_reason="test reason",
    )
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message:
        bot_update = BotUpdateFactory(message=message)

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
    assert mocked_send_message.call_args.kwargs["text"] == (
        "You have banned for reason: *test reason*.\nPlease contact the /developer"
    )


async def test_start_entry(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message:
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/start"))

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert_that(mocked_send_message.call_args_list[0].kwargs).is_equal_to(
            {
                "text": "Выберете команду:",
                "chat_id": bot_update["message"]["chat"]["id"],
                "reply_markup": InlineKeyboardMarkup(
                    inline_keyboard=(
                        (
                            InlineKeyboardButton(callback_data="about_me", text="Обо мне"),
                            InlineKeyboardButton(callback_data="website", text="Веб версия"),
                        ),
                        (
                            InlineKeyboardButton(callback_data="github", text="GitHub"),
                            InlineKeyboardButton(callback_data="about_bot", text="О боте"),
                        ),
                    )
                ),
            },
            include=["text", "chat_id", "reply_markup"],
        )
        assert_that(mocked_send_message.call_args_list[1].kwargs).is_equal_to(
            {
                "text": "Список этих команд всегда можно получить набрав /help",
                "chat_id": bot_update["message"]["chat"]["id"],
                "reply_markup": None,
            },
            include=["text", "chat_id", "reply_markup"],
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


async def test_github_callback_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text:
        bot_update = BotCallBackQueryFactory(
            message=BotMessageFactory.create_instance(text="Список основных команд:"),
            callback_query=CallBackFactory(data=BotStagesEnum.github),
        )

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == ("Проект на [GitHub](https://github.com/Balshgit/gpt_chat_bot)",)
        assert mocked_reply_text.call_args.kwargs == {"parse_mode": "Markdown"}


async def test_about_bot_callback_action(
    dbsession: Session,
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory(priority=0)
    model_with_highest_priority = ChatGptModelFactory(priority=1)
    with mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text:
        bot_update = BotCallBackQueryFactory(
            message=BotMessageFactory.create_instance(text="Список основных команд:"),
            callback_query=CallBackFactory(data=BotStagesEnum.about_bot),
        )

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == (
            f"Бот использует бесплатную модель *{model_with_highest_priority.model}* для ответов на вопросы.\n"
            f"Принимает запросы на разных языках.",
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


async def test_website_callback_action_user_is_banned(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    message = BotMessageFactory.create_instance(text="Список основных команд:")
    user = message["from"]
    UserFactory(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        username=user["username"],
        is_active=False,
        ban_reason="test reason",
    )
    with mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text:
        bot_update = BotCallBackQueryFactory(
            message=message,
            callback_query=CallBackFactory(data=BotStagesEnum.website),
        )

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.kwargs["text"] == (
            "You have banned for reason: *test reason*.\nPlease contact the /developer"
        )


async def test_bug_report_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with (
        mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text,
        mock.patch.object(
            telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
        ) as mocked_send_message,
    ):
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/bug_report"))

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == (
            "Спасибо за баг репорт.\n"
            "Можете попробовать воспользоваться веб версией /website, выбрав различные GPT модели",
        )
        from_user = bot_update["message"]["from"]
        assert mocked_send_message.call_args.kwargs["text"] == (
            f"Bug report from user: "
            f"User(first_name='{from_user['first_name']}', id={from_user['id']}, is_bot={from_user['is_bot']}, "
            f"language_code='{from_user['language_code']}', last_name='{from_user['last_name']}', "
            f"username='{from_user['username']}')"
        )


async def test_bug_report_action_user_is_banned(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    message = BotMessageFactory.create_instance(text="/bug_report")
    user = message["from"]
    UserFactory(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        username=user["username"],
        is_active=False,
        ban_reason="test reason",
    )
    with (
        mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text,
        mock.patch.object(telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)),
    ):
        bot_update = BotUpdateFactory(message=message)

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.kwargs["text"] == (
            "You have banned for reason: *test reason*.\nPlease contact the /developer"
        )


async def test_get_developer_action(
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    with (
        mock.patch.object(telegram._message.Message, "reply_text") as mocked_reply_text,
        mock.patch.object(telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)),
    ):
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="/developer"))

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )

        assert mocked_reply_text.call_args.args == ("Автор бота: *Дмитрий Афанасьев*\n\nTg nickname: *Balshtg*",)


async def test_ask_question_action_bot_user_not_exists(
    dbsession: Session,
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    users = dbsession.query(User).all()
    users_question_count = dbsession.query(UserQuestionCount).all()

    assert len(users) == 0
    assert len(users_question_count) == 0

    message = BotMessageFactory.create_instance(text="Привет!")
    user = message["from"]

    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message, mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text="Привет! Как я могу помочь вам сегодня?"),
    ):
        bot_update = BotUpdateFactory(message=message)
        bot_update["message"].pop("entities")

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
        assert_that(mocked_send_message.call_args_list[0].kwargs).is_equal_to(
            {
                "text": (
                    "Ответ в среднем занимает 10-15 секунд.\n- Список команд: /help\n- Сообщить об ошибке: /bug_report"
                ),
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )
        assert_that(mocked_send_message.call_args_list[1].kwargs).is_equal_to(
            {
                "text": "Привет! Как я могу помочь вам сегодня?",
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )

    created_user = dbsession.query(User).filter_by(id=user["id"]).one()
    assert created_user.username == user["username"]

    created_user_question_count = dbsession.query(UserQuestionCount).filter_by(user_id=user["id"]).one()
    assert created_user_question_count.question_count == 1
    assert created_user_question_count.last_question_at - datetime.datetime.now() < datetime.timedelta(  # noqa: DTZ005
        seconds=2
    )


async def test_ask_question_action_bot_user_already_exists(
    dbsession: Session,
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    message = BotMessageFactory.create_instance(text="Привет!")
    user = message["from"]
    existing_user = UserFactory(
        id=user["id"], first_name=user["first_name"], last_name=user["last_name"], username=user["username"]
    )
    existing_user_question_count = UserQuestionCountFactory(user_id=existing_user.id).question_count

    users = dbsession.query(User).all()
    assert len(users) == 1

    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message, mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text="Привет! Как я могу помочь вам сегодня?"),
    ):
        bot_update = BotUpdateFactory(message=message)
        bot_update["message"].pop("entities")

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
        assert_that(mocked_send_message.call_args_list[0].kwargs).is_equal_to(
            {
                "text": (
                    "Ответ в среднем занимает 10-15 секунд.\n- Список команд: /help\n- Сообщить об ошибке: /bug_report"
                ),
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )
        assert_that(mocked_send_message.call_args_list[1].kwargs).is_equal_to(
            {
                "text": "Привет! Как я могу помочь вам сегодня?",
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )

    users = dbsession.query(User).all()
    assert len(users) == 1

    updated_user_question_count = dbsession.query(UserQuestionCount).filter_by(user_id=user["id"]).one()
    assert updated_user_question_count.question_count == existing_user_question_count + 1
    assert updated_user_question_count.last_question_at - datetime.datetime.now() < datetime.timedelta(  # noqa: DTZ005
        seconds=2
    )


async def test_ask_question_action_user_is_banned(
    dbsession: Session,
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)

    users_question_count = dbsession.query(UserQuestionCount).all()
    assert len(users_question_count) == 0

    message = BotMessageFactory.create_instance(text="Привет!")
    user = message["from"]
    UserFactory(
        id=user["id"],
        first_name=user["first_name"],
        last_name=user["last_name"],
        username=user["username"],
        is_active=False,
        ban_reason="test reason",
    )

    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message, mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        return_value=Response(status_code=httpx.codes.OK, text="Привет! Как я могу помочь вам сегодня?"),
        assert_all_called=False,
    ):
        bot_update = BotUpdateFactory(message=message)
        bot_update["message"].pop("entities")

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
        assert_that(mocked_send_message.call_args_list[0].kwargs).is_equal_to(
            {
                "text": ("You have banned for reason: *test reason*.\nPlease contact the /developer"),
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )

    created_user = dbsession.query(User).filter_by(id=user["id"]).one()
    assert created_user.username == user["username"]
    assert created_user.is_active is False

    created_user_question_count = dbsession.query(UserQuestionCount).filter_by(user_id=user["id"]).scalar()
    assert created_user_question_count is None


async def test_ask_question_action_not_success(
    dbsession: Session,
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message, mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST, return_value=Response(status_code=httpx.codes.INTERNAL_SERVER_ERROR)
    ):
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="Привет!"))
        bot_update["message"].pop("entities")

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
        assert_that(mocked_send_message.call_args.kwargs).is_equal_to(
            {
                "text": "Что-то пошло не так, попробуйте еще раз или обратитесь к администратору",
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )


async def test_ask_question_action_critical_error(
    dbsession: Session,
    main_application: Application,
    test_settings: AppSettings,
) -> None:
    ChatGptModelFactory.create_batch(size=3)
    with mock.patch.object(
        telegram._bot.Bot, "send_message", return_value=lambda *args, **kwargs: (args, kwargs)
    ) as mocked_send_message, mocked_ask_question_api(
        host=test_settings.GPT_BASE_HOST,
        side_effect=Exception(),
    ):
        bot_update = BotUpdateFactory(message=BotMessageFactory.create_instance(text="Привет!"))
        bot_update["message"].pop("entities")

        await main_application.bot_app.application.process_update(
            update=Update.de_json(data=bot_update, bot=main_application.bot_app.bot)
        )
        assert_that(mocked_send_message.call_args.kwargs).is_equal_to(
            {
                "text": "Вообще всё сломалось :(",
                "chat_id": bot_update["message"]["chat"]["id"],
            },
            include=["text", "chat_id"],
        )
