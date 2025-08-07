"""Configura schema completo inicial a partir dos modelos

Revision ID: 5ee30ffa9e84
Revises: 
Create Date: 2025-08-07 01:38:57.347229

"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision: str = '5ee30ffa9e84'
down_revision: Union[str, Sequence[str], None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    """Upgrade schema."""
    # ### Comandos Modificados Manualmente para Deploy em Produção ###
    
    # 1. Cria apenas as tabelas que são NOVAS e não existem em produção.
    # A tabela 'fornecedores' é necessária antes de adicionar a coluna em 'produtos'.
    op.create_table('fornecedores',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('nome', sa.String(), nullable=False),
        sa.Column('cnpj', sa.String(), nullable=True),
        sa.Column('contato_email', sa.String(), nullable=True),
        sa.Column('contato_telefone', sa.String(), nullable=True),
        sa.Column('empresa_id', sa.Integer(), nullable=True),
        sa.ForeignKeyConstraint(['empresa_id'], ['empresas.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_fornecedores_id'), 'fornecedores', ['id'], unique=False)
    op.create_index(op.f('ix_fornecedores_nome'), 'fornecedores', ['nome'], unique=True)
    
    op.create_table('ordens_compra',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('fornecedor_id', sa.Integer(), nullable=True),
        sa.Column('usuario_id', sa.Integer(), nullable=True),
        sa.Column('status', sa.String(), nullable=True),
        sa.Column('data_criacao', sa.DateTime(timezone=True), server_default=sa.text('now()'), nullable=True),
        sa.Column('data_recebimento', sa.DateTime(timezone=True), nullable=True),
        sa.ForeignKeyConstraint(['fornecedor_id'], ['fornecedores.id'], ),
        sa.ForeignKeyConstraint(['usuario_id'], ['usuarios.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ordens_compra_id'), 'ordens_compra', ['id'], unique=False)

    op.create_table('ordens_compra_itens',
        sa.Column('id', sa.Integer(), nullable=False),
        sa.Column('ordem_id', sa.Integer(), nullable=True),
        sa.Column('produto_id', sa.Integer(), nullable=True),
        sa.Column('quantidade_solicitada', sa.Integer(), nullable=False),
        sa.Column('custo_unitario_registrado', sa.Float(), nullable=False),
        sa.ForeignKeyConstraint(['ordem_id'], ['ordens_compra.id'], ),
        sa.ForeignKeyConstraint(['produto_id'], ['produtos.id'], ),
        sa.PrimaryKeyConstraint('id')
    )
    op.create_index(op.f('ix_ordens_compra_itens_id'), 'ordens_compra_itens', ['id'], unique=False)

    # 2. Altera a tabela 'produtos' existente para adicionar a nova coluna e a chave estrangeira.
    # ESTE É O COMANDO ESSENCIAL QUE PRECISA SER EXECUTADO
    op.add_column('produtos', sa.Column('fornecedor_id', sa.Integer(), nullable=True))
    op.create_foreign_key('fk_produtos_fornecedores_fornecedor_id', 'produtos', 'fornecedores', ['fornecedor_id'], ['id'])

    # O Alembic pode tentar recriar índices que já existem. Se o deploy falhar
    # em um erro "index already exists", comente os blocos 'op.create_index' abaixo
    # das tabelas que já existem, como 'empresas', 'usuarios', etc. Por agora,
    # deixaremos eles aqui, pois geralmente são seguros.
    op.create_index(op.f('ix_empresas_cnpj'), 'empresas', ['cnpj'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_empresas_id'), 'empresas', ['id'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_empresas_nome'), 'empresas', ['nome'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_usuarios_email'), 'usuarios', ['email'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_usuarios_id'), 'usuarios', ['id'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_usuarios_nome'), 'usuarios', ['nome'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_produtos_categoria'), 'produtos', ['categoria'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_produtos_codigo'), 'produtos', ['codigo'], unique=True, exist_ok=True)
    op.create_index(op.f('ix_produtos_id'), 'produtos', ['id'], unique=False, exist_ok=True)
    op.create_index(op.f('ix_produtos_nome'), 'produtos', ['nome'], unique=False, exist_ok=True)

    # ### end Alembic commands ###


def downgrade() -> None:
    """Downgrade schema."""
    # ### Comandos Modificados Manualmente para Deploy em Produção ###

    # 1. Remove a coluna e a chave estrangeira da tabela 'produtos'.
    op.drop_constraint('fk_produtos_fornecedores_fornecedor_id', 'produtos', type_='foreignkey')
    op.drop_column('produtos', 'fornecedor_id')

    # 2. Remove as tabelas novas.
    op.drop_index(op.f('ix_ordens_compra_itens_id'), table_name='ordens_compra_itens')
    op.drop_table('ordens_compra_itens')
    op.drop_index(op.f('ix_ordens_compra_id'), table_name='ordens_compra')
    op.drop_table('ordens_compra')
    op.drop_index(op.f('ix_fornecedores_nome'), table_name='fornecedores')
    op.drop_index(op.f('ix_fornecedores_id'), table_name='fornecedores')
    op.drop_table('fornecedores')

    # NÃO iremos remover as tabelas antigas que já existiam, por segurança.
    # ### end Alembic commands ###