"""add_approval_fields_to_movimentacoes_estoque

Revision ID: approval_fields_001
Revises: bffb357ac77f
Create Date: 2025-01-20 10:00:00.000000

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql


# revision identifiers, used by Alembic.
revision: str = 'approval_fields_001'
down_revision: Union[str, Sequence[str], None] = 'bffb357ac77f'
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # Criar o tipo ENUM para status de movimentação
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE status_movimentacao_enum AS ENUM ('PENDENTE', 'CONFIRMADO', 'REJEITADO');
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Criar o tipo ENUM para motivo de movimentação
    op.execute("""
        DO $$ BEGIN
            CREATE TYPE motivo_movimentacao_enum AS ENUM (
                'CARREGAMENTO', 
                'DEVOLUCAO', 
                'AJUSTE_FISICO', 
                'PERDA_AVARIA', 
                'TRANSFERENCIA_INTERNA'
            );
        EXCEPTION
            WHEN duplicate_object THEN null;
        END $$;
    """)
    
    # Adicionar colunas de aprovação
    op.add_column('movimentacoes_estoque', 
        sa.Column('status', sa.Enum('PENDENTE', 'CONFIRMADO', 'REJEITADO', name='status_movimentacao_enum'), 
                  nullable=False, server_default='CONFIRMADO'))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('aprovado_por_id', sa.Integer(), nullable=True))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('data_aprovacao', sa.DateTime(timezone=True), nullable=True))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('motivo_rejeicao', sa.String(), nullable=True))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('motivo_movimentacao', 
                  sa.Enum('CARREGAMENTO', 'DEVOLUCAO', 'AJUSTE_FISICO', 'PERDA_AVARIA', 'TRANSFERENCIA_INTERNA', 
                          name='motivo_movimentacao_enum'), 
                  nullable=True))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('observacao_motivo', sa.String(), nullable=True))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('dados_antes_edicao', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    op.add_column('movimentacoes_estoque', 
        sa.Column('dados_depois_edicao', postgresql.JSON(astext_type=sa.Text()), nullable=True))
    
    # Adicionar foreign key para aprovado_por_id
    op.create_foreign_key(
        'fk_movimentacoes_estoque_aprovado_por',
        'movimentacoes_estoque', 'usuarios',
        ['aprovado_por_id'], ['id'],
        ondelete='SET NULL'
    )
    
    # Criar índice para status para melhor performance nas consultas
    op.create_index('ix_movimentacoes_estoque_status', 'movimentacoes_estoque', ['status'])


def downgrade() -> None:
    """Downgrade schema."""
    # Remover índice
    op.drop_index('ix_movimentacoes_estoque_status', table_name='movimentacoes_estoque')
    
    # Remover foreign key
    op.drop_constraint('fk_movimentacoes_estoque_aprovado_por', 'movimentacoes_estoque', type_='foreignkey')
    
    # Remover colunas
    op.drop_column('movimentacoes_estoque', 'dados_depois_edicao')
    op.drop_column('movimentacoes_estoque', 'dados_antes_edicao')
    op.drop_column('movimentacoes_estoque', 'observacao_motivo')
    op.drop_column('movimentacoes_estoque', 'motivo_movimentacao')
    op.drop_column('movimentacoes_estoque', 'motivo_rejeicao')
    op.drop_column('movimentacoes_estoque', 'data_aprovacao')
    op.drop_column('movimentacoes_estoque', 'aprovado_por_id')
    op.drop_column('movimentacoes_estoque', 'status')
    
    # Remover tipos ENUM
    op.execute("DROP TYPE IF EXISTS motivo_movimentacao_enum")
    op.execute("DROP TYPE IF EXISTS status_movimentacao_enum")

