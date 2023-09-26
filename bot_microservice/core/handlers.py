from dataclasses import dataclass, field
from typing import Any

from constants import BotEntryPoints, BotStagesEnum
from core.commands import (
    about_me,
    ask_question,
    help_command,
    main_command,
    voice_recognize,
    website,
)
from telegram.ext import (
    CallbackQueryHandler,
    CommandHandler,
    ConversationHandler,
    MessageHandler,
    filters,
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
                CallbackQueryHandler(about_me, pattern="^" + str(BotStagesEnum.about_me) + "$"),
                CallbackQueryHandler(website, pattern="^" + str(BotStagesEnum.website) + "$"),
                CallbackQueryHandler(help_command, pattern="^" + str(BotStagesEnum.help) + "$"),
            ],
        },
        fallbacks=[CommandHandler("start", main_command)],
    )
)
bot_event_handlers.add_handler(CallbackQueryHandler(about_me, pattern="^" + str(BotStagesEnum.about_me) + "$"))
bot_event_handlers.add_handler(CallbackQueryHandler(website, pattern="^" + str(BotStagesEnum.website) + "$"))
bot_event_handlers.add_handler(CallbackQueryHandler(help_command, pattern="^" + str(BotStagesEnum.help) + "$"))
