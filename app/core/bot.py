import asyncio
import os
from asyncio import Queue, sleep
from dataclasses import dataclass
from functools import cached_property
from http import HTTPStatus
from typing import Any

from fastapi import Request, Response
from telegram import Update
from telegram.ext import Application

from app.core.utils import logger
from settings.config import AppSettings


class BotApplication:
    def __init__(
        self,
        settings: AppSettings,
        handlers: list[Any],
        application: Application | None = None,  # type: ignore[type-arg]
    ) -> None:
        self.application: Application = application or (  # type: ignore
            Application.builder().token(token=settings.TELEGRAM_API_TOKEN).build()
        )
        self.handlers = handlers
        self.settings = settings
        self.start_with_webhook = settings.START_WITH_WEBHOOK
        self._add_handlers()

    async def set_webhook(self) -> None:
        await self.application.initialize()
        await self.application.bot.set_webhook(url=self.webhook_url)
        logger.info('webhook is set')

    async def delete_webhook(self) -> None:
        await self.application.bot.delete_webhook()
        logger.info('webhook has been deleted')

    async def polling(self) -> None:
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()  # type: ignore
        logger.info("bot started in polling mode")

    async def shutdown(self) -> None:
        await self.application.updater.shutdown()  # type: ignore

    @cached_property
    def webhook_url(self) -> str:
        return os.path.join(self.settings.DOMAIN.strip("/"), self.settings.bot_webhook_url.strip("/"))

    def _add_handlers(self) -> None:
        for handler in self.handlers:
            self.application.add_handler(handler)


@dataclass
class BotQueue:
    bot_app: BotApplication
    queue: Queue = asyncio.Queue()  # type: ignore[type-arg]

    async def put_updates_on_queue(self, request: Request) -> Response:
        """
        Listen /{URL_PREFIX}/{API_PREFIX}/{TELEGRAM_WEB_TOKEN} path and proxy post request to bot
        """
        data = await request.json()
        tg_update = Update.de_json(data=data, bot=self.bot_app.application.bot)
        self.queue.put_nowait(tg_update)

        return Response(status_code=HTTPStatus.ACCEPTED)

    async def get_updates_from_queue(self) -> None:
        while True:
            update = await self.queue.get()
            await self.bot_app.application.process_update(update)
            await sleep(0)
