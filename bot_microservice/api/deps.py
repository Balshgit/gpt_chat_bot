from fastapi import Depends
from fastapi_users_db_sqlalchemy import SQLAlchemyUserDatabase
from sqlalchemy.ext.asyncio import AsyncSession
from starlette.requests import Request
from telegram import Update

from core.auth.models.users import User
from core.bot.app import BotApplication, BotQueue
from core.bot.repository import ChatGPTRepository
from core.bot.services import ChatGptService
from infra.database.db_adapter import Database
from settings.config import AppSettings


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_bot_app(request: Request) -> BotApplication:
    return request.app.state.bot_app


def get_bot_queue(request: Request) -> BotQueue:
    return request.app.state.queue


def get_db_session(request: Request) -> AsyncSession:
    return request.app.state.db_session_factory()


async def get_update_from_request(request: Request, bot_app: BotApplication = Depends(get_bot_app)) -> Update | None:
    data = await request.json()
    return Update.de_json(data, bot_app.bot)


def get_database(settings: AppSettings = Depends(get_settings)) -> Database:
    return Database(settings=settings)


def get_chatgpt_repository(
    db: Database = Depends(get_database), settings: AppSettings = Depends(get_settings)
) -> ChatGPTRepository:
    return ChatGPTRepository(settings=settings, db=db)


def new_bot_queue(bot_app: BotApplication = Depends(get_bot_app)) -> BotQueue:
    return BotQueue(bot_app=bot_app)


def get_chatgpt_service(
    chatgpt_repository: ChatGPTRepository = Depends(get_chatgpt_repository),
) -> ChatGptService:
    return ChatGptService(repository=chatgpt_repository)


async def get_user_db(  # type: ignore[misc]
    session: AsyncSession = Depends(get_db_session),
) -> SQLAlchemyUserDatabase:  # type: ignore[type-arg]
    yield SQLAlchemyUserDatabase(session, User)
