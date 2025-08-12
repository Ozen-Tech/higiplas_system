"""Merge migration branches

Revision ID: dc2a6597c72f
Revises: 000_initial_schema, 07af028af52e
Create Date: 2025-08-11 21:43:46.588046

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'dc2a6597c72f'
down_revision: Union[str, Sequence[str], None] = ('000_initial_schema', '07af028af52e')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
