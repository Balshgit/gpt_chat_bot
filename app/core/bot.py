import asyncio
import os
import time
from asyncio import Queue, sleep
from dataclasses import dataclass
from functools import cached_property
from http import HTTPStatus

from fastapi import Request, Response
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

from app.constants import API_PREFIX
from settings.config import Settings


class BotApplication:
    def __init__(self, settings: Settings, start_with_webhook: bool = False) -> None:
        self.application: Application = (  # type: ignore
            Application.builder().token(token=settings.TELEGRAM_API_TOKEN).build()
        )
        self.add_handlers()
        self.settings = settings
        self.start_with_webhook = start_with_webhook

    async def set_webhook(self) -> None:
        await self.application.initialize()
        # await self.application.start()
        await self.application.bot.set_webhook(url=self.webhook_url)

    async def delete_webhook(self) -> None:
        await self.application.bot.delete_webhook()

    @staticmethod
    async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Send a message when the command /help is issued."""

        if update.message:
            await asyncio.sleep(10)
            await update.message.reply_text(
                'Help!',
                disable_notification=True,
                api_kwargs={
                    "text": "Hello World",
                    "date": int(time.time()) + 30,
                    "schedule_date": int(time.time()) + 30,
                },
            )
        return None

    def add_handlers(self) -> None:
        self.application.add_handler(CommandHandler('help', self.help_command))

    async def polling(self) -> None:
        await self.application.initialize()
        await self.application.start()
        await self.application.updater.start_polling()  # type: ignore

    async def shutdown(self) -> None:
        await self.application.updater.shutdown()  # type: ignore

    @cached_property
    def webhook_url(self) -> str:
        return os.path.join(
            self.settings.WEBHOOK_HOST.strip('/'),
            API_PREFIX.strip('/'),
            self.settings.WEBHOOK_PATH.strip('/'),
            self.settings.TELEGRAM_API_TOKEN.strip('/'),
        )


@dataclass
class BotQueue:
    bot_app: Application  # type: ignore[type-arg]
    queue: Queue = asyncio.Queue()  # type: ignore[type-arg]

    async def put_updates_on_queue(self, request: Request) -> Response:
        """
        Listen {WEBHOOK_PATH}/{TELEGRAM_WEB_TOKEN} path and proxy post request to bot
        """
        data = await request.json()
        tg_update = Update.de_json(data=data, bot=self.bot_app.bot)
        self.queue.put_nowait(tg_update)

        return Response(status_code=HTTPStatus.ACCEPTED)

    async def get_updates_from_queue(self) -> None:
        while True:
            update = await self.queue.get()
            print(update)
            await self.bot_app.process_update(update)
            await sleep(0)
