from fastapi import Depends
from starlette.requests import Request
from telegram import Update

from core.bot.app import BotApplication, BotQueue
from core.bot.repository import ChatGPTRepository
from core.bot.services import ChatGptService, SpeechToTextService
from infra.database.db_adapter import Database
from settings.config import AppSettings


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_bot_app(request: Request) -> BotApplication:
    return request.app.state.bot_app


def get_bot_queue(request: Request) -> BotQueue:
    return request.app.state.queue


async def get_update_from_request(request: Request, bot_app: BotApplication = Depends(get_bot_app)) -> Update | None:
    data = await request.json()
    return Update.de_json(data, bot_app.bot)


def get_database(settings: AppSettings = Depends(get_settings)) -> Database:
    return Database(settings=settings)


def get_chat_gpt_repository(
    db: Database = Depends(get_database), settings: AppSettings = Depends(get_settings)
) -> ChatGPTRepository:
    return ChatGPTRepository(settings=settings, db=db)


def get_speech_to_text_service() -> SpeechToTextService:
    return SpeechToTextService()


def new_bot_queue(bot_app: BotApplication = Depends(get_bot_app)) -> BotQueue:
    return BotQueue(bot_app=bot_app)


def get_chatgpt_service(
    chat_gpt_repository: ChatGPTRepository = Depends(get_chat_gpt_repository),
) -> ChatGptService:
    return ChatGptService(repository=chat_gpt_repository)
