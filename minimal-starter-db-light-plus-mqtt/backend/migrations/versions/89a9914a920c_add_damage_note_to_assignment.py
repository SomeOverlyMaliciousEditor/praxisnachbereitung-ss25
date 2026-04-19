"""add damage_note to assignment

Revision ID: 89a9914a920c
Revises: 
Create Date: 2026-04-19 09:18:02.605082

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '89a9914a920c'
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.add_column(
        "assignment",
        sa.Column("damage_note", sa.Text(), nullable=True),
    )


def downgrade() -> None:
    op.drop_column("assignment", "damage_note")