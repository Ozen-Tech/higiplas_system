"""add_origem_and_quantity_tracking_to_movimentacoes_estoque

Revision ID: bffb357ac77f
Revises: 227dac4b4f63
Create Date: 2025-10-29 18:21:32.273123

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'bffb357ac77f'
down_revision: Union[str, Sequence[str], None] = '227dac4b4f63'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    op.add_column('movimentacoes_estoque', sa.Column('origem', sa.String(length=100), nullable=True))
    op.add_column('movimentacoes_estoque', sa.Column('quantidade_antes', sa.Integer(), nullable=True))
    op.add_column('movimentacoes_estoque', sa.Column('quantidade_depois', sa.Integer(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('movimentacoes_estoque', 'quantidade_depois')
    op.drop_column('movimentacoes_estoque', 'quantidade_antes')
    op.drop_column('movimentacoes_estoque', 'origem')
