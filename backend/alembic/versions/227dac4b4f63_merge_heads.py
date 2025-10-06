"""merge heads

Revision ID: 227dac4b4f63
Revises: 4ba406ef5479, add_cliente_v2_fields
Create Date: 2025-10-05 22:06:50.665737

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '227dac4b4f63'
down_revision: Union[str, Sequence[str], None] = ('4ba406ef5479', 'add_cliente_v2_fields')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
