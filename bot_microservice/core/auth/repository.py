from dataclasses import dataclass

from sqlalchemy import select

from core.auth.models.users import User
from infra.database.db_adapter import Database


@dataclass
class UserRepository:
    db: Database

    async def create_user(
        self,
        id: int,
        email: str | None = None,
        username: str | None = None,
        first_name: str | None = None,
        last_name: str | None = None,
        ban_reason: str | None = None,
        hashed_password: str | None = None,
        is_active: bool = True,
        is_superuser: bool = False,
    ) -> User:
        user = User.build(
            id=id,
            email=email,
            username=username,
            first_name=first_name,
            last_name=last_name,
            ban_reason=ban_reason,
            hashed_password=hashed_password,
            is_active=is_active,
            is_superuser=is_superuser,
        )

        async with self.db.session() as session:
            session.add(user)
            await session.commit()
            await session.refresh(user)
            return user

    async def get_user_by_id(self, user_id: int) -> User | None:
        query = select(User).filter_by(id=user_id)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar()
