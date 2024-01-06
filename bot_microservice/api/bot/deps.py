from fastapi import Depends
from starlette.requests import Request
from telegram import Update

from api.auth.deps import get_user_service
from api.deps import get_database
from core.auth.services import UserService
from core.bot.app import BotApplication, BotQueue
from core.bot.repository import ChatGPTRepository
from core.bot.services import ChatGptService
from infra.database.db_adapter import Database
from settings.config import AppSettings, get_settings


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
