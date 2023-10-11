import asyncio
import tempfile
from urllib.parse import urljoin

from loguru import logger
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import BotEntryPoints
from core.bot.keyboards import main_keyboard
from core.bot.services import ChatGptService, SpeechToTextService
from settings.config import settings


async def main_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Send message on `/start`."""
    if not update.message:
        return BotEntryPoints.end
    reply_markup = InlineKeyboardMarkup(main_keyboard)
    await update.message.reply_text("Выберете команду:", reply_markup=reply_markup)
    return BotEntryPoints.start_routes


async def about_me(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    await update.effective_message.reply_text(
        "Автор бота: *Дмитрий Афанасьев*\n\nTg nickname: *Balshtg*", parse_mode="MarkdownV2"
    )


async def about_bot(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    chatgpt_service = ChatGptService.build()
    model = await chatgpt_service.get_current_chatgpt_model()
    await update.effective_message.reply_text(
        f"Бот использует бесплатную модель {model} для ответов на вопросы. "
        f"\nПринимает запросы на разных языках.\n\nБот так же умеет переводить русские голосовые сообщения в текст. "
        f"Просто пришлите голосовуху и получите поток сознания в виде текста, но без знаков препинания",
        parse_mode="Markdown",
    )


async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    website = urljoin(settings.DOMAIN, f"{settings.chat_prefix}/")
    await update.effective_message.reply_text(f"Веб версия: {website}")


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    if not update.effective_message:
        return
    reply_markup = InlineKeyboardMarkup(main_keyboard)
    await update.effective_message.reply_text(
        "Help!",
        disable_notification=True,
        api_kwargs={"text": "Список основных команд:"},
        reply_markup=reply_markup,
    )


async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text("Пожалуйста подождите, ответ в среднем занимает 10-15 секунд")

    chatgpt_service = ChatGptService.build()
    logger.warning("question asked", user=update.message.from_user, question=update.message.text)
    answer = await chatgpt_service.request_to_chatgpt(question=update.message.text)
    await update.message.reply_text(answer)


async def voice_recognize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    await update.message.reply_text("Пожалуйста, ожидайте :)\nТрехминутная запись обрабатывается примерно 30 секунд")
    if not update.message.voice:
        return

    sound_file = await update.message.voice.get_file()
    sound_bytes = await sound_file.download_as_bytearray()
    with tempfile.NamedTemporaryFile(delete=False) as tmpfile:
        tmpfile.write(sound_bytes)

    logger.info("file has been saved", filename=tmpfile.name)

    speech_to_text_service = SpeechToTextService(filename=tmpfile.name)

    speech_to_text_service.get_text_from_audio()

    part = 0
    while speech_to_text_service.text_parts or not speech_to_text_service.text_recognised:
        if text := speech_to_text_service.text_parts.get(part):
            speech_to_text_service.text_parts.pop(part)
            await update.message.reply_text(text)
            part += 1
        await asyncio.sleep(5)
