from dataclasses import dataclass

from core.auth.models.users import User
from core.auth.repository import UserRepository
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
        email: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        ban_reason: str | None = None,
        hashed_password: str | None = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
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
