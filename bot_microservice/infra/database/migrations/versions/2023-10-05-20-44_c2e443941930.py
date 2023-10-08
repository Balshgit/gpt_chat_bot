"""create chat gpt models

Revision ID: c2e443941930
Revises: eb78565abec7
Create Date: 2025-10-05 20:44:05.414977

"""

from sqlalchemy import create_engine, select
from sqlalchemy.orm import sessionmaker

from constants import ChatGptModelsEnum
from core.bot.models.chat_gpt import ChatGpt
from settings.config import settings

# revision identifiers, used by Alembic.
revision = "c2e443941930"
down_revision = "eb78565abec7"
branch_labels: str | None = None
depends_on: str | None = None

engine = create_engine(str(settings.async_db_url), echo=settings.DB_ECHO)
session_factory = sessionmaker(engine)


def upgrade() -> None:
    with session_factory() as session:
        query = select(ChatGpt)
        results = session.execute(query)
        models = results.scalars().all()

        if models:
            return None
        models = []
        for model in ChatGptModelsEnum.values():
            priority = 0 if model != "gpt-3.5-turbo-stream-FreeGpt" else 1
            fields = {"model": model, "priority": priority}
            models.append(ChatGpt(**fields))
        session.add_all(models)
        session.commit()


def downgrade() -> None:
    with session_factory() as session:
        session.execute(f"""TRUNCATE TABLE {ChatGpt.__tablename__}""")
        session.commit()


engine.dispose()
