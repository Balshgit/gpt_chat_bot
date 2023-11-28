from typing import Awaitable, Callable

from fastapi import FastAPI

from infra.database.db_adapter import Database


def startup(app: FastAPI, database: Database) -> Callable[[], Awaitable[None]]:
    """
    Actions to run on application startup.

    This function use fastAPI app to store data,
    such as db_engine.

    :param app: the fastAPI application.
    :param database: app settings
    :return: function that actually performs actions.

    """

    async def _startup() -> None:
        _setup_db(app, database)

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


def _setup_db(app: FastAPI, database: Database) -> None:
    """
    Create connection to the database.

    This function creates SQLAlchemy engine instance,
    session_factory for creating sessions
    and stores them in the application's state property.

    :param app: fastAPI application.
    """
    app.state.db_engine = database.async_engine
    app.state.db_session_factory = database._async_session_factory
