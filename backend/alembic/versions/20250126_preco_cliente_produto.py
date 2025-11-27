"""preco_cliente_produto

Revision ID: preco_cliente_produto_001
Revises: merge_approval_proposta
Create Date: 2025-01-26 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = 'preco_cliente_produto_001'
down_revision: Union[str, Sequence[str], None] = 'proposta_itens_concorrentes'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar tabela de preços padrão por cliente-produto
    op.create_table(
        'precos_cliente_produto',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('preco_padrao', sa.Float(), nullable=False),
        sa.Column('preco_minimo', sa.Float(), nullable=True),
        sa.Column('preco_maximo', sa.Float(), nullable=True),
        sa.Column('preco_medio', sa.Float(), nullable=True),
        sa.Column('total_vendas', sa.Integer(), default=0),
        sa.Column('data_ultima_venda', sa.DateTime(timezone=True), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('data_atualizacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), onupdate=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ondelete='CASCADE'),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ondelete='CASCADE'),
        sa.PrimaryKeyConstraint('id'),
        sa.UniqueConstraint('cliente_id', 'produto_id', name='uq_cliente_produto')
    )
    op.create_index('idx_preco_cliente_produto', 'precos_cliente_produto', ['cliente_id', 'produto_id'])
    op.create_index('idx_preco_produto', 'precos_cliente_produto', ['produto_id'])


def downgrade() -> None:
    """Downgrade schema."""
    op.drop_index('idx_preco_produto', table_name='precos_cliente_produto')
    op.drop_index('idx_preco_cliente_produto', table_name='precos_cliente_produto')
    op.drop_table('precos_cliente_produto')

