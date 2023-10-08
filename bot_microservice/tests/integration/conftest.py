import asyncio
from asyncio import AbstractEventLoop
from typing import Any, AsyncGenerator, Generator

import pytest
import pytest_asyncio
from httpx import AsyncClient
from pytest_asyncio.plugin import SubRequest
from sqlalchemy import Engine, create_engine
from sqlalchemy.orm import Session, sessionmaker
from telegram import Bot, User
from telegram.ext import Application, ApplicationBuilder, ExtBot

from core.bot.app import BotApplication
from core.bot.handlers import bot_event_handlers
from infra.database.db_adapter import Database
from infra.database.meta import meta
from main import Application as AppApplication
from settings.config import AppSettings, get_settings
from tests.integration.bot.networking import NonchalantHttpxRequest
from tests.integration.factories.bot import BotInfoFactory, BotUserFactory


@pytest.fixture(scope="session")
def test_settings() -> AppSettings:
    return get_settings()


@pytest.fixture(scope="session")
def engine(test_settings: AppSettings) -> Generator[Engine, None, None]:
    """
    Create engine and databases.

    :yield: new engine.
    """
    engine: Engine = create_engine(
        str(test_settings.sync_db_url),
        echo=test_settings.DB_ECHO,
        isolation_level="AUTOCOMMIT",
    )

    try:
        yield engine
    finally:
        engine.dispose()


@pytest_asyncio.fixture(scope="function")
def dbsession(engine: Engine) -> Generator[Session, None, None]:
    """
    Get session to database.

    Fixture that returns a SQLAlchemy session with a SAVEPOINT, and the rollback to it
    after the test completes.

    :param engine: current engine.
    :yields: async session.
    """
    connection = engine.connect()
    trans = connection.begin()

    session_maker = sessionmaker(
        connection,
        expire_on_commit=False,
    )
    session = session_maker()

    try:
        meta.create_all(engine)
        yield session
    finally:
        meta.drop_all(engine)
        session.close()
        trans.rollback()
        connection.close()


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
@pytest.fixture(scope="session", autouse=True)
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
    database = Database(test_settings)
    await database.create_database()
    yield fast_api_app
    await database.drop_database()


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
