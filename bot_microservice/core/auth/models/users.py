from fastapi_users_db_sqlalchemy import SQLAlchemyBaseUserTable
from fastapi_users_db_sqlalchemy.access_token import SQLAlchemyBaseAccessTokenTable
from sqlalchemy import INTEGER, VARCHAR, ForeignKey
from sqlalchemy.orm import Mapped, declared_attr, mapped_column

from infra.database.base import Base


class User(SQLAlchemyBaseUserTable[Mapped[int]], Base):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(length=320), unique=True, nullable=True)  # type: ignore[assignment]
    username: Mapped[str] = mapped_column(VARCHAR(length=32), unique=True, index=True, nullable=False)


class AccessToken(SQLAlchemyBaseAccessTokenTable[Mapped[int]], Base):
    __tablename__ = "access_token"  # type: ignore[assignment]

    @declared_attr
    def user_id(cls) -> Mapped[int]:
        return mapped_column(INTEGER, ForeignKey("users.id", ondelete="cascade"), nullable=False)


class UserQuestionCount(Base):
    __tablename__ = "user_question_count"  # type: ignore[assignment]

    user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("users.id", ondelete="cascade"), primary_key=True)
    question_count: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
