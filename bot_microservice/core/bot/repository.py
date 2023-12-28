import random
from dataclasses import dataclass
from typing import Any, Sequence
from uuid import uuid4

import httpx
from httpx import AsyncClient, AsyncHTTPTransport, Response
from loguru import logger
from sqlalchemy import delete, desc, select, update
from sqlalchemy.dialects.sqlite import insert

from constants import INVALID_GPT_REQUEST_MESSAGES
from core.bot.models.chatgpt import ChatGptModels
from infra.database.db_adapter import Database
from settings.config import AppSettings


@dataclass
class ChatGPTRepository:
    settings: AppSettings
    db: Database

    async def get_chatgpt_models(self) -> Sequence[ChatGptModels]:
        query = select(ChatGptModels).order_by(desc(ChatGptModels.priority))

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalars().all()

    async def change_chatgpt_model_priority(self, model_id: int, priority: int) -> None:
        query = update(ChatGptModels).values(priority=priority).filter(ChatGptModels.id == model_id)
        async with self.db.get_transaction_session() as session:
            await session.execute(query)

    async def reset_all_chatgpt_models_priority(self) -> None:
        query = update(ChatGptModels).values(priority=0)

        async with self.db.session() as session:
            await session.execute(query)

    async def add_chatgpt_model(self, model: str, priority: int) -> dict[str, str | int]:
        query = (
            insert(ChatGptModels)
            .values(
                {ChatGptModels.model: model, ChatGptModels.priority: priority},
            )
            .prefix_with("OR IGNORE")
        )
        async with self.db.session() as session:
            await session.execute(query)
            await session.commit()
            return {"model": model, "priority": priority}

    async def delete_chatgpt_model(self, model_id: int) -> None:
        query = delete(ChatGptModels).filter_by(id=model_id)

        async with self.db.session() as session:
            await session.execute(query)

    async def get_current_chatgpt_model(self) -> str:
        query = select(ChatGptModels.model).order_by(desc(ChatGptModels.priority)).limit(1)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar_one()

    async def ask_question(self, question: str, chatgpt_model: str) -> str:
        try:
            response = await self.request_to_chatgpt_microservice(question=question, chatgpt_model=chatgpt_model)
            status = response.status_code
            for message in INVALID_GPT_REQUEST_MESSAGES:
                if message in response.text:
                    invalid_model_message = f"{message}: {chatgpt_model}"
                    logger.info(invalid_model_message, question=question, chatgpt_model=chatgpt_model)
                    return invalid_model_message
            if status != httpx.codes.OK:
                logger.info(f"got response status: {status} from chat api", response.text)
                return "Что-то пошло не так, попробуйте еще раз или обратитесь к администратору"
        except Exception as error:
            logger.error("error get data from chat api", error=error)
        else:
            return response.text
        return "Вообще всё сломалось :("

    async def request_to_chatgpt_microservice(self, question: str, chatgpt_model: str) -> Response:
        data = self._build_request_data(question=question, chatgpt_model=chatgpt_model)

        transport = AsyncHTTPTransport(retries=3)
        async with AsyncClient(base_url=self.settings.GPT_BASE_HOST, transport=transport, timeout=50) as client:
            return await client.post(self.settings.chatgpt_backend_url, json=data, timeout=50)

    @staticmethod
    def _build_request_data(*, question: str, chatgpt_model: str) -> dict[str, Any]:
        return {
            "conversation_id": str(uuid4()),
            "action": "_ask",
            "model": chatgpt_model,
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
