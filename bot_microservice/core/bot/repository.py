import random
from dataclasses import dataclass
from typing import Any
from uuid import uuid4

import httpx
from httpx import AsyncClient, AsyncHTTPTransport, Response
from loguru import logger
from sqlalchemy import desc, select

from constants import CHAT_GPT_BASE_URI, INVALID_GPT_REQUEST_MESSAGES
from core.bot.models.chat_gpt import ChatGpt
from infra.database.db_adapter import Database
from settings.config import AppSettings


@dataclass
class ChatGPTRepository:
    settings: AppSettings
    db: Database

    async def get_current_chatgpt_model(self) -> str:
        query = select(ChatGpt.model).order_by(desc(ChatGpt.priority)).limit(1)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one()

    async def ask_question(self, question: str, chat_gpt_model: str) -> str:
        try:
            response = await self.request_to_chatgpt_microservice(question=question, chat_gpt_model=chat_gpt_model)
            status = response.status_code
            for message in INVALID_GPT_REQUEST_MESSAGES:
                if message in response.text:
                    message = f"{message}: {chat_gpt_model}"
                    logger.info(message, question=question, chat_gpt_model=chat_gpt_model)
                    return message
            if status != httpx.codes.OK:
                logger.info(f"got response status: {status} from chat api", response.text)
                return "Что-то пошло не так, попробуйте еще раз или обратитесь к администратору"
            return response.text
        except Exception as error:
            logger.error("error get data from chat api", error=error)
        return "Вообще всё сломалось :("

    async def request_to_chatgpt_microservice(self, question: str, chat_gpt_model: str) -> Response:
        data = self._build_request_data(question=question, chat_gpt_model=chat_gpt_model)

        transport = AsyncHTTPTransport(retries=3)
        async with AsyncClient(base_url=self.settings.GPT_BASE_HOST, transport=transport, timeout=50) as client:
            return await client.post(CHAT_GPT_BASE_URI, json=data, timeout=50)

    @staticmethod
    def _build_request_data(*, question: str, chat_gpt_model: str) -> dict[str, Any]:
        return {
            "conversation_id": str(uuid4()),
            "action": "_ask",
            "model": chat_gpt_model,
            "jailbreak": "default",
            "meta": {
                "id": random.randint(10**18, 10**19 - 1),  # noqa: S311
                "content": {
                    "conversation": [],
                    "internet_access": False,
                    "content_type": "text",
                    "parts": [{"content": question, "role": "user"}],
                },
            },
        }
