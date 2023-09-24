import random
import tempfile
from uuid import uuid4

import httpx
from constants import CHAT_GPT_BASE_URL
from core.utils import convert_file_to_wav
from httpx import AsyncClient, AsyncHTTPTransport
from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    if update.message:
        await update.message.reply_text(
            "Help!",
            disable_notification=True,
            api_kwargs={"text": "Hello World"},
        )
    return None


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(  # type: ignore[union-attr]
        "Пожалуйста подождите, ответ в среднем занимает 10-15 секунд"
    )

    chat_gpt_request = {
        "conversation_id": str(uuid4()),
        "action": "_ask",
        "model": "gpt-3.5-turbo",
        "jailbreak": "default",
        "meta": {
            "id": random.randint(10**18, 10**19 - 1),  # noqa: S311
            "content": {
                "conversation": [],
                "internet_access": False,
                "content_type": "text",
                "parts": [{"content": update.message.text, "role": "user"}],  # type: ignore[union-attr]
            },
        },
    }

    transport = AsyncHTTPTransport(retries=1)
    async with AsyncClient(transport=transport) as client:
        try:
            response = await client.post(CHAT_GPT_BASE_URL, json=chat_gpt_request)
            status = response.status_code
            if status != httpx.codes.OK:
                logger.info(f'got response status: {status} from chat api', data=chat_gpt_request)
                await update.message.reply_text(  # type: ignore[union-attr]
                    "Что-то пошло не так, попробуйте еще раз или обратитесь к администратору"
                )
                return

            data = response.json()
            await update.message.reply_text(data)  # type: ignore[union-attr]
        except Exception as error:
            logger.error("error get data from chat api", error=error)
            await update.message.reply_text("Вообще всё сломалось :(")  # type: ignore[union-attr]


async def voice_recognize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(  # type: ignore[union-attr]
        "Пожалуйста, ожидайте :)\nТрехминутная запись обрабатывается примерно 30 секунд"
    )
    sound_bytes = await update.message.voice.get_file()  # type: ignore[union-attr]
    sound_bytes = await sound_bytes.download_as_bytearray()
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(sound_bytes)
        convert_file_to_wav(tmpfile.name)
