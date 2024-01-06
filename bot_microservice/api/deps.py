from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request

from infra.database.db_adapter import Database
from settings.config import AppSettings


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_db_session(request: Request) -> AsyncSession:
    return request.app.state.db_session_factory()


def get_database(settings: AppSettings = Depends(get_settings)) -> Database:
    return Database(settings=settings)
