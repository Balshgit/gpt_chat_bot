from sqlalchemy import INTEGER, SMALLINT, VARCHAR
from sqlalchemy.orm import Mapped, mapped_column

from infra.database.base import Base

__slots__ = ("ChatGpt",)


class ChatGpt(Base):
    id: Mapped[int] = mapped_column("id", INTEGER(), primary_key=True, autoincrement=True)
    model: Mapped[str] = mapped_column("model", VARCHAR(length=256), nullable=False, unique=True)
    priority: Mapped[int] = mapped_column("priority", SMALLINT(), default=0)
