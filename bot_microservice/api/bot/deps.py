from fastapi import Depends, Header, HTTPException
from starlette import status
from starlette.requests import Request
from telegram import Update

from api.auth.deps import get_user_service
from api.bot.constants import BOT_ACCESS_API_HEADER
from api.deps import get_database
from core.auth.services import UserService
from core.bot.app import BotApplication, BotQueue
from core.bot.repository import ChatGPTRepository
from core.bot.services import ChatGptService
from infra.database.db_adapter import Database
from settings.config import AppSettings, get_settings, settings


def get_bot_app(request: Request) -> BotApplication:
    return request.app.state.bot_app


def get_bot_queue(request: Request) -> BotQueue:
    return request.app.state.queue


async def get_update_from_request(request: Request, bot_app: BotApplication = Depends(get_bot_app)) -> Update | None:
    data = await request.json()
    return Update.de_json(data, bot_app.bot)


def get_chatgpt_repository(
    db: Database = Depends(get_database), settings: AppSettings = Depends(get_settings)
) -> ChatGPTRepository:
    return ChatGPTRepository(settings=settings, db=db)


def new_bot_queue(bot_app: BotApplication = Depends(get_bot_app)) -> BotQueue:
    return BotQueue(bot_app=bot_app)


def get_chatgpt_service(
    chatgpt_repository: ChatGPTRepository = Depends(get_chatgpt_repository),
    user_service: UserService = Depends(get_user_service),
) -> ChatGptService:
    return ChatGptService(repository=chatgpt_repository, user_service=user_service)


async def get_access_to_bot_api_or_403(
    bot_api_key: str | None = Header(None, alias=BOT_ACCESS_API_HEADER, description="Ключ доступа до API бота"),
    user_service: UserService = Depends(get_user_service),
) -> None:
    access_token = await user_service.get_user_access_token_by_username(settings.SUPERUSER)

    if not access_token or access_token != bot_api_key:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Could not validate api header")
