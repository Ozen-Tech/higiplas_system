"""add arquivo_processado and reversao fields

Revision ID: add_arquivo_processado_reversao
Revises: 
Create Date: 2026-01-22 10:30:00.000000

"""
from alembic import op
from alembic import context
import sqlalchemy as sa
from sqlalchemy.dialects import postgresql

# revision identifiers, used by Alembic.
revision = 'add_arquivo_processado_reversao'
down_revision = None  # Atualizar com a última revisão
branch_labels = None
depends_on = None


def upgrade():
    connection = context.get_bind()

    # Criar enums apenas se não existirem (idempotente para produção)
    op.execute("""
        DO $$ BEGIN
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_arquivo_enum') THEN
                CREATE TYPE tipo_arquivo_enum AS ENUM ('PDF', 'XML');
            END IF;
            IF NOT EXISTS (SELECT 1 FROM pg_type WHERE typname = 'tipo_mov_arquivo_enum') THEN
                CREATE TYPE tipo_mov_arquivo_enum AS ENUM ('ENTRADA', 'SAIDA');
            END IF;
        END $$;
    """)

    # Criar tabela arquivos_processados apenas se não existir
    result = connection.execute(sa.text(
        "SELECT EXISTS (SELECT FROM information_schema.tables WHERE table_name = 'arquivos_processados')"
    ))
    if not result.scalar():
        op.create_table(
            'arquivos_processados',
            sa.Column('id', sa.Integer(), nullable=False),
            sa.Column('nome_arquivo', sa.String(), nullable=False),
            sa.Column('hash_arquivo', sa.String(), nullable=False),
            sa.Column('nota_fiscal', sa.String(), nullable=True),
            sa.Column('tipo_arquivo', postgresql.ENUM('PDF', 'XML', name='tipo_arquivo_enum', create_type=False), nullable=False),
            sa.Column('tipo_movimentacao', postgresql.ENUM('ENTRADA', 'SAIDA', name='tipo_mov_arquivo_enum', create_type=False), nullable=False),
            sa.Column('data_processamento', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=False),
            sa.Column('usuario_id', sa.Integer(), nullable=False),
            sa.Column('empresa_id', sa.Integer(), nullable=False),
            sa.Column('total_produtos', sa.Integer(), nullable=False, server_default='0'),
            sa.Column('total_movimentacoes', sa.Integer(), nullable=False, server_default='0'),
            sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
            sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
            sa.PrimaryKeyConstraint('id'),
            sa.UniqueConstraint('hash_arquivo')
        )
        op.create_index('ix_arquivos_processados_nome_arquivo', 'arquivos_processados', ['nome_arquivo'])
        op.create_index('ix_arquivos_processados_hash_arquivo', 'arquivos_processados', ['hash_arquivo'])
        op.create_index('ix_arquivos_processados_nota_fiscal', 'arquivos_processados', ['nota_fiscal'])
        op.create_index('ix_arquivos_processados_data_processamento', 'arquivos_processados', ['data_processamento'])
        op.create_index('ix_arquivos_processados_empresa_id', 'arquivos_processados', ['empresa_id'])
        op.create_index('idx_arquivo_empresa_data', 'arquivos_processados', ['empresa_id', 'data_processamento'])
        op.create_index('idx_arquivo_nf', 'arquivos_processados', ['nota_fiscal', 'empresa_id'])

    # Adicionar colunas de reversão em movimentacoes_estoque apenas se não existirem
    cols_result = connection.execute(sa.text(
        "SELECT column_name FROM information_schema.columns WHERE table_name = 'movimentacoes_estoque' AND column_name = 'reversao_de_id'"
    ))
    if cols_result.scalar() is None:
        op.add_column('movimentacoes_estoque', sa.Column('reversao_de_id', sa.Integer(), nullable=True))
        op.add_column('movimentacoes_estoque', sa.Column('revertida', sa.Boolean(), nullable=False, server_default='false'))
        op.add_column('movimentacoes_estoque', sa.Column('data_reversao', sa.DateTime(timezone=True), nullable=True))
        op.add_column('movimentacoes_estoque', sa.Column('revertida_por_id', sa.Integer(), nullable=True))
        op.create_foreign_key(
            'fk_movimentacao_reversao_de',
            'movimentacoes_estoque', 'movimentacoes_estoque',
            ['reversao_de_id'], ['id']
        )
        op.create_foreign_key(
            'fk_movimentacao_revertida_por',
            'movimentacoes_estoque', 'usuarios',
            ['revertida_por_id'], ['id']
        )
        op.create_index('ix_movimentacoes_estoque_reversao_de_id', 'movimentacoes_estoque', ['reversao_de_id'])
        op.create_index('ix_movimentacoes_estoque_revertida', 'movimentacoes_estoque', ['revertida'])


def downgrade():
    # Remover índices e colunas de reversão
    op.drop_index('ix_movimentacoes_estoque_revertida', table_name='movimentacoes_estoque')
    op.drop_index('ix_movimentacoes_estoque_reversao_de_id', table_name='movimentacoes_estoque')
    op.drop_constraint('fk_movimentacao_revertida_por', 'movimentacoes_estoque', type_='foreignkey')
    op.drop_constraint('fk_movimentacao_reversao_de', 'movimentacoes_estoque', type_='foreignkey')
    op.drop_column('movimentacoes_estoque', 'revertida_por_id')
    op.drop_column('movimentacoes_estoque', 'data_reversao')
    op.drop_column('movimentacoes_estoque', 'revertida')
    op.drop_column('movimentacoes_estoque', 'reversao_de_id')
    
    # Remover tabela arquivos_processados
    op.drop_index('idx_arquivo_nf', table_name='arquivos_processados')
    op.drop_index('idx_arquivo_empresa_data', table_name='arquivos_processados')
    op.drop_index('ix_arquivos_processados_empresa_id', table_name='arquivos_processados')
    op.drop_index('ix_arquivos_processados_data_processamento', table_name='arquivos_processados')
    op.drop_index('ix_arquivos_processados_nota_fiscal', table_name='arquivos_processados')
    op.drop_index('ix_arquivos_processados_hash_arquivo', table_name='arquivos_processados')
    op.drop_index('ix_arquivos_processados_nome_arquivo', table_name='arquivos_processados')
    op.drop_table('arquivos_processados')
    
    # Remover enums
    op.execute("DROP TYPE IF EXISTS tipo_mov_arquivo_enum")
    op.execute("DROP TYPE IF EXISTS tipo_arquivo_enum")
