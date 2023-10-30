import asyncio
import os
from asyncio import Queue, sleep
from contextlib import asynccontextmanager
from dataclasses import dataclass
from functools import cached_property
from http import HTTPStatus
from typing import Any, AsyncGenerator

from fastapi import Response
from loguru import logger
from telegram import Bot, Update
from telegram.ext import Application

from settings.config import AppSettings


class BotApplication:
    def __init__(
        self,
        settings: AppSettings,
        handlers: list[Any] | None = None,
    ) -> None:
        self.application: Application = (  # type: ignore[type-arg]
            Application.builder().token(token=settings.TELEGRAM_API_TOKEN).build()
        )
        self.handlers = handlers or []
        self.settings = settings
        self.start_with_webhook = settings.START_WITH_WEBHOOK
        self._add_handlers()

    @property
    def bot(self) -> Bot:
        return self.application.bot

    async def set_webhook(self) -> None:
        _, webhook_info = await asyncio.gather(self.application.initialize(), self.application.bot.get_webhook_info())
        if not webhook_info.url:
            await self.application.bot.set_webhook(url=self.webhook_url)
            webhook_info = await self.application.bot.get_webhook_info()
            logger.info("webhook is set", ip_address=webhook_info.ip_address)

    async def delete_webhook(self) -> None:
        if await self.application.bot.delete_webhook():
            logger.info("webhook has been deleted")

    async def polling(self) -> None:
        if self.settings.STAGE == "runtests":
            return
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()  # type: ignore
        logger.info("bot started in polling mode")

    async def shutdown(self) -> None:
        await asyncio.gather(
            self.delete_webhook(),
            self.application.updater.shutdown(),  # type: ignore[union-attr]
        )
        logger.info("the bot is turned off")

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

    async def put_updates_on_queue(self, tg_update: Update) -> Response:
        """
        Listen /{URL_PREFIX}/{API_PREFIX}/{TELEGRAM_WEB_TOKEN} path and proxy post request to bot
        """
        self.queue.put_nowait(tg_update)
        return Response(status_code=HTTPStatus.ACCEPTED)

    async def get_updates_from_queue(self) -> None:
        while True:
            update = await self.queue.get()
            asyncio.create_task(self.bot_app.application.process_update(update))
            await sleep(0)


@asynccontextmanager
async def get_bot(token: str) -> AsyncGenerator[Bot, None]:
    app = Application.builder().token(token=token).build()
    try:
        yield app.bot
    finally:
        await app.shutdown()
