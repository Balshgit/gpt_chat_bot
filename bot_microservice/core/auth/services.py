from dataclasses import dataclass

from core.auth.models.users import User
from core.auth.repository import UserRepository
from infra.database.db_adapter import Database
from settings.config import settings


@dataclass
class UserService:
    repository: UserRepository

    async def get_user_by_id(self, user_id: int) -> User | None:
        return await self.repository.get_user_by_id(user_id)

    @classmethod
    def build(cls) -> "UserService":
        db = Database(settings=settings)
        repository = UserRepository(db=db)
        return UserService(repository=repository)
