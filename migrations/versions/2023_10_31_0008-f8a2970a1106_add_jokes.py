"""add jokes

Revision ID: f8a2970a1106
Revises: 106e0b020783
Create Date: 2023-10-31 00:08:31.273811

"""
from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op

# revision identifiers, used by Alembic.
revision: str = "f8a2970a1106"
down_revision: Union[str, None] = "106e0b020783"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "joke",
        sa.Column("id", sa.Integer(), nullable=False),
        sa.Column("category", sa.String(), nullable=False),
        sa.Column("title", sa.String(), nullable=True),
        sa.Column("body", sa.String(), nullable=False),
        sa.PrimaryKeyConstraint("id"),
    )
    # ### end Alembic commands ###


def downgrade() -> None:
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_table("joke")
    # ### end Alembic commands ###
