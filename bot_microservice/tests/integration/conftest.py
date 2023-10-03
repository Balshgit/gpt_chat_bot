"""This module contains subclasses of classes from the python-telegram-bot library that
modify behavior of the respective parent classes in order to make them easier to use in the
pytest framework. A common change is to allow monkeypatching of the class members by not
enforcing slots in the subclasses."""
import asyncio
from asyncio import AbstractEventLoop
from datetime import tzinfo
from typing import Any, AsyncGenerator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pytest_asyncio.plugin import SubRequest
from telegram import Bot, User
from telegram.ext import Application, ApplicationBuilder, Defaults, ExtBot

from core.bot.app import BotApplication
from core.bot.handlers import bot_event_handlers
from main import Application as AppApplication
from settings.config import AppSettings, get_settings
from tests.integration.bot.networking import NonchalantHttpxRequest
from tests.integration.factories.bot import BotInfoFactory, BotUserFactory


@pytest.fixture(scope="session")
def test_settings() -> AppSettings:
    return get_settings()


class PytestExtBot(ExtBot):  # type: ignore
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args: Any, **kwargs: Any) -> User:
        return await _mocked_get_me(self)


class PytestBot(Bot):
    def __init__(self, *args: Any, **kwargs: Any) -> None:
        super().__init__(*args, **kwargs)
        # Makes it easier to work with the bot in tests
        self._unfreeze()

    # Here we override get_me for caching because we don't want to call the API repeatedly in tests
    async def get_me(self, *args: Any, **kwargs: Any) -> User:
        return await _mocked_get_me(self)


class PytestApplication(Application):  # type: ignore
    pass


def make_bot(bot_info: dict[str, Any] | None = None, **kwargs: Any) -> PytestExtBot:
    """
    Tests are executed on tg.ext.ExtBot, as that class only extends the functionality of tg.bot
    """
    token = kwargs.pop("token", (bot_info or {}).get("token"))
    kwargs.pop("token", None)
    return PytestExtBot(
        token=token,
        private_key=None,
        request=NonchalantHttpxRequest(connection_pool_size=8),
        get_updates_request=NonchalantHttpxRequest(connection_pool_size=1),
        **kwargs,
    )


async def _mocked_get_me(bot: Bot) -> User:
    if bot._bot_user is None:
        bot._bot_user = _get_bot_user(bot.token)
    return bot._bot_user


def _get_bot_user(token: str) -> User:
    """Used to return a mock user in bot.get_me(). This saves API calls on every init."""
    bot_info = BotInfoFactory()
    # We don't take token from bot_info, because we need to make a bot with a specific ID. So we
    # generate the correct user_id from the token (token from bot_info is random each test run).
    # This is important in e.g. bot equality tests. The other parameters like first_name don't
    # matter as much. In the future we may provide a way to get all the correct info from the token
    user_id = int(token.split(":")[0])
    first_name = bot_info.get(
        "name",
    )
    username = bot_info.get(
        "username",
    ).strip("@")
    return User(
        user_id,
        first_name,
        is_bot=True,
        username=username,
        can_join_groups=True,
        can_read_all_group_messages=False,
        supports_inline_queries=True,
    )


# Redefine the event_loop fixture to have a session scope. Otherwise `bot` fixture can't be
# session. See https://github.com/pytest-dev/pytest-asyncio/issues/68 for more details.
@pytest.fixture(scope="session")
def event_loop(request: SubRequest) -> AbstractEventLoop:
    """
    Пересоздаем луп для изоляции тестов. В основном нужно для запуска юнит тестов
    в связке с интеграционными, т.к. без этого pytest зависает.
    Для интеграционных тестов фикстура определяется дополнительная фикстура на всю сессию.
    """
    loop = asyncio.get_event_loop_policy().new_event_loop()
    asyncio.set_event_loop(loop)
    return loop


@pytest.fixture(scope="session")
def bot_info() -> dict[str, Any]:
    return BotInfoFactory()


@pytest_asyncio.fixture(scope="session")
async def bot_application(bot_info: dict[str, Any]) -> AsyncGenerator[Any, None]:
    # We build a new bot each time so that we use `app` in a context manager without problems
    application = ApplicationBuilder().bot(make_bot(bot_info)).application_class(PytestApplication).build()
    await application.initialize()
    yield application
    if application.running:
        await application.stop()
        await application.shutdown()


@pytest_asyncio.fixture(scope="session")
async def bot(bot_info: dict[str, Any], bot_application: Any) -> AsyncGenerator[PytestExtBot, None]:
    """Makes an ExtBot instance with the given bot_info"""
    async with make_bot(bot_info) as _bot:
        _bot.application = bot_application
        yield _bot


@pytest.fixture()
def one_time_bot(bot_info: dict[str, Any], bot_application: Any) -> PytestExtBot:
    """A function scoped bot since the session bot would shutdown when `async with app` finishes"""
    bot = make_bot(bot_info)
    bot.application = bot_application
    return bot


@pytest_asyncio.fixture(scope="session")
async def cdc_bot(bot_info: dict[str, Any], bot_application: Any) -> AsyncGenerator[PytestExtBot, None]:
    """Makes an ExtBot instance with the given bot_info that uses arbitrary callback_data"""
    async with make_bot(bot_info, arbitrary_callback_data=True) as _bot:
        _bot.application = bot_application
        yield _bot


@pytest_asyncio.fixture(scope="session")
async def raw_bot(bot_info: dict[str, Any], bot_application: Any) -> AsyncGenerator[PytestBot, None]:
    """Makes an regular Bot instance with the given bot_info"""
    async with PytestBot(
        bot_info["token"],
        private_key=None,
        request=NonchalantHttpxRequest(8),
        get_updates_request=NonchalantHttpxRequest(1),
    ) as _bot:
        _bot.application = bot_application
        yield _bot


# Here we store the default bots so that we don't have to create them again and again.
# They are initialized but not shutdown on pytest_sessionfinish because it is causing
# problems with the event loop (Event loop is closed).
_default_bots: dict[Defaults, PytestExtBot] = {}


@pytest_asyncio.fixture(scope="session")
async def default_bot(request: SubRequest, bot_info: dict[str, Any]) -> PytestExtBot:
    param = request.param if hasattr(request, "param") else {}
    defaults = Defaults(**param)

    # If the bot is already created, return it. Else make a new one.
    default_bot = _default_bots.get(defaults)
    if default_bot is None:
        default_bot = make_bot(bot_info, defaults=defaults)
        await default_bot.initialize()
        _default_bots[defaults] = default_bot  # Defaults object is hashable
    return default_bot


@pytest_asyncio.fixture(scope="session")
async def tz_bot(timezone: tzinfo, bot_info: dict[str, Any]) -> PytestExtBot:
    defaults = Defaults(tzinfo=timezone)
    try:  # If the bot is already created, return it. Saves time since get_me is not called again.
        return _default_bots[defaults]
    except KeyError:
        default_bot = make_bot(bot_info, defaults=defaults)
        await default_bot.initialize()
        _default_bots[defaults] = default_bot
        return default_bot


@pytest.fixture(scope="session")
def chat_id(bot_info: dict[str, Any]) -> int:
    return bot_info["chat_id"]


@pytest.fixture(scope="session")
def super_group_id(bot_info: dict[str, Any]) -> int:
    return bot_info["super_group_id"]


@pytest.fixture(scope="session")
def forum_group_id(bot_info: dict[str, Any]) -> int:
    return int(bot_info["forum_group_id"])


@pytest.fixture(scope="session")
def channel_id(bot_info: dict[str, Any]) -> int:
    return bot_info["channel_id"]


@pytest.fixture(scope="session")
def provider_token(bot_info: dict[str, Any]) -> str:
    return bot_info["payment_provider_token"]


@pytest_asyncio.fixture(scope="session")
async def main_application(
    bot_application: PytestApplication, test_settings: AppSettings
) -> AsyncGenerator[AppApplication, None]:
    bot_app = BotApplication(
        settings=test_settings,
        handlers=bot_event_handlers.handlers,
    )
    bot_app.application._initialized = True
    bot_app.application.bot = make_bot(BotInfoFactory())
    bot_app.application.bot._bot_user = BotUserFactory()
    fast_api_app = AppApplication(settings=test_settings, bot_app=bot_app)
    yield fast_api_app


@pytest_asyncio.fixture()
async def rest_client(
    main_application: AppApplication,
) -> AsyncGenerator[AsyncClient, None]:
    """
    Default http client. Use to test unauthorized requests, public endpoints
    or special authorization methods.
    """
    async with AsyncClient(
        app=main_application.fastapi_app,
        base_url="http://test",
        headers={"Content-Type": "application/json"},
    ) as client:
        yield client
