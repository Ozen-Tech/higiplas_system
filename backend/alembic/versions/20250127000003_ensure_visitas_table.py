"""ensure visitas table exists

Revision ID: ensure_visitas_table_001
Revises: merge_heads_visitas_001
Create Date: 2025-01-27 00:00:03.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.sql import text


# revision identifiers, used by Alembic.
revision: str = 'ensure_visitas_table_001'
down_revision: Union[str, Sequence[str], None] = 'merge_heads_visitas_001'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema - Garante que a tabela visitas_vendedor existe."""
    connection = op.get_bind()
    
    # Verificar se a tabela já existe
    result = connection.execute(text("""
        SELECT EXISTS (
            SELECT FROM information_schema.tables 
            WHERE table_schema = 'public' 
            AND table_name = 'visitas_vendedor'
        );
    """))
    table_exists = result.scalar()
    
    if not table_exists:
        # Criar tabela se não existir
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
        op.create_index('idx_visita_vendedor_data', 'visitas_vendedor', ['vendedor_id', 'data_visita'])
        op.create_index('idx_visita_cliente', 'visitas_vendedor', ['cliente_id', 'data_visita'])
        op.create_index('idx_visita_empresa_confirmada', 'visitas_vendedor', ['empresa_id', 'confirmada', 'data_visita'])
        
        print("✓ Tabela visitas_vendedor criada")
    else:
        print("✓ Tabela visitas_vendedor já existe")


def downgrade() -> None:
    """Downgrade schema."""
    # Não removemos a tabela aqui para evitar perda de dados
    pass
