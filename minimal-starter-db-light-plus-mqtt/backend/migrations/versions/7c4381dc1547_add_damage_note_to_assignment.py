"""add damage_note to assignment

Revision ID: 7c4381dc1547
Revises: 89a9914a920c
Create Date: 2026-04-19 09:18:34.146810

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '7c4381dc1547'
down_revision: Union[str, None] = '89a9914a920c'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass
