import asyncio
import tempfile
from urllib.parse import urljoin

from loguru import logger
from telegram import InlineKeyboardMarkup, Update
from telegram.ext import ContextTypes

from constants import BotCommands, BotEntryPoints
from core.auth.services import check_user_is_banned
from core.bot.app import get_bot
from core.bot.keyboards import main_keyboard
from core.bot.services import ChatGptService, SpeechToTextService
from settings.config import settings


async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> str:
    """Send message on `/start`."""
    if not update.message:
        return BotEntryPoints.end
    reply_markup = InlineKeyboardMarkup(main_keyboard)
    await update.message.reply_text("Выберете команду:", reply_markup=reply_markup)
    await update.message.reply_text("Список этих команд всегда можно получить набрав /help")
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
        f"Бот использует бесплатную модель *{model}* для ответов на вопросы.\nПринимает запросы на разных языках.",
        parse_mode="Markdown",
    )


@check_user_is_banned
async def website(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.effective_message:
        return
    website = urljoin(settings.DOMAIN, f"{settings.chat_prefix}/")
    await update.effective_message.reply_text(f"Веб версия: {website}")


@check_user_is_banned
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


@check_user_is_banned
async def bug_report(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /bug-report is issued."""

    if not update.effective_message or not settings.ADMIN_CHAT_ID:
        return
    async with get_bot(settings.TELEGRAM_API_TOKEN) as bot:
        await bot.send_message(chat_id=settings.ADMIN_CHAT_ID, text=f"Bug report from user: {update.effective_user}")
    await update.effective_message.reply_text(
        f"Спасибо за баг репорт.\n"
        f"Можете попробовать воспользоваться веб версией /{BotCommands.website}, выбрав различные GPT модели",
        parse_mode="Markdown",
    )


async def github(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a message when the command /help is issued."""

    if not update.effective_message:
        return
    await update.effective_message.reply_text(
        "Проект на [GitHub](https://github.com/Balshgit/gpt_chat_bot)",
        parse_mode="Markdown",
    )


@check_user_is_banned
async def ask_question(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return

    await update.message.reply_text(
        f"Ответ в среднем занимает 10-15 секунд.\n"
        f"- Список команд: /{BotCommands.help}\n"
        f"- Сообщить об ошибке: /{BotCommands.bug_report}",
    )

    chatgpt_service = ChatGptService.build()
    logger.warning("question asked", user=update.message.from_user, question=update.message.text)
    answer, user = await asyncio.gather(
        chatgpt_service.request_to_chatgpt(question=update.message.text),
        chatgpt_service.get_or_create_bot_user(
            user_id=update.effective_user.id,  # type: ignore[union-attr]
            username=update.effective_user.username,  # type: ignore[union-attr]
            first_name=update.effective_user.first_name,  # type: ignore[union-attr]
            last_name=update.effective_user.last_name,  # type: ignore[union-attr]
        ),
    )
    await asyncio.gather(update.message.reply_text(answer), chatgpt_service.update_bot_user_message_count(user.id))


async def voice_recognize(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not update.message:
        return
    if not update.message.voice:
        await update.message.reply_text("Голосовое сообщение не найдено")
        return
    await update.message.reply_text("Пожалуйста, ожидайте :)\nТрехминутная запись обрабатывается примерно 30 секунд")
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
