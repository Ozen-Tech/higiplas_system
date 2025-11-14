"""merge proposta detalhada and fornecedor nullable

Revision ID: merge_proposta_fornecedor
Revises: add_proposta_detalhada, make_fornecedor_nullable
Create Date: 2025-01-20 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'merge_proposta_fornecedor'
down_revision: Union[str, Sequence[str], None] = ('add_proposta_detalhada', 'make_fornecedor_nullable')
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Esta é uma migração de merge, não precisa fazer alterações no schema
    # As alterações já foram feitas nas migrações anteriores
    pass


def downgrade() -> None:
    """Downgrade schema."""
    # Esta é uma migração de merge, não precisa fazer alterações no schema
    pass

