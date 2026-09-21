"""add row level security policies

Revision ID: 53862a7c4fbb
Revises: 7a71aa5e193e
Create Date: 2026-09-21 12:39:33.082543

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '53862a7c4fbb'
down_revision: Union[str, None] = '7a71aa5e193e'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    pass


def downgrade() -> None:
    pass