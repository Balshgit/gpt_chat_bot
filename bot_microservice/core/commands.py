import asyncio
import random
import tempfile
from urllib.parse import urljoin
from uuid import uuid4

import httpx
from httpx import AsyncClient, AsyncHTTPTransport
from loguru import logger
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import CHAT_GPT_BASE_URL, BotEntryPoints
from core.keyboards import main_keyboard
from core.utils import SpeechToTextService
from settings.config import settings


async def main_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Send message on `/start`."""
    if not update.message:
        return BotEntryPoints.end
    reply_markup = InlineKeyboardMarkup(main_keyboard)
    await update.message.reply_text("Выберете команду:", reply_markup=reply_markup)
    return BotEntryPoints.start_routes


async def about_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return None
    await update.effective_message.reply_text(
        'Автор бота: *Дмитрий Афанасьев*\n\nTg nickname: *Balshtg*', parse_mode='MarkdownV2'
    )


async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return None
    await update.effective_message.reply_text(
        "Бот использует бесплатную модель Chat-GPT3.5 для ответов на вопросы. "
        "Принимает запросы на разных языках. \n\nБот так же умеет переводить голосовые сообщения в текст. "
        "Просто пришлите голосовуху и получите поток сознания без запятых в виде текста",
        parse_mode='Markdown',
    )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return None
    website = urljoin(settings.DOMAIN, f"{settings.URL_PREFIX}/chat/")
    await update.effective_message.reply_text(f"Веб версия: {website}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    if not update.effective_message:
        return None
    reply_markup = InlineKeyboardMarkup(main_keyboard)
    await update.effective_message.reply_text(
        "Help!",
        disable_notification=True,
        api_kwargs={"text": "Список основных команд:"},
        reply_markup=reply_markup,
    )


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return None

    await update.message.reply_text("Пожалуйста подождите, ответ в среднем занимает 10-15 секунд")

    chat_gpt_request = {
        "conversation_id": str(uuid4()),
        "action": "_ask",
        "model": settings.GPT_MODEL,
        "jailbreak": "default",
        "meta": {
            "id": random.randint(10**18, 10**19 - 1),  # noqa: S311
            "content": {
                "conversation": [],
                "internet_access": False,
                "content_type": "text",
                "parts": [{"content": update.message.text, "role": "user"}],
            },
        },
    }

    transport = AsyncHTTPTransport(retries=3)
    async with AsyncClient(transport=transport, timeout=50) as client:
        try:
            response = await client.post(CHAT_GPT_BASE_URL, json=chat_gpt_request, timeout=50)
            status = response.status_code
            if status != httpx.codes.OK:
                logger.info(f'got response status: {status} from chat api', data=chat_gpt_request)
                await update.message.reply_text(
                    "Что-то пошло не так, попробуйте еще раз или обратитесь к администратору"
                )
                return

            await update.message.reply_text(response.text)
        except Exception as error:
            logger.error("error get data from chat api", error=error)
            await update.message.reply_text("Вообще всё сломалось :(")


async def voice_recognize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return None
    await update.message.reply_text("Пожалуйста, ожидайте :)\nТрехминутная запись обрабатывается примерно 30 секунд")
    if not update.message.voice:
        return None

    sound_file = await update.message.voice.get_file()
    sound_bytes = await sound_file.download_as_bytearray()
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(sound_bytes)

    logger.info('file has been saved', filename=tmpfile.name)

    speech_to_text_service = SpeechToTextService(filename=tmpfile.name)

    speech_to_text_service.get_text_from_audio()

    part = 0
    while speech_to_text_service.text_parts or not speech_to_text_service.text_recognised:
        if text := speech_to_text_service.text_parts.get(part):
            speech_to_text_service.text_parts.pop(part)
            await update.message.reply_text(text)
            part += 1
        await asyncio.sleep(5)
