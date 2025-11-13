"""add_historico_vendas_cliente_table

Revision ID: add_historico_vendas_cliente
Revises: 712f9eaddc99
Create Date: 2025-01-15 12:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'add_historico_vendas_cliente'
down_revision: Union[str, Sequence[str], None] = '712f9eaddc99'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar tabela historico_vendas_cliente
    op.create_table(
        'historico_vendas_cliente',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendedor_id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=False),
        sa.Column('produto_id', sa.Integer(), nullable=False),
        sa.Column('orcamento_id', sa.Integer(), nullable=False),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('quantidade_vendida', sa.Integer(), nullable=False),
        sa.Column('preco_unitario_vendido', sa.Float(), nullable=False),
        sa.Column('valor_total', sa.Float(), nullable=False),
        sa.Column('data_venda', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.ForeignKeyConstraint(['vendedor_id'], ['usuarios.id'], ),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.ForeignKeyConstraint(['orcamento_id'], ['orcamentos.id'], ),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices individuais
    op.create_index(op.f('ix_historico_vendas_cliente_vendedor_id'), 'historico_vendas_cliente', ['vendedor_id'], unique=False)
    op.create_index(op.f('ix_historico_vendas_cliente_cliente_id'), 'historico_vendas_cliente', ['cliente_id'], unique=False)
    op.create_index(op.f('ix_historico_vendas_cliente_produto_id'), 'historico_vendas_cliente', ['produto_id'], unique=False)
    op.create_index(op.f('ix_historico_vendas_cliente_orcamento_id'), 'historico_vendas_cliente', ['orcamento_id'], unique=False)
    op.create_index(op.f('ix_historico_vendas_cliente_empresa_id'), 'historico_vendas_cliente', ['empresa_id'], unique=False)
    op.create_index(op.f('ix_historico_vendas_cliente_data_venda'), 'historico_vendas_cliente', ['data_venda'], unique=False)
    
    # Criar índices compostos para otimização
    op.create_index('idx_vendedor_cliente_produto', 'historico_vendas_cliente', ['vendedor_id', 'cliente_id', 'produto_id'], unique=False)
    op.create_index('idx_cliente_produto', 'historico_vendas_cliente', ['cliente_id', 'produto_id'], unique=False)
    op.create_index('idx_cliente_data', 'historico_vendas_cliente', ['cliente_id', 'data_venda'], unique=False)
    op.create_index('idx_produto_data', 'historico_vendas_cliente', ['produto_id', 'data_venda'], unique=False)


def downgrade() -> None:
    """Downgrade schema."""
    # Remover índices compostos
    op.drop_index('idx_produto_data', table_name='historico_vendas_cliente')
    op.drop_index('idx_cliente_data', table_name='historico_vendas_cliente')
    op.drop_index('idx_cliente_produto', table_name='historico_vendas_cliente')
    op.drop_index('idx_vendedor_cliente_produto', table_name='historico_vendas_cliente')
    
    # Remover índices individuais
    op.drop_index(op.f('ix_historico_vendas_cliente_data_venda'), table_name='historico_vendas_cliente')
    op.drop_index(op.f('ix_historico_vendas_cliente_empresa_id'), table_name='historico_vendas_cliente')
    op.drop_index(op.f('ix_historico_vendas_cliente_orcamento_id'), table_name='historico_vendas_cliente')
    op.drop_index(op.f('ix_historico_vendas_cliente_produto_id'), table_name='historico_vendas_cliente')
    op.drop_index(op.f('ix_historico_vendas_cliente_cliente_id'), table_name='historico_vendas_cliente')
    op.drop_index(op.f('ix_historico_vendas_cliente_vendedor_id'), table_name='historico_vendas_cliente')
    
    # Remover tabela
    op.drop_table('historico_vendas_cliente')

