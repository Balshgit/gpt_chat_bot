from dataclasses import dataclass

from sqlalchemy import func, select
from sqlalchemy.dialects.sqlite import insert
from sqlalchemy.orm import load_only

from core.auth.dto import UserIsBannedDTO
from core.auth.models.users import AccessToken, User, UserQuestionCount
from infra.database.db_adapter import Database


@dataclass
class UserRepository:
    db: Database

    async def create_user(
        self,
        id: int,
        email: str | None,
        username: str | None,
        first_name: str | None,
        last_name: str | None,
        ban_reason: str | None,
        hashed_password: str | None,
        is_active: bool,
        is_superuser: bool,
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

    async def check_user_is_banned(self, user_id: int) -> UserIsBannedDTO:
        query = select(User).options(load_only(User.is_active, User.ban_reason)).filter_by(id=user_id)

        async with self.db.session() as session:
            result = await session.execute(query)
            if user := result.scalar():
                return UserIsBannedDTO(is_banned=not bool(user.is_active), ban_reason=user.ban_reason)
            return UserIsBannedDTO()

    async def update_user_message_count(self, user_id: int) -> None:
        query = (
            insert(UserQuestionCount)
            .values({UserQuestionCount.user_id: user_id, UserQuestionCount.question_count: 1})
            .on_conflict_do_update(
                index_elements=[UserQuestionCount.user_id],
                set_={
                    UserQuestionCount.get_real_column_name(
                        UserQuestionCount.question_count.key
                    ): UserQuestionCount.question_count
                    + 1,
                    UserQuestionCount.get_real_column_name(UserQuestionCount.last_question_at.key): func.now(),
                },
            )
        )

        async with self.db.session() as session:
            await session.execute(query)

    async def get_user_access_token(self, username: str | None) -> str | None:
        query = select(AccessToken.token).join(AccessToken.user).where(User.username == username)

        async with self.db.session() as session:
            result = await session.execute(query)
            return result.scalar()
