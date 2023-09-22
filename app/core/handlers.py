from dataclasses import dataclass, field
from typing import Any

from telegram.ext import CommandHandler

from app.core.commands import help_command


@dataclass
class CommandHandlers:
    handlers: list[Any] = field(default_factory=list[Any])

    def add_handler(self, handler: Any) -> None:
        self.handlers.append(handler)


command_handlers = CommandHandlers()


command_handlers.add_handler(CommandHandler("help", help_command))
