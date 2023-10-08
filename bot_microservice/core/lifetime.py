from asyncio import current_task
from typing import Awaitable, Callable

from fastapi import FastAPI
from sqlalchemy.ext.asyncio import (
    AsyncSession,
    async_scoped_session,
    async_sessionmaker,
    create_async_engine,
)

from settings.config import AppSettings


def startup(app: FastAPI, settings: AppSettings) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application startup.

    This function use fastAPI app to store data,
    such as db_engine.

    :param app: the fastAPI application.
    :param settings: app settings
    :return: function that actually performs actions.

    """

    async def _startup() -> None:
        _setup_db(app, settings)

    return _startup


def shutdown(app: FastAPI) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application's shutdown.

    :param app: fastAPI application.
    :return: function that actually performs actions.

    """

    async def _shutdown() -> None:
        await app.state.db_engine.dispose()

    return _shutdown


def _setup_db(app: FastAPI, settings: AppSettings) -> None:
    """
    Create connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    engine = create_async_engine(
        str(settings.async_db_url),
        echo=settings.DB_ECHO,
        execution_options={"isolation_level": "AUTOCOMMIT"},
    )
    session_factory = async_scoped_session(
        async_sessionmaker(
            engine,
            expire_on_commit=False,
            class_=AsyncSession,
        ),
        scopefunc=current_task,
    )
    app.state.db_engine = engine
    app.state.db_session_factory = session_factory
