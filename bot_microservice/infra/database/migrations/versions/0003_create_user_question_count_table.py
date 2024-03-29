"""add_user_question_count_table

Revision ID: 0003_create_user_question_count_table
Revises: 0002_create_auth_tables
Create Date: 2023-12-28 13:24:42.667724

"""

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision = "0003_create_user_question_count_table"
down_revision = "0002_create_auth_tables"
branch_labels = None
depends_on = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "user_question_count",
        sa.Column("user_id", sa.INTEGER(), nullable=False),
        sa.Column("question_count", sa.INTEGER(), nullable=False),
        sa.ForeignKeyConstraint(["user_id"], ["users.id"], ondelete="cascade"),
        sa.PrimaryKeyConstraint("user_id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("user_question_count")
    # ### end Alembic commands ###
