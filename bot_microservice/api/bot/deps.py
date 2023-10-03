from fastapi import Depends
from starlette.requests import Request

from core.bot.services import ChatGptService
from settings.config import AppSettings


def get_settings(request: Request) -> AppSettings:
    return request.app.state.settings


def get_chat_gpt_service(settings: AppSettings = Depends(get_settings)) -> ChatGptService:
    return ChatGptService(settings.GPT_MODEL)
