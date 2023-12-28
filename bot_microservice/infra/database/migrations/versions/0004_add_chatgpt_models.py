"""create chatgpt models

Revision ID: 0004_add_chatgpt_models
Revises: 0003_create_user_question_count_table
Create Date: 2025-10-05 20:44:05.414977

"""
from loguru import logger
from sqlalchemy import select, text

from constants import ChatGptModelsEnum
from core.bot.models.chat_gpt import ChatGpt
from infra.database.deps import get_sync_session

# revision identifiers, used by Alembic.
revision = "0004_add_chatgpt_models"
down_revision = "0003_create_user_question_count_table"
branch_labels: str | None = None
depends_on: str | None = None


def upgrade() -> None:
    with get_sync_session() as session:
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
    with get_sync_session() as session:
        # Truncate doesn't exists for SQLite
        session.execute(text(f"""DELETE FROM {chatgpt_table_name}"""))  # noqa: S608
        session.commit()
        logger.info("chatgpt models table has been truncated", table=chatgpt_table_name)
