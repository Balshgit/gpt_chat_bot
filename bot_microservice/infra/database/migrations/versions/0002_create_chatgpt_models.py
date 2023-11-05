"""create chatgpt models

Revision ID: 0002_create_chatgpt_models
Revises: 0001_create_chatgpt_table
Create Date: 2025-10-05 20:44:05.414977

"""
from loguru import logger
from sqlalchemy import create_engine, select, text
from sqlalchemy.orm import sessionmaker

from constants import ChatGptModelsEnum
from core.bot.models.chat_gpt import ChatGpt
from settings.config import settings

# revision identifiers, used by Alembic.
revision = "0002_create_chatgpt_models"
down_revision = "0001_create_chatgpt_table"
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
            return
        models = []
        for data in ChatGptModelsEnum.base_models_priority():
            models.append(ChatGpt(**data))
        session.add_all(models)
        session.commit()


def downgrade() -> None:
    chatgpt_table_name = ChatGpt.__tablename__
    with session_factory() as session:
        # Truncate doesn't exists for SQLite
        session.execute(text(f"""DELETE FROM {chatgpt_table_name}"""))  # noqa: S608
        session.commit()
        logger.info("chatgpt models table has been truncated", table=chatgpt_table_name)


engine.dispose()
