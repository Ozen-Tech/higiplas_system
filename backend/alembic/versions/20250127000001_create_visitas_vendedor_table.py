"""create_visitas_vendedor_table

Revision ID: create_visitas_vendedor
Revises: create_empresas_higiplas_higitec
Create Date: 2025-01-27 00:00:01.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision: str = 'create_visitas_vendedor'
down_revision: Union[str, Sequence[str], None] = 'create_empresas_higiplas_higitec'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Cria tabela de visitas de vendedores."""
    op.create_table(
        'visitas_vendedor',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('vendedor_id', sa.Integer(), nullable=False),
        sa.Column('cliente_id', sa.Integer(), nullable=True),
        sa.Column('data_visita', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
        sa.Column('latitude', sa.Float(), nullable=False),
        sa.Column('longitude', sa.Float(), nullable=False),
        sa.Column('endereco_completo', sa.String(), nullable=True),
        sa.Column('motivo_visita', sa.String(), nullable=True),
        sa.Column('observacoes', sa.String(), nullable=True),
        sa.Column('foto_comprovante', sa.String(), nullable=True),
        sa.Column('confirmada', sa.Boolean(), nullable=False, server_default='false'),
        sa.Column('empresa_id', sa.Integer(), nullable=False),
        sa.Column('criado_em', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.Column('atualizado_em', sa.DateTime(timezone=True), server_default=sa.text('now()')),
        sa.ForeignKeyConstraint(['vendedor_id'], ['usuarios.id']),
        sa.ForeignKeyConstraint(['cliente_id'], ['clientes.id']),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id']),
        sa.PrimaryKeyConstraint('id')
    )
    
    # Criar índices
    op.create_index('ix_visitas_vendedor_id', 'visitas_vendedor', ['id'])
    op.create_index('ix_visitas_vendedor_vendedor_id', 'visitas_vendedor', ['vendedor_id'])
    op.create_index('ix_visitas_vendedor_cliente_id', 'visitas_vendedor', ['cliente_id'])
    op.create_index('ix_visitas_vendedor_data_visita', 'visitas_vendedor', ['data_visita'])
    op.create_index('ix_visitas_vendedor_confirmada', 'visitas_vendedor', ['confirmada'])
    op.create_index('ix_visitas_vendedor_empresa_id', 'visitas_vendedor', ['empresa_id'])
    
    # Índices compostos
    op.create_index('idx_visita_vendedor_data', 'visitas_vendedor', ['vendedor_id', 'data_visita'])
    op.create_index('idx_visita_cliente', 'visitas_vendedor', ['cliente_id', 'data_visita'])
    op.create_index('idx_visita_empresa_confirmada', 'visitas_vendedor', ['empresa_id', 'confirmada', 'data_visita'])


def downgrade() -> None:
    """Downgrade schema - Remove tabela de visitas de vendedores."""
    op.drop_index('idx_visita_empresa_confirmada', table_name='visitas_vendedor')
    op.drop_index('idx_visita_cliente', table_name='visitas_vendedor')
    op.drop_index('idx_visita_vendedor_data', table_name='visitas_vendedor')
    op.drop_index('ix_visitas_vendedor_empresa_id', table_name='visitas_vendedor')
    op.drop_index('ix_visitas_vendedor_confirmada', table_name='visitas_vendedor')
    op.drop_index('ix_visitas_vendedor_data_visita', table_name='visitas_vendedor')
    op.drop_index('ix_visitas_vendedor_cliente_id', table_name='visitas_vendedor')
    op.drop_index('ix_visitas_vendedor_vendedor_id', table_name='visitas_vendedor')
    op.drop_index('ix_visitas_vendedor_id', table_name='visitas_vendedor')
    op.drop_table('visitas_vendedor')
