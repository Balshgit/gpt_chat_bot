from datetime import datetime

from sqlalchemy import INTEGER, TIMESTAMP, VARCHAR, Boolean, ForeignKey, String
from sqlalchemy.orm import Mapped, mapped_column

from infra.database.base import Base


class User(Base):
    __tablename__ = "users"  # type: ignore[assignment]

    id: Mapped[int] = mapped_column(INTEGER, primary_key=True)
    email: Mapped[str] = mapped_column(VARCHAR(length=255), unique=True, nullable=True)
    username: Mapped[str] = mapped_column(VARCHAR(length=32), unique=True, index=True, nullable=False)
    first_name: Mapped[str] = mapped_column(VARCHAR(length=32), nullable=True)
    last_name: Mapped[str] = mapped_column(VARCHAR(length=32), nullable=True)
    ban_reason: Mapped[str] = mapped_column(String(length=1024), nullable=True)
    hashed_password: Mapped[str] = mapped_column(String(length=1024), nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    is_superuser: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), index=True, nullable=False, default=datetime.now
    )


class AccessToken(Base):
    __tablename__ = "access_token"  # type: ignore[assignment]

    user_id = mapped_column(INTEGER, ForeignKey("users.id", ondelete="cascade"), nullable=False)
    token: Mapped[str] = mapped_column(String(length=42), primary_key=True)
    created_at: Mapped[datetime] = mapped_column(
        TIMESTAMP(timezone=True), index=True, nullable=False, default=datetime.now
    )


class UserQuestionCount(Base):
    __tablename__ = "user_question_count"  # type: ignore[assignment]

    user_id: Mapped[int] = mapped_column(INTEGER, ForeignKey("users.id", ondelete="cascade"), primary_key=True)
    question_count: Mapped[int] = mapped_column(INTEGER, default=0, nullable=False)
