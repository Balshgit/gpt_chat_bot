import uuid
from dataclasses import dataclass
from functools import wraps
from typing import Any

from loguru import logger
from telegram import Update
from telegram.ext import ContextTypes

from constants import BotCommands
from core.auth.dto import UserIsBannedDTO
from core.auth.models.users import User
from core.auth.repository import UserRepository
from core.auth.utils import create_password_hash
from infra.database.db_adapter import Database
from settings.config import settings


@dataclass
class UserService:
    repository: UserRepository

    @classmethod
    def build(cls) -> "UserService":
        db = Database(settings=settings)
        repository = UserRepository(db=db)
        return UserService(repository=repository)

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_user_by_id(user_id)

    async def get_or_create_user_by_id(
        self,
        user_id: int,
        hashed_password: str | None = None,
        email: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        ban_reason: str | None = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        hashed_password = hashed_password or create_password_hash(uuid.uuid4().hex)
        if not (user := await self.repository.get_user_by_id(user_id=user_id)):
            user = await self.repository.create_user(
                id=user_id,
                email=email,
                username=username,
                first_name=first_name,
                last_name=last_name,
                ban_reason=ban_reason,
                hashed_password=hashed_password,
                is_active=is_active,
                is_superuser=is_superuser,
            )
        return user

    async def update_user_message_count(self, user_id: int) -> None:
        await self.repository.update_user_message_count(user_id)

    async def check_user_is_banned(self, user_id: int) -> UserIsBannedDTO:
        return await self.repository.check_user_is_banned(user_id)

    async def get_user_access_token_by_username(self, username: str | None) -> str | None:
        return await self.repository.get_user_access_token(username)


def check_user_is_banned(func: Any) -> Any:
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        if not update.effective_message:
            logger.error('no effective message', update=update, context=context)
            return

        if not update.effective_user:
            logger.error('no effective user', update=update, context=context)
            await update.effective_message.reply_text(
                "Бот не смог определить пользователя. :(\nОб ошибке уже сообщено."
            )
            return

        user_service = UserService.build()  # noqa: NEW100
        user_status = await user_service.check_user_is_banned(update.effective_user.id)
        if user_status.is_banned:
            await update.effective_message.reply_text(
                text=f"You have banned for reason: *{user_status.ban_reason}*."
                f"\nPlease contact the /{BotCommands.developer}",
                parse_mode="Markdown",
            )
        else:
            await func(update, context)

    return wrapper
