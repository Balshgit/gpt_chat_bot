from dataclasses import dataclass, field
from typing import Any

from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
)

from constants import BotEntryPoints, BotStagesEnum
from core.bot.commands import (
    about_bot,
    about_me,
    ask_question,
    github,
    help_command,
    main_command,
    voice_recognize,
    website,
)


@dataclass
class BotEventHandlers:
    handlers: list[Any] = field(default_factory=list[Any])

    def add_handler(self, handler: Any) -> None:
        self.handlers.append(handler)


bot_event_handlers = BotEventHandlers()

bot_event_handlers.add_handler(CommandHandler("help", help_command))
bot_event_handlers.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ask_question))
bot_event_handlers.add_handler(MessageHandler(filters.VOICE | filters.AUDIO, voice_recognize))
bot_event_handlers.add_handler(
    ConversationHandler(
        entry_points=[CommandHandler("start", main_command)],
        states={
            BotEntryPoints.start_routes: [
                CallbackQueryHandler(about_me, pattern="^" + BotStagesEnum.about_me + "$"),
                CallbackQueryHandler(website, pattern="^" + BotStagesEnum.website + "$"),
                CallbackQueryHandler(github, pattern="^" + BotStagesEnum.github + "$"),
                CallbackQueryHandler(about_bot, pattern="^" + BotStagesEnum.about_bot + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", main_command)],
    )
)
bot_event_handlers.add_handler(CallbackQueryHandler(about_me, pattern="^" + BotStagesEnum.about_me + "$"))
bot_event_handlers.add_handler(CallbackQueryHandler(website, pattern="^" + BotStagesEnum.website + "$"))
bot_event_handlers.add_handler(CallbackQueryHandler(github, pattern="^" + BotStagesEnum.github + "$"))
bot_event_handlers.add_handler(CallbackQueryHandler(about_bot, pattern="^" + BotStagesEnum.about_bot + "$"))
