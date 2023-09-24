from dataclasses import dataclass, field
from typing import Any

from core.commands import ask_question, help_command, voice_recognize
from telegram.ext import CommandHandler, MessageHandler, filters


@dataclass
class BotEventHandlers:
    handlers: list[Any] = field(default_factory=list[Any])

    def add_handler(self, handler: Any) -> None:
        self.handlers.append(handler)


bot_event_handlers = BotEventHandlers()

bot_event_handlers.add_handler(CommandHandler("help", help_command))
bot_event_handlers.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))
bot_event_handlers.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_recognize))
