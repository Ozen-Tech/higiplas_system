"""merge heads for visitas

Revision ID: merge_heads_visitas_001
Revises: create_visitas_vendedor, add_data_criacao_foto_perfil_001
Create Date: 2025-01-27 00:00:02.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_heads_visitas_001'
down_revision: Union[str, Sequence[str], None] = ('create_visitas_vendedor', 'add_data_criacao_foto_perfil_001')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Migração de merge apenas."""
    pass


def downgrade() -> None:
    """Downgrade schema."""
    pass
