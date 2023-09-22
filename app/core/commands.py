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
