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
    # Criar o tipo ENUM se não existir
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE origem_movimentacao_enum AS ENUM ('VENDA', 'DEVOLUCAO', 'CORRECAO_MANUAL', 'COMPRA', 'AJUSTE', 'OUTRO');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)

    # Adicionar colunas
    op.add_column('movimentacoes_estoque', sa.Column('origem', sa.Enum('VENDA', 'DEVOLUCAO', 'CORRECAO_MANUAL', 'COMPRA', 'AJUSTE', 'OUTRO', name='origem_movimentacao_enum'), nullable=True))
    op.add_column('movimentacoes_estoque', sa.Column('quantidade_antes', sa.Float(), nullable=True))
    op.add_column('movimentacoes_estoque', sa.Column('quantidade_depois', sa.Float(), nullable=True))


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_column('movimentacoes_estoque', 'quantidade_depois')
    op.drop_column('movimentacoes_estoque', 'quantidade_antes')
    op.drop_column('movimentacoes_estoque', 'origem')

    # Remover o tipo ENUM
    op.execute("DROP TYPE IF EXISTS origem_movimentacao_enum")
