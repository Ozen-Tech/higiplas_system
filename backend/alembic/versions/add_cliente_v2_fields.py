"""add cliente v2 fields

Revision ID: add_cliente_v2_fields
Revises: 
Create Date: 2024-10-04 16:00:00

"""
from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = 'add_cliente_v2_fields'
down_revision = None
branch_labels = None
depends_on = None


def upgrade():
    # Adicionar campos novos na tabela clientes
    op.add_column('clientes', sa.Column('observacoes', sa.String(500), nullable=True))
    op.add_column('clientes', sa.Column('referencia_localizacao', sa.String(200), nullable=True))
    op.add_column('clientes', sa.Column('vendedor_id', sa.Integer(), nullable=True))
    op.add_column('clientes', sa.Column('criado_em', sa.DateTime(timezone=True), nullable=True))
    op.add_column('clientes', sa.Column('atualizado_em', sa.DateTime(timezone=True), nullable=True))
    
    # Adicionar foreign key para vendedor
    op.create_foreign_key(
        'fk_cliente_vendedor',
        'clientes',
        'usuarios',
        ['vendedor_id'],
        ['id']
    )
    
    # Adicionar índices para melhor performance
    op.create_index('ix_clientes_telefone', 'clientes', ['telefone'])
    op.create_index('ix_clientes_vendedor_id', 'clientes', ['vendedor_id'])
    op.create_index('ix_clientes_criado_em', 'clientes', ['criado_em'])


def downgrade():
    # Remover índices
    op.drop_index('ix_clientes_criado_em', table_name='clientes')
    op.drop_index('ix_clientes_vendedor_id', table_name='clientes')
    op.drop_index('ix_clientes_telefone', table_name='clientes')
    
    # Remover foreign key
    op.drop_constraint('fk_cliente_vendedor', 'clientes', type_='foreignkey')
    
    # Remover colunas
    op.drop_column('clientes', 'atualizado_em')
    op.drop_column('clientes', 'criado_em')
    op.drop_column('clientes', 'vendedor_id')
    op.drop_column('clientes', 'referencia_localizacao')
    op.drop_column('clientes', 'observacoes')
